"""Cost arithmetic for declared fictional request counts, not a CloudFront simulator."""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def nonnegative_money(value: object, field: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{field} must be a finite nonnegative amount") from error
    if not number.is_finite() or number < 0:
        raise ValueError(f"{field} must be a finite nonnegative amount")
    return number


def count(value: object, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} must be a nonnegative integer")
    return value


def estimate(case: dict) -> dict:
    if type(case.get("cacheable")) is not bool:
        raise ValueError("cacheable must be a Boolean teaching assumption")
    viewers = count(case.get("viewer_requests"), "viewer_requests")
    misses = count(case.get("regional_cache_misses"), "regional_cache_misses")
    shield_origin = count(case.get("estimated_origin_requests_with_shield"), "estimated_origin_requests_with_shield")
    shield_billable = count(case.get("estimated_billable_shield_requests"), "estimated_billable_shield_requests")
    if misses > viewers or shield_origin > misses or shield_billable > misses:
        raise ValueError("Request counts exceed their declared upstream count")
    origin_rate = nonnegative_money(case.get("origin_work_usd_per_1000_requests"), "origin_work_usd_per_1000_requests")
    shield_rate = nonnegative_money(case.get("shield_usd_per_10000_requests"), "shield_usd_per_10000_requests")
    origin_without = Decimal(misses) * origin_rate / 1000
    origin_with = Decimal(shield_origin) * origin_rate / 1000
    shield_cost = Decimal(shield_billable) * shield_rate / 10000
    total_with = origin_with + shield_cost
    avoided = misses - shield_origin
    return {
        "id": case["id"],
        "viewer_requests": viewers,
        "regional_cache_misses": misses,
        "miss_fraction_of_viewers": str(Decimal(misses) / viewers) if viewers else None,
        "origin_requests_avoided_assumed": avoided,
        "break_even_origin_work_usd_per_1000_requests": str(shield_cost * 1000 / avoided) if avoided else None,
        "break_even_interpretation": (
            "threshold" if avoided else
            "no rate breaks even: added Shield cost with no avoided requests" if shield_cost else
            "all rates tie: no added Shield cost and no avoided requests"
        ),
        "origin_work_without_usd": str(origin_without),
        "origin_work_with_usd": str(origin_with),
        "incremental_shield_usd": str(shield_cost),
        "modeled_total_with_usd": str(total_with),
        "modeled_difference_with_minus_without_usd": str(total_with - origin_without),
        "decision_scope": "Arithmetic on declared fictional counts only; no measured AWS cache, latency, full bill or customer result"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_file", nargs="?", type=Path, default=Path(__file__).with_name("cases.json"),
                        help="JSON fixture to evaluate (default: bundled cases.json)")
    args = parser.parse_args()
    data = json.loads(args.case_file.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    for case in data["cases"]:
        print(json.dumps(estimate(case), sort_keys=True))


if __name__ == "__main__":
    main()
