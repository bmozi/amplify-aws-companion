"""Cloud-free reconciliation of a fictional multi-destination release packet."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Destination:
    name: str
    operation: str
    image_digest: str
    capacity_ready: bool
    customer_check: bool


EXPECTED = ("test-east", "prod-east", "prod-west")
REVIEWED_IMAGE = "sha256:reviewed-42"
REVIEWED_SOURCE = "commit-reviewed-42"
REVIEWED_PLAN = "plan-reviewed-42"


def assess(operation_status, failed_instance_count, destinations,
           source_revision=REVIEWED_SOURCE, plan_revision=REVIEWED_PLAN,
           expected=EXPECTED):
    """Return a release decision from supplied receipts; perform no deployment."""
    reasons = []
    by_name = {destination.name: destination for destination in destinations}
    if source_revision != REVIEWED_SOURCE:
        reasons.append("Source revision differs from reviewed change")
    if plan_revision != REVIEWED_PLAN:
        reasons.append("Infrastructure plan differs from reviewed change")
    if len(by_name) != len(destinations):
        reasons.append("Duplicate destination receipt")
    if operation_status != "SUCCEEDED":
        reasons.append("Top-level operation has not succeeded")
    if failed_instance_count != 0:
        reasons.append("Top-level operation reports failed stack instances")
    if set(by_name) != set(expected):
        reasons.append("Destination receipts do not match the reviewed target set")
    for name in expected:
        receipt = by_name.get(name)
        if receipt is None:
            continue
        if receipt.operation != "CURRENT":
            reasons.append(f"{name}: destination operation is not current")
        if receipt.image_digest != REVIEWED_IMAGE:
            reasons.append(f"{name}: image differs from reviewed artifact")
        if not receipt.capacity_ready:
            reasons.append(f"{name}: usable capacity is unproven")
        if not receipt.customer_check:
            reasons.append(f"{name}: customer behavior is unproven")
    return not reasons, reasons


def clean_destinations():
    return [Destination(name, "CURRENT", REVIEWED_IMAGE, True, True) for name in EXPECTED]


if __name__ == "__main__":
    cases = [
        ("all receipts", "SUCCEEDED", 0, clean_destinations()),
        ("headline success with one failed instance", "SUCCEEDED", 1,
         clean_destinations()[:-1] + [Destination("prod-west", "OUTDATED", REVIEWED_IMAGE, False, False)]),
        ("missing destination", "SUCCEEDED", 0, clean_destinations()[:-1]),
        ("old image in production", "SUCCEEDED", 0,
         clean_destinations()[:-1] + [Destination("prod-west", "CURRENT", "sha256:old-41", True, True)]),
        ("green infrastructure, failed customer check", "SUCCEEDED", 0,
         clean_destinations()[:-1] + [Destination("prod-west", "CURRENT", REVIEWED_IMAGE, True, False)]),
    ]
    for label, operation, failures, receipts in cases:
        accepted, reasons = assess(operation, failures, receipts)
        print(f"{label}: {'ACCEPT' if accepted else 'HOLD'}")
        for reason in reasons:
            print("  -", reason)
