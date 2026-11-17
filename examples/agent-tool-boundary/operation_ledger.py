"""One-host operation-claim model for an already-authorized fictional tool call.

This module records claims and receipts. It does not authenticate callers,
approve actions, call a provider, or guarantee an external effect.
"""

from dataclasses import dataclass
from pathlib import Path
import sqlite3
import tempfile


@dataclass(frozen=True)
class Operation:
    operation_id: str
    actor: str
    job: str
    amount_cents: int
    approval_id: str


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=5, isolation_level=None)
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def initialize(path: Path) -> None:
    with _connect(path) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS operations (
            operation_id TEXT PRIMARY KEY,
            actor TEXT NOT NULL,
            job TEXT NOT NULL,
            amount_cents INTEGER NOT NULL,
            approval_id TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('pending', 'confirmed')),
            provider_receipt TEXT
        )""")


def reserve(path: Path, operation: Operation, max_new_actions: int = 1) -> str:
    """Claim an authorized operation once; pending retries need reconciliation."""
    if not operation.operation_id or max_new_actions < 1:
        raise ValueError("A stable operation ID and positive limit are required")
    connection = _connect(path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT actor, job, amount_cents, approval_id, status FROM operations WHERE operation_id=?",
            (operation.operation_id,),
        ).fetchone()
        if row:
            if row[:4] != (operation.actor, operation.job, operation.amount_cents, operation.approval_id):
                result = "conflict"
            else:
                result = "receipt_available" if row[4] == "confirmed" else "reconcile_required"
        elif connection.execute("SELECT COUNT(*) FROM operations").fetchone()[0] >= max_new_actions:
            result = "limit_reached"
        else:
            connection.execute(
                "INSERT INTO operations VALUES (?, ?, ?, ?, ?, 'pending', NULL)",
                (operation.operation_id, operation.actor, operation.job,
                 operation.amount_cents, operation.approval_id),
            )
            result = "reserved"
        connection.execute("COMMIT")
        return result
    except Exception:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()


def confirm(path: Path, operation_id: str, provider_receipt: str) -> str:
    """Record a supplied provider receipt; its authenticity is outside this lab."""
    if not provider_receipt:
        raise ValueError("A provider receipt is required")
    connection = _connect(path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT status, provider_receipt FROM operations WHERE operation_id=?",
            (operation_id,),
        ).fetchone()
        if row is None:
            result = "unknown_operation"
        elif row[0] == "confirmed":
            result = "same_receipt" if row[1] == provider_receipt else "receipt_conflict"
        else:
            connection.execute(
                "UPDATE operations SET status='confirmed', provider_receipt=? WHERE operation_id=?",
                (provider_receipt, operation_id),
            )
            result = "confirmed"
        connection.execute("COMMIT")
        return result
    except Exception:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "claims.sqlite3"
        initialize(path)
        operation = Operation("op-17", "maya", "repair-17", 1200, "approval-17")
        print("first claim:", reserve(path, operation))
        print("reply lost; same ID:", reserve(path, operation))
        print("different new action:", reserve(path, Operation("op-18", "maya", "repair-17", 1200, "approval-17")))
        print("trusted provider receipt supplied:", confirm(path, "op-17", "fictional-provider-17"))
        print("same ID after receipt:", reserve(path, operation))


if __name__ == "__main__":
    main()
