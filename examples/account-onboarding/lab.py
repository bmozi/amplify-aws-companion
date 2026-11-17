"""Review fictional multi-account onboarding packets; never call AWS."""
from copy import deepcopy
import json
import math


def ready_packet(kind="create_new"):
    packet = {
        "request_id": "REQ-2401",
        "mode": "design_only",
        "account_kind": kind,
        "account_email": f"aws-account+{kind}@example.test",
        "business_owner": "Maya Patel",
        "business_purpose": "Repair booking production workload",
        "cost_owner": "Cloud finance team",
        "cost_center": "REPAIRS-01",
        "monthly_budget_usd": 250.0,
        "estimated_first_run_usd": 1.4,
        "data_classification": "customer-confidential",
        "target_ou": "Workloads/Production",
        "regions": ["us-east-2"],
        "allowed_regions": ["us-east-2", "us-west-2"],
        "approved_ous": ["Workloads/Production", "Workloads/Sandbox"],
        "access_group": "Booking-Operators",
        "permission_set": "Booking-Deploy",
        "baseline_version": "workload-baseline-3",
        "baseline_status": "verified",
        "baseline_evidence": ["fictional-control-report-01"],
        "recovery_owner": "Platform on-call",
        "access_allowed_test": "passed",
        "unrelated_access_denied_test": "passed",
        "application_smoke_test": "passed",
        "recovery_check": "passed",
        "cost_approval": "approved",
        "organization_change": True,
        "environment": "fictional-organization",
        "live_lab": False,
    }
    if kind == "create_new":
        packet.update({
            "account_creation_status": "succeeded",
            "account_id": "111122223333",
            "default_role_trust_review": "passed",
        })
    elif kind == "invite_existing":
        packet.update({
            "invitation_status": "accepted",
            "existing_owner_approval": "approved",
            "discovery_complete": True,
            "separate_access_path_verified": True,
        })
    return packet


def review(packet, seen_request_ids=()):
    """Return blockers; a clean packet needs a human decision before deployment."""
    blockers = []
    required = (
        "request_id", "account_email", "business_owner", "business_purpose", "cost_owner",
        "cost_center", "data_classification", "target_ou", "regions", "allowed_regions",
        "access_group", "permission_set", "baseline_version", "recovery_owner",
    )
    for field in required:
        if not packet.get(field):
            blockers.append(f"missing {field}")
    request_id = packet.get("request_id")
    if request_id in set(seen_request_ids):
        blockers.append("duplicate request_id: reconcile the existing request before retrying")
    if not isinstance(packet.get("regions"), list) or not packet.get("regions"):
        blockers.append("at least one intended Region is required")
    budget = packet.get("monthly_budget_usd")
    if not isinstance(budget, (int, float)) or isinstance(budget, bool) or not math.isfinite(budget) or budget <= 0:
        blockers.append("monthly budget must be a positive approved amount")
    if packet.get("cost_approval") != "approved":
        blockers.append("cost envelope lacks owner approval")
    if packet.get("target_ou") not in packet.get("approved_ous", []):
        blockers.append("target OU is not in the approved OU list")
    if not isinstance(packet.get("regions"), list) or not set(packet.get("regions", [])) <= set(packet.get("allowed_regions", [])):
        blockers.append("requested Regions include a Region outside the approved list")

    kind = packet.get("account_kind")
    if kind == "create_new":
        if packet.get("account_email", "").casefold() in {email.casefold() for email in packet.get("existing_account_emails", [])}:
            blockers.append("account email is already in use; reconcile identity before requesting creation")
        if packet.get("account_creation_status") != "succeeded" or not packet.get("account_id"):
            blockers.append("new-account creation result and account ID are not verified")
        if packet.get("default_role_trust_review") != "passed":
            blockers.append("default OrganizationAccountAccessRole trust is not reviewed")
    elif kind == "invite_existing":
        if packet.get("invitation_status") != "accepted":
            blockers.append("existing account owner has not accepted the invitation")
        if packet.get("existing_owner_approval") != "approved":
            blockers.append("existing account owner has not approved the onboarding plan")
        if packet.get("discovery_complete") is not True:
            blockers.append("existing resources, identities, data and dependencies are not inventoried")
        if packet.get("separate_access_path_verified") is not True:
            blockers.append("invitation did not prove a usable, approved access path")
    else:
        blockers.append("account_kind must be create_new or invite_existing")

    if packet.get("baseline_status") != "verified" or not packet.get("baseline_evidence"):
        blockers.append("baseline status and evidence are not verified")
    for field, label in (
        ("access_allowed_test", "intended access test"),
        ("unrelated_access_denied_test", "unrelated-action deny test"),
        ("application_smoke_test", "application smoke test"),
        ("recovery_check", "recovery check"),
    ):
        if packet.get(field) != "passed":
            blockers.append(f"{label} is missing or failed")

    if packet.get("environment") == "personal-trial" and packet.get("organization_change") is True:
        blockers.append("organization change is not permitted in the personal trial workflow")
    if packet.get("live_lab") is True:
        estimate = packet.get("estimated_first_run_usd")
        reserve = packet.get("credit_reserve_usd")
        if not isinstance(estimate, (int, float)) or isinstance(estimate, bool) or not math.isfinite(estimate) or estimate < 0 or estimate > 5:
            blockers.append("live lab estimate must be at or below USD 5")
        if not isinstance(reserve, (int, float)) or isinstance(reserve, bool) or not math.isfinite(reserve) or reserve < 100:
            blockers.append("live lab must preserve at least USD 100 of credits")

    return {"status": "blocked" if blockers else "ready_for_acceptance_review", "blockers": blockers}


def main():
    create = ready_packet("create_new")
    invite = ready_packet("invite_existing")
    existing_request_ids = [create["request_id"]]
    invite["request_id"] = "REQ-2402"

    # Positive cases: synthetic post-provisioning evidence; neither requests AWS.
    assert review(create)["status"] == "ready_for_acceptance_review"
    assert review(invite)["status"] == "ready_for_acceptance_review"

    cases = {}
    missing_owner = deepcopy(create)
    missing_owner["business_owner"] = ""
    cases["missing_business_owner"] = review(missing_owner)

    unaccepted = deepcopy(invite)
    unaccepted["invitation_status"] = "pending"
    unaccepted["separate_access_path_verified"] = False
    cases["unaccepted_invitation"] = review(unaccepted)

    duplicate = deepcopy(create)
    cases["duplicate_request"] = review(duplicate, existing_request_ids)

    failed_access = deepcopy(create)
    failed_access["unrelated_access_denied_test"] = "failed"
    cases["broad_access"] = review(failed_access)

    personal_trial = deepcopy(create)
    personal_trial["environment"] = "personal-trial"
    cases["trial_organization_guard"] = review(personal_trial)

    over_budget = deepcopy(create)
    over_budget["live_lab"] = True
    over_budget["estimated_first_run_usd"] = 5.01
    over_budget["credit_reserve_usd"] = 99.0
    cases["live_lab_budget_guard"] = review(over_budget)

    out_of_scope = deepcopy(create)
    out_of_scope["regions"] = ["eu-west-1"]
    cases["unapproved_region"] = review(out_of_scope)

    reused_email = deepcopy(create)
    reused_email["existing_account_emails"] = [create["account_email"].upper()]
    cases["duplicate_account_email"] = review(reused_email)

    expected = {
        "missing_business_owner", "unaccepted_invitation", "duplicate_request",
        "broad_access", "trial_organization_guard", "live_lab_budget_guard",
        "unapproved_region", "duplicate_account_email",
    }
    assert set(cases) == expected
    assert all(result["status"] == "blocked" and result["blockers"] for result in cases.values())
    report = {
        "scope": "fictional local request packets; no AWS API, credentials, account or policy changes",
        "ready_examples": 2,
        "blocked_changed_cases": cases,
        "meaning": "ready_for_acceptance_review is not authorization to deploy or proof that AWS accepted the request",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
