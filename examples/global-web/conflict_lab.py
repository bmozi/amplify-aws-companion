"""Two independent local writers expose a business conflict after convergence.

The selected winner is an invented ordering, not DynamoDB replication behavior.
No AWS service is called.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from failback_lab import Store, copy_and_check


def collision(first: Store, second: Store, winner: str) -> dict:
    """Confirm the same scarce slot independently, then select one toy winner."""
    if winner not in {"first", "second"}:
        raise ValueError("winner must be first or second")
    first.writer_open = True
    second.writer_open = True
    assert first.book("r-alice", "09:00", "Alice") == "ACCEPTED"
    assert second.book("r-bob", "09:00", "Bob") == "ACCEPTED"
    first.writer_open = second.writer_open = False

    acknowledged = first.rows() + second.rows()
    visible = (first if winner == "first" else second).rows()
    visible_receipts = {row[0] for row in visible}
    return {
        "both_confirmed": [row[0] for row in acknowledged],
        "toy_converged_winner": winner,
        "visible_receipts": sorted(visible_receipts),
        "missing_confirmed": sorted(row[0] for row in acknowledged
                                    if row[0] not in visible_receipts),
        "customer_promise": "FAILED_RECONCILIATION_REQUIRED",
    }


def single_writer_transfer(first: Store, second: Store) -> dict:
    """A cooperative handoff allows only one local booking writer at a time."""
    first.writer_open = True
    assert first.book("r-alice", "09:00", "Alice") == "ACCEPTED"
    closed_response = second.book("r-bob", "09:00", "Bob")
    first.writer_open = False
    transfer = copy_and_check(first, second, {"r-alice"})
    if transfer != "READY":
        raise RuntimeError(f"toy handoff stopped: {transfer}")
    second.writer_open = True
    same_slot = second.book("r-bob", "09:00", "Bob")
    other_slot = second.book("r-bob", "10:00", "Bob")
    second.writer_open = False
    return {
        "before_handoff": closed_response,
        "copy_receipt": transfer,
        "same_slot": same_slot,
        "other_slot": other_slot,
        "visible_receipts": [row[0] for row in second.rows()],
    }


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="a21-conflict-") as folder:
        root = Path(folder)
        first = Store(root / "first.sqlite", "first")
        second = Store(root / "second.sqlite", "second")
        try:
            unsafe = collision(first, second, "second")
        finally:
            first.close()
            second.close()

        first = Store(root / "first-safe.sqlite", "first-safe")
        second = Store(root / "second-safe.sqlite", "second-safe")
        try:
            guarded = single_writer_transfer(first, second)
        finally:
            first.close()
            second.close()
    return {"two_writers": unsafe, "one_writer_handoff": guarded}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
