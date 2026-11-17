"""Local schema transformation and cutover guard. No cloud, live clients, or CDC."""
from decimal import Decimal
import json
from pathlib import Path
import sqlite3
import tempfile


def cents(value):
    number=Decimal(value)*100
    if not number.is_finite() or number != number.to_integral_value() or number < 0:
        raise ValueError('Amount must be finite nonnegative whole cents')
    return int(number)


def old_rows(path):
    with sqlite3.connect(path) as db:return db.execute('SELECT id,amount FROM orders ORDER BY id').fetchall()


def new_rows(path):
    with sqlite3.connect(path) as db:return db.execute('SELECT id,amount_cents FROM orders ORDER BY id').fetchall()


def transform(source,target,converter):
    with sqlite3.connect(target) as db:
        db.execute('CREATE TABLE orders(id TEXT PRIMARY KEY,amount_cents INTEGER NOT NULL)')
        db.executemany('INSERT INTO orders VALUES (?,?)',[(i,converter(amount)) for i,amount in old_rows(source)])


def reconciles(source,target):
    return [(i,cents(amount)) for i,amount in old_rows(source)]==new_rows(target)


def select_if_reconciled(source,target,pointer):
    # Real systems must stop or reconcile concurrent writes before this decision.
    if not reconciles(source,target):return False
    temporary=pointer.with_suffix('.tmp');temporary.write_text(target.name);temporary.replace(pointer)
    return True


def return_to_source_if_reconciled(source,target,pointer):
    # Fixture-only decision; production needs a reverse-data and effect plan.
    if not reconciles(source,target):return False
    temporary=pointer.with_suffix('.tmp');temporary.write_text(source.name);temporary.replace(pointer)
    return True


def run(folder):
    source=folder/'source.sqlite';bad=folder/'bad.sqlite';good=folder/'good.sqlite';pointer=folder/'selected.txt'
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE orders(id TEXT PRIMARY KEY,amount TEXT NOT NULL)')
        db.executemany('INSERT INTO orders VALUES (?,?)',[('a','12.99'),('b','0.01'),('c','100.00')])
    pointer.write_text(source.name)
    transform(source,bad,lambda amount:int(Decimal(amount))*100)  # Deliberately discards cents.
    assert len(old_rows(source))==len(new_rows(bad))
    assert not select_if_reconciled(source,bad,pointer) and pointer.read_text()==source.name
    transform(source,good,cents)
    # A confirmed write after the initial copy makes that otherwise-correct copy incomplete.
    with sqlite3.connect(source) as db:db.execute('INSERT INTO orders VALUES (?,?)',('d','3.50'))
    assert not select_if_reconciled(source,good,pointer)
    # Fixture now pauses writes. Replay the known missing record once, then validate all records.
    with sqlite3.connect(good) as db:db.execute('INSERT INTO orders VALUES (?,?)',('d',350))
    assert select_if_reconciled(source,good,pointer) and pointer.read_text()==good.name
    # Before target-only writes, source and target represent the same business data.
    assert reconciles(source,good)
    with sqlite3.connect(good) as db:db.execute('INSERT INTO orders VALUES (?,?)',('e',250))
    # Returning to the untouched source would hide a confirmed target-side order.
    rollback_safe=reconciles(source,good)
    assert not rollback_safe and pointer.read_text()==good.name
    rejected=0
    for value in ['1.001','-1.00','NaN','Infinity']:
        try:cents(value)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid monetary value accepted')
    assert rejected==4
    return {'bad_transform_count_matches':True,'bad_transform_cutover_blocked':True,
            'post_copy_write_detected':True,'reconciled_target_selected':True,
            'rollback_after_target_write_blocked_by_comparison':not rollback_safe,
            'invalid_amounts_rejected':rejected,
            'scope':'SQLite data transformation and local selection pointer only; no live traffic switch, concurrent writes, CDC, AWS migration or reverse synchronization'}

if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-migration-') as tmp:
        folder=Path(tmp);result=run(folder)
    result['temporary_resources_removed']=not folder.exists()
    assert result['temporary_resources_removed']
    print(json.dumps(result,indent=2))
