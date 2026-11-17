"""Fictional recovery dependency screen. No AWS calls or measured durations."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Step:
    name: str
    minutes: int
    after: tuple[str, ...] = ()


def schedule(steps: tuple[Step, ...]) -> dict[str, dict[str, object]]:
    """Find earliest starts in a reviewed dependency graph, not a cloud RTO."""
    names = [step.name for step in steps]
    if len(names) != len(set(names)) or not names:
        raise ValueError("steps need distinct names")
    by_name = {step.name: step for step in steps}
    for step in steps:
        if not isinstance(step.minutes, int) or isinstance(step.minutes, bool) or step.minutes < 0:
            raise ValueError(f"invalid duration: {step.name}")
        if step.name in step.after or any(dep not in by_name for dep in step.after):
            raise ValueError(f"invalid dependency: {step.name}")

    result: dict[str, dict[str, object]] = {}
    visiting: set[str] = set()

    def visit(name: str) -> dict[str, object]:
        if name in result:
            return result[name]
        if name in visiting:
            raise ValueError("dependency cycle")
        visiting.add(name)
        step = by_name[name]
        prior = [visit(dep) for dep in step.after]
        longest = max(prior, key=lambda item: int(item["end"]), default=None)
        start = int(longest["end"]) if longest else 0
        chain = (*longest["chain"], name) if longest else (name,)
        result[name] = {"start": start, "end": start + step.minutes, "chain": chain}
        visiting.remove(name)
        return result[name]

    for name in names:
        visit(name)
    return result


def plan(worker_minutes: int = 12, restore_minutes: int = 8) -> tuple[Step, ...]:
    return (
        Step("detect_and_decide", 4),
        Step("destination_key_check", 2, ("detect_and_decide",)),
        Step("restore_data", restore_minutes, ("destination_key_check",)),
        Step("reconcile_confirmations", 6, ("restore_data",)),
        Step("prepare_workers", worker_minutes, ("detect_and_decide",)),
        Step("prove_capacity", 2, ("prepare_workers",)),
        Step("fence_old_writer", 3, ("detect_and_decide",)),
        Step("customer_read_and_write", 3,
             ("reconcile_confirmations", "prove_capacity", "fence_old_writer")),
        Step("route_and_confirm", 2, ("customer_read_and_write",)),
    )


@dataclass(frozen=True)
class Evidence:
    confirmed: tuple[tuple[str, int], ...] = (("B110", 1200), ("B111", 2300))
    candidate: tuple[tuple[str, int], ...] = (("B110", 1200),)
    journal: tuple[tuple[str, int], ...] = (("B111", 2300),)
    confirmation_inventory_complete: bool = False
    copy_complete: bool = False
    destination_key_usable: bool = False
    old_writer_fenced: bool = False
    customer_check_passed: bool = False
    capacity_per_minute: int = 80
    demand_per_minute: int = 80


def booking_values(rows: tuple[tuple[str, int], ...], source: str) -> dict[str, int]:
    """Reject malformed or duplicate supplied receipts before comparing them."""
    values = {}
    if not isinstance(rows, tuple):
        raise ValueError(f"{source} receipts must be a tuple")
    for row in rows:
        if (not isinstance(row, tuple) or len(row) != 2
                or not isinstance(row[0], str) or not row[0]
                or type(row[1]) is not int or row[1] <= 0):
            raise ValueError(f"invalid {source} booking receipt")
        booking_id, amount_cents = row
        if booking_id in values:
            raise ValueError(f"duplicate {source} booking ID: {booking_id}")
        values[booking_id] = amount_cents
    return values


def evaluate(steps: tuple[Step, ...], evidence: Evidence, target_minute: int = 20) -> dict:
    checks = (evidence.confirmation_inventory_complete, evidence.copy_complete, evidence.destination_key_usable,
              evidence.old_writer_fenced, evidence.customer_check_passed)
    if any(type(value) is not bool for value in checks):
        raise ValueError("evidence checks must be explicit booleans; unknown requires investigation")
    if (any(type(value) is not int for value in
            (target_minute, evidence.demand_per_minute, evidence.capacity_per_minute))
            or target_minute <= 0 or evidence.demand_per_minute <= 0 or evidence.capacity_per_minute < 0):
        raise ValueError("target, demand and capacity need valid nonnegative units")
    timeline = schedule(steps)
    if "route_and_confirm" not in timeline:
        raise ValueError("route_and_confirm step is required")
    projected = int(timeline["route_and_confirm"]["end"])
    blockers = []
    if not evidence.copy_complete:
        blockers.append("copy job has no completed receipt")
    if not evidence.destination_key_usable:
        blockers.append("destination recovery role cannot use the key")
    confirmed = booking_values(evidence.confirmed, "confirmed")
    if not evidence.confirmation_inventory_complete:
        blockers.append("confirmation inventory completeness is not established")
    candidate = booking_values(evidence.candidate, "candidate")
    journal = booking_values(evidence.journal, "journal")
    source_conflicts = sorted(key for key in candidate.keys() & journal.keys()
                              if candidate[key] != journal[key])
    recovered = candidate | journal
    missing = sorted(confirmed.keys() - recovered.keys())
    extra = sorted(recovered.keys() - confirmed.keys())
    changed = sorted(key for key in confirmed.keys() & recovered.keys()
                     if confirmed[key] != recovered[key])
    if missing or extra or changed or source_conflicts:
        blockers.append("confirmation reconciliation differs: "
                        f"missing={missing}, extra={extra}, changed={changed}, "
                        f"source_conflicts={source_conflicts}")
    if not evidence.old_writer_fenced:
        blockers.append("old writer remains able to accept work")
    if evidence.capacity_per_minute < evidence.demand_per_minute:
        blockers.append("surviving capacity is below declared demand")
    if not evidence.customer_check_passed:
        blockers.append("customer read/write acceptance has not passed")
    if projected > target_minute:
        blockers.append(f"projected {projected} min exceeds {target_minute} min target")
    return {
        "projected_customer_minute": projected,
        "critical_chain": timeline["route_and_confirm"]["chain"],
        "blockers": blockers,
        "decision": "PLAN_FITS_ASSUMPTIONS" if not blockers else "NO_GO",
        "scope": "Authored durations and supplied booking values; no elapsed AWS time, IAM, key, RPO or customer result measured",
    }


def main() -> None:
    # These are supplied fictional claims for the worked example, not observations.
    base = Evidence(confirmation_inventory_complete=True, copy_complete=True,
                    destination_key_usable=True, old_writer_fenced=True,
                    customer_check_passed=True)
    cases = (
        ("pilot_light", plan(), base),
        ("warm_workers_only", plan(worker_minutes=2), base),
        ("faster_restore_only", plan(restore_minutes=3), base),
        ("both_paths", plan(worker_minutes=2, restore_minutes=3), base),
        ("key_denied", plan(worker_minutes=2, restore_minutes=3),
         replace(base, destination_key_usable=False)),
        ("missing_confirmation", plan(worker_minutes=2, restore_minutes=3),
         replace(base, journal=())),
        ("wrong_amount", plan(worker_minutes=2, restore_minutes=3),
         replace(base, candidate=(("B110", 1300),))),
        ("conflicting_sources", plan(worker_minutes=2, restore_minutes=3),
         replace(base, candidate=(("B110", 1200), ("B111", 2500)))),
    )
    for name, steps, evidence in cases:
        answer = evaluate(steps, evidence)
        print(f"{name}: {answer['projected_customer_minute']} min; "
              f"{answer['decision']}; blockers={answer['blockers']}")
    print("All minutes and receipts are fictional. No AWS calls or customer RTO measurement.")


if __name__ == "__main__":
    main()
