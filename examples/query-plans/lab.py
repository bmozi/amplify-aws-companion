"""Compare real SQLite query plans and VM work, preserving exact result membership."""
import sqlite3
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

QUERY = '''SELECT id,created FROM appointments
WHERE tenant=? AND status=? ORDER BY created,id LIMIT 20'''
PARAMS = ('tenant-07', 'open')


def observe(db, query, params):
    plan = [row[3] for row in db.execute('EXPLAIN QUERY PLAN ' + query, params)]
    steps = 0

    def progress():
        nonlocal steps
        steps += 1
        return 0

    # One callback per SQLite VM instruction. This instruments work, not latency.
    db.set_progress_handler(progress, 1)
    try:
        rows = db.execute(query, params).fetchall()
    finally:
        db.set_progress_handler(None, 0)
    return rows, steps, plan


def run():
    if sys.flags.optimize:
        raise SystemExit('Run without -O: assertions verify the results')
    fixture = [(i, f'tenant-{i % 100:02}', 'open' if i % 3 else 'closed',
                (i * 37) % 10007) for i in range(20000)]
    expected = sorted([(i, created) for i, tenant, status, created in fixture
                       if tenant == PARAMS[0] and status == PARAMS[1]], key=lambda r: (r[1],r[0]))[:20]
    assert len(expected) == 20
    with TemporaryDirectory(prefix='query-plans-') as temporary:
        path = Path(temporary) / 'appointments.sqlite'
        db = sqlite3.connect(path, cached_statements=0)
        try:
            db.execute('CREATE TABLE appointments(id INTEGER PRIMARY KEY,tenant TEXT,status TEXT,created INTEGER)')
            db.executemany('INSERT INTO appointments VALUES(?,?,?,?)', fixture)
            db.commit()
            baseline = observe(db, QUERY, PARAMS)
            assert baseline[0] == expected
            db.execute('CREATE INDEX by_tenant_status_time ON appointments(tenant,status,created,id)')
            indexed = observe(db, QUERY, PARAMS)
            assert indexed[0] == expected == baseline[0]
            assert indexed[1] < baseline[1], 'Investigate engine/plan change: this fixture should use less VM work'
            print('SQLite version:', sqlite3.sqlite_version)
            for label, result in [('baseline',baseline),('indexed',indexed)]:
                print(label, 'rows=',len(result[0]),'VM instructions=',result[1])
                for detail in result[2]:
                    print('  plan:',detail)

            # An index is not an access-control boundary: omit tenant intentionally.
            unsafe_query = QUERY.replace('tenant=? AND ', '')
            unsafe = observe(db,unsafe_query,(PARAMS[1],))
            assert unsafe[0] != expected
            by_id = {row[0]:row for row in fixture}
            assert any(by_id[row[0]][1] != PARAMS[0] for row in unsafe[0])
            print('PASS: omitted tenant predicate exposes other tenants despite the index')

            # A different query shape can need a different index; report, do not force a plan.
            changed_query = 'SELECT id,created FROM appointments WHERE status=? ORDER BY created,id LIMIT 20'
            changed_expected = sorted([(i,t) for i,tenant,status,t in fixture if status=='closed'], key=lambda r:(r[1],r[0]))[:20]
            changed = observe(db,changed_query,('closed',))
            assert changed[0] == changed_expected
            print('Changed access pattern VM instructions=',changed[1])
            for detail in changed[2]:
                print('  plan:',detail)
            print('PASS: exact ordered results checked independently from SQL for both safe queries')
        finally:
            db.close()
    assert not path.exists()
    print('PASS: temporary database removed; no latency, AWS cost or production-scale claim')


if __name__ == '__main__':
    run()
