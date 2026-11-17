"""Show a local committed outbox obligation across sequential process exit."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile


def child(mode, path):
    from outbox_lab import book, database, process, reconcile, relay
    db = database(path)
    try:
        if mode == 'write':
            book(db, 'restart', 1200)
            print(json.dumps({'stage': 'before_writer_exit', **reconcile(db)}))
        elif mode == 'recover':
            pending = db.execute('SELECT count(*) FROM outbox WHERE published=0').fetchone()[0]
            deliveries = []
            if pending != 1 or not relay(db, deliveries) or len(deliveries) != 1:
                raise RuntimeError('Expected exactly one pending local obligation')
            outcome = process(db, deliveries[0])
            print(json.dumps({'stage': 'after_second_process', 'pending_before_send': pending,
                              'delivery_outcome': outcome, **reconcile(db)}))
        else:
            raise ValueError('Unknown child stage')
    finally:
        db.close()


def main():
    if len(sys.argv) == 3 and sys.argv[1] in ('write', 'recover'):
        child(sys.argv[1], sys.argv[2])
        return
    if len(sys.argv) != 1:
        raise SystemExit('Run without arguments')
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / 'booking.sqlite')
        observations = []
        for mode in ('write', 'recover'):
            result = subprocess.run([sys.executable, __file__, mode, path],
                                    check=True, capture_output=True, text=True)
            observations.append(json.loads(result.stdout))
        print(json.dumps({'observations': observations,
                          'scope': 'temporary SQLite file, two sequential local processes; no AWS'}, indent=2))


if __name__ == '__main__':
    main()
