"""Compare collected publisher-role documents with a declared candidate; no AWS calls.

This is a source-drift screen, not an IAM policy evaluator or deploy approval.
"""
import argparse
import json
from pathlib import Path


ROLE = "AmplifyLabGitHubPublisher"
INLINE = "PublishOneAmplifyBranch"


def canonical(document):
    """Ignore document statement/action ordering while retaining every field."""
    if not isinstance(document, dict) or document.get("Version") != "2012-10-17":
        raise ValueError("Unsupported or missing IAM policy document")
    statements = document.get("Statement")
    if isinstance(statements, dict):
        statements = [statements]
    if not isinstance(statements, list):
        raise ValueError("IAM policy statements are missing")
    rows = []
    for statement in statements:
        if not isinstance(statement, dict):
            raise ValueError("IAM policy statement is malformed")
        row = dict(statement)
        for key in ("Action", "Resource"):
            if isinstance(row.get(key), list):
                row[key] = sorted(row[key])
        rows.append(json.dumps(row, sort_keys=True, separators=(",", ":")))
    return tuple(sorted(rows))


def review(receipt, expected_policy, *, account_id, subject):
    """Return document-alignment findings without deciding effective access."""
    reasons = []
    checks = receipt.get("checks", {})
    identity = checks.get("identity", {})
    if identity.get("account_id") != account_id or receipt.get("expected_account_id") != account_id:
        reasons.append("Receipt or caller account differs from the declared account")
    role = checks.get("publisher_role", {})
    if role.get("arn") != f"arn:aws:iam::{account_id}:role/{ROLE}":
        reasons.append("Publisher role ARN is missing or differs")
    if role.get("max_session_duration") != 3600:
        reasons.append("Publisher maximum session duration needs review")
    provider_arn = f"arn:aws:iam::{account_id}:oidc-provider/token.actions.githubusercontent.com"
    provider = checks.get("github_provider", {})
    detail = checks.get("github_provider_detail", {})
    if provider.get("exists") is not True or provider.get("arn") != provider_arn:
        reasons.append("GitHub provider existence or ARN is unverified")
    if detail.get("url") != "token.actions.githubusercontent.com" or "sts.amazonaws.com" not in detail.get("client_ids", []):
        reasons.append("GitHub provider URL or audience is unverified")
    expected_trust = {"Version": "2012-10-17", "Statement": [{
        "Effect": "Allow", "Action": "sts:AssumeRoleWithWebIdentity",
        "Principal": {"Federated": provider_arn},
        "Condition": {"StringEquals": {
            "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
            "token.actions.githubusercontent.com:sub": subject}}}]}
    try:
        if canonical(role.get("trust_document")) != canonical(expected_trust):
            reasons.append("Role trust differs from the declared GitHub subject and audience")
    except ValueError:
        reasons.append("Role trust document is unavailable or malformed")
    if role.get("permissions_boundary") is not None:
        reasons.append("A permissions boundary exists and needs separate evaluation")
    inline_names = checks.get("publisher_inline_names")
    if not isinstance(inline_names, list):
        reasons.append("Inline-policy inventory is unavailable")
    elif inline_names != [INLINE]:
        reasons.append("Inline-policy inventory has an unexpected name or count")
    try:
        if canonical(checks.get("publisher_inline_" + INLINE)) != canonical(expected_policy):
            reasons.append("Publisher inline policy differs from the declared candidate")
    except ValueError:
        reasons.append("Publisher inline policy document is unavailable or malformed")
    attached_names = checks.get("publisher_attached_names")
    if not isinstance(attached_names, list):
        reasons.append("Attached-policy inventory is unavailable")
    elif attached_names:
        reasons.append("An additional attached policy needs review")
    return {"document_alignment": "matched" if not reasons else "review_required",
            "reasons": reasons,
            "limit": "Document comparison only; resource policies, session/org controls and live service behavior are not evaluated"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="Private publisher-account-preflight JSON receipt")
    parser.add_argument("--expected-policy", type=Path, required=True)
    parser.add_argument("--account-id", required=True)
    parser.add_argument("--subject", required=True, help="Verified GitHub OIDC sub claim")
    args = parser.parse_args()
    result = review(json.loads(args.receipt.read_text()), json.loads(args.expected_policy.read_text()),
                    account_id=args.account_id, subject=args.subject)
    print(json.dumps(result, indent=2))
    return 0 if result["document_alignment"] == "matched" else 2


if __name__ == "__main__":
    raise SystemExit(main())
