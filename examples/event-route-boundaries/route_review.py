"""Review supplied EventBridge Classic rule-route facts without AWS calls."""

from __future__ import annotations

import json
from pathlib import Path
import sys


def review(case: dict) -> dict:
    """Find explicit design holds; a clear paper case still needs AWS review."""
    holds: list[str] = []
    source = case["source"]
    destination = case["destination"]
    event = case["test_event"]
    forwarding = case["forwarding_rule"]
    bus = case["receiving_bus"]
    receiver = case["receiving_rule"]
    recovery = case["recovery"]
    cost = case["cost"]

    if forwarding["source_pattern"] != event["source"]:
        holds.append("sender_rule_misses_test_event")
    if not forwarding["role_can_put_events"]:
        holds.append("sender_role_not_reviewed")
    if (not destination["region_supported"] or
            forwarding["target_region"] != destination["region"]):
        holds.append("destination_region_not_reviewed")
    if source["account"] not in bus["allowed_sender_accounts"]:
        holds.append("receiver_bus_does_not_admit_sender")
    if receiver["account_filter"] != [source["account"]] or receiver["source_filter"] != event["source"]:
        holds.append("receiver_rule_scope_not_reviewed")
    if not receiver["target_permission_reviewed"]:
        holds.append("receiver_target_permission_missing")
    if recovery["third_bus_hop"]:
        holds.append("unsupported_third_bus_hop")
    if (not forwarding["dlq_policy_reviewed"] or
            forwarding["dlq_region"] != source["region"]):
        holds.append("forwarding_failure_destination_missing")
    if (not receiver["dlq_policy_reviewed"] or
            receiver["dlq_region"] != destination["region"]):
        holds.append("receiver_failure_destination_missing")
    if recovery["archive_source_bus"] != recovery["replay_destination_bus"]:
        holds.append("archive_replay_wrong_bus")
    if not recovery["operation_id_deduplication_reviewed"]:
        holds.append("replay_effect_deduplication_missing")
    if not recovery["failure_owner_named"]:
        holds.append("failure_owner_missing")

    amount = cost["estimated_gross_usd"]
    if amount < 0 or amount > cost["run_limit_usd"]:
        holds.append("run_limit_exceeded")
    if amount > cost["gross_headroom_usd"]:
        holds.append("gross_budget_exceeded")
    if cost["credit_balance_usd"] - amount < cost["credit_reserve_usd"]:
        holds.append("credit_reserve_breached")
    if not {"source_events", "forwarded_events", "dlq", "archive", "target", "logs"} <= set(cost["included_meters"]):
        holds.append("route_cost_meters_missing")

    return {
        "case": case["id"],
        "decision": "hold" if holds else "ready_for_design_review",
        "holds": holds,
        "scope": "fictional assertions only; no AWS IAM, EventBridge, SQS, Region, bill or recipient observed",
    }


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).with_name("cases.json")
    cases = json.loads(path.read_text())["cases"]
    print(json.dumps([review(case) for case in cases], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
