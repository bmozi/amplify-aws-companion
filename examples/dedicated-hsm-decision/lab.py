"""Audit fictional HSM promises without creating or simulating AWS resources."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Plan:
    hsms_by_zone: tuple[int, ...]
    invented_ops_per_hsm: int
    promised_peak_ops: int
    latest_known_backup_age_hours: int
    promised_rpo_hours: int
    custom_store_connected: bool
    high_volume_s3_path: bool = False


def review(plan: Plan) -> tuple[str, ...]:
    """Find contradictory claims in supplied numbers; do not predict live service behavior."""
    if (not plan.hsms_by_zone or any(n < 0 for n in plan.hsms_by_zone)
            or min(plan.invented_ops_per_hsm, plan.promised_peak_ops,
                   plan.latest_known_backup_age_hours, plan.promised_rpo_hours) < 0):
        raise ValueError("Use nonnegative counts and an explicit zone list")
    observations = []
    total = sum(plan.hsms_by_zone)
    if total < 2 or sum(n > 0 for n in plan.hsms_by_zone) < 2:
        observations.append("multi-zone HSM availability claim unsupported")
    if total < 3:
        observations.append("three-HSM new-key durability guidance not met")
    if total and (total - 1) * plan.invented_ops_per_hsm < plan.promised_peak_ops:
        observations.append("single-HSM-loss toy capacity below promised peak")
    if total and (total - max(plan.hsms_by_zone)) * plan.invented_ops_per_hsm < plan.promised_peak_ops:
        observations.append("largest-zone-loss toy capacity below promised peak")
    if plan.latest_known_backup_age_hours > plan.promised_rpo_hours:
        observations.append("latest known backup older than promised RPO")
    if not plan.custom_store_connected:
        observations.append("disconnected custom store cannot serve fresh KMS cryptographic operations")
    if plan.high_volume_s3_path:
        observations.append("high-volume S3 path conflicts with custom-store performance guidance")
    return tuple(observations)


def fixture() -> Plan:
    return Plan((2, 1, 0), 40, 70, 27, 12, False)


def demonstrate() -> None:
    base = fixture()
    for label, plan in (
        ("first proposal", base),
        ("three zones", replace(base, hsms_by_zone=(1, 1, 1))),
        ("recent backup and connected store", replace(base, hsms_by_zone=(1, 1, 1),
                                                       latest_known_backup_age_hours=4,
                                                       custom_store_connected=True)),
    ):
        print(label + ":")
        for observation in review(plan):
            print("  - " + observation)
        if not review(plan):
            print("  - toy contradictions cleared; live outcome unproven")


if __name__ == "__main__":
    demonstrate()
