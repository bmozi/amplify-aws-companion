"""Synthetic scan plus distinct human review over one immutable local file record."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import threading

from lab import delete, initialize, read, upload


def initialize_review(path):
    initialize(path)
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE actor_roles (actor TEXT NOT NULL, role TEXT NOT NULL, PRIMARY KEY(actor, role))')
        db.execute('CREATE TABLE gate_decisions (object_id TEXT NOT NULL, gate TEXT NOT NULL, digest TEXT NOT NULL, actor TEXT NOT NULL, decision TEXT NOT NULL, PRIMARY KEY(object_id, gate))')
        db.executemany('INSERT INTO actor_roles VALUES (?,?)', [
            ('scanner-1', 'scanner'), ('reviewer-1', 'reviewer'),
            ('reviewer-2', 'reviewer'), ('alice', 'owner')])


def decide(path, object_id, digest, actor, gate, decision):
    choices = {'scan': {'pass', 'fail', 'inconclusive'}, 'review': {'approve', 'reject'}}
    if gate not in choices or type(decision) is not str or decision not in choices[gate]:
        raise ValueError('Known gate and explicit decision required')
    required_role = 'scanner' if gate == 'scan' else 'reviewer'
    with sqlite3.connect(path, timeout=5) as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT owner,digest,body,status FROM objects WHERE id=?', (object_id,)).fetchone()
        if row is None:
            raise ValueError('Unknown object')
        owner, stored_digest, body, status = row
        allowed = db.execute('SELECT 1 FROM actor_roles WHERE actor=? AND role=?',
                             (actor, required_role)).fetchone()
        if not allowed or (gate == 'review' and actor == owner):
            raise PermissionError('Actor lacks this gate')
        if digest != stored_digest:
            raise ValueError('Decision does not match current bytes')
        if status == 'deleted':
            return 'ignored_deleted'
        if hashlib.sha256(body).hexdigest() != digest:
            raise ValueError('Stored bytes changed')
        existing = db.execute('SELECT digest,actor,decision FROM gate_decisions WHERE object_id=? AND gate=?',
                              (object_id, gate)).fetchone()
        if existing:
            if existing == (digest, actor, decision):
                return 'duplicate'
            raise ValueError('Conflicting gate decision')
        if gate == 'scan':
            if status != 'quarantined':
                raise ValueError('Scan gate is no longer open')
            target = {'pass': 'awaiting_review', 'fail': 'rejected',
                      'inconclusive': 'needs_investigation'}[decision]
        else:
            scan = db.execute("SELECT actor,decision FROM gate_decisions WHERE object_id=? AND gate='scan'",
                              (object_id,)).fetchone()
            if status != 'awaiting_review' or not scan or scan[1] != 'pass' or scan[0] == actor:
                raise ValueError('Distinct reviewer requires a passed scan and open review')
            target = 'available' if decision == 'approve' else 'rejected'
        db.execute('INSERT INTO gate_decisions VALUES (?,?,?,?,?)',
                   (object_id, gate, digest, actor, decision))
        db.execute('UPDATE objects SET status=? WHERE id=?', (target, object_id))
        return target


def must_reject(error_type, call):
    try:
        call()
    except error_type:
        return
    raise AssertionError('Expected rejection did not occur')


def run(path):
    initialize_review(path)
    first = upload(path, 'document-1', 'alice', b'Invented enrollment document')
    must_reject(PermissionError, lambda: read(path, 'document-1', 'alice'))
    must_reject(ValueError, lambda: decide(path, 'document-1', first, 'reviewer-1', 'review', 'approve'))
    must_reject(PermissionError, lambda: decide(path, 'document-1', first, 'alice', 'scan', 'pass'))
    must_reject(ValueError, lambda: decide(path, 'document-1', 'wrong-digest', 'scanner-1', 'scan', 'pass'))
    assert decide(path, 'document-1', first, 'scanner-1', 'scan', 'pass') == 'awaiting_review'
    assert decide(path, 'document-1', first, 'scanner-1', 'scan', 'pass') == 'duplicate'
    must_reject(ValueError, lambda: decide(path, 'document-1', first, 'scanner-1', 'scan', 'fail'))
    must_reject(PermissionError, lambda: read(path, 'document-1', 'alice'))
    must_reject(PermissionError, lambda: decide(path, 'document-1', first, 'alice', 'review', 'approve'))
    must_reject(PermissionError, lambda: decide(path, 'document-1', first, 'scanner-1', 'review', 'approve'))
    assert decide(path, 'document-1', first, 'reviewer-1', 'review', 'approve') == 'available'
    assert decide(path, 'document-1', first, 'reviewer-1', 'review', 'approve') == 'duplicate'
    must_reject(ValueError, lambda: decide(path, 'document-1', first, 'reviewer-2', 'review', 'reject'))
    assert read(path, 'document-1', 'alice') == b'Invented enrollment document'
    must_reject(PermissionError, lambda: read(path, 'document-1', 'reviewer-1'))

    failed = upload(path, 'document-2', 'alice', b'Invented rejected document')
    assert decide(path, 'document-2', failed, 'scanner-1', 'scan', 'fail') == 'rejected'
    must_reject(ValueError, lambda: decide(path, 'document-2', failed, 'reviewer-1', 'review', 'approve'))
    must_reject(PermissionError, lambda: read(path, 'document-2', 'alice'))

    unknown = upload(path, 'document-unknown', 'alice', b'Invented unscanned document')
    assert decide(path, 'document-unknown', unknown, 'scanner-1', 'scan', 'inconclusive') == 'needs_investigation'
    must_reject(ValueError, lambda: decide(path, 'document-unknown', unknown, 'reviewer-1', 'review', 'approve'))
    must_reject(PermissionError, lambda: read(path, 'document-unknown', 'alice'))

    late = upload(path, 'document-3', 'alice', b'Invented removed document')
    assert decide(path, 'document-3', late, 'scanner-1', 'scan', 'pass') == 'awaiting_review'
    delete(path, 'document-3', 'alice')
    assert decide(path, 'document-3', late, 'reviewer-1', 'review', 'approve') == 'ignored_deleted'
    must_reject(PermissionError, lambda: decide(path, 'document-3', late, 'alice', 'review', 'approve'))
    must_reject(ValueError, lambda: decide(path, 'document-3', 'wrong-digest', 'reviewer-1', 'review', 'approve'))
    must_reject(ValueError, lambda: upload(path, 'document-3', 'alice', b'Invented removed document'))

    race = upload(path, 'document-4', 'alice', b'Invented contested document')
    assert decide(path, 'document-4', race, 'scanner-1', 'scan', 'pass') == 'awaiting_review'
    barrier = threading.Barrier(2)
    def compete(actor, decision):
        barrier.wait()
        try:
            return decide(path, 'document-4', race, actor, 'review', decision)
        except ValueError:
            return 'conflict'
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda x: compete(*x), [('reviewer-1', 'approve'), ('reviewer-2', 'reject')]))
    assert results.count('conflict') == 1
    assert any(value in {'available', 'rejected'} for value in results)
    with sqlite3.connect(path) as db:
        final = db.execute('SELECT status FROM objects WHERE id=?', ('document-4',)).fetchone()[0]
        decisions = db.execute("SELECT COUNT(*) FROM gate_decisions WHERE object_id='document-4' AND gate='review'").fetchone()[0]
    assert final in {'available', 'rejected'} and decisions == 1

    revoked = upload(path, 'document-5', 'alice', b'Invented eligibility change')
    assert decide(path, 'document-5', revoked, 'scanner-1', 'scan', 'pass') == 'awaiting_review'
    with sqlite3.connect(path) as db:
        db.execute("DELETE FROM actor_roles WHERE actor='reviewer-2' AND role='reviewer'")
    must_reject(PermissionError, lambda: decide(path, 'document-5', revoked, 'reviewer-2', 'review', 'approve'))
    assert decide(path, 'document-5', revoked, 'reviewer-1', 'review', 'approve') == 'available'
    return {
        'two_gates_required': True, 'scanner_failure_not_overridden': True,
        'inconclusive_scan_not_approved': True,
        'late_review_cannot_resurrect': True, 'revoked_fixture_reviewer_denied': True,
        'one_race_winner': True,
        'race_outcome': final, 'race_results': sorted(results),
        'scope': 'Local SQLite transitions with trusted actor strings and synthetic decisions; no scanner, authentication, S3 or AWS workflow'}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-review-') as raw:
        folder = Path(raw)
        result = run(folder/'review.sqlite')
    result['temporary_resources_removed'] = not folder.exists()
    assert result['temporary_resources_removed']
    print(json.dumps(result, indent=2))
