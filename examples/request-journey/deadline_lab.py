"""Local one-hour contact worklist. No AWS calls or customer notifications."""

import json
import sqlite3
from contextlib import contextmanager


SCHEMA = """
CREATE TABLE requests (
    request_id TEXT PRIMARY KEY,
    accepted_at INTEGER NOT NULL CHECK (accepted_at >= 0)
);
CREATE TABLE contacts (
    request_id TEXT PRIMARY KEY REFERENCES requests(request_id),
    contacted_at INTEGER NOT NULL CHECK (contacted_at >= 0)
);
CREATE TABLE escalations (
    request_id TEXT PRIMARY KEY REFERENCES requests(request_id),
    opened_at INTEGER NOT NULL CHECK (opened_at >= 0)
);
"""

PROMISE_SECONDS = 60 * 60


def second(value):
    if type(value) is not int or value < 0:
        raise ValueError("Use a trusted nonnegative integer second")
    return value


@contextmanager
def database():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    try:
        yield connection
    finally:
        connection.close()


def accept(connection, request_id, accepted_at):
    """Return the original acceptance time; a retry cannot move the deadline."""
    if not isinstance(request_id, str) or not request_id or len(request_id) > 64:
        raise ValueError("Use a short request ID")
    second(accepted_at)
    with connection:
        connection.execute(
            "INSERT OR IGNORE INTO requests VALUES (?, ?)", (request_id, accepted_at)
        )
    return connection.execute(
        "SELECT accepted_at FROM requests WHERE request_id = ?", (request_id,)
    ).fetchone()[0]


def inspect_due(connection, now, limit=20):
    """Record newly overdue work; the return value is not the open worklist."""
    second(now)
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Use a 1–100 item limit")
    # The exact deadline second still permits a contact; open work afterward.
    cutoff = now - PROMISE_SECONDS - 1
    if cutoff < 0:
        return []
    with connection:
        # A contact after the deadline does not erase the historical breach.
        rows = connection.execute(
            """SELECT r.request_id, r.accepted_at
               FROM requests AS r LEFT JOIN contacts AS c USING (request_id)
               WHERE r.accepted_at <= ?
                 AND (c.request_id IS NULL OR c.contacted_at > r.accepted_at + ?)
                 AND NOT EXISTS (SELECT 1 FROM escalations AS e
                                 WHERE e.request_id = r.request_id)
               ORDER BY r.accepted_at, r.request_id LIMIT ?""",
            (cutoff, PROMISE_SECONDS, limit),
        ).fetchall()
        connection.executemany(
            "INSERT INTO escalations VALUES (?, ?)",
            [(request_id, now) for request_id, _ in rows],
        )
    return [{"request_id": request_id, "accepted_at": accepted_at,
             "deadline_at": accepted_at + PROMISE_SECONDS} for request_id, accepted_at in rows]


def read_open_worklist(connection, limit=20, after=None):
    """Read unresolved escalations again, even if the check's reply was lost.

    The cursor is (accepted_at, request_id). Re-start from the beginning after
    working a batch: this local keyset traversal is not a distributed snapshot.
    """
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Use a 1–100 item limit")
    if after is not None:
        if (not isinstance(after, tuple) or len(after) != 2
                or type(after[0]) is not int or after[0] < 0
                or not isinstance(after[1], str) or not after[1]):
            raise ValueError("Use an (accepted_at, request_id) cursor")
    where = "" if after is None else "AND (r.accepted_at, r.request_id) > (?, ?)"
    args = [] if after is None else list(after)
    rows = connection.execute(
        f"""SELECT r.request_id, r.accepted_at, e.opened_at
            FROM escalations AS e
            JOIN requests AS r USING (request_id)
            LEFT JOIN contacts AS c USING (request_id)
            WHERE c.request_id IS NULL {where}
            ORDER BY r.accepted_at, r.request_id LIMIT ?""",
        (*args, limit + 1),
    ).fetchall()
    visible = rows[:limit]
    items = [{"request_id": request_id, "accepted_at": accepted_at,
              "deadline_at": accepted_at + PROMISE_SECONDS, "opened_at": opened_at}
             for request_id, accepted_at, opened_at in visible]
    next_cursor = ((visible[-1][1], visible[-1][0])
                   if len(rows) > limit else None)
    return {"items": items, "next_cursor": next_cursor}


def record_contact(connection, request_id, contacted_at):
    second(contacted_at)
    row = connection.execute(
        "SELECT accepted_at FROM requests WHERE request_id = ?", (request_id,)
    ).fetchone()
    if row is None or contacted_at < row[0]:
        raise ValueError("Contact requires an accepted request and later time")
    with connection:
        connection.execute(
            "INSERT OR IGNORE INTO contacts VALUES (?, ?)", (request_id, contacted_at)
        )
    first = connection.execute(
        "SELECT contacted_at FROM contacts WHERE request_id = ?", (request_id,)
    ).fetchone()[0]
    return {"request_id": request_id, "first_contact_at": first,
            "met_one_hour_promise": first <= row[0] + PROMISE_SECONDS}


def run():
    with database() as connection:
        original = accept(connection, "maya-r1", 0)
        retry = accept(connection, "maya-r1", 200)
        before = inspect_due(connection, 3599)
        at_deadline = inspect_due(connection, 3600)
        overdue = inspect_due(connection, 3601)
        repeated_tick = inspect_due(connection, 3602)
        open_after_lost_reply = read_open_worklist(connection)
        late_contact = record_contact(connection, "maya-r1", 4 * 3600)
        open_after_contact = read_open_worklist(connection)
        remaining = connection.execute("SELECT COUNT(*) FROM escalations").fetchone()[0]
        result = {"accepted_at": original, "retry_accepted_at": retry,
                  "before_deadline": before, "at_deadline": at_deadline,
                  "overdue": overdue,
                  "repeated_tick": repeated_tick,
                  "open_after_lost_reply": open_after_lost_reply,
                  "late_contact": late_contact,
                  "open_after_contact": open_after_contact,
                  "escalation_records": remaining,
                  "human_contact_or_notification_sent": False}
        assert original == retry == 0
        assert before == [] and at_deadline == [] and len(overdue) == 1 and repeated_tick == []
        assert len(open_after_lost_reply["items"]) == 1
        assert open_after_contact["items"] == []
        assert late_contact["met_one_hour_promise"] is False and remaining == 1
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
