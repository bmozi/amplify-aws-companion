"""Paper recovery gate for a fictional two-cluster design; no AWS operations."""

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
GATES = (
    "reviewed_image_and_config",
    "target_capacity",
    "data_checkpoint_within_rpo",
    "key_and_identity_access",
    "customer_path_healthy",
    "old_writer_fenced",
)


def review(case):
    if case.get("fictional") is not True:
        raise ValueError("Only explicitly fictional recovery cases are accepted")
    gates = case.get("gates")
    if not isinstance(gates, dict) or set(gates) != set(GATES) or any(type(value) is not bool for value in gates.values()):
        raise ValueError("Recovery requires six explicit boolean gate observations")
    failed = [name for name in GATES if not gates[name]]
    return {
        "decision": "hold" if failed else "candidate_for_observed_drill",
        "failed_gates": failed,
        "rto_proven": False,
    }


def main():
    case = json.loads((HERE / "case.json").read_text())
    result = review(case)
    print(f"Paper decision: {result['decision']}")
    print("Missing gate evidence: " + (", ".join(result["failed_gates"]) or "none in this fictional card"))
    print("RTO proven: no. Run a timed customer-level drill before making that claim.")


if __name__ == "__main__":
    main()
