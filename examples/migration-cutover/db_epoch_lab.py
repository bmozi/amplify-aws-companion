"""A database-scoped cutover gate, using separate SQLite connections.

All stores and the route live in one temporary database. This is deliberately
not a distributed transaction, CDC implementation, DNS switch, or AWS test.
"""

from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import threading


SCHEMA = """CREATE TABLE route (id INTEGER PRIMARY KEY CHECK(id=1), selected TEXT NOT NULL
    CHECK(selected IN ('old','new')), epoch INTEGER NOT NULL);
CREATE TABLE orders (store TEXT NOT NULL CHECK(store IN ('old','new')),
    order_id TEXT NOT NULL, amount_cents INTEGER NOT NULL,
    PRIMARY KEY(store,order_id));
INSERT INTO route VALUES (1,'old',0);
INSERT INTO orders VALUES ('old','a',250),('new','a',250);"""


class StaleRoute(ValueError):
    pass


class DivergentStores(ValueError):
    pass


def connect(path: Path):
    return sqlite3.connect(path, timeout=5, isolation_level=None)


def setup(path: Path):
    with closing(connect(path)) as db:
        db.executescript(SCHEMA)


def route(db):
    return db.execute('SELECT selected,epoch FROM route WHERE id=1').fetchone()


def orders(db, store):
    return db.execute('SELECT order_id,amount_cents FROM orders WHERE store=? ORDER BY order_id',
                      (store,)).fetchall()


def write(path: Path, observed_epoch: int, order_id: str, amount_cents: int):
    """A cooperative writer rechecks its earlier route observation after lock acquisition."""
    with closing(connect(path)) as db:
        try:
            db.execute('BEGIN IMMEDIATE')
            selected, current_epoch = route(db)
            if observed_epoch != current_epoch:
                raise StaleRoute(f'route changed from epoch {observed_epoch} to {current_epoch}')
            db.execute('INSERT INTO orders VALUES (?,?,?)',
                       (selected, order_id, amount_cents))
            db.commit()
            return selected
        except Exception:
            db.rollback()
            raise


def switch(path: Path, checked: threading.Event | None = None,
           release: threading.Event | None = None):
    with closing(connect(path)) as db:
        try:
            db.execute('BEGIN IMMEDIATE')
            if orders(db, 'old') != orders(db, 'new'):
                raise DivergentStores('old and new differ before selection')
            if checked is not None:
                checked.set()
            if release is not None and not release.wait(timeout=5):
                raise TimeoutError('selector held too long in this fixture')
            selected, epoch = route(db)
            if selected != 'old':
                raise StaleRoute('route already changed')
            db.execute("UPDATE route SET selected='new',epoch=? WHERE id=1", (epoch + 1,))
            db.commit()
            return epoch + 1
        except Exception:
            db.rollback()
            raise


def unsafe_switch_after_check(path: Path, after_check):
    """Negative control: a gap between a read-only comparison and the route update."""
    with closing(connect(path)) as db:
        if orders(db, 'old') != orders(db, 'new'):
            raise DivergentStores('initial stores differ')
    after_check()
    with closing(connect(path)) as db:
        db.execute("UPDATE route SET selected='new',epoch=epoch+1 WHERE id=1")


def run(folder: Path):
    unsafe = folder / 'unsafe.sqlite'
    setup(unsafe)
    unsafe_switch_after_check(unsafe, lambda: write(unsafe, 0, 'late', 375))
    with closing(connect(unsafe)) as db:
        unsafe_result = {'route': route(db), 'old': orders(db, 'old'), 'new': orders(db, 'new')}

    gated = folder / 'gated.sqlite'
    setup(gated)
    checked, release = threading.Event(), threading.Event()
    outcome = {}

    def selector():
        try:
            outcome['new_epoch'] = switch(gated, checked, release)
        except Exception as exc:
            outcome['selector_error'] = repr(exc)

    def delayed_writer():
        try:
            outcome['stale_writer_store'] = write(gated, 0, 'late', 375)
        except StaleRoute:
            outcome['stale_writer_rejected'] = True
        except Exception as exc:
            outcome['writer_error'] = repr(exc)

    selecting = threading.Thread(target=selector)
    selecting.start()
    if not checked.wait(timeout=5):
        release.set()
        selecting.join()
        raise TimeoutError('selector did not reach the checked point')
    writing = threading.Thread(target=delayed_writer)
    writing.start()
    release.set()
    selecting.join(timeout=6)
    writing.join(timeout=6)
    if selecting.is_alive() or writing.is_alive() or 'selector_error' in outcome or 'writer_error' in outcome:
        raise RuntimeError(f'toy concurrency run did not complete: {outcome}')
    outcome['fresh_writer_store'] = write(gated, 1, 'late', 375)
    with closing(connect(gated)) as db:
        gated_result = {'route': route(db), 'old': orders(db, 'old'), 'new': orders(db, 'new')}
    assert unsafe_result['route'] == ('new', 1)
    assert ('late', 375) in unsafe_result['old'] and ('late', 375) not in unsafe_result['new']
    assert outcome['stale_writer_rejected'] and outcome['fresh_writer_store'] == 'new'
    assert gated_result['route'] == ('new', 1)
    assert ('late', 375) not in gated_result['old'] and ('late', 375) in gated_result['new']
    return {'unsafe_check_switch_gap': unsafe_result,
            'transactional_gate': gated_result, 'writer_outcome': outcome,
            'scope': 'one SQLite database, separate connections, cooperative writers; no independent CDC, external effects, DNS, AWS or distributed writer fence'}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-db-epoch-') as temp:
        folder = Path(temp)
        result = run(folder)
    result['temporary_resources_removed'] = not folder.exists()
    print(json.dumps(result, sort_keys=True))
