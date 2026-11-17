"""Durable local approval binding and atomic fixture effect. No real users or external actions."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from threading import Barrier
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile


def digest(action):return hashlib.sha256(json.dumps(action,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def initialize(path):
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript('''CREATE TABLE requests(id TEXT PRIMARY KEY, action TEXT, digest TEXT, reviewer TEXT, expires INTEGER, status TEXT);
        CREATE TABLE effects(request_id TEXT PRIMARY KEY, action TEXT);''')


def create(path, key, action, reviewer, expires):
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('INSERT INTO requests VALUES (?,?,?,?,?,?)',(key,json.dumps(action,sort_keys=True),digest(action),reviewer,expires,'pending'))


def approve(path,key,actor,reviewed_digest,now):
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT digest,reviewer,expires,status FROM requests WHERE id=?',(key,)).fetchone()
        if not row:raise ValueError('Unknown request')
        expected,reviewer,expires,status=row
        if actor!=reviewer:raise PermissionError('Reviewer mismatch')
        if reviewed_digest!=expected:raise ValueError('Reviewed action differs')
        if now>=expires:raise ValueError('Approval expired')
        if status in ['approved','executed']:return 'duplicate'
        if status!='pending':raise ValueError('Request no longer pending')
        db.execute("UPDATE requests SET status='approved' WHERE id=?",(key,))
        return 'approved'


def cancel(path,key,actor):
    # Fixture policy: the designated reviewer can withdraw a pending/approved request.
    # Cancellation remains allowed after expiry; it cannot undo a committed effect.
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT reviewer,status FROM requests WHERE id=?',(key,)).fetchone()
        if not row:raise ValueError('Unknown request')
        reviewer,status=row
        if actor!=reviewer:raise PermissionError('Reviewer mismatch')
        if status=='executed':return 'too_late'
        if status=='cancelled':return 'duplicate'
        if status not in ['pending','approved']:raise ValueError('Request cannot be cancelled')
        db.execute("UPDATE requests SET status='cancelled' WHERE id=?",(key,))
        return 'cancelled'


def execute(path,key,action,now):
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        stored,expected,expires,status=db.execute('SELECT action,digest,expires,status FROM requests WHERE id=?',(key,)).fetchone()
        if digest(action)!=expected:raise ValueError('Action changed after review')
        if status=='executed':return 'duplicate'
        if now>=expires or status!='approved':raise ValueError('No current approval')
        # Fixture effect and execution receipt share one database transaction.
        # This does not make an external email/payment/cloud API transactionally atomic.
        db.execute('INSERT INTO effects VALUES (?,?)',(key,stored))
        db.execute("UPDATE requests SET status='executed' WHERE id=?",(key,))
        return 'executed'


def rejects(kind,call):
    try:call()
    except kind:return
    raise AssertionError('Expected rejection missing')


def run(path):
    initialize(path)
    action={'operation':'publish_fixture','artifact':'sha256:example','target':'teaching-only'}
    create(path,'r1',action,'reviewer-a',100)
    rejects(ValueError,lambda:execute(path,'r1',action,10))
    rejects(PermissionError,lambda:approve(path,'r1','reviewer-b',digest(action),10))
    rejects(ValueError,lambda:approve(path,'r1','reviewer-a','different',10))
    assert approve(path,'r1','reviewer-a',digest(action),10)=='approved'
    assert approve(path,'r1','reviewer-a',digest(action),11)=='duplicate'
    changed={**action,'target':'another-target'}
    rejects(ValueError,lambda:execute(path,'r1',changed,12))
    assert execute(path,'r1',action,12)=='executed'
    assert execute(path,'r1',action,150)=='duplicate'  # receipt lookup, not a new action
    create(path,'r2',action,'reviewer-a',100)
    rejects(ValueError,lambda:approve(path,'r2','reviewer-a',digest(action),100))
    create(path,'r3',action,'reviewer-a',100)
    assert approve(path,'r3','reviewer-a',digest(action),90)=='approved'
    rejects(ValueError,lambda:execute(path,'r3',action,100))
    # Controlled order 1: cancellation beats the delayed reviewer's approval.
    create(path,'r4',action,'reviewer-a',100)
    rejects(PermissionError,lambda:cancel(path,'r4','reviewer-b'))
    assert cancel(path,'r4','reviewer-a')=='cancelled'
    assert cancel(path,'r4','reviewer-a')=='duplicate'
    rejects(ValueError,lambda:approve(path,'r4','reviewer-a',digest(action),20))
    rejects(ValueError,lambda:execute(path,'r4',action,20))
    # Controlled order 2: approved work is cancelled before execution starts.
    create(path,'r5',action,'reviewer-a',100)
    assert approve(path,'r5','reviewer-a',digest(action),10)=='approved'
    assert cancel(path,'r5','reviewer-a')=='cancelled'
    rejects(ValueError,lambda:execute(path,'r5',action,20))
    rejects(ValueError,lambda:approve(path,'r5','reviewer-a',digest(action),20))
    # Controlled order 3: committed execution cannot be reversed by cancellation.
    assert cancel(path,'r1','reviewer-a')=='too_late'
    assert execute(path,'r1',action,150)=='duplicate'
    # An expired approved request can still be marked cancelled under this policy.
    assert cancel(path,'r3','reviewer-a')=='cancelled'
    rejects(ValueError,lambda:cancel(path,'missing','reviewer-a'))
    with closing(sqlite3.connect(path)) as db, db:
        assert db.execute('SELECT request_id FROM effects').fetchall()==[('r1',)]
        statuses=dict(db.execute('SELECT id,status FROM requests'))
        assert statuses=={'r1':'executed','r2':'pending','r3':'cancelled',
                          'r4':'cancelled','r5':'cancelled'}
    return {'unapproved_execution_denied':True,'wrong_reviewer_denied':True,'reviewed_digest_required':True,
            'duplicate_approval_safe':True,'changed_target_denied':True,'one_fixture_effect':True,
            'approval_and_execution_expiry_checked':True,'late_approval_cannot_reactivate':True,
            'cancel_before_execution_blocks_effect':True,'cancel_after_execution_reports_too_late':True,'scope':'SQLite fixture actions with trusted actor/time arguments; no authentication, callback token, cloud workflow or external exactly-once guarantee'}

def overlap(left, right):
    gate=Barrier(2,timeout=5)
    def attempt(operation):
        gate.wait()
        try:return operation()
        except ValueError as error:
            # Only the intended state rejections are acceptable race outcomes.
            if str(error) not in ['Request no longer pending','No current approval']:raise
            return 'rejected'
    with ThreadPoolExecutor(max_workers=2) as workers:
        a=workers.submit(attempt,left)
        b=workers.submit(attempt,right)
        return a.result(timeout=10),b.result(timeout=10)


def concurrent_cases(path):
    initialize(path)
    action={'operation':'publish_fixture','artifact':'sha256:example','target':'teaching-only'}
    create(path,'review_race',action,'reviewer-a',100)
    review_result=overlap(
        lambda:approve(path,'review_race','reviewer-a',digest(action),10),
        lambda:cancel(path,'review_race','reviewer-a'))
    assert review_result in [('approved','cancelled'),('rejected','cancelled')]
    create(path,'execute_race',action,'reviewer-a',100)
    assert approve(path,'execute_race','reviewer-a',digest(action),10)=='approved'
    execution_result=overlap(
        lambda:execute(path,'execute_race',action,20),
        lambda:cancel(path,'execute_race','reviewer-a'))
    assert execution_result in [('executed','too_late'),('rejected','cancelled')]
    create(path,'duplicate_race',action,'reviewer-a',100)
    assert approve(path,'duplicate_race','reviewer-a',digest(action),10)=='approved'
    duplicate_result=overlap(
        lambda:execute(path,'duplicate_race',action,20),
        lambda:execute(path,'duplicate_race',action,20))
    assert sorted(duplicate_result)==['duplicate','executed']
    with closing(sqlite3.connect(path)) as db:
        statuses=dict(db.execute('SELECT id,status FROM requests'))
        effects=dict(db.execute('SELECT request_id,action FROM effects'))
        assert statuses['review_race']=='cancelled' and 'review_race' not in effects
        # Check state and effect together, not just the returned status strings.
        executed=execution_result[0]=='executed'
        assert statuses['execute_race']==('executed' if executed else 'cancelled')
        expected={'duplicate_race':json.dumps(action,sort_keys=True)}
        if executed:expected['execute_race']=json.dumps(action,sort_keys=True)
        assert effects==expected
        assert statuses['duplicate_race']=='executed'
    return {'approval_vs_cancel':review_result,'execution_vs_cancel':execution_result,
            'duplicate_execution':duplicate_result,
            'scope':'Barrier-released local threads with independent SQLite connections; acquisition order unspecified'}


if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-approval-') as tmp:
        folder=Path(tmp);report=run(folder/'approval.sqlite')
        report['overlapping_callers']=concurrent_cases(folder/'contention.sqlite')
    report['temporary_resources_removed']=not folder.exists()
    assert report['temporary_resources_removed']
    print(json.dumps(report,indent=2))
