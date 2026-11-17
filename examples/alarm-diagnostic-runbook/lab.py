"""Fictional evidence-path drill; this is not an EventBridge or SSM emulator."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATTERN = json.loads((ROOT / "event-pattern.json").read_text())


def matches_subset(pattern: dict, event: dict) -> bool:
    """Only the exact nested string-list subset used in event-pattern.json."""
    for key, allowed in pattern.items():
        if key not in event:
            return False
        if isinstance(allowed, dict):
            if not isinstance(event[key], dict) or not matches_subset(allowed, event[key]):
                return False
        elif not isinstance(allowed, list) or event[key] not in allowed:
            return False
    return True


def diagnose(case: dict) -> str:
    """Return the first unproven boundary, not an invented root cause."""
    event = case.get("event")
    if event is None:
        return "SOURCE_UNOBSERVED"
    if not matches_subset(PATTERN, event):
        return "RULE_NO_MATCH"
    if case["triggered_rules"] == 0:
        return "RULE_NOT_OBSERVED"
    if case["invocation_attempts"] == 0:
        return "TARGET_NOT_ATTEMPTED"
    if case["successful_invocation_attempts"] == 0:
        if case.get("invocations_failed_to_be_sent_to_dlq", 0) > 0:
            return "DLQ_DELIVERY_FAILED"
        if case.get("invocations_sent_to_dlq", 0) > 0:
            return "TARGET_IN_DLQ"
        return "TARGET_DELIVERY_UNPROVEN"
    if case.get("automation_state") is None:
        return "AUTOMATION_UNOBSERVED"
    if case["automation_state"] != "Success":
        return "AUTOMATION_NOT_SUCCESSFUL"
    if case.get("current_alarm_state") != "OK":
        return "ALARM_NOT_RECOVERED"
    if case.get("customer_completion") is not True:
        return "CUSTOMER_OUTCOME_UNPROVEN"
    links = case.get("evidence_links")
    if not isinstance(links, dict):
        return "CORRELATION_UNPROVEN"
    for left, right in (
        (event.get("id"), links.get("target_event_id")),
        (event.get("id"), links.get("automation_event_id")),
        (links.get("started_execution_id"), links.get("observed_execution_id")),
        (links.get("expected_customer_scope"), links.get("observed_customer_scope")),
    ):
        if not isinstance(left, str) or not left or left != right:
            return "CORRELATION_UNPROVEN"
    return "LOCAL_EVIDENCE_ALIGNED"


def sample_event() -> dict:
    return json.loads((ROOT / "sample-event.json").read_text())


def main() -> None:
    base = {
        "event": sample_event(),
        "triggered_rules": 1,
        "invocation_attempts": 1,
        "successful_invocation_attempts": 1,
        "failed_invocations": 0,
        "invocations_sent_to_dlq": 0,
        "invocations_failed_to_be_sent_to_dlq": 0,
        "automation_state": "Success",
        "current_alarm_state": "OK",
        "customer_completion": True,
        "evidence_links": {
            "target_event_id": sample_event()["id"],
            "automation_event_id": sample_event()["id"],
            "started_execution_id": "fictional-execution-01",
            "observed_execution_id": "fictional-execution-01",
            "expected_customer_scope": "fictional-booking-cohort-01",
            "observed_customer_scope": "fictional-booking-cohort-01",
        },
    }
    cases = [
        ("reconciled fictional path", base),
        ("wrong region", {**base, "event": {**sample_event(), "region": "us-east-1"}}),
        ("target not attempted", {**base, "invocation_attempts": 0, "successful_invocation_attempts": 0}),
        ("target in dead-letter queue", {**base, "successful_invocation_attempts": 0, "failed_invocations": 1, "invocations_sent_to_dlq": 1}),
        ("runbook missing", {**base, "automation_state": None}),
        ("runbook succeeded, booking still late", {**base, "customer_completion": False}),
        ("green counts, wrong execution", {**base, "evidence_links": {**base["evidence_links"], "observed_execution_id": "fictional-execution-02"}}),
    ]
    for label, case in cases:
        print(f"{label}: {diagnose(case)}")


if __name__ == "__main__":
    main()
