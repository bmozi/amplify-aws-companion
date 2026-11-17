"""Local SQLite model of a stale capacity check; no AWS calls or quota claims."""

from pathlib import Path
import sqlite3
import tempfile


def open_ledger(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=5)
    connection.execute("PRAGMA busy_timeout=5000")
    return connection


def initialize(path: Path, *, limit: int, used: int) -> None:
    if limit < 0 or used < 0 or used > limit:
        raise ValueError("Limit and use must be nonnegative, with use within limit")
    with open_ledger(path) as connection:
        connection.execute(
            "CREATE TABLE capacity (id INTEGER PRIMARY KEY CHECK (id = 1), "
            "unit_limit INTEGER NOT NULL, used INTEGER NOT NULL)"
        )
        connection.execute(
            "INSERT INTO capacity (id, unit_limit, used) VALUES (1, ?, ?)",
            (limit, used),
        )
        connection.execute(
            "CREATE TABLE requests (request_id TEXT PRIMARY KEY, "
            "units INTEGER NOT NULL, outcome TEXT NOT NULL "
            "CHECK (outcome IN ('reserved', 'full')))"
        )


def observe(path: Path, requested: int) -> dict[str, int | bool]:
    if requested <= 0:
        raise ValueError("A request must use positive units")
    with open_ledger(path) as connection:
        limit, used = connection.execute(
            "SELECT unit_limit, used FROM capacity WHERE id = 1"
        ).fetchone()
    return {
        "limit": limit,
        "used": used,
        "available": limit - used,
        "requested": requested,
        "fits_snapshot": used + requested <= limit,
    }


def reserve_if_current(path: Path, requested: int) -> bool:
    """One local conditional update; callers outside this ledger are not governed."""
    if requested <= 0:
        raise ValueError("A request must use positive units")
    with open_ledger(path) as connection:
        result = connection.execute(
            "UPDATE capacity SET used = used + ? "
            "WHERE id = 1 AND used + ? <= unit_limit",
            (requested, requested),
        )
        return result.rowcount == 1


def reserve_once(path: Path, request_id: str, requested: int) -> str:
    """Record one local intent and replay its outcome after a lost reply."""
    if not request_id.strip() or requested <= 0:
        raise ValueError("A nonempty request ID and positive units are required")
    with open_ledger(path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        prior = connection.execute(
            "SELECT units, outcome FROM requests WHERE request_id = ?", (request_id,)
        ).fetchone()
        if prior is not None:
            if prior[0] != requested:
                return "conflict"
            return prior[1]
        updated = connection.execute(
            "UPDATE capacity SET used = used + ? "
            "WHERE id = 1 AND used + ? <= unit_limit",
            (requested, requested),
        ).rowcount
        outcome = "reserved" if updated == 1 else "full"
        connection.execute(
            "INSERT INTO requests (request_id, units, outcome) VALUES (?, ?, ?)",
            (request_id, requested, outcome),
        )
        return outcome


def demonstrate() -> None:
    with tempfile.TemporaryDirectory(prefix="quota-race-") as directory:
        path = Path(directory) / "capacity.sqlite"
        initialize(path, limit=20, used=12)
        a = observe(path, 6)
        b = observe(path, 6)
        print(f"A and B both see {a['available']} free units; each 6-unit request fits its snapshot: "
              f"{a['fits_snapshot']} / {b['fits_snapshot']}")
        print("If both act solely on those snapshots: 12 + 6 + 6 = 24, above the fictional limit 20")
        accepted_a = reserve_if_current(path, 6)
        accepted_b = reserve_if_current(path, 6)
        end = observe(path, 6)
        print(f"Shared local conditional record: A={accepted_a}, B={accepted_b}, "
              f"recorded use={end['used']}, free={end['available']}")
        print("This record coordinates only its participants; it grants no AWS quota, permission or supply.")
        print("Lost reply example: request C's same ID returns its recorded outcome, not a second claim:")
        print(f"  C original/replay = {reserve_once(path, 'C', 2)} / "
              f"{reserve_once(path, 'C', 2)}; used={observe(path, 1)['used']}")


if __name__ == "__main__":
    demonstrate()
