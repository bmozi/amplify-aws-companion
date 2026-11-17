"""Cloud-free model of the proposed separate publisher and probe OIDC trust.

Fictional claims are not signed GitHub tokens. This is not an IAM simulator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "infra/github-publisher/main.tf"
CASES = Path(__file__).with_name("cases.json")
SUBJECT = "repo:paper-owner@101/cloud-lab@202:ref:refs/heads/main"
PUBLISHER_WORKFLOW = "Publish the Amplify lab frontend"
PROBE_WORKFLOW = "Probe the Amplify reader identity without deploying"
PUBLISHER_JOB_REF = "paper-owner/cloud-lab/.github/workflows/reusable-amplify-publish.yml@refs/heads/main"


def workflow_sources() -> tuple[Path, Path, Path]:
    """Use the active private workflows or all three inert reader copies."""
    active = (ROOT / ".github/workflows/amplify-publish.yml",
              ROOT / ".github/workflows/probe-amplify-publisher-identity.yml",
              ROOT / ".github/workflows/reusable-amplify-publish.yml")
    inert = (ROOT / "examples/github-workflows/amplify-publish.yml",
             ROOT / "examples/github-workflows/probe-amplify-publisher-identity.yml",
             ROOT / "examples/github-workflows/reusable-amplify-publish.yml")
    present = tuple(path.is_file() for path in active)
    if all(present):
        for original, copy in zip(active, inert):
            if copy.is_file() and copy.read_bytes() != original.read_bytes():
                raise ValueError("Inert workflow copy differs from the active workflow")
        return active
    if any(present):
        raise ValueError("Only part of the active workflow set is present; review the lesson")
    if not all(path.is_file() for path in inert):
        raise ValueError("All three inert workflow copies are required in a reduced packet")
    return inert


def named_block(source: str, kind: str, name: str) -> str:
    marker = f'{kind} "{name}" {{'
    if source.count(marker) != 1:
        raise ValueError(f"Expected one Terraform {name} block")
    return source.split(marker, 1)[1].split("\n}\n\n", 1)[0]


def require_current_trust_shape(source: str) -> None:
    """Stop teaching from an old snapshot if the checked-in trust changes."""
    formula = '"repo:${var.github_owner}@${var.github_owner_id}/${var.github_repository}@${var.github_repository_id}:ref:refs/heads/${var.github_branch}"'
    if not re.search(r'github_subject\s*=\s*' + re.escape(formula), source):
        raise ValueError("Terraform subject formula changed; review the lesson")
    for local, expected in (("publisher_workflow_name", PUBLISHER_WORKFLOW),
                            ("probe_workflow_name", PROBE_WORKFLOW)):
        if not re.search(rf'{local}\s*=\s*"{re.escape(expected)}"', source):
            raise ValueError(f"Terraform {local} changed; review the lesson")
    if 'publisher_job_workflow_ref = "${var.github_owner}/${var.github_repository}/.github/workflows/reusable-amplify-publish.yml@refs/heads/${var.github_branch}"' not in source:
        raise ValueError("Terraform called-workflow path changed; review the lesson")
    publisher_path, probe_path, reusable_path = workflow_sources()
    for path, expected in ((publisher_path, PUBLISHER_WORKFLOW),
                           (probe_path, PROBE_WORKFLOW)):
        if path.read_text().splitlines()[0] != f"name: {expected}":
            raise ValueError(f"Workflow name differs from Terraform trust: {path}")
    probe_workflow = probe_path.read_text()
    publisher_workflow = publisher_path.read_text()
    reusable_workflow = reusable_path.read_text()
    if ("uses: ./.github/workflows/reusable-amplify-publish.yml" not in publisher_workflow or
            reusable_workflow.splitlines()[0] != "name: Reviewed Amplify publication job" or
            "workflow_call:" not in reusable_workflow or
            "  build:\n" not in reusable_workflow or
            reusable_workflow.count("github.workflow_ref == 'bmozi/aws-capabilities-lab/.github/workflows/amplify-publish.yml@refs/heads/main'") != 2 or
            "  publish:\n    needs: build\n" not in reusable_workflow or
            "archive_sha256:\n        required: true" in reusable_workflow or
            "  build:\n    if:" not in reusable_workflow or
            "    permissions:\n      contents: read\n    outputs:" not in reusable_workflow or
            "  publish:\n    needs: build\n    if:" not in reusable_workflow or
            "      id-token: write" not in reusable_workflow.split("  publish:\n", 1)[1] or
            "      id-token: write" in reusable_workflow.split("  publish:\n", 1)[0] or
            "      - name: Package the built site" not in reusable_workflow.split("  publish:\n", 1)[0] or
            "EXPECTED_ARCHIVE_SHA256: ${{ needs.build.outputs.archive_sha256 }}" not in reusable_workflow or
            "publisher-run-estimate.py" not in reusable_workflow or
            reusable_workflow.index("publisher-run-estimate.py") > reusable_workflow.index("configure-aws-credentials@")):
        raise ValueError("Reusable publisher boundary changed; review the lesson")
    if ("vars.AMPLIFY_PROBE_ENABLED == 'true'" not in probe_workflow or
            "role-to-assume: arn:aws:iam::${{ vars.AWS_LAB_EXPECTED_ACCOUNT_ID }}:role/AmplifyLabGitHubProbeReader" not in probe_workflow or
            "AWS_LAB_AMPLIFY_PUBLISH_ROLE_ARN" in probe_workflow):
        raise ValueError("Probe workflow is not held on its dedicated role")
    for document, role, workflow_local in (("github_trust", "publisher", "publisher_workflow_name"),
                                           ("probe_trust", "probe", "probe_workflow_name")):
        block = named_block(source, 'data "aws_iam_policy_document"', document)
        expected_conditions = 4 if role == "publisher" else 3
        if block.count("statement {") != 1 or block.count("condition {") != expected_conditions:
            raise ValueError(f"Terraform {document} statement/conditions changed")
        if ('effect  = "Allow"' not in block or
                'actions = ["sts:AssumeRoleWithWebIdentity"]' not in block or
                'type        = "Federated"' not in block or
                'identifiers = [local.github_oidc_provider_arn]' not in block):
            raise ValueError(f"Terraform {document} trust action or principal changed")
        pairs = set()
        for condition in re.findall(r'condition \{([^{}]+)\}', block, re.S):
            test = re.search(r'test\s*=\s*"([^"]+)"', condition)
            variable = re.search(r'variable\s*=\s*"([^"]+)"', condition)
            values = re.search(r'values\s*=\s*\[([^\]]+)\]', condition)
            if not (test and variable and values):
                raise ValueError("Terraform trust condition needs review")
            pairs.add((test.group(1), variable.group(1), values.group(1).strip()))
        expected = {
            ("StringEquals", "token.actions.githubusercontent.com:aud", '"sts.amazonaws.com"'),
            ("StringEquals", "token.actions.githubusercontent.com:sub", "local.github_subject"),
            ("StringEquals", "token.actions.githubusercontent.com:workflow", f"local.{workflow_local}"),
        }
        if role == "publisher":
            expected.add(("StringEquals", "token.actions.githubusercontent.com:job_workflow_ref", "local.publisher_job_workflow_ref"))
        if pairs != expected:
            raise ValueError(f"Terraform {document} conditions differ from this exercise")
        role_block = named_block(source, 'resource "aws_iam_role"', role)
        if f'assume_role_policy   = data.aws_iam_policy_document.{document}.json' not in role_block:
            raise ValueError(f"Terraform {role} uses another trust document")
    probe_policy = named_block(source, 'data "aws_iam_policy_document"', "probe_read")
    actions = set(re.findall(r'actions\s*=\s*\["([^"]+)"\]', probe_policy))
    if actions != {"amplify:GetJob", "freetier:GetAccountPlanState", "budgets:ViewBudget"}:
        raise ValueError("Probe policy actions differ from the read-only lesson")
    if ('resources = ["${local.branch_arn}/jobs/*"]' not in probe_policy or
            'resources = ["arn:aws:budgets::${var.account_id}:budget/${var.budget_name}"]' not in probe_policy):
        raise ValueError("Probe resource scope changed")
    publisher_policy = named_block(source, 'data "aws_iam_policy_document"', "publish")
    if 'actions   = ["amplify:CreateDeployment", "amplify:StartDeployment"]' not in publisher_policy:
        raise ValueError("Publisher write scope changed")


def evaluate(cases: list[dict[str, object]]) -> list[dict[str, object]]:
    results = []
    names = set()
    for case in cases:
        if set(case) != {"name", "aud", "sub", "workflow", "workflow_ref", "job_workflow_ref", "publish_flag"}:
            raise ValueError("Unexpected case shape")
        name = case["name"]
        if not isinstance(name, str) or name in names:
            raise ValueError("Case names must be unique strings")
        names.add(name)
        if any(not isinstance(case[key], str) for key in ("aud", "sub", "workflow", "workflow_ref", "job_workflow_ref")) or not isinstance(case["publish_flag"], bool):
            raise ValueError("Invalid fictional claim type")
        aud_ok = case["aud"] == "sts.amazonaws.com"
        sub_ok = case["sub"] == SUBJECT
        publisher_workflow_ok = case["workflow"] == PUBLISHER_WORKFLOW
        probe_workflow_ok = case["workflow"] == PROBE_WORKFLOW
        results.append({"name": name, "aud_matches": aud_ok, "sub_matches": sub_ok,
                        "publisher_name_match": aud_ok and sub_ok and publisher_workflow_ok,
                        "publisher_trust_match": aud_ok and sub_ok and publisher_workflow_ok and case["job_workflow_ref"] == PUBLISHER_JOB_REF,
                        "probe_trust_match": aud_ok and sub_ok and probe_workflow_ok})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=CASES)
    args = parser.parse_args()
    require_current_trust_shape(SOURCE.read_text())
    results = evaluate(json.loads(args.cases.read_text()))
    print(json.dumps({"model": "four publisher and three probe StringEquals conditions in proposed source trusts",
                      "scope": "Fictional unsigned claims; no GitHub token, STS call, IAM evaluation or publication",
                      "results": results}, indent=2))


if __name__ == "__main__":
    main()
