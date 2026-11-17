#!/usr/bin/env python3
"""Check declared coverage in a fictional control matrix; makes no AWS calls."""
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
ALLOWED = {"active", "missing", "stale", "exception", "not_applicable"}


def review(data):
    accounts, regions = data["accounts"], data["regions"]
    controls, observations = data["expected_controls"], data["observations"]
    max_age = data["max_age_hours"]
    expected = {(a, r, c) for a in accounts for r in regions for c in controls}
    by_key = {}
    issues = []
    for row in observations:
        key = (row["account"], row["region"], row["control"])
        if key not in expected:
            issues.append(("OUT_OF_SCOPE", key, "observation is outside the declared matrix"))
        if key in by_key:
            issues.append(("DUPLICATE", key, "more than one observation claims this scope"))
        by_key[key] = row
        if row["status"] not in ALLOWED:
            issues.append(("INVALID_STATUS", key, row["status"]))
        if row["status"] == "exception" and not row.get("compensating_control"):
            issues.append(("UNSUPPORTED_EXCEPTION", key, "name a compensating control"))

    for key in sorted(expected):
        row = by_key.get(key)
        if row is None:
            issues.append(("MISSING_ROW", key, "no scoped observation supplied"))
            continue
        status, age = row["status"], row.get("age_hours")
        if status == "active" and (age is None or age < 0 or age > max_age):
            issues.append(("STALE_EVIDENCE", key, f"age={age}; limit={max_age} hours"))
        elif status == "missing":
            issues.append(("CONTROL_MISSING", key, "declared required control is absent"))
        elif status == "stale":
            issues.append(("STALE_EVIDENCE", key, f"age={age}; limit={max_age} hours"))
        elif status == "exception":
            days = row.get("exception_expires_in_days")
            issues.append(("EXCEPTION_REVIEW", key, f"compensating={row.get('compensating_control')}; expires_in_days={days}"))
        elif status == "not_applicable" and not row.get("reason"):
            issues.append(("UNEXPLAINED_NA", key, "record why the control does not apply"))
    return issues, len(expected)


def main(path):
    data = json.loads(Path(path).read_text())
    issues, expected_count = review(data)
    print(f"Scenario: {data['scenario']}")
    print(f"Declared scope: {len(data['accounts'])} accounts x {len(data['regions'])} Regions x {len(data['expected_controls'])} controls = {expected_count} cells")
    if not issues:
        print("No matrix gaps found. This is not proof of AWS configuration or control effectiveness.")
        return 0
    for code, key, detail in issues:
        print(f"{code:22} {key[0]}/{key[1]}/{key[2]} — {detail}")
    print(f"Review items: {len(issues)}. Resolve or explicitly accept each one with evidence and an owner.")
    print("The checker validates supplied declarations only; it makes no AWS calls and does not judge policy semantics.")
    return 1


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "controls.json"
    raise SystemExit(main(target))
