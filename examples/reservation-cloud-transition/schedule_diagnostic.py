"""Local evidence-classification drill for A03; no AWS client or account access."""

import json


CASES = (
    {
        "name": "target_not_delivered", "scheduler_delivery": "failed",
        "lambda_result": "not_accepted", "delivery_queue": 1,
        "execution_queue": 0, "due_base_records": 2, "page_limit_reached": False,
        "expected": "delivery_failure",
    },
    {
        "name": "page_two_exception", "scheduler_delivery": "accepted",
        "lambda_result": "failed", "delivery_queue": 0,
        "execution_queue": 1, "due_base_records": 2, "page_limit_reached": False,
        "committed_releases": 5, "expected": "execution_failure",
    },
    {
        "name": "fifteen_entry_cap", "scheduler_delivery": "accepted",
        "lambda_result": "succeeded", "delivery_queue": 0,
        "execution_queue": 0, "due_base_records": 1, "page_limit_reached": True,
        "expected": "unfinished_backlog",
    },
    {
        "name": "quiet_queues_unknown_work", "scheduler_delivery": "accepted",
        "lambda_result": "unknown", "delivery_queue": 0,
        "execution_queue": 0, "due_base_records": None,
        "page_limit_reached": False, "expected": "insufficient_evidence",
    },
    {
        "name": "index_looked_empty", "scheduler_delivery": "accepted",
        "lambda_result": "succeeded", "delivery_queue": 0,
        "execution_queue": 0, "due_base_records": 1,
        "page_limit_reached": False, "expected": "reconcile_base_records",
    },
    {
        "name": "observed_clear_pass", "scheduler_delivery": "accepted",
        "lambda_result": "succeeded", "delivery_queue": 0,
        "execution_queue": 0, "due_base_records": 0,
        "page_limit_reached": False, "expected": "clear_at_observation",
    },
    {
        "name": "both_failure_records", "scheduler_delivery": "failed",
        "lambda_result": "failed", "delivery_queue": 1,
        "execution_queue": 1, "due_base_records": None,
        "page_limit_reached": False, "expected": "investigate_both_paths",
    },
)


def classify(evidence):
    """Return the narrowest supported observation, never a future SLA claim."""
    delivery = evidence["scheduler_delivery"]
    result = evidence["lambda_result"]
    delivery_failed = delivery == "failed" or evidence["delivery_queue"] > 0
    execution_failed = result == "failed" or evidence["execution_queue"] > 0
    if delivery_failed and execution_failed:
        return "investigate_both_paths"
    if delivery_failed:
        return "delivery_failure"
    if execution_failed:
        return "execution_failure"
    if delivery != "accepted" or result != "succeeded":
        return "insufficient_evidence"
    due = evidence["due_base_records"]
    if due is None:
        return "insufficient_evidence"
    if evidence["page_limit_reached"]:
        return "unfinished_backlog"
    if due > 0:
        return "reconcile_base_records"
    return "clear_at_observation"


def quiet_queue_shortcut(evidence):
    """Intentionally wrong shortcut for the learner's negative control."""
    return "all_clear" if not evidence["delivery_queue"] and not evidence["execution_queue"] else "investigate"


def main():
    rows = []
    for case in CASES:
        observed = classify(case)
        assert observed == case["expected"], case["name"]
        rows.append({"case": case["name"], "shortcut": quiet_queue_shortcut(case),
                     "supported_observation": observed})
    assert sum(row["shortcut"] == "all_clear" and row["supported_observation"] != "clear_at_observation"
               for row in rows) == 3
    print(json.dumps({"scope": "authored local evidence; no AWS event or learner result",
                      "cases": rows}, indent=2))


if __name__ == "__main__":
    main()
