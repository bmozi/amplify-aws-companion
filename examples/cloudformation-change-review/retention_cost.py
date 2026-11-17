"""Offline arithmetic and evidence screen for a fictional retained S3 archive.

The rate is a study input, not an AWS price. No account or service is queried.
"""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "retention-cost.json"


def nonnegative_decimal(value: object, label: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{label} must be a finite nonnegative number") from error
    if not number.is_finite() or number < 0:
        raise ValueError(f"{label} must be a finite nonnegative number")
    return number


def evaluate(study: dict) -> dict:
    if study.get("study_only") is not True:
        raise ValueError("this worksheet requires an explicit study_only marker")
    days = nonnegative_decimal(study["days_both_buckets_exist"], "days")
    rate = nonnegative_decimal(study["fictional_usd_per_gib_month"], "rate")
    old = sum((nonnegative_decimal(study["old_bucket"][key], f"old {key}")
               for key in ("current_gib", "noncurrent_gib")), Decimal(0))
    new = sum((nonnegative_decimal(study["new_bucket"][key], f"new {key}")
               for key in ("current_gib", "noncurrent_gib")), Decimal(0))
    old_cost = old * rate * days / Decimal(30)
    new_cost = new * rate * days / Decimal(30)
    checks = (
        "old_object_inventory_recorded", "copied_objects_reconciled",
        "customer_read_tested", "cleanup_owner_named", "old_bucket_deletion_verified",
    )
    missing_evidence = [key for key in checks if study.get(key) is not True]
    unpriced = study.get("unpriced_categories")
    if not isinstance(unpriced, list) or not all(isinstance(item, str) and item.strip() for item in unpriced):
        raise ValueError("unpriced_categories must be a list of nonempty descriptions")
    return {
        "fictional_30_day_month": True,
        "old_gib": str(old),
        "new_gib": str(new),
        "old_retained_storage_usd": str(old_cost),
        "new_storage_usd": str(new_cost),
        "combined_storage_usd": str(old_cost + new_cost),
        "unpriced_categories": unpriced,
        "missing_evidence": missing_evidence,
        "decision": "HOLD_FULL_COST_AND_CLEANUP" if unpriced or missing_evidence else "REVIEW_FULL_ESTIMATE",
        "live_aws_price_or_bill_observed": False,
    }


def main() -> None:
    print(json.dumps(evaluate(json.loads(FIXTURE.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
