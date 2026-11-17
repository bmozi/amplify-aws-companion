"""Read-only inventory of the caller, CDK bootstrap roles and selected stack."""

if __name__ == '__main__':
    raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')


import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote


BOOTSTRAP_ROLE_IDS = (
    "CloudFormationExecutionRole", "DeploymentActionRole", "FilePublishingRole",
    "ImagePublishingRole", "LookupRole",
)


def aws_json(service, operation, *arguments, profile, region):
    command = ["aws", service, operation, *arguments, "--region", region,
               "--output", "json", "--no-cli-pager"]
    if profile:
        command += ["--profile", profile]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        return {"error": result.stderr.strip()[:500] or "AWS CLI call failed"}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "AWS CLI returned invalid JSON"}


def document(value):
    result = None
    if isinstance(value, dict):
        result = value
    elif isinstance(value, str):
        try:
            result = json.loads(unquote(value))
        except json.JSONDecodeError:
            result = None
    if isinstance(result, dict) and "Statement" in result:
        return result
    raise ValueError("IAM policy document unavailable")


def inspect(account_id, *, profile=None, region="us-east-2", stack_name=None, call=aws_json):
    if not re.fullmatch(r"[0-9]{12}", account_id):
        raise ValueError("Expected a 12-digit account ID")
    if stack_name is not None and not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]{0,127}", stack_name):
        raise ValueError("Expected one exact CloudFormation stack name")
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "expected_account_id": account_id, "region": region, "stack_name": stack_name,
              "scope": "Read-only inventory; not an effective-permissions verdict or deployment approval",
              "checks": {}, "review_required": []}

    def query(label, service, operation, *args):
        value = call(service, operation, *args, profile=profile, region=region)
        if not isinstance(value, dict) or "error" in value:
            report["checks"][label] = value
            report["review_required"].append(label + ": read unavailable")
            return None
        return value

    identity = query("identity", "sts", "get-caller-identity")
    if identity is None:
        return report
    arn = identity.get("Arn", "")
    report["checks"]["identity"] = {"account_id": identity.get("Account"), "arn": arn}
    if identity.get("Account") != account_id:
        report["review_required"].append("Wrong account; no further AWS calls made")
        return report
    match = re.fullmatch(rf"arn:aws:sts::{account_id}:assumed-role/([^/]+)/[^/]+", arn)
    if not match:
        report["review_required"].append("Caller is not an assumed-role session; no deployment")
    else:
        report["checks"]["caller_role_name"] = match.group(1)

    def policy_version(label, policy_arn):
        metadata = query(label + "_metadata", "iam", "get-policy", "--policy-arn", policy_arn)
        if metadata is None:
            return
        version = (metadata.get("Policy") or {}).get("DefaultVersionId")
        if not isinstance(version, str):
            report["review_required"].append(label + ": default version missing")
            return
        body = query(label + "_version", "iam", "get-policy-version",
                     "--policy-arn", policy_arn, "--version-id", version)
        if body is not None:
            try:
                report["checks"][label + "_version"] = {
                    "policy_arn": policy_arn, "version": version,
                    "document": document((body.get("PolicyVersion") or {}).get("Document"))}
            except ValueError:
                report["review_required"].append(label + ": policy document unavailable")

    def read_role(label, role_name, *, expected_arn=None):
        role = query(label, "iam", "get-role", "--role-name", role_name)
        if role is None:
            return None
        item = role.get("Role") or {}
        role_arn = item.get("Arn")
        prefix = f"arn:aws:iam::{account_id}:role/"
        if (not isinstance(role_arn, str) or not role_arn.startswith(prefix) or
                role_arn.split("/")[-1] != role_name or
                (expected_arn is not None and role_arn != expected_arn)):
            report["review_required"].append(label + ": role ARN does not match expected account/name")
            return None
        summary = {"arn": role_arn, "role_id": item.get("RoleId"),
                   "permissions_boundary": item.get("PermissionsBoundary")}
        try:
            summary["trust_document"] = document(item.get("AssumeRolePolicyDocument"))
        except ValueError:
            report["review_required"].append(label + ": trust document unavailable")
        report["checks"][label] = summary

        attached = query(label + "_attached", "iam", "list-attached-role-policies",
                         "--role-name", role_name)
        if attached is not None:
            policies = attached.get("AttachedPolicies")
            if not isinstance(policies, list) or attached.get("IsTruncated") or attached.get("NextToken"):
                report["review_required"].append(label + ": attached-policy inventory incomplete")
            else:
                report["checks"][label + "_attached"] = policies
                for index, policy in enumerate(policies):
                    policy_arn = policy.get("PolicyArn") if isinstance(policy, dict) else None
                    if not isinstance(policy_arn, str):
                        report["review_required"].append(label + ": attached policy ARN missing")
                        continue
                    if policy_arn == "arn:aws:iam::aws:policy/AdministratorAccess":
                        report["review_required"].append(label + ": AdministratorAccess attached")
                    policy_version(f"{label}_attached_{index}", policy_arn)

        inline = query(label + "_inline_names", "iam", "list-role-policies",
                       "--role-name", role_name)
        if inline is not None:
            names = inline.get("PolicyNames")
            if not isinstance(names, list) or inline.get("IsTruncated") or inline.get("NextToken"):
                report["review_required"].append(label + ": inline-policy inventory incomplete")
            else:
                report["checks"][label + "_inline_names"] = names
                for index, name in enumerate(names):
                    if not isinstance(name, str):
                        report["review_required"].append(label + ": inline policy name malformed")
                        continue
                    body = query(f"{label}_inline_{index}", "iam", "get-role-policy",
                                 "--role-name", role_name, "--policy-name", name)
                    if body is not None:
                        try:
                            report["checks"][f"{label}_inline_{index}"] = {
                                "name": name, "document": document(body.get("PolicyDocument"))}
                        except ValueError:
                            report["review_required"].append(label + ": inline policy document unavailable")

        boundary = item.get("PermissionsBoundary") or {}
        boundary_arn = boundary.get("PermissionsBoundaryArn") if isinstance(boundary, dict) else None
        if boundary_arn:
            policy_version(label + "_boundary", boundary_arn)
        return role_arn

    discovered = {}
    for logical_id in BOOTSTRAP_ROLE_IDS:
        label = "bootstrap_" + logical_id
        response = query(label + "_resource", "cloudformation", "describe-stack-resource",
                         "--stack-name", "CDKToolkit", "--logical-resource-id", logical_id)
        if response is None:
            continue
        item = response.get("StackResourceDetail") or {}
        physical_id = item.get("PhysicalResourceId")
        report["checks"][label + "_resource"] = {
            "stack_id": item.get("StackId"), "logical_id": item.get("LogicalResourceId"),
            "resource_type": item.get("ResourceType"), "physical_id": physical_id}
        stack_prefix = f"arn:aws:cloudformation:{region}:{account_id}:stack/CDKToolkit/"
        if (item.get("LogicalResourceId") != logical_id or
                item.get("ResourceType") != "AWS::IAM::Role" or
                not str(item.get("StackId", "")).startswith(stack_prefix) or
                not isinstance(physical_id, str) or
                not re.fullmatch(r"[\w+=,.@-]+", physical_id)):
            report["review_required"].append(label + ": resource identity unexpected; IAM read skipped")
            continue
        discovered[logical_id] = read_role(label, physical_id)

    if stack_name:
        response = query("target_stack", "cloudformation", "describe-stacks",
                         "--stack-name", stack_name)
        if response is not None:
            stacks = response.get("Stacks")
            prefix = f"arn:aws:cloudformation:{region}:{account_id}:stack/{stack_name}/"
            if (not isinstance(stacks, list) or len(stacks) != 1 or
                    not isinstance(stacks[0], dict) or stacks[0].get("StackName") != stack_name or
                    not str(stacks[0].get("StackId", "")).startswith(prefix)):
                report["review_required"].append("Target stack identity unexpected; role read skipped")
            else:
                stack = stacks[0]
                service_arn = stack.get("RoleARN")
                report["checks"]["target_stack"] = {
                    "stack_id": stack.get("StackId"), "stack_status": stack.get("StackStatus"),
                    "service_role_arn": service_arn}
                if service_arn:
                    if service_arn in discovered.values():
                        report["checks"]["target_stack"]["bootstrap_role_match"] = [
                            key for key, value in discovered.items() if value == service_arn]
                    else:
                        prefix = f"arn:aws:iam::{account_id}:role/"
                        if not isinstance(service_arn, str) or not service_arn.startswith(prefix):
                            report["review_required"].append("Target stack service role is outside expected account")
                        else:
                            read_role("target_service_role", service_arn.split("/")[-1],
                                      expected_arn=service_arn)
                else:
                    report["review_required"].append(
                        "Target stack has no associated service role in this response; review caller-path authority")

    report["review_required"].append(
        "Review caller and stack operators, every CDK role, other IAM controls and live allow/deny behavior")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account-id", required=True)
    parser.add_argument("--profile")
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--stack-name", help="Exact backend CloudFormation stack to inspect, when known")
    parser.add_argument("--output-dir", type=Path, default=Path("evidence/backend-role"))
    args = parser.parse_args()
    report = inspect(args.account_id, profile=args.profile, region=args.region,
                     stack_name=args.stack_name)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-read-only.json")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as output:
        output.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"saved_to": str(path), "checks": list(report["checks"]),
                      "review_required": report["review_required"]}, indent=2))
    return 0 if report["checks"].get("identity", {}).get("account_id") == args.account_id else 2


if __name__ == "__main__":
    raise SystemExit(main())
