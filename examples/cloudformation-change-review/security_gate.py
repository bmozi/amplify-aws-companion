"""Local security-invariant screen for the fictional archive template.

This intentionally checks the lesson's specific design contract. It is not
CloudFormation Guard, schema validation, an effective-policy test, or AWS access.
"""

from __future__ import annotations

import json

from review import proposed_template


PUBLIC_BLOCK_KEYS = (
    "BlockPublicAcls",
    "BlockPublicPolicy",
    "IgnorePublicAcls",
    "RestrictPublicBuckets",
)


def findings(template: dict) -> list[str]:
    resources = template.get("Resources", {})
    bucket = resources.get("ArchiveBucket", {})
    policy = resources.get("TransportPolicy", {})
    props = bucket.get("Properties", {})
    issues = []

    public = props.get("PublicAccessBlockConfiguration", {})
    for key in PUBLIC_BLOCK_KEYS:
        if public.get(key) is not True:
            issues.append(f"ArchiveBucket.{key}: public-access block must be true")

    encryption = props.get("BucketEncryption", {}).get("ServerSideEncryptionConfiguration", [])
    if not any(
        item.get("ServerSideEncryptionByDefault", {}).get("SSEAlgorithm") in {"AES256", "aws:kms"}
        for item in encryption if isinstance(item, dict)
    ):
        issues.append("ArchiveBucket.BucketEncryption: default encryption is missing")
    if props.get("VersioningConfiguration", {}).get("Status") != "Enabled":
        issues.append("ArchiveBucket.VersioningConfiguration: versioning must be enabled")

    for name, resource in (("ArchiveBucket", bucket), ("TransportPolicy", policy)):
        for attribute in ("DeletionPolicy", "UpdateReplacePolicy"):
            if resource.get(attribute) != "Retain":
                issues.append(f"{name}.{attribute}: explicit retention is required for this study")

    if policy.get("Type") != "AWS::S3::BucketPolicy":
        issues.append("TransportPolicy.Type: expected a separate S3 bucket policy")
    policy_props = policy.get("Properties", {})
    if policy_props.get("Bucket") != {"Ref": "ArchiveBucket"}:
        issues.append("TransportPolicy.Bucket: must target ArchiveBucket")
    statements = policy_props.get("PolicyDocument", {}).get("Statement", [])
    expected_resources = [
        {"Fn::GetAtt": ["ArchiveBucket", "Arn"]},
        {"Fn::Sub": "${ArchiveBucket.Arn}/*"},
    ]
    transport_deny = any(
        statement.get("Effect") == "Deny"
        and statement.get("Principal") == "*"
        and statement.get("Action") == "s3:*"
        and statement.get("Resource") == expected_resources
        and statement.get("Condition", {}).get("Bool", {}).get("aws:SecureTransport") == "false"
        for statement in statements if isinstance(statement, dict)
    )
    if not transport_deny:
        issues.append("TransportPolicy.PolicyDocument: expected non-TLS deny for bucket and objects")
    return issues


def main() -> None:
    for case in ("tag", "name", "public", "transport", "unknown"):
        issues = findings(proposed_template(case))
        print(json.dumps({"case": case, "local_security_gate": "HOLD" if issues else "PASS",
                          "findings": issues}))


if __name__ == "__main__":
    main()
