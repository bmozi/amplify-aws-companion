"""Negative and positive controls for the transaction boundary in the toy lab."""

from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from db_epoch_lab import (DivergentStores, StaleRoute, connect, orders, route,
                          run, setup, switch, unsafe_switch_after_check, write)


class DatabaseEpochTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.dbpath = self.folder / 'store.sqlite'
        setup(self.dbpath)

    def test_separate_connection_stale_writer_is_rejected_after_switch(self):
        self.assertEqual(switch(self.dbpath), 1)
        with self.assertRaises(StaleRoute):
            write(self.dbpath, 0, 'late', 375)
        self.assertEqual(write(self.dbpath, 1, 'late', 375), 'new')
        with closing(connect(self.dbpath)) as db:
            self.assertEqual(route(db), ('new', 1))
            self.assertEqual(orders(db, 'old'), [('a', 250)])
            self.assertEqual(orders(db, 'new'), [('a', 250), ('late', 375)])

    def test_divergence_stops_switch_and_preserves_epoch(self):
        self.assertEqual(write(self.dbpath, 0, 'late', 375), 'old')
        with self.assertRaises(DivergentStores):
            switch(self.dbpath)
        with closing(connect(self.dbpath)) as db:
            self.assertEqual(route(db), ('old', 0))

    def test_read_only_check_then_switch_loses_late_old_write(self):
        unsafe_switch_after_check(self.dbpath, lambda: write(self.dbpath, 0, 'late', 375))
        with closing(connect(self.dbpath)) as db:
            self.assertEqual(route(db), ('new', 1))
            self.assertIn(('late', 375), orders(db, 'old'))
            self.assertNotIn(('late', 375), orders(db, 'new'))

    def test_direct_uncooperative_old_write_still_bypasses_application_rule(self):
        self.assertEqual(switch(self.dbpath), 1)
        with closing(connect(self.dbpath)) as db:
            db.execute("INSERT INTO orders VALUES ('old','bypass',999)")
            self.assertIn(('bypass', 999), orders(db, 'old'))
        # The lab has no DB privilege design or trigger that forbids this bypass.

    def test_selector_transaction_holds_database_write_authority(self):
        checked, release = threading.Event(), threading.Event()
        errors = []

        def select():
            try:
                switch(self.dbpath, checked, release)
            except Exception as exc:
                errors.append(exc)

        worker = threading.Thread(target=select)
        worker.start()
        try:
            self.assertTrue(checked.wait(timeout=5))
            with closing(sqlite3.connect(self.dbpath, timeout=0, isolation_level=None)) as other:
                with self.assertRaisesRegex(sqlite3.OperationalError, 'locked'):
                    other.execute('BEGIN IMMEDIATE')
        finally:
            release.set()
            worker.join(timeout=6)
        self.assertFalse(worker.is_alive())
        self.assertEqual(errors, [])
        with closing(connect(self.dbpath)) as db:
            self.assertEqual(route(db), ('new', 1))

    def test_concurrent_demo_completes_with_the_two_distinct_outcomes(self):
        result = run(self.folder)
        self.assertTrue(result['writer_outcome']['stale_writer_rejected'])
        self.assertEqual(result['writer_outcome']['fresh_writer_store'], 'new')


if __name__ == '__main__':
    unittest.main()
