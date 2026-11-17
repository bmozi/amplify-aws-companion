"""Price only selected fictional Amplify meters; fail closed on whole-run claims."""

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re

from lab import trace
from refresh_public_prices import SELECTIONS


HERE = Path(__file__).resolve().parent
OMISSIONS = [
    "Current account Free plan, service allowances, per-credit eligibility, balance and expiration",
    "Existing Hosting and backend resources, retention, teardown and delayed charges",
    "Actual Cognito pool tier, MAUs, verification email and any added auth features",
    "Generated AppSync GraphQL resolver/subscription operations, WebSocket traffic and outbound transfer",
    "Actual DynamoDB billing mode, resolver fanout, table storage, backup and stream use",
    "Actual S3 GET/DELETE and transfer paths, object versions and retention",
    "Actual Lambda configured memory, duration and extra invocations",
    "Actual CloudWatch log retention, other ingestion, metrics, alarms and queries",
    "Amplify WAF or AppSync cache if enabled; either could create a recurring charge",
    "Other network, DNS, email and AWS charges; GitHub Actions has separate billing",
    "The publisher audience and action mix require review; matching visit counts do not establish backend quantities",
]


def decimal(value, label):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"{label} needs a finite nonnegative decimal") from None
    if not result.is_finite() or result < 0:
        raise ValueError(f"{label} needs a finite nonnegative decimal")
    return result


def price_selected(plan, scenario, snapshot):
    if (not isinstance(scenario, dict) or set(scenario) != {"status", "hosting_storage_gb_month"}
            or scenario.get("status") != "fictional selected-meter exercise; not a cloud or whole-run forecast"):
        raise ValueError("The public-price scenario changed scope")
    if (snapshot.get("schema_version") != 1 or snapshot.get("region") != "us-east-2"
            or snapshot.get("status") != "public on-demand rates; selected meters only; not a whole-run estimate"
            or set(snapshot.get("rates", {})) != set(SELECTIONS)):
        raise ValueError("The public-price snapshot is missing its reviewed meter scope")
    services = {selection[0] for selection in SELECTIONS.values()}
    if set(snapshot.get("offers", {})) != services or not snapshot.get("checked_at_utc"):
        raise ValueError("Public offer identity or check time is missing")
    for service in services:
        source = snapshot["offers"][service]
        if (source.get("url") != f"https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{service}/current/us-east-2/index.json"
                or not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", ""))):
            raise ValueError(f"Public offer provenance changed for {service}")
    traced = trace(plan)
    usage = traced["quantities"]
    q = {key: decimal(value, key) for key, value in usage.items()}
    rates = {}
    for meter, (service, sku, begin, unit) in SELECTIONS.items():
        row = snapshot["rates"][meter]
        if (row.get("service"), row.get("sku"), row.get("begin_range"), row.get("unit")) != (service, sku, begin, unit):
            raise ValueError(f"Selected {meter} price identity changed")
        rates[meter] = decimal(row.get("usd_per_unit"), meter + " rate")
    quantities = {
        "hosting_storage_gb_month": decimal(scenario["hosting_storage_gb_month"], "hosting storage"),
        "hosting_transfer_gb": q["hosting_transfer_gb"],
        "cognito_essentials_mau_before_free_tier": q["cognito_distinct_users_proxy"],
        "appsync_graphql_operation": q["appsync_operations_proxy"],
        "appsync_realtime_message": q["appsync_realtime_updates_proxy"],
        "appsync_connection_minute": q["appsync_connection_minutes_proxy"],
        "dynamodb_on_demand_read_unit": q["dynamodb_read_units_proxy"],
        "dynamodb_on_demand_write_unit": q["dynamodb_write_units_proxy"],
        "s3_standard_storage_gb_month": q["s3_added_storage_gb"],
        "s3_put_or_list_request": q["s3_upload_requests_proxy"] + q["s3_list_requests_proxy"],
        "s3_get_request": q["s3_get_requests_proxy"],
        "lambda_request": q["lambda_invocations_proxy"],
        "lambda_gb_second_tier_1": q["lambda_gb_seconds_proxy"],
        "cloudwatch_standard_log_ingest_gb": q["cloudwatch_new_log_gb_proxy"],
        "cloudwatch_standard_log_storage_gb_month": q["cloudwatch_retained_log_gb_month_proxy"],
    }
    selected = {meter: {"quantity": str(quantity), "unit": snapshot["rates"][meter]["unit"],
                        "rate_usd": str(rates[meter]), "extended_usd": str(quantity * rates[meter])}
                for meter, quantity in quantities.items()}
    subtotal = sum((Decimal(row["extended_usd"]) for row in selected.values()), Decimal("0"))
    return {"status": "incomplete_selected_meter_subtotal_only",
            "region": "us-east-2", "public_offer_checked_at_utc": snapshot["checked_at_utc"],
            "public_offer_sha256_by_service": {name: snapshot["offers"][name]["sha256"] for name in sorted(services)},
            "fictional_visits": usage["visits"], "selected_meters": selected,
            "selected_preallowance_subtotal_usd": str(subtotal),
            "fits_5gb_hosting_transfer_assumption_only": traced["fits_5gb_hosting_transfer_assumption"],
            "missing_for_whole_run": OMISSIONS,
            "not_a_publisher_estimate": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=HERE / "plan.json",
                        help="Fictional usage assumptions; default is the 100-visit lesson")
    parser.add_argument("--visits", help="Change only fictional visits; recheck every linked assumption")
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text())
        if args.visits is not None:
            plan["visits"] = args.visits
        result = price_selected(plan, json.loads((HERE / "public-price-scenario.json").read_text()),
                                json.loads((HERE / "public-prices-us-east-2.json").read_text()))
    except (ValueError, OSError) as error:
        parser.exit(2, f"Selected-meter review stopped: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
