"""Compare separate credit checks with one transactional local commitment record."""

import json
from pathlib import Path
import sqlite3
import tempfile
from threading import Barrier, Thread


REMAINING_CENTS = 8_000   # Invented USD 80.00; not the AWS account balance.
RESERVE_CENTS = 7_500     # Invented choice for this case, not advice or policy.
RUN_CENTS = 300           # Each invented experiment forecasts USD 3.00.


def naive_decision(estimate_cents: int) -> bool:
    return REMAINING_CENTS - estimate_cents >= RESERVE_CENTS


def create_register(path: Path):
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE commitments(run_id TEXT PRIMARY KEY, estimate_cents INTEGER NOT NULL)')


def commit(path: Path, run_id: str, estimate_cents: int) -> bool:
    """Serialize cooperating local writers before allocating projected headroom."""
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError('Fixture run ID must be a nonblank string')
    if type(estimate_cents) is not int or not 0 < estimate_cents <= 500:
        raise ValueError('Fixture estimate must be whole cents between 1 and 500')
    with sqlite3.connect(path, timeout=3, isolation_level=None) as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            if db.execute('SELECT 1 FROM commitments WHERE run_id = ?', (run_id,)).fetchone():
                db.rollback()
                return False
            committed = db.execute('SELECT COALESCE(SUM(estimate_cents),0) FROM commitments').fetchone()[0]
            if REMAINING_CENTS - committed - estimate_cents < RESERVE_CENTS:
                db.rollback()
                return False
            db.execute('INSERT INTO commitments VALUES (?,?)', (run_id, estimate_cents))
            db.commit()
            return True
        except BaseException:
            db.rollback()
            raise


def run(folder: Path) -> dict:
    assert naive_decision(RUN_CENTS)
    assert naive_decision(RUN_CENTS)
    assert REMAINING_CENTS - 2 * RUN_CENTS < RESERVE_CENTS

    register = folder / 'commitments.sqlite'
    create_register(register)
    barrier = Barrier(3)
    results = {}
    failures = []

    def worker(run_id: str):
        try:
            barrier.wait(timeout=3)
            results[run_id] = commit(register, run_id, RUN_CENTS)
        except BaseException as error:
            failures.append(error)

    threads = [Thread(target=worker, args=(run_id,)) for run_id in ('A', 'B')]
    for thread in threads:
        thread.start()
    barrier.wait(timeout=3)
    for thread in threads:
        thread.join(timeout=3)
        if thread.is_alive():
            raise RuntimeError('Commitment fixture thread did not finish')
    if failures:
        raise failures[0]
    with sqlite3.connect(register) as db:
        rows = db.execute('SELECT run_id,estimate_cents FROM commitments').fetchall()
    assert sorted(results.values()) == [False, True]
    assert len(rows) == 1 and rows[0][1] == RUN_CENTS
    assert REMAINING_CENTS - rows[0][1] - RESERVE_CENTS == 200
    return {'invented_remaining_usd': '80.00', 'reserve_usd': '75.00',
            'each_run_estimate_usd': '3.00', 'independent_checks_passed': 2,
            'combined_unreserved_headroom_usd': '-1.00',
            'transactional_commitments_accepted': 1,
            'transactional_commitments_rejected': 1,
            'remaining_uncommitted_headroom_usd': '2.00',
            'scope': 'one local SQLite register with cooperating threads; not AWS credits, billing, cross-host coordination or a spending cap'}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-credit-commitments-') as temp:
        folder = Path(temp)
        outcome = run(folder)
    outcome['temporary_resources_removed'] = not folder.exists()
    assert outcome['temporary_resources_removed']
    print(json.dumps(outcome, sort_keys=True))
