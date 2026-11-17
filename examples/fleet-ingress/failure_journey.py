"""Local two-failure-path fleet drill; supplied identity and forwarding result are fixtures."""

import json
from pathlib import Path
import sqlite3
import tempfile

from reading_ledger import accept_in_transaction, open_ledger, report, validate_reading_inputs


def open_journey(path):
    db = open_ledger(path)
    db.execute('''CREATE TABLE IF NOT EXISTS deliveries (
        attempt_id TEXT PRIMARY KEY,
        trusted_device TEXT NOT NULL,
        claimed_device TEXT NOT NULL,
        event_id TEXT NOT NULL,
        occurred_second INTEGER NOT NULL,
        arrival_second INTEGER NOT NULL,
        temperature_c INTEGER NOT NULL,
        forward_state TEXT NOT NULL,
        business_outcome TEXT NOT NULL,
        reviewer TEXT,
        review_evidence TEXT
    )''')
    return db


def submit(db, attempt_id, trusted_device, claimed_device, event_id,
           occurred_second, arrival_second, temperature_c, *, forwarded):
    """Join one supplied forwarding result and ledger result in one local transaction."""
    if type(attempt_id) is not str or not attempt_id or len(attempt_id) > 80:
        raise ValueError('Attempt ID must be a bounded nonempty string')
    if type(forwarded) is not bool:
        raise ValueError('Forwarded must be a fixture boolean')
    validate_reading_inputs(trusted_device, claimed_device, event_id, occurred_second,
                            arrival_second, temperature_c)
    values = (trusted_device, claimed_device, event_id, occurred_second,
              arrival_second, temperature_c)
    with db:
        prior = db.execute('''SELECT trusted_device, claimed_device, event_id,
                             occurred_second, arrival_second, temperature_c
                             FROM deliveries WHERE attempt_id = ?''', (attempt_id,)).fetchone()
        if prior is not None:
            if prior != values:
                raise ValueError('Attempt ID reused for different reading')
            return 'duplicate_delivery'
        outcome = ('not_seen' if not forwarded else
                   accept_in_transaction(db, *values))
        db.execute('''INSERT INTO deliveries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)''',
                   (attempt_id, *values, 'admitted' if forwarded else 'failed', outcome))
        return outcome if forwarded else 'forwarding_failed'


def retry_forwarding(db, attempt_id, reviewer, evidence):
    """A supplied human-review receipt permits one local retry of a failed forward."""
    if any(type(x) is not str or not x.strip() or len(x) > 120 for x in (reviewer, evidence)):
        raise ValueError('Reviewer and evidence must be bounded nonempty strings')
    with db:
        row = db.execute('''SELECT trusted_device, claimed_device, event_id,
                           occurred_second, arrival_second, temperature_c, forward_state
                           FROM deliveries WHERE attempt_id = ?''', (attempt_id,)).fetchone()
        if row is None or row[-1] != 'failed':
            raise ValueError('Only a recorded forwarding failure may be retried')
        outcome = accept_in_transaction(db, *row[:-1])
        db.execute('''UPDATE deliveries SET forward_state = 'admitted', business_outcome = ?,
                      reviewer = ?, review_evidence = ? WHERE attempt_id = ?''',
                   (outcome, reviewer.strip(), evidence.strip(), attempt_id))
        return outcome


def unresolved(db):
    return db.execute('''SELECT attempt_id, forward_state, business_outcome
                         FROM deliveries WHERE forward_state = 'failed'
                         OR business_outcome LIKE 'rejected_%' ORDER BY attempt_id''').fetchall()


def main():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / 'fleet.sqlite')
        db = open_journey(path)
        failed = submit(db, 'attempt-1', 'van-17', 'van-17', 'e1', 60, 600, 35,
                        forwarded=False)
        mismatch = submit(db, 'attempt-2', 'van-17', 'van-18', 'e2', 120, 601, 85,
                          forwarded=True)
        before = report(db, 'van-17', 0, 360, ['e1', 'e2'])
        db.close()
        db = open_journey(path)
        retained = unresolved(db)
        repaired = retry_forwarding(db, 'attempt-1', 'fixture-operator', 'reviewed source e1')
        after = report(db, 'van-17', 0, 360, ['e1', 'e2'])
        remaining = unresolved(db)
        assert failed == 'forwarding_failed' and mismatch == 'rejected_claim_mismatch'
        assert before['received'] == 0 and len(retained) == 2
        assert repaired == 'accepted' and after['received'] == 1
        assert remaining == [('attempt-2', 'admitted', 'rejected_claim_mismatch')]
        print(json.dumps({'before': before, 'retained_issues': retained,
                          'reviewed_retry': repaired, 'after': after,
                          'remaining_issues': remaining,
                          'scope': 'one SQLite database and supplied fixture facts; no IoT rule, stream, identity or cloud delivery'},
                         indent=2))
        db.close()


if __name__ == '__main__':
    main()
