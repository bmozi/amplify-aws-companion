"""Single-threaded real SQLite borrowing/rollback exercise; not a production pool."""
from contextlib import contextmanager, closing
from pathlib import Path
from queue import Empty, Queue
import sqlite3
import sys
import tempfile


def connect(path):
    # Use explicit SQL BEGIN/COMMIT/ROLLBACK rather than changing Python defaults.
    options = {'autocommit': True} if hasattr(sqlite3, 'LEGACY_TRANSACTION_CONTROL') else {}
    return sqlite3.connect(path, isolation_level=None, **options)


class TeachingPool:
    def __init__(self, path):
        self.connection = connect(path)
        self.available = Queue(maxsize=1)
        self.available.put_nowait(self.connection)

    @contextmanager
    def borrow(self):
        try:
            connection = self.available.get(timeout=0.01)
        except Empty:
            raise TimeoutError('No connection available within the fixture wait') from None
        try:
            yield connection
        finally:
            try:
                if connection.in_transaction:
                    connection.execute('ROLLBACK')
            except sqlite3.Error:
                # Never return a connection whose cleanup failed; no replacement in this drill.
                connection.close()
                raise
            self.available.put_nowait(connection)

    def close(self):
        self.connection.close()


def run():
    if sys.flags.optimize:
        raise SystemExit('Run without -O')
    with tempfile.TemporaryDirectory(prefix='connection-pool-') as directory:
        path = Path(directory) / 'records.sqlite'
        with closing(connect(path)) as observer:
            observer.execute('CREATE TABLE records(id INTEGER PRIMARY KEY, note TEXT)')
            # Negative control: a raw return does not reset connection transaction state.
            with closing(connect(path)) as unsafe:
                slot = Queue(maxsize=1)
                slot.put_nowait(unsafe)
                first = slot.get_nowait()
                first.execute('BEGIN')
                first.execute('INSERT INTO records VALUES (1, ?)', ('unfinished',))
                slot.put_nowait(first)  # deliberately wrong: no cleanup
                next_borrower = slot.get_nowait()
                assert next_borrower.execute('SELECT * FROM records').fetchall() == [(1, 'unfinished')]
                assert observer.execute('SELECT * FROM records').fetchall() == []
                next_borrower.execute('ROLLBACK')
            print('Negative control: reused connection sees unfinished work; independent connection sees no committed row')

            pool = TeachingPool(path)
            try:
                try:
                    with pool.borrow() as connection:
                        connection.execute('BEGIN')
                        connection.execute('INSERT INTO records VALUES (2, ?)', ('must roll back',))
                        raise ValueError('Injected application failure')
                except ValueError as error:
                    assert str(error) == 'Injected application failure'
                else:
                    raise AssertionError('Failure injection did not execute')
                with pool.borrow() as connection:
                    assert not connection.in_transaction
                    assert connection.execute('SELECT * FROM records').fetchall() == []
                assert observer.execute('SELECT * FROM records').fetchall() == []
                print('Exception cleanup: next borrower is outside a transaction and failed row is absent')

                with pool.borrow() as held:
                    held.execute('BEGIN')
                    held.execute('INSERT INTO records VALUES (3, ?)', ('committed later',))
                    for _ in range(2):
                        try:
                            with pool.borrow():
                                raise AssertionError('Exhausted pool handed out a second connection')
                        except TimeoutError:
                            pass
                    assert held.in_transaction
                    assert observer.execute('SELECT * FROM records').fetchall() == []
                    held.execute('COMMIT')
                with pool.borrow() as reused:
                    assert reused is held
                    assert not reused.in_transaction
                    assert reused.execute('SELECT * FROM records').fetchall() == [(3, 'committed later')]
                assert observer.execute('SELECT * FROM records').fetchall() == [(3, 'committed later')]
                print('Wait timeout: holder remains active; explicit commit and release permit clean reuse')

                with pool.borrow() as forgotten:
                    forgotten.execute('BEGIN')
                    forgotten.execute('INSERT INTO records VALUES (4, ?)', ('forgotten commit',))
                assert observer.execute('SELECT * FROM records').fetchall() == [(3, 'committed later')]
                print('Success without explicit commit: unfinished work rolled back by the stated pool contract')
            finally:
                pool.close()
        assert path.exists()
    assert not Path(directory).exists()
    print('PASS: real local connections; temporary database removed; no cloud or concurrent-driver claim')


if __name__ == '__main__':
    run()
