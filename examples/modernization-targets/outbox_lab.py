"""Local transactional-outbox teaching model; no AWS client or network access."""
from contextlib import closing
import json
import sqlite3


def database(path=":memory:"):
    db = sqlite3.connect(path)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS bookings (id TEXT PRIMARY KEY, cents INTEGER NOT NULL CHECK(cents > 0));
        CREATE TABLE IF NOT EXISTS outbox (event_id TEXT PRIMARY KEY, booking_id TEXT NOT NULL UNIQUE,
                             cents INTEGER NOT NULL, published INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS processed (event_id TEXT PRIMARY KEY, booking_id TEXT NOT NULL UNIQUE,
                                cents INTEGER NOT NULL);
    """)
    return db


def book(db, booking_id, cents, *, fail_before_outbox=False):
    if not isinstance(booking_id, str) or not booking_id or type(cents) is not int or cents <= 0:
        raise ValueError("A nonempty booking ID and positive integer cents are required")
    with db:
        db.execute("INSERT INTO bookings VALUES (?,?)", (booking_id, cents))
        if fail_before_outbox:
            raise RuntimeError("synthetic crash before recording report work")
        db.execute("INSERT INTO outbox(event_id,booking_id,cents) VALUES (?,?,?)",
                   (f"booking:{booking_id}", booking_id, cents))


def relay(db, deliveries, *, fail_after_send=False):
    """Copy one pending row to a local list; a lost acknowledgment causes redelivery."""
    row = db.execute("SELECT event_id,booking_id,cents FROM outbox WHERE published=0 "
                     "ORDER BY event_id LIMIT 1").fetchone()
    if row is None:
        return False
    deliveries.append(dict(zip(("event_id", "booking_id", "cents"), row)))
    if fail_after_send:
        raise RuntimeError("synthetic crash after send, before outbox acknowledgment")
    with db:
        db.execute("UPDATE outbox SET published=1 WHERE event_id=?", (row[0],))
    return True


def process(db, event):
    """Apply one local delivery to a report projection, keyed by stable event ID."""
    if (not isinstance(event, dict) or set(event) != {"event_id", "booking_id", "cents"}
            or not all(isinstance(event[key], str) and event[key]
                       for key in ("event_id", "booking_id"))
            or event["event_id"] != f'booking:{event["booking_id"]}'
            or type(event["cents"]) is not int or event["cents"] <= 0):
        raise ValueError("Invalid local event envelope")
    with db:
        previous = db.execute("SELECT booking_id,cents FROM processed WHERE event_id=?",
                              (event["event_id"],)).fetchone()
        if previous is not None:
            if previous != (event["booking_id"], event["cents"]):
                raise ValueError("Conflicting redelivery for an accepted event ID")
            return "duplicate"
        db.execute("INSERT INTO processed VALUES (?,?,?)",
                   (event["event_id"], event["booking_id"], event["cents"]))
    return "accepted"


def reconcile(db):
    source = {row[0]: row[1] for row in db.execute("SELECT id,cents FROM bookings")}
    pending = {row[0]: row[1] for row in db.execute("SELECT booking_id,cents FROM outbox")}
    report = {row[0]: row[1] for row in db.execute("SELECT booking_id,cents FROM processed")}
    return {
        "source_count": len(source), "source_cents": sum(source.values()),
        "report_count": len(report), "report_cents": sum(report.values()),
        "missing_outbox": sorted(set(source) - set(pending)),
        "missing_report": sorted(set(source) - set(report)),
        "unexpected_report": sorted(set(report) - set(source)),
        "amount_mismatch": sorted(key for key in source.keys() & report.keys()
                                  if source[key] != report[key]),
    }


def main():
    with closing(database()) as db:
        deliveries = []
        book(db, "A", 1200)
        book(db, "B", 800)
        try:
            book(db, "C", 300, fail_before_outbox=True)
        except RuntimeError:
            pass
        try:
            relay(db, deliveries, fail_after_send=True)
        except RuntimeError:
            pass
        relay(db, deliveries)  # The same A event is sent again.
        relay(db, deliveries)  # B follows.
        before = reconcile(db)
        outcomes = [process(db, event) for event in deliveries]
        after = reconcile(db)
        assert before["missing_report"] == ["A", "B"]
        assert outcomes == ["accepted", "duplicate", "accepted"]
        assert after["source_cents"] == after["report_cents"] == 2000
        assert not any(after[key] for key in ("missing_outbox", "missing_report",
                                             "unexpected_report", "amount_mismatch"))
        print(json.dumps({"before_delivery": before, "delivery_outcomes": outcomes,
                          "after_reconciliation": after,
                          "scope": "sequential in-memory SQLite and list; no SQS, Lambda, AWS or concurrency"},
                         indent=2))


if __name__ == "__main__":
    main()
