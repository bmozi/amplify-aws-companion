"""Cloud-free engineering drills. SQLite and synthetic events do not emulate AWS services."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import time


def initialize(path):
    with sqlite3.connect(path) as db:
        db.executescript('''
        CREATE TABLE seats (course TEXT PRIMARY KEY, remaining INTEGER NOT NULL CHECK(remaining >= 0));
        CREATE TABLE reservations (actor TEXT PRIMARY KEY, course TEXT NOT NULL);
        INSERT INTO seats VALUES ('cloud-class', 1);
        ''')


def reserve(path, actor):
    with sqlite3.connect(path, timeout=10) as db:
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT 1 FROM reservations WHERE actor=?', (actor,)).fetchone():
            return 'replay'
        updated = db.execute('UPDATE seats SET remaining=remaining-1 WHERE course=? AND remaining>0', ('cloud-class',))
        if updated.rowcount == 0:
            return 'full'
        db.execute('INSERT INTO reservations VALUES (?, ?)', (actor, 'cloud-class'))
        return 'reserved'


def snapshot(path):
    with sqlite3.connect(path) as db:
        return {'seats': db.execute('SELECT * FROM seats ORDER BY course').fetchall(),
                'reservations': db.execute('SELECT * FROM reservations ORDER BY actor').fetchall()}


def concurrency_drill(folder):
    path=folder/'reservations.sqlite'; initialize(path)
    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes=list(workers.map(lambda actor: reserve(path,actor), ['alice','bob']))
    state=snapshot(path)
    assert sorted(outcomes)==['full','reserved'], outcomes
    winner=state['reservations'][0][0]
    assert reserve(path,winner)=='replay'
    assert snapshot(path)==state
    assert state['seats']==[('cloud-class',0)] and len(state['reservations'])==1
    return {'outcomes':outcomes,'winner':winner,'remaining':0,'replay_changed_state':False}


def restore_drill(folder):
    source=folder/'source.sqlite'; backup=folder/'backup.sqlite'; restored=folder/'restored.sqlite'
    initialize(source);reserve(source,'alice');expected=snapshot(source)
    with sqlite3.connect(source) as db, sqlite3.connect(backup) as target:
        db.backup(target)
    # Corrupt business state after the backup; leave the recovery copy untouched.
    with sqlite3.connect(source) as db:db.execute('DELETE FROM reservations')
    assert snapshot(source)!=expected
    start=time.perf_counter()
    with sqlite3.connect(backup) as db, sqlite3.connect(restored) as target:db.backup(target)
    with sqlite3.connect(restored) as db:assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert snapshot(restored)==expected
    elapsed=time.perf_counter()-start
    return {'application_data_matches':True,'sqlite_integrity':'ok','local_restore_validation_seconds':elapsed,
            'aws_rto_measured':False,'limitation':'No post-backup confirmed writes in this fixture; no production RPO claim'}


def evaluate_window(events, minimum_requests=20, error_threshold=0.05):
    # Request outcomes are synthetic and represent one already-closed window.
    if not events:return {'status':'no_data','requests':0,'error_fraction':None}
    if any(e not in {'ok','error'} for e in events):raise ValueError('Unknown request outcome')
    rate=events.count('error')/len(events)
    state='insufficient_sample' if len(events)<minimum_requests else ('alarm' if rate>error_threshold else 'healthy')
    return {'status':state,'requests':len(events),'error_fraction':rate}


def signals_drill():
    windows={'healthy':['ok']*100,'degraded':['ok']*90+['error']*10,'missing':[], 'tiny':['error']}
    observed={name:evaluate_window(events) for name,events in windows.items()}
    assert [observed[n]['status'] for n in windows]==['healthy','alarm','no_data','insufficient_sample']
    return observed


def release_drill(folder):
    # A local artifact-selection exercise, not a running web deployment or cloud pipeline.
    old=b'{"version":1,"result":42}';bad=b'{"version":2,"result":0}';good=b'{"version":3,"result":42}'
    artifact_dir=folder/'releases';artifact_dir.mkdir();selected=folder/'selected.txt'
    def store(content):
        digest=hashlib.sha256(content).hexdigest();(artifact_dir/digest).write_bytes(content);return digest
    old_id=store(old);selected.write_text(old_id)
    def check(content, configuration, destination):
        # This trusted in-process receipt is not a signature or authorization token.
        if json.loads(content)['result'] * configuration['multiplier'] != 42:
            return None
        return {'artifact': hashlib.sha256(content).hexdigest(),
                'configuration': json.dumps(configuration, sort_keys=True),
                'destination': destination}
    def promote(content, configuration, destination, receipt):
        if receipt is None:
            return False
        digest=hashlib.sha256(content).hexdigest()
        if (receipt['artifact'] != digest or
            receipt['configuration'] != json.dumps(configuration, sort_keys=True) or
            receipt['destination'] != destination):
            return False
        store(content)
        # Atomic replacement avoids a partially written selection file.
        tmp=folder/'selection.tmp';tmp.write_text(digest);tmp.replace(selected);return True
    config={'multiplier':1};target='practice'
    assert check(bad,config,target) is None
    assert not promote(bad,config,target,None);assert selected.read_text()==old_id
    receipt=check(good,config,target);assert receipt is not None
    # Same claimed version and correct result, but different bytes were never checked.
    rebuilt=b'{"version":3, "result":42}'
    assert json.loads(rebuilt)==json.loads(good)
    assert not promote(rebuilt,config,target,receipt);assert selected.read_text()==old_id
    assert not promote(good,{'multiplier':2},target,receipt);assert selected.read_text()==old_id
    assert not promote(good,config,'production',receipt);assert selected.read_text()==old_id
    assert promote(good,config,target,receipt);good_id=selected.read_text()
    assert hashlib.sha256((artifact_dir/good_id).read_bytes()).hexdigest()==good_id
    # A fresh check can legitimately approve different bytes for the same contract.
    rebuilt_receipt=check(rebuilt,config,target)
    assert promote(rebuilt,config,target,rebuilt_receipt)
    assert selected.read_text()==hashlib.sha256(rebuilt).hexdigest()!=good_id
    selected.write_text(old_id)
    assert json.loads((artifact_dir/selected.read_text()).read_bytes())['version']==1
    return {'bad_candidate_blocked':True,'good_candidate_promoted':True,'previous_artifact_reselected':True,
            'unchecked_rebuild_blocked':True,'changed_configuration_blocked':True,
            'wrong_destination_blocked':True,'rechecked_rebuild_promoted':True,
            'limitation':'Trusted in-process receipt; no signature, IAM, concurrent publisher, schema migration or traffic switching tested'}



def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Optional JSON report; parent must exist')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='amplify-local-drills-') as tmp:
        folder=Path(tmp)
        report={'scope':'local SQLite and synthetic fixtures; no AWS calls',
                'concurrency':concurrency_drill(folder),'restore':restore_drill(folder),
                'signals':signals_drill(),'release':release_drill(folder)}
    report['temporary_resources_removed']=not folder.exists()
    assert report['temporary_resources_removed']
    content=json.dumps(report,indent=2)+'\n'
    if args.output:args.output.write_text(content)
    print(content,end='')


if __name__=='__main__':main()
