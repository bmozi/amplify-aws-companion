"""Evaluate one fictional standby quote and two shared credit commitments.

No AWS API, price lookup, credit reservation or billing observation occurs.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path


REQUIRED_METERS = {
    "compute",
    "replica_backup_storage",
    "transfer",
    "dns_logs_alarms",
    "test_traffic_teardown_retained",
}


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def read_case(path: Path) -> dict:
    with path.open(encoding="utf-8") as source:
        return json.load(source, parse_float=Decimal, object_pairs_hook=unique_object)


def amount(value: object, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError(f"{label} needs an exact nonnegative decimal")
    try:
        number = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"{label} needs an exact nonnegative decimal") from error
    if not number.is_finite() or number < 0:
        raise ValueError(f"{label} needs an exact nonnegative decimal")
    return number


def evaluate(case: dict) -> dict:
    if not isinstance(case, dict) or not isinstance(case.get("meters_usd"), dict):
        raise ValueError("meters_usd must be an object")
    meters = case["meters_usd"]
    missing = REQUIRED_METERS - meters.keys()
    if missing:
        raise ValueError("missing meter groups: " + ", ".join(sorted(missing)))
    if any(not isinstance(key, str) or not key.strip() for key in meters):
        raise ValueError("meter group names must be nonempty strings")
    costs = {key: amount(value, f"meters_usd.{key}") for key, value in meters.items()}
    rate = amount(case.get("uncertainty_rate"), "uncertainty_rate")
    if rate > 1:
        raise ValueError("uncertainty_rate must be at most 1 in this exercise")
    other = amount(case.get("other_run_whole_estimate_usd"), "other_run_whole_estimate_usd")
    limit = amount(case.get("per_run_limit_usd"), "per_run_limit_usd")
    balance = amount(case.get("assumed_eligible_credit_balance_usd"), "assumed_eligible_credit_balance_usd")
    reserve = amount(case.get("reserve_floor_usd"), "reserve_floor_usd")
    subtotal = sum(costs.values(), Decimal("0"))
    allowance = subtotal * rate
    first = subtotal + allowance
    combined = first + other
    remaining = balance - combined
    first_fits = first <= limit
    other_fits = other <= limit
    reserve_survives = remaining >= reserve
    holds = []
    if not first_fits:
        holds.append("standby run exceeds its chosen per-run limit")
    if not other_fits:
        holds.append("other run exceeds its chosen per-run limit")
    if not reserve_survives:
        holds.append("combined commitments cross the chosen credit reserve")
    return {
        "meter_groups_counted": sorted(costs),
        "standby_subtotal_usd": format(subtotal, "f"),
        "standby_allowance_usd": format(allowance, "f"),
        "standby_whole_estimate_usd": format(first, "f"),
        "other_whole_estimate_usd": format(other, "f"),
        "combined_commitment_usd": format(combined, "f"),
        "assumed_credits_after_both_usd": format(remaining, "f"),
        "standby_within_per_run_limit": first_fits,
        "other_within_per_run_limit": other_fits,
        "combined_reserve_survives": reserve_survives,
        "arithmetic_holds": holds,
        "live_run_authorized": False,
        "evidence_limit": (
            "Fictional gross estimates and assumed eligible credits only; no current rates, "
            "credit applicability, account balance, scoped identity, active-run claim, "
            "resource behavior, cleanup or bill observed"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, nargs="?", default=Path(__file__).with_name("standby-cost.json"))
    args = parser.parse_args()
    print(json.dumps(evaluate(read_case(args.case)), indent=2))


if __name__ == "__main__":
    main()
