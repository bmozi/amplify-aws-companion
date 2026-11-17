"""Fictional, account-neutral cost decision drill. Makes no AWS calls."""

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path


FIELDS = (
    "run_estimate_usd", "chosen_run_limit_usd", "credit_balance_usd",
    "chosen_credit_reserve_usd", "gross_monthly_used_usd",
    "gross_monthly_budget_usd", "chosen_budget_margin_usd",
)


def amount(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("Use a finite, nonnegative USD amount") from error
    if not result.is_finite() or result < 0:
        raise ValueError("Use a finite, nonnegative USD amount")
    return result


def assess(case):
    """Evaluate supplied fictional facts; never interpret this as authorization."""
    values = {field: amount(case[field]) for field in FIELDS}
    evidence_holds = []
    if case.get("credit_applicability_checked") is not True:
        evidence_holds.append("Credit applicability is unverified")
    if case.get("usage_snapshot_current") is not True:
        evidence_holds.append("Gross usage snapshot is unverified or stale")
    if evidence_holds:
        return {"decision": "hold", "reasons": evidence_holds}

    estimate = values["run_estimate_usd"]
    after_credits = values["credit_balance_usd"] - estimate
    after_gross = (values["gross_monthly_budget_usd"]
                   - values["gross_monthly_used_usd"]
                   - estimate - values["chosen_budget_margin_usd"])
    reasons = []
    if estimate > values["chosen_run_limit_usd"]:
        reasons.append("Run estimate exceeds the chosen per-run limit")
    if after_credits < values["chosen_credit_reserve_usd"]:
        reasons.append("Projected credits fall below the chosen reserve")
    if after_gross < 0:
        reasons.append("Run and margin exceed gross monthly budget headroom")
    return {
        "decision": "review_candidate" if not reasons else "hold",
        "reasons": reasons,
        "projected_credit_balance_usd": str(after_credits),
        "gross_headroom_after_run_and_margin_usd": str(after_gross),
        "limit": "Arithmetic on supplied facts only; no hard cap, account check or live authorization",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_file", nargs="?", type=Path,
                        default=Path(__file__).with_name("cases.json"),
                        help="JSON case list to evaluate (default: bundled cases.json)")
    args = parser.parse_args()
    cases = json.loads(args.case_file.read_text(encoding="utf-8"))
    for case in cases:
        result = assess(case)
        print(json.dumps({"case": case["name"], **result}, indent=2))


if __name__ == "__main__":
    main()
