"""Cloud-free evidence screen for a proposed A02 scan-to-index pilot."""

import argparse
import json
from pathlib import Path


def review(case):
    required = {"windows", "key_violations", "cost_reviewed", "operator_assigned"}
    if set(case) != required or not isinstance(case["windows"], list):
        raise ValueError("Supply windows, key_violations, cost_reviewed and operator_assigned")
    if not case["windows"]:
        raise ValueError("At least one observation window is required")
    if not isinstance(case["key_violations"], list) or any(
        not isinstance(x, str) or not x for x in case["key_violations"]
    ):
        raise ValueError("key_violations must list nonempty identifiers")
    if type(case["cost_reviewed"]) is not bool or type(case["operator_assigned"]) is not bool:
        raise ValueError("Cost and operator decisions must be Boolean")

    windows = []
    seen_active = False
    for number, window in enumerate(case["windows"], 1):
        if set(window) != {"status", "scan_complete", "base_due", "index_visible"}:
            raise ValueError("Each window needs status, scan_complete, base_due and index_visible")
        if window["status"] not in {"CREATING", "ACTIVE"} or type(window["scan_complete"]) is not bool:
            raise ValueError("Use CREATING/ACTIVE and an explicit scan_complete Boolean")
        if seen_active and window["status"] == "CREATING":
            raise ValueError("One index cannot return to CREATING after ACTIVE in this fixture")
        seen_active = seen_active or window["status"] == "ACTIVE"
        for name in ("base_due", "index_visible"):
            values = window[name]
            if not isinstance(values, list) or any(not isinstance(x, str) or not x for x in values):
                raise ValueError(f"{name} must list nonempty identifiers")
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must contain distinct identifiers")
        truth, candidates = set(window["base_due"]), set(window["index_visible"])
        windows.append({
            "window": number,
            "status": window["status"],
            "scan_complete": window["scan_complete"],
            "missed_by_index": sorted(truth - candidates),
            "stale_candidates_to_base_check": sorted(candidates - truth),
        })

    active = [w for w in windows if w["status"] == "ACTIVE"]
    reasons = []
    if windows[-1]["status"] != "ACTIVE":
        reasons.append("index_not_active")
    if len(active) < 2:
        reasons.append("fewer_than_two_active_observations")
    if any(not w["scan_complete"] for w in active):
        reasons.append("incomplete_base_reconciliation")
    if any(w["missed_by_index"] for w in active):
        reasons.append("observed_index_miss_needs_investigation")
    if case["key_violations"]:
        reasons.append("unresolved_index_key_violations")
    if not case["cost_reviewed"]:
        reasons.append("whole_run_cost_not_reviewed")
    if not case["operator_assigned"]:
        reasons.append("no_reconciliation_owner")
    return {
        "kind": "authored_sequential_observations_not_dynamodb_measurement",
        "recommendation": "keep_scan" if reasons else "consider_bounded_pilot_with_scan_fallback",
        "reasons": reasons,
        "windows": windows,
        "required_even_for_pilot": [
            "base_record_recheck_and_final_condition",
            "periodic_complete_reconciliation",
            "monitored_operator_and_rollback_path",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    args = parser.parse_args()
    print(json.dumps(review(json.loads(args.case.read_text())), indent=2))


if __name__ == "__main__":
    main()
