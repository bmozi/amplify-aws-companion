"""Group selected public-rate teaching meters for the pending smoke audience.

This deliberately cannot produce a reviewed whole-run publisher record.
"""

from decimal import Decimal
import json
from pathlib import Path

from public_price_lab import price_selected


HERE = Path(__file__).resolve().parent
RECORD = HERE.parent / "publisher-smoke-run-estimate.json"
GROUPS = {
    "hosting": ("hosting_storage_gb_month", "hosting_transfer_gb"),
    "cognito": ("cognito_essentials_mau_before_free_tier",),
    "appsync": ("appsync_graphql_operation", "appsync_realtime_message",
                "appsync_connection_minute"),
    "dynamodb": ("dynamodb_on_demand_read_unit", "dynamodb_on_demand_write_unit"),
    "s3": ("s3_standard_storage_gb_month", "s3_put_or_list_request", "s3_get_request"),
    "lambda": ("lambda_request", "lambda_gb_second_tier_1"),
    "cloudwatch": ("cloudwatch_standard_log_ingest_gb",
                   "cloudwatch_standard_log_storage_gb_month"),
}
UNRESOLVED = {
    "cognito": "Actual user-pool tier, MAUs, verification messages, triggers and allowances",
    "appsync": "Generated resolver/subscription work, retries, outbound bytes and real-time payload units",
    "dynamodb": "Actual billing mode, table/storage/backup/stream retention and resolver fanout",
    "s3": "Actual file GET/DELETE and transfer, versions, existing storage and retention",
    "lambda": "Configured memory, measured duration, extra invocations and retained functions",
    "cloudwatch": "Existing/new logs, metrics, alarms, queries and actual retention",
    "network": "Backend response transfer, other egress paths, DNS and shared network meters",
    "other_aws": "Existing resources, optional WAF/cache, teardown and delayed charges",
    "github": "Actions minutes and artifact storage belong to a separate billing account",
}


def bridge(plan, scenario, snapshot, record):
    if record.get("schema_version") != 8 or record.get("review_status") != "review_needed":
        raise ValueError("Use the pending schema-8 smoke record; this bridge cannot approve it")
    if record.get("scenario") != "static_smoke_100_visit_1d" or record.get("region") != "us-east-2":
        raise ValueError("The selected smoke scenario or Region changed")
    if set(record.get("backend_components", {})) != set(GROUPS) - {"hosting"} | {"network"}:
        raise ValueError("The pending record's backend categories changed")
    if any(row.get("review_status") != "pending" or Decimal(str(row.get("estimated_usd"))) != 0
           for row in record["backend_components"].values()):
        raise ValueError("This bridge expects unreviewed backend placeholders, not account decisions")
    result = price_selected(plan, scenario, snapshot)
    if result["status"] != "incomplete_selected_meter_subtotal_only" or not result["not_a_publisher_estimate"]:
        raise ValueError("The selected-rate model changed its evidence boundary")
    audience = record.get("audience", {})
    if (Decimal(str(plan.get("visits"))) != Decimal(str(audience.get("visits")))
            or Decimal(str(plan.get("hosting_bytes_per_visit"))) !=
            Decimal(str(audience.get("hosting_bytes_per_visit")))):
        raise ValueError("The teaching plan must use the pending record's exact audience")
    selected = result["selected_meters"]
    record_rows = {row["meter"]: row for row in record.get("line_items", [])}
    for meter in GROUPS["hosting"]:
        if (Decimal(selected[meter]["quantity"]) != Decimal(str(record_rows[meter]["quantity"]))
                or Decimal(selected[meter]["rate_usd"]) !=
                Decimal(str(record_rows[meter]["unit_price_usd"]))):
            raise ValueError("The selected Hosting meter disagrees with the pending smoke record")
    grouped = {
        name: {
            "selected_meters": list(meters),
            "selected_preallowance_usd": str(sum(
                (Decimal(selected[meter]["extended_usd"]) for meter in meters), Decimal(0))),
        }
        for name, meters in GROUPS.items()
    }
    grouped["network"] = {"selected_meters": [], "selected_preallowance_usd": None}
    subtotal = sum((Decimal(row["selected_preallowance_usd"]) for row in grouped.values()
                    if row["selected_preallowance_usd"] is not None), Decimal(0))
    if subtotal != Decimal(result["selected_preallowance_subtotal_usd"]):
        raise ValueError("Grouped meters do not reconcile to the selected subtotal")
    return {
        "status": "incomplete_selected_meter_proposal_only",
        "record_review_status": record["review_status"],
        "region": record["region"],
        "visits": str(audience["visits"]),
        "hosting_bytes_per_visit": str(audience["hosting_bytes_per_visit"]),
        "public_offer_checked_at_utc": result["public_offer_checked_at_utc"],
        "groups": grouped,
        "selected_preallowance_subtotal_usd": str(subtotal),
        "unresolved_by_group": UNRESOLVED,
        "can_copy_to_reviewed_record": False,
        "reason": "Selected fictional quantities and public rates omit live configuration, other meters, credit terms, budget room and cleanup",
    }


def main():
    plan = json.loads((HERE / "smoke-plan.json").read_text())
    scenario = json.loads((HERE / "public-price-scenario.json").read_text())
    snapshot = json.loads((HERE / "public-prices-us-east-2.json").read_text())
    record = json.loads(RECORD.read_text())
    print(json.dumps(bridge(plan, scenario, snapshot, record), indent=2))


if __name__ == "__main__":
    main()
