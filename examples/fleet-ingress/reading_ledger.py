"""Synthetic fleet reading ledger. No device authentication or AWS integration."""

import json
import sqlite3


def open_ledger(path=':memory:'):
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE IF NOT EXISTS readings (
        device TEXT NOT NULL,
        event_id TEXT NOT NULL,
        occurred_second INTEGER NOT NULL,
        first_arrival_second INTEGER NOT NULL,
        temperature_c INTEGER NOT NULL,
        PRIMARY KEY (device, event_id)
    )''')
    return db


def accept(db, trusted_device, claimed_device, event_id, occurred_second,
           arrival_second, temperature_c):
    """Compare a trusted *fixture input* with the body's claim before accounting."""
    with db:
        return accept_in_transaction(db, trusted_device, claimed_device, event_id,
                                     occurred_second, arrival_second, temperature_c)


def accept_in_transaction(db, trusted_device, claimed_device, event_id, occurred_second,
                          arrival_second, temperature_c):
    """Caller owns the SQLite transaction when joining an acceptance to a receipt."""
    validate_reading_inputs(trusted_device, claimed_device, event_id, occurred_second,
                            arrival_second, temperature_c)
    if claimed_device != trusted_device:
        return 'rejected_claim_mismatch'
    inserted = db.execute('''INSERT OR IGNORE INTO readings
        (device, event_id, occurred_second, first_arrival_second, temperature_c)
        VALUES (?, ?, ?, ?, ?)''',
        (trusted_device, event_id, occurred_second, arrival_second, temperature_c))
    if inserted.rowcount == 1:
        return 'accepted'
    old = db.execute('''SELECT occurred_second, temperature_c FROM readings
                        WHERE device = ? AND event_id = ?''',
                     (trusted_device, event_id)).fetchone()
    return 'duplicate' if old == (occurred_second, temperature_c) else 'rejected_conflict'


def validate_reading_inputs(trusted_device, claimed_device, event_id, occurred_second,
                            arrival_second, temperature_c):
    if any(type(value) is not str or not value or len(value) > 80
           for value in (trusted_device, claimed_device, event_id)):
        raise ValueError('Device and event identifiers must be bounded nonempty strings')
    if (any(type(value) is not int or value < 0 for value in (occurred_second, arrival_second))
            or type(temperature_c) is not int):
        raise ValueError('Times must be nonnegative integers and temperature an integer')
    if occurred_second > arrival_second:
        raise ValueError('This fixture does not model clocks ahead of arrival')


def report(db, device, start, end, expected_ids, warning_at_c=80):
    """Report one event-time window against an invented expected-ID manifest."""
    if type(device) is not str or not device or any(type(x) is not int for x in (start, end, warning_at_c)):
        raise ValueError('Invalid report identity or window')
    if start < 0 or end <= start or warning_at_c < 0:
        raise ValueError('Invalid report bounds')
    expected = list(expected_ids)
    if any(type(x) is not str or not x for x in expected) or len(expected) != len(set(expected)):
        raise ValueError('Expected IDs must be unique nonempty strings')
    rows = db.execute('''SELECT event_id, temperature_c FROM readings
                         WHERE device = ? AND occurred_second >= ? AND occurred_second < ?''',
                      (device, start, end)).fetchall()
    received = {event_id for event_id, _ in rows}
    missing = sorted(set(expected) - received)
    unexpected = sorted(received - set(expected))
    maximum = max((temp for _, temp in rows), default=None)
    status = ('warning' if maximum is not None and maximum >= warning_at_c else
              'unknown' if not expected or missing or unexpected else 'normal_against_manifest')
    return {'device': device, 'window': [start, end], 'received': len(rows),
            'missing_expected_ids': missing, 'unexpected_ids': unexpected,
            'maximum_observed_c': maximum, 'status': status,
            'scope': 'trusted fixture identity and expected-ID manifest; not physical truth'}


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization so fixture assertions execute')
    db = open_ledger()
    expected = [f'e{i}' for i in range(6)]
    before = report(db, 'van-17', 0, 360, expected)
    arrivals = [accept(db, 'van-17', 'van-17', f'e{i}', i * 60, 600 + i, 85 if i == 2 else 35)
                for i in range(5)]
    partial = report(db, 'van-17', 0, 360, expected)
    last = accept(db, 'van-17', 'van-17', 'e5', 300, 605, 35)
    complete = report(db, 'van-17', 0, 360, expected)
    duplicate = accept(db, 'van-17', 'van-17', 'e2', 120, 700, 85)
    conflict = accept(db, 'van-17', 'van-17', 'e2', 120, 701, 99)
    spoof = accept(db, 'van-17', 'van-18', 'e6', 330, 702, 90)
    other = accept(db, 'van-18', 'van-18', 'e2', 120, 703, 45)
    assert before['status'] == 'unknown' and before['maximum_observed_c'] is None
    assert arrivals == ['accepted'] * 5 and partial['missing_expected_ids'] == ['e5']
    assert partial['status'] == 'warning' and last == 'accepted'
    assert complete['received'] == 6 and complete['status'] == 'warning'
    assert duplicate == 'duplicate' and conflict == 'rejected_conflict'
    assert spoof == 'rejected_claim_mismatch' and other == 'accepted'
    assert report(db, 'van-17', 0, 360, expected) == complete
    print(json.dumps({'before': before, 'after_five': partial, 'after_six': complete,
                      'duplicate': duplicate, 'conflict': conflict, 'claim_mismatch': spoof,
                      'same_event_id_other_device': other,
                      'scope': 'sequential in-memory SQLite fixture; no device certificate, IoT rule, stream or AWS'},
                     indent=2))
    db.close()


if __name__ == '__main__':
    main()
