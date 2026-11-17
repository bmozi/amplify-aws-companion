"""Offline teaching check for preview self-managed hosting cost scope.

Invented prices are accepted only as a fictional exercise; this never approves AWS use.
"""

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path


ALWAYS = {
    "cloudfront_transfer_gb", "cloudfront_requests", "s3_storage_gb_month",
    "s3_requests", "build_execution", "backend_services", "retained_resources",
}
FEATURE_METERS = {
    "monitoring": {"cloudwatch_alarms", "sns_notifications"},
    "custom_domain": {"domain_dns_certificate"},
    "waf": {"waf_acl_rules_requests"},
    "access_logging": {"access_log_storage_requests"},
    "ssr": {"ssr_compute_requests_duration"},
    "managed_pipeline": {"managed_pipeline"},
}
ALL = ALWAYS | set().union(*FEATURE_METERS.values())


def money(value, label):
    if isinstance(value, bool):
        raise ValueError(f"{label}: expected nonnegative number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"{label}: expected nonnegative number") from None
    if not result.is_finite() or result < 0:
        raise ValueError(f"{label}: expected nonnegative finite number")
    return result


def assess(plan):
    if plan.get("mode") != "self_managed_preview":
        raise ValueError("Only the self-managed preview route belongs in this worksheet")
    if plan.get("price_basis") != "fictional_teaching_rates":
        raise ValueError("This exercise accepts fictional rates only, never a live approval")
    features = plan.get("features")
    if not isinstance(features, dict) or set(features) != set(FEATURE_METERS) or any(type(v) is not bool for v in features.values()):
        raise ValueError("Every selected feature needs an explicit true/false value")
    rows = plan.get("meters")
    if not isinstance(rows, list):
        raise ValueError("Missing meter inventory")
    by_name = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("name") not in ALL:
            raise ValueError("Unknown meter or copied managed Hosting subtotal")
        name = row["name"]
        if name in by_name:
            raise ValueError(f"Duplicate meter: {name}")
        by_name[name] = row
    if set(by_name) != ALL:
        raise ValueError("Missing meters: " + ", ".join(sorted(ALL - set(by_name))))
    selected = ALWAYS | set().union(*(names for flag, names in FEATURE_METERS.items() if features[flag]))
    base = Decimal("0")
    for name, row in by_name.items():
        if name in selected:
            if row.get("state") != "estimated" or not isinstance(row.get("basis"), str) or not row["basis"].strip():
                raise ValueError(f"Selected meter needs quantity, rate and basis: {name}")
            base += money(row.get("quantity"), name + " quantity") * money(row.get("rate_usd"), name + " rate")
        elif row.get("state") != "not_applicable" or not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise ValueError(f"Unselected meter needs a reason: {name}")
    contingency = money(plan.get("contingency_usd"), "contingency")
    if contingency < base * Decimal("0.25"):
        raise ValueError("Contingency must be at least 25% of the modeled base")
    total = base + contingency
    balance = money(plan.get("fictional_credit_balance_usd"), "fictional balance")
    reserve = money(plan.get("reserve_usd"), "reserve")
    if reserve < 100:
        raise ValueError("Reserve must be at least USD 100")
    if total > 5:
        raise ValueError("Modeled whole-run estimate exceeds USD 5")
    if balance - total < reserve:
        raise ValueError("Fictional balance would fall below reserve")
    return {"base_usd": str(base), "contingency_usd": str(contingency),
            "total_usd": str(total), "fictional_remaining_usd": str(balance - total),
            "decision": "fictional arithmetic passes; live deployment remains unapproved"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        result = assess(json.loads(args.plan.read_text()))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        parser.exit(2, f"Plan needs review: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
