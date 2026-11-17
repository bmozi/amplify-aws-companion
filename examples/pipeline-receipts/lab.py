"""Review fictional pipeline receipts without starting a CI service or AWS call."""
from dataclasses import dataclass, replace


SOURCE = "commit-C42"
ARTIFACT = "sha256:release-A42"
REQUIRED = ("pr-unit", "pr-static", "merge-build", "test-integration",
            "test-acceptance", "test-security")


@dataclass(frozen=True)
class Receipt:
    stage: str
    source: str
    artifact: str | None
    exit_code: int
    tests_run: int
    failed_tests: int
    environment: str


def clean_receipts():
    return [
        Receipt("pr-unit", SOURCE, None, 0, 24, 0, "local"),
        Receipt("pr-static", SOURCE, None, 0, 12, 0, "local"),
        Receipt("merge-build", SOURCE, ARTIFACT, 0, 0, 0, "build"),
        Receipt("test-integration", SOURCE, ARTIFACT, 0, 8, 0, "isolated"),
        Receipt("test-acceptance", SOURCE, ARTIFACT, 0, 5, 0, "isolated"),
        Receipt("test-security", SOURCE, ARTIFACT, 0, 3, 0, "isolated"),
    ]


def assess(receipts, *, performance_change=False, estimated_run_usd=None,
           credit_reserve_usd=None, stop_condition=False):
    """Return (accepted, reasons); every receipt is a supplied teaching fact."""
    reasons = []
    stages = {receipt.stage: receipt for receipt in receipts}
    if len(stages) != len(receipts):
        reasons.append("Duplicate stage receipt")
    required = set(REQUIRED) | ({"test-load"} if performance_change else set())
    missing = required - set(stages)
    if missing:
        reasons.append("Missing required stage: " + ", ".join(sorted(missing)))
    for stage in sorted(required & set(stages)):
        receipt = stages[stage]
        if receipt.source != SOURCE:
            reasons.append(f"{stage}: source differs from reviewed change")
        if stage.startswith("pr-"):
            if receipt.artifact is not None:
                reasons.append(f"{stage}: PR check claims a release artifact")
        elif receipt.artifact != ARTIFACT:
            reasons.append(f"{stage}: artifact differs from tested release")
        if receipt.exit_code != 0:
            reasons.append(f"{stage}: command failed with exit {receipt.exit_code}")
        if stage != "merge-build" and receipt.tests_run == 0:
            reasons.append(f"{stage}: no checks actually ran")
        if receipt.failed_tests != 0:
            reasons.append(f"{stage}: test report contains failures")
        if stage.startswith("test-") and receipt.environment != "isolated":
            reasons.append(f"{stage}: test environment is not isolated")
    if performance_change:
        if (estimated_run_usd is None or estimated_run_usd < 0 or estimated_run_usd > 5
                or credit_reserve_usd is None or credit_reserve_usd < 100
                or not stop_condition):
            reasons.append("Load drill lacks the personal-account cost and stop guard")
    return not reasons, reasons


if __name__ == "__main__":
    good = clean_receipts()
    for label, receipts, options in [
        ("complete fictional packet", good, {}),
        ("green command with failed test report",
         [replace(r, failed_tests=1) if r.stage == "test-acceptance" else r for r in good], {}),
        ("unreviewed rebuilt artifact",
         [replace(r, artifact="sha256:other") if r.stage == "test-acceptance" else r for r in good], {}),
        ("performance change without load evidence", good, {"performance_change": True}),
    ]:
        accepted, reasons = assess(receipts, **options)
        print(f"{label}: {'ACCEPT' if accepted else 'HOLD'}")
        for reason in reasons:
            print("  -", reason)
