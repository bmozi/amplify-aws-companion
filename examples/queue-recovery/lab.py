"""Local supplier receipts and failure windows; not an SQS emulator."""
import sqlite3
import tempfile
from pathlib import Path


def book(path, operation, appointment, lose_response=False):
    """Fictional supplier atomically stores its effect and durable receipt."""
    with sqlite3.connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        prior = db.execute('SELECT appointment FROM receipts WHERE operation=?',
                           (operation,)).fetchone()
        if prior and prior[0] != appointment:
            raise ValueError('Same operation identity with different appointment')
        if not prior:
            db.execute('INSERT INTO receipts VALUES (?, ?)', (operation, appointment))
    # Commit has completed, but the caller may never see the response.
    if lose_response:
        raise TimeoutError('Supplier committed; simulated response lost')
    return operation


def receipts(path):
    with sqlite3.connect(path) as db:
        return db.execute('SELECT operation, appointment FROM receipts ORDER BY operation').fetchall()


def process(operation, appointment, supplier, fail_before_call=False):
    if fail_before_call:
        raise RuntimeError('Injected worker crash before supplier call')
    return supplier(operation, appointment)


def main():
    with tempfile.TemporaryDirectory(prefix='queue-recovery-') as directory:
        path = Path(directory) / 'supplier.sqlite'
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE receipts (operation TEXT PRIMARY KEY, appointment TEXT NOT NULL)')

        # Negative control: delivery identity changes while business intent does not.
        try:
            book(path, 'unsafe-attempt-1', 'repair-shop-A-0900', lose_response=True)
        except TimeoutError:
            pass
        else:
            raise AssertionError('Failure injection did not run')
        book(path, 'unsafe-attempt-2', 'repair-shop-A-0900')
        assert len(receipts(path)) == 2
        print('UNSAFE: two delivery identities created two supplier effects for one appointment.')

        # A separate request uses its business identity across all deliveries.
        caller_state = 'pending'
        try:
            book(path, 'request-B', 'repair-shop-B-1000', lose_response=True)
        except TimeoutError:
            caller_state = 'unknown'
        assert caller_state == 'unknown'
        assert ('request-B', 'repair-shop-B-1000') in receipts(path)
        # A new database connection represents durable supplier evidence, not caller memory.
        receipt = book(path, 'request-B', 'repair-shop-B-1000')
        assert receipt == 'request-B'
        assert len(receipts(path)) == 3
        caller_state = 'completed'
        print('STABLE: lost response left caller uncertain; retry returned the existing receipt.')

        before = receipts(path)
        try:
            book(path, 'request-B', 'repair-shop-B-1100')
        except ValueError:
            pass
        else:
            raise AssertionError('Identity reuse with changed intent was accepted')
        assert receipts(path) == before
        print('CONFLICT: changed appointment with reused identity rejected; effects unchanged.')

        # Explicit fictional transport fixture: three deliveries crash before the call.
        deliveries = ['delivery-1', 'delivery-2', 'delivery-3']
        supplier_calls = 0
        def counted_supplier(operation, appointment):
            nonlocal supplier_calls
            supplier_calls += 1
            return book(path, operation, appointment)

        for delivery in deliveries:
            try:
                process('request-C', 'repair-shop-C-1200', counted_supplier,
                        fail_before_call=True)
            except RuntimeError:
                pass
            else:
                raise AssertionError(f'{delivery}: pre-call crash was not injected')
        failed_work = ['request-C']
        ledger = {'request-B': caller_state, 'request-C': 'unfinished'}
        assert len(deliveries) == 3 and supplier_calls == 0
        assert receipts(path) == before
        print('PRE-CALL: three fictional receives, zero supplier calls, one unresolved request.')

        # Moving/deleting failed transport work cannot update the business ledger.
        failed_work.clear()
        unresolved = [key for key, state in ledger.items() if state != 'completed']
        assert not failed_work and unresolved == ['request-C']
        print('EMPTY: failed-work list empty; request-C still unfinished in the ledger.')

        # Controlled retry after repairing the injected failure, preserving identity.
        assert process('request-C', 'repair-shop-C-1200', counted_supplier) == 'request-C'
        assert supplier_calls == 1 and len(receipts(path)) == 4
        ledger['request-C'] = 'completed'
        assert all(state == 'completed' for state in ledger.values())
        print('RECOVERED: repaired worker obtained request-C receipt before marking completion.')
    assert not path.exists()
    print('PASS: local sequential cases; temporary database removed; no AWS calls.')


if __name__ == '__main__':
    import sys
    if sys.flags.optimize:
        raise SystemExit('Run without -O: this teaching exercise uses assertions')
    main()
