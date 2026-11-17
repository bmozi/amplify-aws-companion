"""SQLite hold transitions and bounded concurrent callers with fictional time and trusted payment events."""
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
import tempfile
import json
import sqlite3


def expire(db, now):
    """Caller owns the transaction; count only actual HELD -> EXPIRED transitions."""
    released = db.execute("UPDATE holds SET state='EXPIRED' WHERE state='HELD' AND expires<=?", (now,)).rowcount
    db.execute('UPDATE inventory SET free=free+? WHERE id=1', (released,))
    return released


def hold(db, key, actor, now, expires):
    if expires <= now:
        raise ValueError('Expiry must be later than acquisition')
    with db:
        db.execute('BEGIN IMMEDIATE')
        expire(db, now)
        existing = db.execute('SELECT actor,state FROM holds WHERE id=?', (key,)).fetchone()
        if existing:
            if existing[0] != actor:
                raise ValueError('Hold key belongs to another actor')
            return existing[1]
        if not db.execute('UPDATE inventory SET free=free-1 WHERE id=1 AND free>0').rowcount:
            return 'FULL'
        db.execute("INSERT INTO holds VALUES (?,?,?,'HELD')", (key, actor, expires))
        return 'HELD'


def capture_result(db, payment, key, now):
    """Fixture says capture already succeeded externally; no real money moves."""
    with db:
        db.execute('BEGIN IMMEDIATE')
        previous = db.execute('SELECT hold_id,outcome FROM payments WHERE id=?', (payment,)).fetchone()
        if previous:
            if previous[0] != key:
                raise ValueError('Payment ID reused for another hold')
            return previous[1]
        if not db.execute('SELECT 1 FROM holds WHERE id=?', (key,)).fetchone():
            raise ValueError('Unknown hold requires separate investigation')
        expire(db, now)
        confirmed = db.execute("UPDATE holds SET state='CONFIRMED' WHERE id=? AND state='HELD' AND expires>?", (key, now)).rowcount
        outcome = 'CONFIRMED' if confirmed else 'REFUND_PENDING'
        db.execute('INSERT INTO payments VALUES (?,?,?)', (payment,key,outcome))
        if not confirmed:
            db.execute('INSERT INTO compensation VALUES (?,?)', (payment,'PENDING'))
        return outcome


def initialize(db):
    db.executescript('''
      CREATE TABLE inventory(id INTEGER PRIMARY KEY,free INTEGER CHECK(free BETWEEN 0 AND 1));
      INSERT INTO inventory VALUES (1,1);
      CREATE TABLE holds(id TEXT PRIMARY KEY,actor TEXT NOT NULL,expires INTEGER NOT NULL,state TEXT NOT NULL);
      CREATE TABLE payments(id TEXT PRIMARY KEY,hold_id TEXT NOT NULL,outcome TEXT NOT NULL);
      CREATE TABLE compensation(payment_id TEXT PRIMARY KEY,state TEXT NOT NULL);
    ''')


def run():
    with closing(sqlite3.connect(':memory:')) as db:
        initialize(db)
        assert hold(db,'A','alice',0,10)=='HELD'
        assert hold(db,'B','bob',9,20)=='FULL'
        # At the exact boundary A is no longer confirmable; B can take the capacity.
        assert hold(db,'B','bob',10,20)=='HELD'
        assert db.execute('SELECT id,state FROM holds ORDER BY id').fetchall()==[('A','EXPIRED'),('B','HELD')]
        assert capture_result(db,'payment-A','A',11)=='REFUND_PENDING'
        assert capture_result(db,'payment-A','A',12)=='REFUND_PENDING'
        assert db.execute('SELECT * FROM compensation').fetchall()==[('payment-A','PENDING')]
        assert db.execute('SELECT free FROM inventory').fetchone()==(0,)
        try:
            capture_result(db,'payment-A','B',12)
        except ValueError:
            pass
        else:
            raise AssertionError('Conflicting payment replay accepted')
        assert capture_result(db,'payment-B','B',12)=='CONFIRMED'
        assert capture_result(db,'payment-B','B',13)=='CONFIRMED'
        # A second distinct successful capture for B must not create another booking.
        assert capture_result(db,'payment-B-extra','B',14)=='REFUND_PENDING'
        with db:
            assert expire(db,100)==0
            assert expire(db,101)==0
        assert db.execute('SELECT free FROM inventory').fetchone()==(0,)
        assert db.execute("SELECT id FROM holds WHERE state='CONFIRMED'").fetchall()==[('B',)]
        pending=db.execute('SELECT payment_id,state FROM compensation ORDER BY payment_id').fetchall()
        assert pending==[('payment-A','PENDING'),('payment-B-extra','PENDING')]
        assert hold(db,'A','alice',102,110)=='EXPIRED', 'old hold identity must not silently resurrect'
        return {'confirmed_hold':'B','available_capacity':0,'compensation':pending,
                'scope':'fictional timestamps and capture events; no payment provider, refund or live concurrency'}



def cancel(db, key, now):
    """Fixture policy: cancellation may release HELD, never CONFIRMED, capacity."""
    with db:
        db.execute('BEGIN IMMEDIATE')
        expire(db, now)
        row = db.execute('SELECT state FROM holds WHERE id=?', (key,)).fetchone()
        if row is None:
            raise ValueError('Unknown hold')
        changed = db.execute("UPDATE holds SET state='CANCELLED' WHERE id=? AND state='HELD'", (key,)).rowcount
        if changed:
            db.execute('UPDATE inventory SET free=free+1 WHERE id=1')
            return 'CANCELLED'
        return row[0]


def race_case(path, order):
    with closing(sqlite3.connect(path)) as db:
        initialize(db)
        assert hold(db,'R','reader',0,10)=='HELD'
    gate = Barrier(2, timeout=5)

    def act(kind, overlap=False):
        with closing(sqlite3.connect(path, timeout=5)) as db:
            if overlap:
                gate.wait()
            if kind=='cancel':
                return cancel(db,'R',4)
            return capture_result(db,'capture-R','R',4)

    if order=='overlap':
        with ThreadPoolExecutor(max_workers=2) as pool:
            a=pool.submit(act,'cancel',True)
            b=pool.submit(act,'capture',True)
            results=(a.result(timeout=10),b.result(timeout=10))
    elif order=='duplicate-capture':
        with ThreadPoolExecutor(max_workers=2) as pool:
            a=pool.submit(act,'capture',True)
            b=pool.submit(act,'capture',True)
            results=(a.result(timeout=10),b.result(timeout=10))
        assert results==('CONFIRMED','CONFIRMED')
    elif order=='cancel-first':
        results=(act('cancel'),act('capture'))
        assert results==('CANCELLED','REFUND_PENDING')
    else:
        captured=act('capture')
        results=(act('cancel'),captured)
        assert results==('CONFIRMED','CONFIRMED')
    assert results in [('CANCELLED','REFUND_PENDING'),('CONFIRMED','CONFIRMED')]
    with closing(sqlite3.connect(path)) as db:
        state=db.execute('SELECT state FROM holds').fetchone()[0]
        free=db.execute('SELECT free FROM inventory').fetchone()[0]
        payments=db.execute('SELECT id,outcome FROM payments').fetchall()
        compensation=db.execute('SELECT payment_id,state FROM compensation').fetchall()
        if state=='CONFIRMED':
            assert free==0 and compensation==[]
            assert payments==[('capture-R','CONFIRMED')]
        else:
            assert state=='CANCELLED' and free==1
            assert payments==[('capture-R','REFUND_PENDING')]
            assert compensation==[('capture-R','PENDING')]
        assert cancel(db,'R',5)==state
        assert db.execute('SELECT free FROM inventory').fetchone()[0]==free
    return {'schedule':order,'caller_results':results,'state':state,'free':free}


def concurrent_cases():
    with tempfile.TemporaryDirectory(prefix='amplify-hold-race-') as folder:
        root=Path(folder)
        cases=[race_case(root/(name+'.sqlite'),name) for name in
               ('cancel-first','capture-first','overlap','duplicate-capture')]
    assert not root.exists()
    return cases


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    print(json.dumps({'sequential':run(),'local_contention':concurrent_cases()},indent=2))
