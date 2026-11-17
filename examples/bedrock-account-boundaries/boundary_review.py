"""Evaluate supplied multi-account Bedrock design facts without AWS calls."""

from __future__ import annotations

import json
from pathlib import Path
import sys


REQUIRED_METERS = {
    "input_tokens",
    "output_tokens",
    "retrieval",
    "logs_and_storage",
    "retries",
}
RESIDENCY_RULES = {"single_region", "approved_geography", "flexible"}
LOG_MODES = {"off", "content"}


def review(proposal: dict) -> dict:
    """Return design holds; a clear record is still not deployment approval."""
    holds: list[str] = []
    app = proposal["application_account"]
    inference = proposal["inference_account"]
    source = proposal["source_region"]
    destinations = proposal["candidate_processing_regions"]
    rule = proposal["residency_rule"]
    allowed = proposal["approved_processing_regions"]
    logging = proposal["logging"]
    cost = proposal["cost"]

    if inference != proposal["approved_inference_account"]:
        holds.append("inference_account_not_approved")
    if app != inference and not proposal["cross_account_role_reviewed"]:
        holds.append("cross_account_trust_not_reviewed")
    if rule not in RESIDENCY_RULES or not destinations:
        holds.append("processing_rule_or_destinations_missing")
    elif rule == "single_region" and set(destinations) != {source}:
        holds.append("processing_outside_source_region")
    elif rule == "approved_geography" and not set(destinations) <= set(allowed):
        holds.append("processing_outside_approved_geography")
    if logging["mode"] not in LOG_MODES:
        holds.append("logging_choice_missing")
    elif logging["mode"] == "content":
        if (logging["account"] != inference or logging["region"] != source):
            holds.append("invocation_log_destination_wrong")
        if not logging["content_retention_approved"]:
            holds.append("content_retention_not_approved")
    if not proposal["metrics_and_request_id_plan"]:
        holds.append("observation_plan_missing")
    if not REQUIRED_METERS <= set(cost["included_meters"]):
        holds.append("cost_meters_missing")
    amount = cost["estimated_total_usd"]
    if amount < 0 or amount > cost["run_limit_usd"]:
        holds.append("run_limit_exceeded")
    if amount > cost["gross_budget_headroom_usd"]:
        holds.append("gross_budget_exceeded")
    if cost["credit_balance_usd"] - amount < cost["credit_reserve_usd"]:
        holds.append("credit_reserve_breached")

    return {
        "case": proposal["id"],
        "decision": "hold" if holds else "ready_for_design_review",
        "holds": holds,
        "scope": "supplied fictional facts only; no IAM, Bedrock, billing, Region or log configuration checked",
    }


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).with_name("cases.json")
    cases = json.loads(path.read_text())["cases"]
    print(json.dumps([review(case) for case in cases], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
