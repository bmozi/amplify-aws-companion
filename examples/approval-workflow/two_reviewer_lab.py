"""Local two-person admission policy. Trusted identities/clock; no external effect."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from threading import Barrier
import tempfile


def digest(action):
    return sha256(json.dumps(action,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def review(path,key,actor,seen,now,expires):
    with closing(sqlite3.connect(path,timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        requester,revision,expected,state=db.execute('SELECT requester,revision,digest,state FROM actions WHERE id=?',(key,)).fetchone()
        eligible=db.execute('SELECT active FROM eligibility WHERE actor=?',(actor,)).fetchone()
        if actor==requester or eligible!=(1,): return 'denied'
        if state!='pending' or seen!=expected or now>=expires: return 'rejected'
        old=db.execute('SELECT expires FROM reviews WHERE action=? AND revision=? AND actor=?',(key,revision,actor)).fetchone()
        if old: return 'duplicate' if old==(expires,) else 'conflict'
        db.execute('INSERT INTO reviews VALUES (?,?,?,?,?)',(key,revision,actor,seen,expires))
        return 'reviewed'


def admit(path,key,now):
    with closing(sqlite3.connect(path,timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        requester,revision,expected,state=db.execute('SELECT requester,revision,digest,state FROM actions WHERE id=?',(key,)).fetchone()
        if state=='admitted': return 'duplicate'
        if state!='pending': return 'rejected'
        count=db.execute('''SELECT count(*) FROM reviews r JOIN eligibility e ON e.actor=r.actor
            WHERE r.action=? AND r.revision=? AND r.digest=? AND r.actor!=?
            AND r.expires>? AND e.active=1''',(key,revision,expected,requester,now)).fetchone()[0]
        if count<2: return 'insufficient'
        db.execute('INSERT INTO admissions VALUES (?,?,?)',(key,revision,expected))
        db.execute("UPDATE actions SET state='admitted' WHERE id=?",(key,))
        return 'admitted'


def cancel(path,key,actor):
    with closing(sqlite3.connect(path,timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        requester,state=db.execute('SELECT requester,state FROM actions WHERE id=?',(key,)).fetchone()
        if actor!=requester:return 'denied'
        if state=='admitted':return 'already_admitted'
        if state=='cancelled':return 'duplicate'
        db.execute("UPDATE actions SET state='cancelled' WHERE id=?",(key,))
        return 'cancelled'


def run(path):
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript('''CREATE TABLE actions(id TEXT PRIMARY KEY,requester TEXT,revision INTEGER,digest TEXT,state TEXT);
            CREATE TABLE eligibility(actor TEXT PRIMARY KEY,active INTEGER);
            CREATE TABLE reviews(action TEXT,revision INTEGER,actor TEXT,digest TEXT,expires INTEGER,
                PRIMARY KEY(action,revision,actor));
            CREATE TABLE admissions(action TEXT PRIMARY KEY,revision INTEGER,digest TEXT);
            INSERT INTO eligibility VALUES ('requester',1),('A',1),('B',1),('C',1);''')

    def create(key):
        action={'id':key,'revision':1,'artifact':'fixture-digest','destination':'training','effective_date':'fictional-day-2'}
        with closing(sqlite3.connect(path)) as db, db:
            db.execute('INSERT INTO actions VALUES (?,?,?,?,?)',(key,'requester',1,digest(action),'pending'))
        return action

    def scalar(sql,params=()):
        with closing(sqlite3.connect(path)) as db: return db.execute(sql,params).fetchone()[0]

    a=create('changed')
    assert review(path,'changed','requester',digest(a),10,100)=='denied'
    assert review(path,'changed','unknown',digest(a),10,100)=='denied'
    assert review(path,'changed','A',digest(a),10,100)=='reviewed'
    assert review(path,'changed','A',digest(a),11,100)=='duplicate'
    assert review(path,'changed','A',digest(a),11,200)=='conflict'
    assert admit(path,'changed',12)=='insufficient'
    # Negative control: counting successful HTTP-like attempts would count A twice.
    assert scalar('SELECT count(*) FROM reviews WHERE action=?',('changed',))==1
    changed={**a,'revision':2,'destination':'public'}
    # Operator fixture prepares a new revision, preserving prior review history.
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('UPDATE actions SET revision=2,digest=? WHERE id=?',(digest(changed),'changed'))
    assert review(path,'changed','B',digest(a),13,100)=='rejected'
    assert review(path,'changed','B',digest(changed),13,100)=='reviewed'
    assert admit(path,'changed',14)=='insufficient'  # two rows, different revisions
    assert scalar('SELECT count(*) FROM reviews WHERE action=?',('changed',))==2
    print('Requester excluded; duplicate approval counts once; two revisions do not combine.')

    a=create('revoked')
    for actor in ('A','B'): assert review(path,'revoked',actor,digest(a),10,100)=='reviewed'
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE'); db.execute("UPDATE eligibility SET active=0 WHERE actor='B'")
    assert admit(path,'revoked',20)=='insufficient'
    assert scalar("SELECT count(*) FROM reviews WHERE action='revoked'")==2
    assert review(path,'revoked','C',digest(a),21,100)=='reviewed'
    barrier=Barrier(2)
    def concurrent_admit():
        barrier.wait(timeout=5)
        return admit(path,'revoked',22)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(concurrent_admit) for _ in range(2)]
        results=sorted(f.result(timeout=10) for f in futures)
    assert results==['admitted','duplicate']
    assert scalar('SELECT count(*) FROM admissions')==1
    assert cancel(path,'revoked','requester')=='already_admitted'
    print('Revocation blocks admission; actual replacement review permits one concurrent admission.')

    a=create('expiry')
    for actor in ('A','C'): assert review(path,'expiry',actor,digest(a),90,100)=='reviewed'
    assert admit(path,'expiry',100)=='insufficient'
    assert cancel(path,'expiry','A')=='denied'
    assert cancel(path,'expiry','requester')=='cancelled'
    assert cancel(path,'expiry','requester')=='duplicate'
    assert admit(path,'expiry',99)=='rejected'  # cancellation wins regardless of supplied fixture time
    a=create('cancelled')
    for actor in ('A','C'): assert review(path,'cancelled',actor,digest(a),10,100)=='reviewed'
    assert cancel(path,'cancelled','requester')=='cancelled'
    assert admit(path,'cancelled',20)=='rejected'
    assert scalar('SELECT count(*) FROM admissions')==1
    print('Exact expiry and cancellation prevent admission; admitted state is not a publication receipt.')


if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='two-reviewer-') as directory:
        run(Path(directory)/'policy.db')
    print('PASS: temporary database removed; no real identity, external eligibility, publication or AWS.')
