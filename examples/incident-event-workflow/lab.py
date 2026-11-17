"""Fictional event routing and approval-gated workflow model; no AWS calls."""

from __future__ import annotations

import json


ALLOWED_ACCOUNT = "111111111111"
ALLOWED_REGION = "us-east-2"
ALLOWED_RESOURCE = "sg-lab-001"


def _matches(actual, expected):
    if isinstance(expected, list):
        return actual in expected
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _matches(actual[key], value) for key, value in expected.items())
    return actual == expected


def matches_pattern(event: dict, pattern: dict) -> bool:
    """Small exact subset of EventBridge matching for the teaching fixture."""
    return all(key in event and _matches(event[key], expected)
               for key, expected in pattern.items())


HEALTH_PATTERN = {
    "source": ["aws.health"],
    "detail-type": ["AWS Health Event"],
    "account": [ALLOWED_ACCOUNT],
    "detail": {"eventTypeCategory": ["scheduledChange"]},
}

CLOUDTRAIL_PATTERN = {
    "source": ["aws.ec2"],
    "detail-type": ["AWS API Call via CloudTrail"],
    "account": [ALLOWED_ACCOUNT],
    "region": [ALLOWED_REGION],
    "detail": {
        "eventSource": ["ec2.amazonaws.com"],
        "eventName": ["AuthorizeSecurityGroupIngress"],
        "requestParameters": {"groupId": [ALLOWED_RESOURCE]},
    },
}


def scoped_identity(event: dict) -> str | None:
    """Return the local effect identity only when required scope is present."""
    account = event.get("account")
    source = event.get("source")
    event_id = event.get("id")
    if not all(isinstance(value, str) and value for value in (account, source, event_id)):
        return None
    if source == "aws.health":
        detail = event.get("detail", {})
        if not all(isinstance(detail.get(key), str) and detail.get(key)
                   for key in ("eventArn", "communicationId", "eventRegion")):
            return None
        # The outer EventBridge Region is where a notice was delivered. The detail field
        # is the Health event's affected Region, so include both scopes explicitly.
        return "|".join((account, detail["eventRegion"], detail["eventArn"],
                         detail["communicationId"]))
    if source == "aws.ec2":
        detail = event.get("detail", {})
        if not isinstance(detail.get("eventID"), str) or not detail.get("eventID"):
            return None
        return "|".join((account, event.get("region", ""), "cloudtrail", detail["eventID"]))
    return None


def route_event(event: dict, seen: set[str], notifications: list,
                response_queue: list) -> str:
    """Route supported fixture events while preserving separate consumer records."""
    identity = scoped_identity(event)
    if identity is None:
        return "QUARANTINE"
    if event.get("account") != ALLOWED_ACCOUNT:
        return "OUT_OF_SCOPE"

    health = matches_pattern(event, HEALTH_PATTERN)
    cloudtrail = matches_pattern(event, CLOUDTRAIL_PATTERN)
    if not health and not cloudtrail:
        # Public Health notices remain useful context but cannot authorize resource work.
        if (event.get("source") == "aws.health"
                and event.get("detail-type") == "AWS Health Event"
                and event.get("detail", {}).get("eventScopeCode") == "PUBLIC"):
            if identity not in seen:
                seen.add(identity)
                notifications.append({"identity": identity, "kind": "public-health-notice"})
            return "NOTICE_ONLY"
        return "NO_MATCH"

    if identity in seen:
        return "DUPLICATE"
    seen.add(identity)
    kind = "account-health-review" if health else "security-group-api-review"
    # Independent subscribers receive their own local records.
    notifications.append({"identity": identity, "kind": kind})
    affected_region = (event.get("detail", {}).get("eventRegion")
                       if health else event.get("region"))
    response_queue.append({"identity": identity, "kind": kind,
                           "account": event["account"], "region": affected_region,
                           "resource": (event.get("resources") or [ALLOWED_RESOURCE])[0]})
    return "NOTICE_AND_REVIEW"


def response_workflow(work_item: dict, *, evidence_complete: bool,
                      approved_by: str | None, action_outcome: str,
                      verification_succeeded: bool, attempted_effects: set[str],
                      verified_effects: set[str]) -> str:
    """Model local gates for one fictional response action."""
    if work_item.get("account") != ALLOWED_ACCOUNT:
        return "STOP_SCOPE"
    if work_item.get("region") != ALLOWED_REGION:
        return "STOP_REGION"
    if work_item.get("resource") != ALLOWED_RESOURCE:
        return "STOP_RESOURCE"
    identity = work_item.get("identity")
    if not isinstance(identity, str) or not identity:
        return "STOP_IDENTITY"
    if identity in verified_effects:
        return "ALREADY_VERIFIED_IN_FIXTURE"
    if identity in attempted_effects:
        return "INSPECT_PREVIOUS_ATTEMPT"
    if not evidence_complete:
        return "WAIT_FOR_EVIDENCE"
    if not isinstance(approved_by, str) or not approved_by:
        return "WAIT_FOR_APPROVAL"
    if action_outcome == "UNKNOWN":
        attempted_effects.add(identity)
        return "INSPECT_PREVIOUS_ATTEMPT"
    if action_outcome != "SUCCEEDED":
        return "ACTION_REJECTED_STOP"
    attempted_effects.add(identity)
    if not verification_succeeded:
        return "UNVERIFIED_STOP"
    verified_effects.add(identity)
    return "VERIFIED"


def fixtures() -> list[dict]:
    return [
        {"version": "0", "id": "health-event-1", "source": "aws.health",
         "detail-type": "AWS Health Event", "account": ALLOWED_ACCOUNT,
         "region": "us-east-1", "resources": [ALLOWED_RESOURCE],
         "detail": {"eventArn": "arn:health:event-1", "communicationId": "page-1",
                    "eventRegion": ALLOWED_REGION, "eventTypeCategory": "scheduledChange",
                    "eventScopeCode": "ACCOUNT_SPECIFIC"}},
        {"version": "0", "id": "health-public-1", "source": "aws.health",
         "detail-type": "AWS Health Event", "account": ALLOWED_ACCOUNT,
         "region": "us-east-1", "resources": [],
         "detail": {"eventArn": "arn:health:public", "communicationId": "public-1",
                    "eventRegion": "us-west-2", "eventTypeCategory": "issue",
                    "eventScopeCode": "PUBLIC"}},
        {"version": "0", "id": "cloudtrail-event-1", "source": "aws.ec2",
         "detail-type": "AWS API Call via CloudTrail", "account": ALLOWED_ACCOUNT,
         "region": ALLOWED_REGION, "resources": [ALLOWED_RESOURCE],
         "detail": {"eventSource": "ec2.amazonaws.com",
                    "eventName": "AuthorizeSecurityGroupIngress",
                    "eventID": "api-call-1",
                    "requestParameters": {"groupId": ALLOWED_RESOURCE}}},
        {"version": "0", "id": "cloudtrail-event-other-account", "source": "aws.ec2",
         "detail-type": "AWS API Call via CloudTrail", "account": "222222222222",
         "region": ALLOWED_REGION, "resources": [ALLOWED_RESOURCE],
         "detail": {"eventSource": "ec2.amazonaws.com",
                    "eventName": "AuthorizeSecurityGroupIngress",
                    "eventID": "api-call-other",
                    "requestParameters": {"groupId": ALLOWED_RESOURCE}}},
    ]


def run_packet() -> dict:
    seen: set[str] = set()
    notifications: list[dict] = []
    response_queue: list[dict] = []
    events = fixtures()
    verdicts = [route_event(event, seen, notifications, response_queue) for event in events]
    duplicate = route_event(events[2], seen, notifications, response_queue)
    work = next(item for item in response_queue if item["kind"] == "security-group-api-review")
    attempted: set[str] = set()
    verified: set[str] = set()
    workflow = [
        response_workflow(work, evidence_complete=False, approved_by=None,
                          action_outcome="SUCCEEDED", verification_succeeded=True,
                          attempted_effects=attempted, verified_effects=verified),
        response_workflow(work, evidence_complete=True, approved_by=None,
                          action_outcome="SUCCEEDED", verification_succeeded=True,
                          attempted_effects=attempted, verified_effects=verified),
    ]
    workflow.append(response_workflow(work, evidence_complete=True,
                                      approved_by="reviewer-fixture",
                                      action_outcome="SUCCEEDED", verification_succeeded=True,
                                      attempted_effects=attempted,
                                      verified_effects=verified))
    workflow.append(response_workflow(work, evidence_complete=True,
                                      approved_by="reviewer-fixture",
                                      action_outcome="SUCCEEDED", verification_succeeded=True,
                                      attempted_effects=attempted,
                                      verified_effects=verified))
    return {"routing": verdicts + [duplicate], "notifications": len(notifications),
            "response_queue": len(response_queue), "workflow": workflow}


def main() -> None:
    expected = {"routing": ["NOTICE_AND_REVIEW", "NOTICE_ONLY", "NOTICE_AND_REVIEW",
                            "OUT_OF_SCOPE", "DUPLICATE"],
                "notifications": 3, "response_queue": 2,
                "workflow": ["WAIT_FOR_EVIDENCE", "WAIT_FOR_APPROVAL", "VERIFIED",
                             "ALREADY_VERIFIED_IN_FIXTURE"]}
    result = run_packet()
    if result != expected:
        raise SystemExit(f"Unexpected fictional routing result: {result!r}")
    print(json.dumps(result, indent=2))
    print("Local event/workflow assertions passed; no AWS services or resources were used.")


if __name__ == "__main__":
    main()
