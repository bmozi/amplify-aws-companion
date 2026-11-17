"""Changed-failure tests for the local modernization seam, not AWS behavior."""
from contextlib import closing
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import json

from outbox_lab import book, database, process, reconcile, relay


class OutboxLessonTests(unittest.TestCase):
    def test_restart_demo_reports_the_observed_transition(self):
        script = Path(__file__).resolve().parent / 'restart_demo.py'
        result = subprocess.run([sys.executable, str(script)], check=True, capture_output=True, text=True)
        before, after = json.loads(result.stdout)['observations']
        self.assertEqual(before['missing_report'], ['restart'])
        self.assertEqual(after['pending_before_send'], 1)
        self.assertEqual(after['delivery_outcome'], 'accepted')
        self.assertEqual(after['report_cents'], 1200)
        self.assertEqual(after['missing_report'], [])

    def test_committed_obligation_survives_process_exit_before_first_send(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = str(Path(directory) / "outbox.sqlite")
            module_dir = str(Path(__file__).resolve().parent)
            writer = ("import sys; sys.path.insert(0, sys.argv[1]); "
                      "from outbox_lab import database, book; "
                      "db=database(sys.argv[2]); book(db, 'restart', 1200); db.close()")
            reader = ("import sys; sys.path.insert(0, sys.argv[1]); "
                      "from outbox_lab import database, relay, process, reconcile; "
                      "db=database(sys.argv[2]); deliveries=[]; "
                      "assert relay(db, deliveries); assert len(deliveries)==1; "
                      "assert process(db, deliveries[0])=='accepted'; "
                      "assert reconcile(db)['report_cents']==1200; db.close()")
            subprocess.run([sys.executable, '-c', writer, module_dir, database_path], check=True)
            subprocess.run([sys.executable, '-c', reader, module_dir, database_path], check=True)

    def test_reopening_a_different_empty_file_cannot_recover_the_obligation(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / 'original.sqlite'
            different = Path(directory) / 'different.sqlite'
            with closing(database(str(original))) as db:
                book(db, 'restart', 1200)
            with closing(database(str(different))) as db:
                deliveries = []
                self.assertFalse(relay(db, deliveries))
                self.assertEqual(reconcile(db)['source_count'], 0)
                self.assertEqual(deliveries, [])
            with closing(database(str(original))) as db:
                self.assertEqual(reconcile(db)['missing_report'], ['restart'])

    def test_booking_and_outbox_roll_back_together(self):
        with closing(database()) as db:
            with self.assertRaises(RuntimeError):
                book(db, "failed", 100, fail_before_outbox=True)
            self.assertEqual(reconcile(db)["source_count"], 0)
            self.assertEqual(db.execute("SELECT count(*) FROM outbox").fetchone()[0], 0)

    def test_lost_send_ack_replays_without_double_counting(self):
        with closing(database()) as db:
            book(db, "A", 1200)
            deliveries = []
            with self.assertRaises(RuntimeError):
                relay(db, deliveries, fail_after_send=True)
            self.assertTrue(relay(db, deliveries))
            self.assertEqual(len(deliveries), 2)
            self.assertEqual(process(db, deliveries[0]), "accepted")
            self.assertEqual(process(db, deliveries[1]), "duplicate")
            self.assertEqual(reconcile(db)["report_cents"], 1200)

    def test_published_does_not_mean_report_completed(self):
        with closing(database()) as db:
            book(db, "A", 1200)
            deliveries = []
            self.assertTrue(relay(db, deliveries))
            self.assertEqual(reconcile(db)["missing_report"], ["A"])
            self.assertEqual(process(db, deliveries[0]), "accepted")
            self.assertEqual(reconcile(db)["missing_report"], [])

    def test_changed_redelivery_is_rejected(self):
        with closing(database()) as db:
            book(db, "A", 1200)
            deliveries = []
            relay(db, deliveries)
            self.assertEqual(process(db, deliveries[0]), "accepted")
            changed = dict(deliveries[0], cents=9999)
            with self.assertRaises(ValueError):
                process(db, changed)
            self.assertEqual(reconcile(db)["report_cents"], 1200)

    def test_wrong_report_amount_exposed_by_reconciliation(self):
        with closing(database()) as db:
            book(db, "A", 1200)
            self.assertEqual(process(db, {"event_id": "booking:A", "booking_id": "A", "cents": 999}),
                             "accepted")
            self.assertEqual(reconcile(db)["amount_mismatch"], ["A"])

    def test_event_id_must_name_its_booking(self):
        with closing(database()) as db:
            book(db, "A", 1200)
            with self.assertRaises(ValueError):
                process(db, {"event_id": "booking:B", "booking_id": "A", "cents": 1200})
            self.assertEqual(reconcile(db)["missing_report"], ["A"])

    def test_invalid_cents_and_empty_ids_do_not_write(self):
        with closing(database()) as db:
            for booking_id, cents in (("", 100), ("A", 0), ("A", True)):
                with self.assertRaises(ValueError):
                    book(db, booking_id, cents)
            self.assertEqual(reconcile(db)["source_count"], 0)


if __name__ == "__main__":
    unittest.main()
