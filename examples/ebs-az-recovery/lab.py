"""Cloud-free EBS recovery clock; every time is fictional, not an AWS measurement."""

from dataclasses import dataclass
import argparse
import json


@dataclass(frozen=True)
class Case:
    snapshot_captured_min: int = 10
    snapshot_available_min: int = 11
    failure_min: int = 14
    detect_min: int = 2
    create_and_attach_min: int = 3
    initialize_min: int = 6
    reconnect_and_check_min: int = 4
    rpo_target_min: int = 2
    rto_target_min: int = 15


def evaluate(case: Case) -> dict:
    if min(case.snapshot_captured_min, case.snapshot_available_min,
           case.failure_min, case.detect_min, case.create_and_attach_min,
           case.initialize_min, case.reconnect_and_check_min,
           case.rpo_target_min, case.rto_target_min) < 0:
        raise ValueError("Times and targets cannot be negative")
    if case.snapshot_captured_min > case.snapshot_available_min:
        raise ValueError("A snapshot cannot be available before its capture time")
    if case.snapshot_captured_min > case.failure_min:
        raise ValueError("A future snapshot cannot protect an earlier failure")

    ready = case.snapshot_available_min <= case.failure_min
    loss_window = case.failure_min - case.snapshot_captured_min
    restore_clock = (case.detect_min + case.create_and_attach_min +
                     case.initialize_min + case.reconnect_and_check_min)
    rpo_fits = ready and loss_window <= case.rpo_target_min
    rto_fits = ready and restore_clock <= case.rto_target_min
    return {
        "case": case.__dict__,
        "snapshot_ready_at_failure": ready,
        "possible_write_loss_window_min": loss_window,
        "fictional_recovery_clock_min": restore_clock,
        "rpo_arithmetic_fits": rpo_fits,
        "rto_arithmetic_fits": rto_fits,
        "decision": ("DESIGN_CANDIDATE_NEEDS_DRILL" if rpo_fits and rto_fits
                     else "HOLD_PROMISE"),
        "limits": ("A snapshot is a point-in-time copy, not a live second disk. "
                   "This clock omits observed AWS restore time, key permission, "
                   "instance capacity, data consistency, routing and customer checks."),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rpo", type=int, default=2, help="Fictional RPO minutes")
    parser.add_argument("--rto", type=int, default=15, help="Fictional RTO minutes")
    parser.add_argument("--capture", type=int, default=10)
    parser.add_argument("--available", type=int, default=11)
    parser.add_argument("--failure", type=int, default=14)
    parser.add_argument("--initialize", type=int, default=6)
    args = parser.parse_args()
    print(json.dumps(evaluate(Case(snapshot_captured_min=args.capture,
                                   snapshot_available_min=args.available,
                                   failure_min=args.failure,
                                   initialize_min=args.initialize,
                                   rpo_target_min=args.rpo,
                                   rto_target_min=args.rto)), indent=2))


if __name__ == "__main__":
    main()
