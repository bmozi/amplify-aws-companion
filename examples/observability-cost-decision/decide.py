"""Price fictional signal plans and check their declared incident evidence.

No AWS API, current price, deployed log group, alarm or operator is observed.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path


METER_KEYS = (
    "standard_ingest_gb",
    "infrequent_ingest_gb",
    "stored_gb_month",
    "query_scanned_gb",
    "custom_metric_month",
)
PLAN_UNITS = (
    "standard_ingest_gb",
    "infrequent_ingest_gb",
    "stored_gb_month",
    "query_scanned_gb",
    "custom_metric_months",
)


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
        raise ValueError(f"{label} must be a nonnegative decimal")
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"{label} must be a nonnegative decimal") from error
    if not result.is_finite() or result < 0:
        raise ValueError(f"{label} must be a nonnegative decimal")
    return result


def natural(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a nonnegative whole number")
    return value


def evaluate(case: dict) -> dict:
    if not isinstance(case, dict) or not isinstance(case.get("rates_usd_per_unit"), dict):
        raise ValueError("rates_usd_per_unit must be an object")
    if not isinstance(case.get("plans"), dict) or not case["plans"]:
        raise ValueError("plans must be a nonempty object")
    rates = case["rates_usd_per_unit"]
    if set(rates) != set(METER_KEYS):
        raise ValueError("rates_usd_per_unit must list exactly the five modeled meters")
    parsed_rates = {key: amount(rates[key], key) for key in METER_KEYS}
    age = natural(case.get("incident_age_days"), "incident_age_days")
    required = case.get("required_records")
    if not isinstance(required, list) or not required or any(not isinstance(x, str) or not x for x in required) or len(set(required)) != len(required):
        raise ValueError("required_records must be a unique nonempty list")
    results = {}
    for name, plan in case["plans"].items():
        if not isinstance(name, str) or not name or not isinstance(plan, dict):
            raise ValueError("each plan needs a name and object")
        units = {key: amount(plan.get(key), f"{name}.{key}") for key in PLAN_UNITS}
        parts = {
            "standard_ingestion": units["standard_ingest_gb"] * parsed_rates["standard_ingest_gb"],
            "infrequent_ingestion": units["infrequent_ingest_gb"] * parsed_rates["infrequent_ingest_gb"],
            "storage": units["stored_gb_month"] * parsed_rates["stored_gb_month"],
            "query_scan": units["query_scanned_gb"] * parsed_rates["query_scanned_gb"],
            "custom_metrics": units["custom_metric_months"] * parsed_rates["custom_metric_month"],
        }
        log_class = plan.get("critical_log_class")
        filter_class = plan.get("metric_filter_source_class")
        if log_class not in {"STANDARD", "INFREQUENT_ACCESS"} or filter_class not in {"STANDARD", "INFREQUENT_ACCESS"}:
            raise ValueError(f"{name}: unsupported critical log class")
        retention = natural(plan.get("critical_retention_days"), f"{name}.critical_retention_days")
        records = plan.get("captured_records")
        if not isinstance(records, list) or any(not isinstance(x, str) or not x for x in records) or len(set(records)) != len(records):
            raise ValueError(f"{name}: captured_records must be a unique list")
        receipt = plan.get("operator_receipt_recorded")
        if not isinstance(receipt, bool):
            raise ValueError(f"{name}: operator_receipt_recorded must be boolean")
        holds = []
        if log_class != "STANDARD" or filter_class != "STANDARD":
            holds.append("metric-filter alert path requires a Standard source log group")
        if units["standard_ingest_gb"] == 0:
            holds.append("modeled Standard ingestion is zero despite declared critical records")
        if units["stored_gb_month"] == 0:
            holds.append("modeled stored GB-month is zero despite retained incident records")
        if units["custom_metric_months"] == 0:
            holds.append("modeled custom metric usage is zero despite the declared metric-filter alert")
        if retention <= age:
            holds.append("retention does not safely cover the incident review boundary")
        missing = sorted(set(required) - set(records))
        if missing:
            holds.append("missing incident records: " + ", ".join(missing))
        if not receipt:
            holds.append("operator notification receipt is absent")
        results[name] = {
            "modeled_cost_usd": format(sum(parts.values(), Decimal("0")), "f"),
            "components_usd": {key: format(value, "f") for key, value in parts.items()},
            "missing_records": missing,
            "design_holds": holds,
            "declared_incident_path_complete": not holds,
            "live_path_verified": False,
        }
    return {
        "plans": results,
        "scope": "Invented rates and self-declared signals; no AWS price, event delivery, alarm, operator receipt or customer outcome verified",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, nargs="?", default=Path(__file__).with_name("case.json"))
    args = parser.parse_args()
    print(json.dumps(evaluate(read_case(args.case)), indent=2))


if __name__ == "__main__":
    main()
