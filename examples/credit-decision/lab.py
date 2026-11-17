"""Cloud-free credit-decision exercise; never reads or changes an AWS account."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json


NOW = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)


def dollars(value: object) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("A money amount cannot be a boolean")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError) as error:
        raise ValueError("A money amount is missing or invalid") from error
    if not result.is_finite() or result < 0:
        raise ValueError("A money amount must be finite and nonnegative")
    return result


def when(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("A timestamp is missing")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("A timestamp is invalid") from error
    if result.tzinfo is None:
        raise ValueError("A timestamp needs a timezone")
    return result.astimezone(timezone.utc)


def assess(case: dict, now: datetime = NOW) -> dict:
    """Evaluate explicitly supplied *fictional* observations; never infer credit eligibility."""
    if now.tzinfo is None:
        raise ValueError("The observation time needs a timezone")
    reasons = []
    plan = case["plan"]
    terms = case["credit_terms"]
    run = case["run"]
    remaining = dollars(plan["remaining_usd"])
    estimate = dollars(run["estimate_usd"])
    reserve = dollars(run["reserve_usd"])
    spending_limit = dollars(run["spending_limit_usd"])
    headroom = remaining - estimate - reserve
    end = when(run["planned_end"])
    if plan["type"] != "FREE" or plan["status"] != "ACTIVE":
        reasons.append("The account is not a verified active Free plan")
    if not plan["selected_services_available"]:
        reasons.append("Selected services have not been confirmed available on this plan")
    if when(plan["expires_at"]) <= end:
        reasons.append("The Free plan expires before the run ends")
    if not terms["reviewed"] or not terms["selected_meters_applicable"]:
        reasons.append("Individual credit terms have not been reviewed for the selected meters")
    if when(terms["expires_at"]) <= end:
        reasons.append("The reviewed credit expires before the run ends")
    if spending_limit <= 0 or estimate <= 0 or estimate > spending_limit or not run["whole_cost_reviewed"]:
        reasons.append("A positive, reviewed whole-run estimate within the chosen limit is missing")
    if headroom < 0:
        reasons.append("The estimate would use the chosen credit reserve")
    if run["other_active_runs"] != 0:
        reasons.append("Another active run may claim the same credit headroom")
    if not run["scoped_non_root_identity"]:
        reasons.append("The execution identity is not confirmed scoped and non-root")
    if not run["cleanup_owner"] or when(run["cleanup_deadline"]) < end:
        reasons.append("Cleanup ownership and a deadline after the run are missing")
    return {
        "case": case["name"],
        "headroom_after_estimate_and_reserve_usd": str(headroom),
        "decision": "hold" if reasons else "candidate_for_separate_live_review",
        "reasons": reasons,
        "limit": "Fictional inputs; no AWS credit eligibility, current balance, spending cap, cleanup or deployment permission is proven",
    }


def cases() -> list[dict]:
    base = {
        "name": "reviewed bounded candidate",
        "plan": {"type": "FREE", "status": "ACTIVE", "remaining_usd": "81",
                 "selected_services_available": True, "expires_at": "2026-12-31T00:00:00Z"},
        "credit_terms": {"reviewed": True, "selected_meters_applicable": True,
                         "expires_at": "2026-12-31T00:00:00Z"},
        "run": {"estimate_usd": "3", "spending_limit_usd": "10", "reserve_usd": "75",
                "whole_cost_reviewed": True,
                "planned_end": "2026-10-22T00:00:00Z", "other_active_runs": 0,
                "scoped_non_root_identity": True, "cleanup_owner": "Maya",
                "cleanup_deadline": "2026-10-23T00:00:00Z"},
    }
    result = [base]
    for name, path, value in [
        ("balance but unknown terms", ("credit_terms", "reviewed"), False),
        ("service blocked on plan", ("plan", "selected_services_available"), False),
        ("plan ends during run", ("plan", "expires_at"), "2026-10-21T00:00:00Z"),
        ("parallel experiment", ("run", "other_active_runs"), 1),
        ("root execution", ("run", "scoped_non_root_identity"), False),
        ("reserve breached", ("plan", "remaining_usd"), "77"),
        ("missing cleanup owner", ("run", "cleanup_owner"), ""),
    ]:
        changed = deepcopy(base)
        changed["name"] = name
        changed[path[0]][path[1]] = value
        result.append(changed)
    return result


if __name__ == "__main__":
    print(json.dumps([assess(case) for case in cases()], indent=2))
