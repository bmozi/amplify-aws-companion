"""Reconcile fictional note-save observations; no AWS access or dependencies."""

import json
from pathlib import Path


def review(case):
    """Return a bounded observation, never infer unseen customer attempts."""
    observed = case["observed_attempt_ids"]
    confirmed = case["confirmed_after_refresh_ids"]
    expected = case["independent_attempt_ids"]
    if len(observed) != len(set(observed)) or len(confirmed) != len(set(confirmed)):
        raise ValueError("duplicate event ID: resolve replay before counting")
    if expected is not None and len(expected) != len(set(expected)):
        raise ValueError("duplicate independent attempt ID: resolve ledger identity")
    if not set(confirmed) <= set(observed):
        raise ValueError("confirmation without a matching observed attempt")

    missing = sorted(set(expected) - set(observed)) if expected is not None else None
    unexpected = sorted(set(observed) - set(expected)) if expected is not None else None
    complete = (case["window_closed"] and case["confirmation_window_closed"] and
                expected is not None and
                not missing and not unexpected)
    rate = len(confirmed) / len(expected) if complete and expected else None
    return {
        "name": case["name"],
        "page_success_count": case["page_success_count"],
        "page_success_rate": None,  # No fixture supplies all page-load attempts.
        "observed_save_attempts": len(observed),
        "missing_attempt_ids": missing,
        "unexpected_attempt_ids": unexpected,
        "heartbeat_seen": case["heartbeat_seen"],
        "save_confirmation_rate": rate,
        "coverage": "reconciled_for_fixture" if complete else "unknown_or_incomplete",
    }


def main():
    cases = json.loads(Path(__file__).with_name("cases.json").read_text())
    for case in cases:
        print(json.dumps(review(case), sort_keys=True))


if __name__ == "__main__":
    main()
