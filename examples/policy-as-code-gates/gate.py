"""Tiny offline specimen: inspect two template properties, not AWS policy enforcement."""

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BLOCK_KEYS = ("BlockPublicAcls", "BlockPublicPolicy", "IgnorePublicAcls", "RestrictPublicBuckets")


def inspect_template(template):
    resources = template.get("Resources")
    if not isinstance(resources, dict):
        raise ValueError("A CloudFormation-shaped Resources map is required")
    findings = []
    for logical_id, resource in resources.items():
        if resource.get("Type") != "AWS::S3::Bucket":
            continue
        props = resource.get("Properties", {})
        if not props.get("BucketEncryption"):
            findings.append(f"{logical_id}: BucketEncryption absent")
        block = props.get("PublicAccessBlockConfiguration", {})
        if any(block.get(key) is not True for key in BLOCK_KEYS):
            findings.append(f"{logical_id}: all four PublicAccessBlockConfiguration flags must be true")
    return findings


def main():
    template = json.loads((HERE / "template.json").read_text())
    findings = inspect_template(template)
    if findings:
        print("Local specimen rejected template: " + "; ".join(findings))
        raise SystemExit(1)
    print("Local specimen passed two declared bucket-property checks; no AWS Hook, policy, resource or drift was evaluated")


if __name__ == "__main__":
    main()
