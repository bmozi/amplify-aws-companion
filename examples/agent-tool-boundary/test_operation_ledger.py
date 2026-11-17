"""Boundary checks for the one-host operation ledger, not provider safety tests."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
import unittest

from operation_ledger import Operation, confirm, initialize, reserve


OP = Operation("op-17", "maya", "repair-17", 1200, "approval-17")


class OperationLedgerTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "claims.sqlite3"
        initialize(self.path)

    def test_lost_reply_stays_pending_and_consumes_limit(self):
        self.assertEqual(reserve(self.path, OP), "reserved")
        self.assertEqual(reserve(self.path, OP), "reconcile_required")
        other = Operation("op-18", "maya", "repair-17", 1200, "approval-17")
        self.assertEqual(reserve(self.path, other), "limit_reached")
        self.assertEqual(confirm(self.path, "op-17", "fictional-provider-17"), "confirmed")
        self.assertEqual(reserve(self.path, OP), "receipt_available")

    def test_changed_payload_cannot_borrow_stable_id(self):
        self.assertEqual(reserve(self.path, OP), "reserved")
        changed = Operation("op-17", "maya", "repair-17", 1300, "approval-17")
        self.assertEqual(reserve(self.path, changed), "conflict")
        self.assertEqual(reserve(self.path, OP), "reconcile_required")

    def test_receipt_must_be_supplied_and_cannot_be_rewritten(self):
        self.assertEqual(confirm(self.path, "missing", "receipt"), "unknown_operation")
        self.assertEqual(reserve(self.path, OP), "reserved")
        with self.assertRaises(ValueError):
            confirm(self.path, "op-17", "")
        self.assertEqual(reserve(self.path, OP), "reconcile_required")
        self.assertEqual(confirm(self.path, "op-17", "receipt-1"), "confirmed")
        self.assertEqual(confirm(self.path, "op-17", "receipt-1"), "same_receipt")
        self.assertEqual(confirm(self.path, "op-17", "receipt-2"), "receipt_conflict")

    def test_two_local_workers_get_one_claim_for_same_id(self):
        barrier = Barrier(2)

        def attempt():
            barrier.wait()
            return reserve(self.path, OP)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: attempt(), range(2)))
        self.assertCountEqual(results, ["reserved", "reconcile_required"])

    def test_two_local_workers_cannot_both_take_last_slot(self):
        barrier = Barrier(2)
        operations = [OP, Operation("op-18", "maya", "repair-17", 1200, "approval-17")]

        def attempt(operation):
            barrier.wait()
            return reserve(self.path, operation)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, operations))
        self.assertCountEqual(results, ["reserved", "limit_reached"])


if __name__ == "__main__":
    unittest.main()
