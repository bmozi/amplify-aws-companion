"""Cloud-free teaching model for a narrow CloudFormation template change.

This is not cfn-lint, a CloudFormation change set, drift detection, or AWS access.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASELINE = HERE / "baseline.json"
KNOWN_UPDATE_BEHAVIOR = {
    "Tags": "No interruption",
    "BucketName": "Replacement",
    "PublicAccessBlockConfiguration": "No interruption",
}


def load_baseline() -> dict:
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def proposed_template(case: str) -> dict:
    template = copy.deepcopy(load_baseline())
    props = template["Resources"]["ArchiveBucket"]["Properties"]
    if case == "tag":
        props["Tags"].append({"Key": "Review", "Value": "approved-fictional"})
    elif case == "name":
        props["BucketName"] = {"Fn::Sub": "${AWS::StackName}-replacement-study"}
    elif case == "public":
        props["PublicAccessBlockConfiguration"]["BlockPublicPolicy"] = False
    elif case == "transport":
        template["Resources"]["TransportPolicy"]["Properties"]["PolicyDocument"]["Statement"] = []
    elif case == "unknown":
        props["UnfamiliarFutureProperty"] = "unknown"
    else:
        raise ValueError(f"unknown study case: {case}")
    return template


def review(case: str) -> dict:
    old = load_baseline()
    new = proposed_template(case)
    before = old["Resources"]["ArchiveBucket"]["Properties"]
    after = new["Resources"]["ArchiveBucket"]["Properties"]
    changed = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
    changed_other_resources = sorted(
        name for name in old["Resources"].keys() | new["Resources"].keys()
        if name != "ArchiveBucket" and old["Resources"].get(name) != new["Resources"].get(name)
    )
    classifications = {key: KNOWN_UPDATE_BEHAVIOR.get(key, "Unknown: stop and consult current resource reference") for key in changed}
    public_block = after.get("PublicAccessBlockConfiguration", {})
    security_hold = not all(public_block.get(key) is True for key in (
        "BlockPublicAcls", "BlockPublicPolicy", "IgnorePublicAcls", "RestrictPublicBuckets"
    ))
    replacement_candidate = "BucketName" in changed
    unknown = any(key not in KNOWN_UPDATE_BEHAVIOR for key in changed)
    decision = "HOLD" if security_hold or replacement_candidate or unknown or changed_other_resources else "REVIEW_WITH_CHANGE_SET"
    return {
        "case": case,
        "changed_bucket_properties": changed,
        "changed_other_resources": changed_other_resources,
        "documented_property_update_behavior": classifications,
        "decision": decision,
        "reason": (
            "Public-access guard weakened" if security_hold else
            "Replacement may create a new empty bucket while the old one remains retained" if replacement_candidate else
            "A separate resource changed outside this bucket-property model" if changed_other_resources else
            "Property behavior is not in this narrow study" if unknown else
            "A tag-only candidate still needs a real change set and owner review"
        ),
        "old_bucket_object_count_observed": None,
        "new_bucket_object_count_observed": None,
        "real_change_set_observed": False,
        "customer_read_observed": False,
        "aws_resources_created": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", nargs="?", choices=("tag", "name", "public", "transport", "unknown"))
    args = parser.parse_args()
    cases = (args.case,) if args.case else ("tag", "name", "public", "transport", "unknown")
    for case in cases:
        print(json.dumps(review(case), indent=2))


if __name__ == "__main__":
    main()
