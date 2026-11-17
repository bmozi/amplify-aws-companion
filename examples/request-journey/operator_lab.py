"""Local overdue-contact ownership drill; never contacts a person or calls AWS."""

import json
import sqlite3
from contextlib import contextmanager

from deadline_lab import accept, database, inspect_due, read_open_worklist, second


OPERATOR_SCHEMA = """
CREATE TABLE claims (
    request_id TEXT PRIMARY KEY REFERENCES escalations(request_id),
    operator_id TEXT NOT NULL,
    generation INTEGER NOT NULL CHECK (generation > 0),
    claimed_at INTEGER NOT NULL,
    lease_until INTEGER NOT NULL
);
CREATE TABLE attestations (
    request_id TEXT PRIMARY KEY REFERENCES requests(request_id),
    operator_id TEXT NOT NULL,
    generation INTEGER NOT NULL,
    contacted_at INTEGER NOT NULL,
    recorded_at INTEGER NOT NULL
);
"""


def operator_id(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 64:
        raise ValueError("Use a named fixture operator")
    return value


@contextmanager
def operator_database():
    with database() as connection:
        connection.executescript(OPERATOR_SCHEMA)
        yield connection


def _transaction(connection, action):
    connection.execute("BEGIN IMMEDIATE")
    try:
        result = action()
        connection.commit()
        return result
    except Exception:
        connection.rollback()
        raise


def claim_open_contact(connection, request_id, operator, now, lease_seconds=300):
    """Give one local operator a bounded claim on already-open work."""
    operator_id(operator)
    second(now)
    if type(lease_seconds) is not int or not 1 <= lease_seconds <= 900:
        raise ValueError("Lease must be 1–900 whole seconds")
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("Use a request ID")

    def act():
        open_row = connection.execute(
            """SELECT e.opened_at FROM escalations AS e
               LEFT JOIN contacts AS c USING (request_id)
               WHERE e.request_id = ? AND c.request_id IS NULL""", (request_id,)
        ).fetchone()
        if open_row is None or now < open_row[0]:
            raise ValueError("Request is not open overdue work at this time")
        row = connection.execute(
            "SELECT operator_id, generation, claimed_at, lease_until FROM claims WHERE request_id = ?",
            (request_id,),
        ).fetchone()
        if row and row[3] > now:
            if row[0] != operator:
                raise ValueError("Another operator holds the active claim")
            return {"request_id": request_id, "operator_id": operator,
                    "generation": row[1], "claimed_at": row[2], "lease_until": row[3]}
        generation = 1 if row is None else row[1] + 1
        if row is None:
            connection.execute("INSERT INTO claims VALUES (?, ?, ?, ?, ?)",
                               (request_id, operator, generation, now, now + lease_seconds))
        else:
            connection.execute(
                """UPDATE claims SET operator_id = ?, generation = ?, claimed_at = ?, lease_until = ?
                   WHERE request_id = ?""",
                (operator, generation, now, now + lease_seconds, request_id),
            )
        return {"request_id": request_id, "operator_id": operator,
                "generation": generation, "claimed_at": now, "lease_until": now + lease_seconds}

    return _transaction(connection, act)


def attest_first_contact(connection, claim, contacted_at, recorded_at):
    """Record a fixture claim once; a claim is not proof of customer contact."""
    if not isinstance(claim, dict):
        raise ValueError("Use a claim receipt")
    request_id = claim.get("request_id")
    operator = operator_id(claim.get("operator_id"))
    generation = claim.get("generation")
    if not isinstance(request_id, str) or not request_id or type(generation) is not int or generation < 1:
        raise ValueError("Use a valid claim receipt")
    second(contacted_at)
    second(recorded_at)
    if recorded_at < contacted_at:
        raise ValueError("A record time cannot precede the claimed contact")

    def act():
        accepted = connection.execute(
            "SELECT accepted_at FROM requests WHERE request_id = ?", (request_id,)
        ).fetchone()
        if accepted is None:
            raise ValueError("Request is missing")
        prior = connection.execute(
            """SELECT operator_id, generation, contacted_at, recorded_at
               FROM attestations WHERE request_id = ?""", (request_id,)
        ).fetchone()
        if prior:
            if prior[:3] != (operator, generation, contacted_at):
                raise ValueError("The first contact record cannot be rewritten")
            return {"request_id": request_id, "operator_id": operator,
                    "first_contact_at": prior[2], "recorded_at": prior[3],
                    "met_one_hour_promise": prior[2] <= accepted[0] + 3600}
        row = connection.execute(
            "SELECT operator_id, generation, claimed_at, lease_until FROM claims WHERE request_id = ?",
            (request_id,),
        ).fetchone()
        if (row is None or row[0] != operator or row[1] != generation
                or not row[2] <= contacted_at <= recorded_at < row[3]):
            raise ValueError("No active matching claim covers this contact attestation")
        if connection.execute("SELECT 1 FROM contacts WHERE request_id = ?", (request_id,)).fetchone():
            raise ValueError("A first contact is already recorded outside this claim")
        connection.execute("INSERT INTO contacts VALUES (?, ?)", (request_id, contacted_at))
        connection.execute("INSERT INTO attestations VALUES (?, ?, ?, ?, ?)",
                           (request_id, operator, generation, contacted_at, recorded_at))
        return {"request_id": request_id, "operator_id": operator,
                "first_contact_at": contacted_at, "recorded_at": recorded_at,
                "met_one_hour_promise": contacted_at <= accepted[0] + 3600}

    return _transaction(connection, act)


def run():
    with operator_database() as connection:
        accept(connection, "maya-r1", 0)
        inspect_due(connection, 3601)
        first = claim_open_contact(connection, "maya-r1", "operator-a", 3610, 60)
        retry = claim_open_contact(connection, "maya-r1", "operator-a", 3620, 60)
        late = attest_first_contact(connection, first, 3650, 3660)
        lost_reply_retry = attest_first_contact(connection, first, 3650, 4000)
        assert first == retry and late == lost_reply_retry
        assert late["met_one_hour_promise"] is False
        assert read_open_worklist(connection)["items"] == []
        accept(connection, "maya-r2", 0)
        inspect_due(connection, 4001)
        old = claim_open_contact(connection, "maya-r2", "operator-a", 4010, 20)
        replacement = claim_open_contact(connection, "maya-r2", "operator-b", 4030, 20)
        try:
            attest_first_contact(connection, old, 4020, 4031)
        except ValueError:
            stale_refused = True
        else:
            stale_refused = False
        assert stale_refused and replacement["generation"] == 2
        assert [x["request_id"] for x in read_open_worklist(connection)["items"]] == ["maya-r2"]
        print(json.dumps({"first_claim": first, "same_operator_retry": retry,
                          "late_fixture_attestation": late,
                          "lost_reply_retry_same_record": lost_reply_retry == late,
                          "replacement_claim": replacement,
                          "stale_attestation_refused": stale_refused,
                          "unresolved_open_work": ["maya-r2"],
                          "human_contact_observed": False,
                          "aws_called": False}, indent=2))


if __name__ == "__main__":
    run()
