"""Fictional configuration-change decision gates; no AWS calls or effects."""

from __future__ import annotations

import json


ALLOWED_ACCOUNT = "111111111111"
ALLOWED_REGION = "us-east-2"
ALLOWED_RESOURCES = {"asg-lab-01", "node-lab-01", "bucket-lab-01"}
RESOURCE_KINDS = {"asg-lab-01": "ASG", "node-lab-01": "MANAGED_NODE",
                  "bucket-lab-01": "BUCKET"}


def plan_change(event: dict, planned_events: dict[str, tuple[str, ...]]) -> str:
    """Select a local plan, without implying that it ran or repaired anything."""
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        return "STOP_IDENTITY"
    if (event.get("account") != ALLOWED_ACCOUNT
            or event.get("region") != ALLOWED_REGION
            or event.get("resource_id") not in ALLOWED_RESOURCES):
        return "STOP_SCOPE"
    boolean_fields = ("deployment_active", "previous_attempt_unknown",
                      "approval_required", "approval_present",
                      "ssm_managed", "agent_online")
    if any(type(event.get(name)) is not bool for name in boolean_fields):
        return "STOP_EVIDENCE"
    numeric_fields = ("evaluation_age_minutes", "max_age_minutes", "attempts",
                      "max_attempts", "error_count", "max_errors",
                      "active_targets", "max_concurrent_targets")
    if any(type(event.get(name)) is not int or event[name] < 0 for name in numeric_fields):
        return "STOP_EVIDENCE"
    if (event["max_attempts"] < 1 or event["max_errors"] < 1
            or event["max_concurrent_targets"] < 1):
        return "STOP_EVIDENCE"
    if event.get("evaluation_age_minutes", 10**9) > event.get("max_age_minutes", 0):
        return "STOP_STALE"
    if event.get("compliance") != "NON_COMPLIANT":
        return "STOP_NOT_NONCOMPLIANT"
    if (not isinstance(event.get("observed_revision"), str)
            or not event["observed_revision"]
            or not isinstance(event.get("desired_revision"), str)
            or not event["desired_revision"]):
        return "STOP_EVIDENCE"
    if event.get("observed_revision") != event.get("desired_revision"):
        return "STOP_REVISION"
    if event.get("deployment_active"):
        return "STOP_DEPLOYMENT"
    if event.get("previous_attempt_unknown"):
        return "INSPECT_PREVIOUS_ATTEMPT"
    if event.get("attempts", 0) >= event.get("max_attempts", 0):
        return "STOP_RETRIES"
    if event.get("error_count", 0) >= event.get("max_errors", 0):
        return "STOP_ERROR_BUDGET"
    if event.get("active_targets", 0) >= event.get("max_concurrent_targets", 0):
        return "WAIT_CONCURRENCY"
    if event.get("approval_required") and not event.get("approval_present"):
        return "WAIT_APPROVAL"

    source = event.get("desired_state_owner")
    target = event.get("target_kind")
    # AWS_RESOURCE is the fixture's generic Terraform route; specific routes
    # must match this fictional inventory, not just an allowed resource ID.
    if target in {"ASG", "MANAGED_NODE"} and RESOURCE_KINDS[event["resource_id"]] != target:
        return "STOP_TARGET_KIND"
    if source == "LAUNCH_TEMPLATE" and target == "ASG":
        decision = "UPDATE_TEMPLATE_AND_REFRESH"
    elif source == "TERRAFORM" and target == "AWS_RESOURCE":
        decision = "REVIEW_IAC_PLAN"
    elif source == "STATE_MANAGER" and target == "MANAGED_NODE":
        if not event.get("ssm_managed") or not event.get("agent_online"):
            return "STOP_SSM_READINESS"
        decision = "APPLY_VERSIONED_ASSOCIATION"
    else:
        return "STOP_OWNER"

    identity = (event["account"], event["region"], event["resource_id"],
                event["desired_revision"], source, target)
    if event_id in planned_events:
        if planned_events[event_id] != identity:
            return "STOP_ID_REUSE"
        return "INSPECT_PRIOR_PLAN"
    planned_events[event_id] = identity
    return decision


def fixtures() -> list[dict]:
    base = {"account": ALLOWED_ACCOUNT, "region": ALLOWED_REGION,
            "evaluation_age_minutes": 2, "max_age_minutes": 10,
            "compliance": "NON_COMPLIANT", "observed_revision": "rev-18",
            "desired_revision": "rev-18", "deployment_active": False,
            "previous_attempt_unknown": False, "attempts": 0, "max_attempts": 2,
            "error_count": 0, "max_errors": 1, "active_targets": 0,
            "max_concurrent_targets": 1, "approval_required": False,
            "approval_present": False, "desired_state_owner": "LAUNCH_TEMPLATE",
            "target_kind": "ASG", "ssm_managed": False, "agent_online": False}
    cases = [
        {**base, "event_id": "event-asg-1", "resource_id": "asg-lab-01"},
        {**base, "event_id": "event-stale", "resource_id": "node-lab-01",
         "desired_state_owner": "STATE_MANAGER", "target_kind": "MANAGED_NODE",
         "ssm_managed": True, "agent_online": True, "evaluation_age_minutes": 42},
        {**base, "event_id": "event-wrong-account", "resource_id": "asg-lab-01",
         "account": "222222222222"},
        {**base, "event_id": "event-revision", "resource_id": "bucket-lab-01",
         "desired_state_owner": "TERRAFORM", "target_kind": "AWS_RESOURCE",
         "observed_revision": "rev-17"},
        {**base, "event_id": "event-asg-duplicate", "resource_id": "asg-lab-01"},
    ]
    return cases


def run_packet() -> dict[str, list[str]]:
    planned: dict[str, tuple[str, ...]] = {}
    results = [plan_change(event, planned) for event in fixtures()]
    results.append(plan_change(fixtures()[0], planned))
    return {"change_plan": results}


def main() -> None:
    expected = {"change_plan": ["UPDATE_TEMPLATE_AND_REFRESH", "STOP_STALE",
                                "STOP_SCOPE", "STOP_REVISION",
                                "UPDATE_TEMPLATE_AND_REFRESH", "INSPECT_PRIOR_PLAN"]}
    result = run_packet()
    if result != expected:
        raise SystemExit(f"Unexpected fictional decision packet: {result!r}")
    print(json.dumps(result, indent=2))
    print("Local decision assertions passed; no AWS services or resources were used.")


if __name__ == "__main__":
    main()
