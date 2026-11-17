"""Read-only AWS snapshot for the manual Amplify publisher; never grants or deploys."""

if __name__ == '__main__':
    raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')


import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote


def policy_document(value):
    """Accept the CLI's decoded IAM JSON or its URL-encoded API form."""
    if isinstance(value, dict):
        document = value
    elif isinstance(value, str):
        try:
            document = json.loads(unquote(value))
        except json.JSONDecodeError as error:
            raise ValueError("IAM policy document is not valid JSON") from error
    else:
        raise ValueError("IAM policy document is missing")
    if not isinstance(document, dict) or "Statement" not in document:
        raise ValueError("IAM policy document lacks statements")
    return document


def aws_json(service, operation, *arguments, profile=None, region="us-east-2"):
    command = ["aws", service, operation, *arguments, "--region", region,
               "--output", "json", "--no-cli-pager"]
    if profile:
        command.extend(["--profile", profile])
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    if process.returncode:
        error = process.stderr
        if "AccessDenied" in error or "Unauthorized" in error:
            category = "access_denied"
        elif "NotFound" in error or "NoSuchEntity" in error or "not found" in error or "does not exist" in error:
            category = "not_found"
        elif "NoCredentials" in error or "ExpiredToken" in error or "session has expired" in error.lower():
            category = "credentials_unavailable"
        else:
            category = "cli_error"
        return {"error": category}
    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError:
        return {"error": "invalid_cli_json"}


def inspect(account_id, app_id, branch_name, *, profile=None, region="us-east-2",
            budget_name="AWS-Learning-Monthly-Cost", call=aws_json):
    if not re.fullmatch(r"[0-9]{12}", account_id):
        raise ValueError("Expected a 12-digit account ID")
    if not re.fullmatch(r"d[a-z0-9]+", app_id):
        raise ValueError("Expected an Amplify app ID")
    if not branch_name or any(character in branch_name for character in "?*"):
        raise ValueError("Expected one exact branch name")
    now = datetime.now(timezone.utc)
    report = {"checked_at_utc": now.isoformat(), "scope": "Read-only snapshot; not a deployment approval",
              "expected_account_id": account_id, "region": region, "app_id": app_id,
              "branch_name": branch_name, "checks": {}, "review_required": []}

    def query(name, service, operation, *arguments, query_region=region):
        result = call(service, operation, *arguments, profile=profile, region=query_region)
        if "error" in result:
            report["checks"][name] = result
            report["review_required"].append(name + ": " + result["error"])
            return None
        return result

    identity = query("identity", "sts", "get-caller-identity")
    if identity is None:
        return report
    report["checks"]["identity"] = {"account_id": identity.get("Account"),
                                      "arn": identity.get("Arn")}
    if identity.get("Account") != account_id:
        report["review_required"].append("Wrong account; no further AWS calls made")
        return report
    if identity.get("Arn", "").endswith(":root"):
        report["review_required"].append("Root identity: read-only inspection only; use a scoped role for deployment")

    plan = query("free_plan", "freetier", "get-account-plan-state", query_region="us-east-1")
    if plan is not None:
        credits = plan.get("accountPlanRemainingCredits") or {}
        report["checks"]["free_plan"] = {
            "account_id": plan.get("accountId"), "type": plan.get("accountPlanType"),
            "status": plan.get("accountPlanStatus"), "remaining_credits": credits,
            "expiration": plan.get("accountPlanExpirationDate")}
        if plan.get("accountId") != account_id or plan.get("accountPlanType") != "FREE" or plan.get("accountPlanStatus") != "ACTIVE":
            report["review_required"].append("Free plan identity or active status is not confirmed")
        try:
            remaining = Decimal(str(credits["amount"]))
            if credits.get("unit") != "USD" or not remaining.is_finite() or remaining < Decimal("100"):
                report["review_required"].append("USD 100 credit reserve is not confirmed")
        except (KeyError, InvalidOperation, TypeError):
            report["review_required"].append("USD credit balance is unavailable")
        try:
            expiration = datetime.fromisoformat(plan["accountPlanExpirationDate"].replace("Z", "+00:00"))
            if expiration.tzinfo is None or expiration <= now:
                report["review_required"].append("Free plan expiration is missing or passed")
        except (KeyError, TypeError, ValueError):
            report["review_required"].append("Free plan expiration cannot be read")

    # The aggregate Free-plan balance does not describe each credit's product
    # eligibility or expiration. Keep this owner-side read out of the narrowly
    # scoped GitHub publisher role and save the result only in the private receipt.
    credit_start = int((now - timedelta(days=364)).timestamp())
    terms = query("credit_terms", "billing", "get-credits", "--account-id", account_id,
                  "--start-date", str(credit_start), "--no-payer-account-flag",
                  query_region="us-east-1")
    if terms is not None:
        items = terms.get("credits")
        if not isinstance(items, list):
            report["checks"]["credit_terms"] = {"error": "missing_credit_list"}
            report["review_required"].append("Credit terms response has no usable credit list")
        elif any(not isinstance(item, dict) or item.get("accountId") != account_id for item in items):
            report["checks"]["credit_terms"] = {"error": "credit_account_mismatch"}
            report["review_required"].append("Credit terms contain a different or missing account ID")
        else:
            report["checks"]["credit_terms"] = {
                "queried_account_id": account_id, "start_date_epoch": credit_start,
                "payer_account_flag": False, "credits": items,
            }
            if not items:
                report["review_required"].append("No per-credit terms returned; do not infer service eligibility")
            else:
                report["review_required"].append(
                    "Review each credit's enabled status, remaining amount, expiration, applicable products and offer terms for the selected run")

    app = query("app", "amplify", "get-app", "--app-id", app_id)
    if app is not None:
        item = app.get("app") or {}
        report["checks"]["app"] = {"app_id": item.get("appId"), "arn": item.get("appArn"),
                                    "repository": item.get("repository"),
                                    "auto_branch_creation": item.get("enableAutoBranchCreation")}
        if item.get("appId") != app_id or item.get("appArn") != f"arn:aws:amplify:{region}:{account_id}:apps/{app_id}":
            report["review_required"].append("Amplify app identity does not match the expected target")
        if item.get("repository"):
            report["review_required"].append("Amplify app has a repository connection; inspect automatic build behavior")
        if item.get("enableAutoBranchCreation") is not False:
            report["review_required"].append("Automatic branch creation is not confirmed off")

    branch = query("branch", "amplify", "get-branch", "--app-id", app_id,
                   "--branch-name", branch_name)
    if branch is not None:
        item = branch.get("branch") or {}
        report["checks"]["branch"] = {"branch_name": item.get("branchName"),
                                       "arn": item.get("branchArn"),
                                       "auto_build": item.get("enableAutoBuild"),
                                       "pull_request_preview": item.get("enablePullRequestPreview")}
        expected_arn = f"arn:aws:amplify:{region}:{account_id}:apps/{app_id}/branches/{branch_name}"
        if item.get("branchName") != branch_name or item.get("branchArn") != expected_arn:
            report["review_required"].append("Amplify branch identity does not match the expected target")
        if item.get("enableAutoBuild") is not False or item.get("enablePullRequestPreview") is not False:
            report["review_required"].append("Automatic build or preview is not confirmed off")

    providers = query("github_provider", "iam", "list-open-id-connect-providers")
    if providers is not None:
        expected_arn = f"arn:aws:iam::{account_id}:oidc-provider/token.actions.githubusercontent.com"
        listed_items = providers.get("OpenIDConnectProviderList")
        if not isinstance(listed_items, list):
            report["checks"]["github_provider"] = {"error": "missing_provider_list"}
            report["review_required"].append("GitHub provider inventory is incomplete")
        else:
            found = expected_arn in [item.get("Arn") for item in listed_items]
            report["checks"]["github_provider"] = {"exists": found, "arn": expected_arn if found else None}
        if isinstance(listed_items, list) and found:
            provider = query("github_provider_detail", "iam", "get-open-id-connect-provider",
                             "--open-id-connect-provider-arn", expected_arn)
            if provider is not None:
                report["checks"]["github_provider_detail"] = {
                    "url": provider.get("Url"), "client_ids": provider.get("ClientIDList")}
                if provider.get("Url") != "token.actions.githubusercontent.com" or "sts.amazonaws.com" not in provider.get("ClientIDList", []):
                    report["review_required"].append("Existing GitHub provider URL/audience needs review")

    role = query("publisher_role", "iam", "get-role", "--role-name", "AmplifyLabGitHubPublisher")
    if role is not None:
        item = role.get("Role") or {}
        report["checks"]["publisher_role"] = {
            "arn": item.get("Arn"), "role_id": item.get("RoleId"),
            "max_session_duration": item.get("MaxSessionDuration"),
            "permissions_boundary": item.get("PermissionsBoundary")}
        try:
            report["checks"]["publisher_role"]["trust_document"] = policy_document(item.get("AssumeRolePolicyDocument"))
        except ValueError as error:
            report["review_required"].append("Publisher trust document unavailable: " + str(error))

        inline = query("publisher_inline_names", "iam", "list-role-policies",
                       "--role-name", "AmplifyLabGitHubPublisher")
        if inline is not None:
            names = inline.get("PolicyNames")
            if not isinstance(names, list) or inline.get("IsTruncated") or inline.get("NextToken"):
                report["review_required"].append("Publisher inline-policy inventory is incomplete")
            else:
                report["checks"]["publisher_inline_names"] = names
                for name in names:
                    result = query("publisher_inline_" + name, "iam", "get-role-policy",
                                   "--role-name", "AmplifyLabGitHubPublisher", "--policy-name", name)
                    if result is not None:
                        try:
                            report["checks"]["publisher_inline_" + name] = policy_document(result.get("PolicyDocument"))
                        except ValueError as error:
                            report["review_required"].append(name + ": " + str(error))

        attached = query("publisher_attached_names", "iam", "list-attached-role-policies",
                         "--role-name", "AmplifyLabGitHubPublisher")
        if attached is not None:
            policies = attached.get("AttachedPolicies")
            if not isinstance(policies, list) or attached.get("IsTruncated") or attached.get("NextToken"):
                report["review_required"].append("Publisher attached-policy inventory is incomplete")
            else:
                report["checks"]["publisher_attached_names"] = policies
                for index, policy in enumerate(policies):
                    arn = policy.get("PolicyArn")
                    if not isinstance(arn, str):
                        report["review_required"].append("Attached policy ARN is missing")
                        continue
                    metadata = query(f"publisher_managed_{index}_metadata", "iam", "get-policy", "--policy-arn", arn)
                    if metadata is None:
                        continue
                    version = (metadata.get("Policy") or {}).get("DefaultVersionId")
                    if not isinstance(version, str):
                        report["review_required"].append("Default version missing for " + arn)
                        continue
                    result = query(f"publisher_managed_{index}_version", "iam", "get-policy-version",
                                   "--policy-arn", arn, "--version-id", version)
                    if result is not None:
                        try:
                            report["checks"][f"publisher_managed_{index}_version"] = {
                                "policy_arn": arn, "version": version,
                                "document": policy_document((result.get("PolicyVersion") or {}).get("Document"))}
                        except ValueError as error:
                            report["review_required"].append(arn + ": " + str(error))

        boundary = item.get("PermissionsBoundary") or {}
        boundary_arn = boundary.get("PermissionsBoundaryArn")
        if boundary_arn:
            metadata = query("publisher_boundary_metadata", "iam", "get-policy", "--policy-arn", boundary_arn)
            if metadata is not None:
                version = (metadata.get("Policy") or {}).get("DefaultVersionId")
                if not isinstance(version, str):
                    report["review_required"].append("Publisher boundary default version is missing")
                else:
                    result = query("publisher_boundary_version", "iam", "get-policy-version",
                                   "--policy-arn", boundary_arn, "--version-id", version)
                    if result is not None:
                        try:
                            report["checks"]["publisher_boundary_version"] = {
                                "policy_arn": boundary_arn, "version": version,
                                "document": policy_document((result.get("PolicyVersion") or {}).get("Document"))}
                        except ValueError as error:
                            report["review_required"].append("Publisher boundary: " + str(error))

        report["review_required"].append("Review collected role trust, inline and attached permissions, boundary, other applicable controls and live session behavior before publication")

    budget = query("budget", "budgets", "describe-budget", "--account-id", account_id,
                   "--budget-name", budget_name, query_region="us-east-1")
    if budget is not None:
        item = budget.get("Budget") or {}
        types = item.get("CostTypes") or {}
        if not isinstance(types, dict):
            types = {}
        report["checks"]["budget"] = {"name": item.get("BudgetName"),
                                        "limit": item.get("BudgetLimit"),
                                        "actual_spend": (item.get("CalculatedSpend") or {}).get("ActualSpend"),
                                        "budget_type": item.get("BudgetType"),
                                        "time_unit": item.get("TimeUnit"),
                                        "include_credit": types.get("IncludeCredit"),
                                        "include_refund": types.get("IncludeRefund")}
        if item.get("BudgetName") != budget_name or types.get("IncludeCredit") is not False or types.get("IncludeRefund") is not False:
            report["review_required"].append("Pre-credit budget configuration needs review")
        try:
            limit = item["BudgetLimit"]
            if not isinstance(limit, dict):
                raise ValueError("Budget limit is missing")
            if limit.get("Unit") != "USD" or Decimal(str(limit["Amount"])) != Decimal("50"):
                report["review_required"].append("Expected USD 50 monthly budget limit needs review")
        except (KeyError, InvalidOperation, TypeError, ValueError):
            report["review_required"].append("Budget limit is unavailable")
        if item.get("BudgetType") != "COST" or item.get("TimeUnit") != "MONTHLY":
            report["review_required"].append("Expected monthly cost budget type is not confirmed")
        try:
            actual = (item.get("CalculatedSpend") or {})["ActualSpend"]
            if not isinstance(actual, dict):
                raise ValueError("Actual spend is missing")
            if actual.get("Unit") != "USD":
                raise ValueError("Actual spend is not in USD")
            amount = Decimal(str(actual["Amount"]))
            if not amount.is_finite() or amount < 0:
                raise ValueError("Actual spend is invalid")
            limit = item["BudgetLimit"]
            if not isinstance(limit, dict):
                raise ValueError("Budget limit is missing")
            limit_amount = Decimal(str(limit["Amount"]))
            if not limit_amount.is_finite() or limit_amount < 0 or limit["Unit"] != "USD":
                raise ValueError("Budget limit is invalid")
            gross_room = limit_amount - amount
            after_buffer = gross_room - Decimal("5")
            report["checks"]["budget"]["gross_room_usd"] = str(gross_room)
            report["checks"]["budget"]["room_after_usd_5_buffer_usd"] = str(after_buffer)
            if after_buffer < Decimal("5"):
                report["review_required"].append(
                    "Reported budget room after USD 5 buffer is below a USD 5 whole-run estimate; hold new cloud runs")
        except (KeyError, InvalidOperation, TypeError, ValueError):
            report["review_required"].append("Budget actual spend or comparable USD limit is unavailable; hold new cloud runs")
        report["review_required"].append(
            "Budgets actual spend can lag; arithmetic room is not a hard cap or deployment approval")

    report["review_required"].append("Still verify current prices, full run estimate, role authority, GitHub gate, cleanup and delayed billing")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account-id", required=True)
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--profile")
    parser.add_argument("--budget-name", default="AWS-Learning-Monthly-Cost")
    parser.add_argument("--output-dir", type=Path, default=Path("evidence/publisher-account"))
    args = parser.parse_args()
    report = inspect(args.account_id, args.app_id, args.branch, profile=args.profile,
                     region=args.region, budget_name=args.budget_name)
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
