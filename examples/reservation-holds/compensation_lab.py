"""Crash after a separate local provider ledger commits; no real refund or AWS call."""
from contextlib import closing
from pathlib import Path
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from lab import initialize, hold, capture_result


def provider_record(path, operation, payment):
    """Authored idempotency contract of this local simulator only."""
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        previous=db.execute('SELECT payment FROM refunds WHERE operation=?',(operation,)).fetchone()
        if previous:
            if previous[0]!=payment:
                raise ValueError('Operation reused for different payment')
            return 'RECORDED'
        db.execute('INSERT INTO refunds VALUES (?,?)',(operation,payment))
        return 'RECORDED'


def work(local_path, provider_path, lose_ack=False):
    with closing(sqlite3.connect(local_path)) as db:
        pending=db.execute("SELECT payment_id FROM compensation WHERE state='PENDING' ORDER BY payment_id").fetchall()
        for (payment,) in pending:
            operation='refund:'+payment
            result=provider_record(provider_path,operation,payment)
            if lose_ack:
                os._exit(23)  # Actual child exit after provider commit, before local acknowledgement.
            if result!='RECORDED':
                raise RuntimeError('Provider result not accepted')
            with db:
                db.execute("UPDATE compensation SET state='SIMULATED_DONE' WHERE payment_id=? AND state='PENDING'",(payment,))


def inspect(path, query):
    with closing(sqlite3.connect(path)) as db:
        return db.execute(query).fetchall()


def run():
    with tempfile.TemporaryDirectory(prefix='amplify-compensation-') as folder:
        root=Path(folder);local=root/'local.sqlite';provider=root/'provider.sqlite'
        with closing(sqlite3.connect(local)) as db:
            initialize(db)
            assert hold(db,'A','alice',0,10)=='HELD'
            assert capture_result(db,'payment-A','A',11)=='REFUND_PENDING'
        with closing(sqlite3.connect(provider)) as db, db:
            db.execute('CREATE TABLE refunds(operation TEXT PRIMARY KEY,payment TEXT NOT NULL)')
        command=[sys.executable,str(Path(__file__).resolve()),'--worker',str(local),str(provider)]
        lost=subprocess.run(command+['--lose-ack'],capture_output=True,text=True,timeout=10)
        assert lost.returncode==23,(lost.returncode,lost.stderr)
        assert inspect(provider,'SELECT * FROM refunds')==[('refund:payment-A','payment-A')]
        assert inspect(local,'SELECT * FROM compensation')==[('payment-A','PENDING')]
        restarted=subprocess.run(command,capture_output=True,text=True,timeout=10)
        assert restarted.returncode==0,restarted.stderr
        assert inspect(provider,'SELECT * FROM refunds')==[('refund:payment-A','payment-A')]
        assert inspect(local,'SELECT * FROM compensation')==[('payment-A','SIMULATED_DONE')]
        work(local,provider)
        assert inspect(provider,'SELECT * FROM refunds')==[('refund:payment-A','payment-A')]
        try:provider_record(provider,'refund:payment-A','different-payment')
        except ValueError:pass
        else:raise AssertionError('Conflicting operation replay accepted')
        assert inspect(provider,'SELECT * FROM refunds')==[('refund:payment-A','payment-A')]
    assert not root.exists()
    return {'child_exit_after_provider_commit':23,'provider_records_after_restart':1,
            'local_obligation':'SIMULATED_DONE','scope':'two local SQLite ledgers; no real refund or provider integration'}


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    if len(sys.argv)>1 and sys.argv[1]=='--worker':
        if len(sys.argv) not in (4,5) or (len(sys.argv)==5 and sys.argv[4]!='--lose-ack'):
            raise SystemExit('Invalid worker arguments')
        work(Path(sys.argv[2]),Path(sys.argv[3]),len(sys.argv)==5)
    else:
        print(json.dumps(run(),indent=2))
