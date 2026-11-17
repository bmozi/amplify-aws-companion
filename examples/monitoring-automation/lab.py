"""Small local control-decision model; no AWS APIs or external dependencies."""

from __future__ import annotations

import json
from pathlib import Path


def process_s3_object(record: dict, seen: set[tuple[str, str, str]], *, bucket: str,
                      prefix: str, suffix: str, output_prefix: str) -> str:
    """Return a local teaching verdict for one decoded object record."""
    if record.get("bucket") != bucket:
        return "FILTERED_BUCKET"
    key = record.get("key", "")
    if not key.startswith(prefix) or not key.endswith(suffix):
        return "FILTERED_OUTPUT" if key.startswith(output_prefix) else "FILTERED_KEY"
    version = record.get("version_id")
    if not isinstance(version, str) or not version:
        return "STOP_MISSING_VERSION"
    identity = (bucket, key, version)
    if identity in seen:
        return "DUPLICATE"
    seen.add(identity)
    return "PROCESS"


def matches_eventbridge(event: dict, pattern: dict) -> bool:
    """Match only exact top-level and one-level detail fields for this fixture."""
    if any(event.get(key) != value for key, value in pattern.items() if key != "detail"):
        return False
    expected_detail = pattern.get("detail", {})
    actual_detail = event.get("detail", {})
    return all(actual_detail.get(key) == value for key, value in expected_detail.items())


def alarm_action(previous: str, current: str, *, configured_states: set[str]) -> str:
    """Model a configured action on a transition into a selected state."""
    if previous == current:
        return "NO_TRANSITION"
    return "NOTIFY" if current in configured_states else "NO_ACTION"


def remediation_gate(*, resource_id: str, compliance: str, evaluation_age_minutes: int,
                     max_age_minutes: int, action: str, known_actions: set[str],
                     attempts_already: int, max_attempts: int,
                     allowed_resources: set[str]) -> str:
    """Apply explicit local safety gates before a fictional remediation."""
    if resource_id not in allowed_resources:
        return "STOP_SCOPE"
    if evaluation_age_minutes > max_age_minutes:
        return "STOP_STALE"
    if compliance != "NON_COMPLIANT":
        return "STOP_NOT_NONCOMPLIANT"
    if action not in known_actions:
        return "STOP_ACTION"
    if attempts_already >= max_attempts:
        return "STOP_RETRIES"
    return "REMEDIATE"


def run_packet() -> dict[str, list[str]]:
    seen: set[tuple[str, str, str]] = set()
    s3_records = [
        {"bucket": "fictional-intake", "key": "incoming/logs/branch-7/day.jsonl", "version_id": "v1"},
        {"bucket": "fictional-intake", "key": "incoming/logs/branch-7/day.jsonl", "version_id": "v1"},
        {"bucket": "fictional-intake", "key": "processed/day.jsonl", "version_id": "v2"},
    ]
    s3 = [process_s3_object(record, seen, bucket="fictional-intake",
                            prefix="incoming/logs/", suffix=".jsonl",
                            output_prefix="processed/") for record in s3_records]

    pattern = {"source": "aws.ec2", "detail-type": "EC2 Instance State-change Notification",
               "detail": {"state": "terminated"}}
    eventbridge_events = [
        {"source": "aws.ec2", "detail-type": "EC2 Instance State-change Notification",
         "detail": {"state": "terminated"}},
        {"source": "aws.ec2", "detail-type": "EC2 Instance State-change Notification",
         "detail": {"state": "running"}},
    ]
    eventbridge = ["ROUTE" if matches_eventbridge(event, pattern) else "NO_MATCH"
                   for event in eventbridge_events]

    alarms = [alarm_action("OK", "ALARM", configured_states={"ALARM"}),
              alarm_action("ALARM", "ALARM", configured_states={"ALARM"})]

    common = {"max_age_minutes": 10, "known_actions": {"restore-encryption"},
              "max_attempts": 2, "allowed_resources": {"lab-bucket-01"}}
    config_results = [
        remediation_gate(resource_id="lab-bucket-01", compliance="NON_COMPLIANT",
                         evaluation_age_minutes=3, action="restore-encryption",
                         attempts_already=0, **common),
        remediation_gate(resource_id="lab-bucket-01", compliance="NON_COMPLIANT",
                         evaluation_age_minutes=42, action="restore-encryption",
                         attempts_already=0, **common),
        remediation_gate(resource_id="production-bucket-99", compliance="NON_COMPLIANT",
                         evaluation_age_minutes=3, action="restore-encryption",
                         attempts_already=0, **common),
        remediation_gate(resource_id="lab-bucket-01", compliance="NON_COMPLIANT",
                         evaluation_age_minutes=3, action="delete-bucket",
                         attempts_already=0, **common),
        remediation_gate(resource_id="lab-bucket-01", compliance="NON_COMPLIANT",
                         evaluation_age_minutes=3, action="restore-encryption",
                         attempts_already=2, **common),
    ]

    return {"s3": s3, "eventbridge": eventbridge, "cloudwatch_alarm": alarms,
            "config": config_results}


def main() -> None:
    result = run_packet()
    expected = {"s3": ["PROCESS", "DUPLICATE", "FILTERED_OUTPUT"],
                "eventbridge": ["ROUTE", "NO_MATCH"],
                "cloudwatch_alarm": ["NOTIFY", "NO_TRANSITION"],
                "config": ["REMEDIATE", "STOP_STALE", "STOP_SCOPE", "STOP_ACTION", "STOP_RETRIES"]}
    if result != expected:
        raise SystemExit(f"Unexpected teaching-packet result: {result!r}")
    print(json.dumps(result, indent=2))
    print("Local policy assertions passed; no AWS services or resources were used.")


if __name__ == "__main__":
    main()
