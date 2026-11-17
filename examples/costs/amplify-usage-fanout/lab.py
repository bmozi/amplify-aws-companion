"""Cloud-free quantity tracing for the fictional Amplify Field Lab visit.

Amounts are decimal GB and illustrative service-meter proxies, not AWS bills.
"""

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path


FIELDS = {
    "visits", "distinct_signed_in_users", "hosting_bytes_per_visit",
    "lists_per_visit", "saves_per_visit", "uploads_per_visit", "file_downloads_per_visit",
    "inspections_per_visit", "assumed_dynamodb_read_units_per_list",
    "assumed_dynamodb_write_units_per_save", "bytes_per_upload",
    "log_bytes_per_inspection", "api_response_bytes_per_operation",
    "lambda_memory_gb", "lambda_duration_seconds_per_inspection",
    "log_storage_gb_months_per_new_gb",
    "realtime_connection_minutes_per_visit", "assumed_realtime_updates_per_save",
}
GB = Decimal("1000000000")


def number(value, name):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"{name} needs a finite nonnegative number") from None
    if not result.is_finite() or result < 0:
        raise ValueError(f"{name} needs a finite nonnegative number")
    return result


def trace(plan, *, visits_override=None):
    if not isinstance(plan, dict) or set(plan) != FIELDS | {"status"}:
        raise ValueError("The plan needs exactly the named usage assumptions")
    if plan["status"] != "fictional teaching assumptions, not a cloud forecast":
        raise ValueError("This lab only accepts its fictional teaching status")
    q = {name: number(plan[name], name) for name in FIELDS}
    if visits_override is not None:
        q["visits"] = number(visits_override, "visits override")
    if q["visits"] != q["visits"].to_integral_value() or q["visits"] == 0:
        raise ValueError("visits must be a positive whole number")
    if q["distinct_signed_in_users"] > q["visits"]:
        raise ValueError("distinct users cannot exceed visits")
    for name in ("lambda_memory_gb", "lambda_duration_seconds_per_inspection",
                 "log_storage_gb_months_per_new_gb"):
        if q[name] <= 0:
            raise ValueError(name + " must be positive for this priced path")
    for name in ("distinct_signed_in_users", "hosting_bytes_per_visit",
                 "bytes_per_upload", "log_bytes_per_inspection",
                 "api_response_bytes_per_operation"):
        if q[name] != q[name].to_integral_value():
            raise ValueError(name + " must be a whole number")
    counts = {
        "list": q["visits"] * q["lists_per_visit"],
        "save": q["visits"] * q["saves_per_visit"],
        "upload": q["visits"] * q["uploads_per_visit"],
        "download": q["visits"] * q["file_downloads_per_visit"],
        "inspect": q["visits"] * q["inspections_per_visit"],
    }
    if any(n != n.to_integral_value() for n in counts.values()):
        raise ValueError("Action counts must be whole numbers for this run")
    api = counts["list"] + counts["save"] + counts["inspect"]
    result = {
        "visits": q["visits"],
        "cognito_distinct_users_proxy": q["distinct_signed_in_users"],
        "hosting_transfer_gb": q["visits"] * q["hosting_bytes_per_visit"] / GB,
        "appsync_operations_proxy": api,
        "appsync_connection_minutes_proxy": q["visits"] * q["realtime_connection_minutes_per_visit"],
        "appsync_realtime_updates_proxy": counts["save"] * q["assumed_realtime_updates_per_save"],
        "dynamodb_read_units_proxy": counts["list"] * q["assumed_dynamodb_read_units_per_list"],
        "dynamodb_write_units_proxy": counts["save"] * q["assumed_dynamodb_write_units_per_save"],
        "s3_upload_requests_proxy": counts["upload"],
        "s3_get_requests_proxy": counts["download"],
        "s3_list_requests_proxy": q["visits"] + counts["upload"],
        "s3_added_storage_gb": counts["upload"] * q["bytes_per_upload"] / GB,
        "lambda_invocations_proxy": counts["inspect"],
        "lambda_gb_seconds_proxy": counts["inspect"] * q["lambda_memory_gb"] * q["lambda_duration_seconds_per_inspection"],
        "cloudwatch_new_log_gb_proxy": counts["inspect"] * q["log_bytes_per_inspection"] / GB,
        "cloudwatch_retained_log_gb_month_proxy": counts["inspect"] * q["log_bytes_per_inspection"] / GB * q["log_storage_gb_months_per_new_gb"],
        "appsync_response_transfer_gb_proxy": api * q["api_response_bytes_per_operation"] / GB,
    }
    return {"quantities": {key: str(value) for key, value in result.items()},
            "fits_5gb_hosting_transfer_assumption": result["hosting_transfer_gb"] <= 5,
            "scope": "Fictional incremental quantities only; no prices, free allowance, existing resources, retries, exact subscription behavior, cleanup or live AWS evidence"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, nargs="?", default=Path(__file__).with_name("plan.json"))
    parser.add_argument("--visits", help="replace visit count for a changed-audience exercise")
    args = parser.parse_args()
    try:
        result = trace(json.loads(args.plan.read_text()), visits_override=args.visits)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Usage trace needs review: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
