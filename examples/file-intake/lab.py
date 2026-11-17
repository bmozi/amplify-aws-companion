"""Local file-intake state machine. Verdicts and identities are synthetic; no malware scanner or AWS calls."""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile


def initialize(path):
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE objects (id TEXT PRIMARY KEY, owner TEXT NOT NULL, digest TEXT NOT NULL, body BLOB, status TEXT NOT NULL)')


def upload(path, object_id, owner, body):
    if not owner or not object_id or not isinstance(body, bytes) or not 0 < len(body) <= 1024:
        raise ValueError('Synthetic upload requires identity, ID and 1-1024 bytes')
    digest=hashlib.sha256(body).hexdigest()
    with sqlite3.connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        existing=db.execute('SELECT owner,digest,status FROM objects WHERE id=?',(object_id,)).fetchone()
        if existing:
            if existing != (owner,digest,'quarantined'):raise ValueError('Immutable ID already used')
            return digest
        db.execute('INSERT INTO objects VALUES (?,?,?,?,?)',(object_id,owner,digest,body,'quarantined'))
    return digest


def verdict(path, object_id, expected_digest, clean):
    if type(clean) is not bool:raise ValueError('Explicit synthetic boolean verdict required')
    with sqlite3.connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT digest,body,status FROM objects WHERE id=?',(object_id,)).fetchone()
        if not row:raise ValueError('Unknown object')
        digest,body,status=row
        if digest != expected_digest:raise ValueError('Verdict targets different bytes')
        if status=='deleted':return 'ignored_deleted'
        target='available' if clean else 'rejected'
        if status==target:return 'duplicate'
        if status!='quarantined':raise ValueError('Conflicting terminal verdict')
        if hashlib.sha256(body).hexdigest()!=digest:raise ValueError('Stored bytes changed')
        db.execute('UPDATE objects SET status=? WHERE id=?',(target,object_id))
        return target


def read(path, object_id, actor):
    with sqlite3.connect(path) as db:
        row=db.execute('SELECT owner,body,status FROM objects WHERE id=?',(object_id,)).fetchone()
        if not row or row[0]!=actor or row[2]!='available':raise PermissionError('Not available to actor')
        return row[1]


def delete(path, object_id, actor):
    with sqlite3.connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT owner FROM objects WHERE id=?',(object_id,)).fetchone()
        if not row or row[0]!=actor:raise PermissionError('Not available to actor')
        db.execute("UPDATE objects SET status='deleted',body=NULL WHERE id=?",(object_id,))


def must_reject(exception, operation):
    try:operation()
    except exception:return
    raise AssertionError('Expected rejection did not occur')


def run(path):
    initialize(path)
    digest=upload(path,'immutable-1','alice',b'Synthetic repair photo placeholder')
    assert upload(path,'immutable-1','alice',b'Synthetic repair photo placeholder')==digest
    must_reject(PermissionError,lambda:read(path,'immutable-1','alice'))
    must_reject(ValueError,lambda:verdict(path,'immutable-1','wrong-digest',True))
    must_reject(ValueError,lambda:upload(path,'immutable-1','alice',b'Changed bytes'))
    assert verdict(path,'immutable-1',digest,True)=='available'
    assert verdict(path,'immutable-1',digest,True)=='duplicate'
    assert read(path,'immutable-1','alice')==b'Synthetic repair photo placeholder'
    must_reject(PermissionError,lambda:read(path,'immutable-1','bob'))
    must_reject(PermissionError,lambda:delete(path,'immutable-1','bob'))
    must_reject(ValueError,lambda:verdict(path,'immutable-1',digest,False))
    rejected=upload(path,'immutable-2','alice',b'Synthetic rejected file')
    assert verdict(path,'immutable-2',rejected,False)=='rejected'
    must_reject(PermissionError,lambda:read(path,'immutable-2','alice'))
    delete(path,'immutable-1','alice');delete(path,'immutable-1','alice')
    assert verdict(path,'immutable-1',digest,True)=='ignored_deleted'
    must_reject(PermissionError,lambda:read(path,'immutable-1','alice'))
    must_reject(ValueError,lambda:upload(path,'immutable-1','alice',b'Synthetic repair photo placeholder'))
    must_reject(ValueError,lambda:upload(path,'oversize','alice',b'x'*1025))
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT body,status FROM objects WHERE id=?',('immutable-1',)).fetchone()==(None,'deleted')
    return {'quarantine_denial':True,'digest_binding':True,'overwrite_rejected':True,
            'duplicate_verdict_safe':True,'other_owner_denied':True,'rejected_file_unreadable':True,
            'late_verdict_cannot_resurrect':True,'deleted_payload_removed_from_record':True,
            'scope':'Actual SQLite transitions and synthetic actor checks; no malware scan, secure disk erasure, concurrent cloud events or AWS policy verification'}


if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-intake-') as tmp:
        folder=Path(tmp);report=run(folder/'intake.sqlite')
    report['temporary_resources_removed']=not folder.exists()
    assert report['temporary_resources_removed']
    print(json.dumps(report,indent=2))
