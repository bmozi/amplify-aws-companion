import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from local_lab import ExportDenied
from persistent_lab import LostReply, OwnerLedger, SupplierShelf


class PersistentExportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.owner_path, self.supplier_path = root / "owner.sqlite", root / "supplier.sqlite"
        self.owner, self.shelf = OwnerLedger(self.owner_path), SupplierShelf(self.supplier_path)
        self.candidate = self.owner.stage("weekly-parts", "v1", [{"part_number": "P-7", "quantity": 2}])

    def tearDown(self):
        self.temp.cleanup()

    def test_lost_approval_reply_recovers_same_exact_decision_after_reopen(self):
        c = self.candidate
        with self.assertRaises(LostReply):
            self.owner.approve(c.key, c.version, c.digest, "Supplier P", "Maya", lose_reply=True)
        self.owner = OwnerLedger(self.owner_path)
        self.assertEqual(self.owner.approve(c.key, c.version, c.digest, "Supplier P", "Maya")["result"],
                         "already_approved")
        with self.assertRaises(ExportDenied):
            self.owner.approve(c.key, c.version, c.digest, "Supplier Q", "Maya")
        with self.assertRaises(ExportDenied):
            self.owner.approve(c.key, c.version, "wrong", "Supplier P", "Maya")

    def test_replacement_version_needs_its_own_approval(self):
        c = self.candidate
        self.owner.approve(c.key, c.version, c.digest, "Supplier P", "Maya")
        v2 = self.owner.stage(c.key, "v2", [{"part_number": "P-7", "quantity": 3}])
        with self.assertRaises(ExportDenied):
            self.owner.approved_bytes(v2.key, v2.version, "Supplier P")
        with self.assertRaises(ExportDenied):
            self.owner.stage(c.key, c.version, [{"part_number": "P-7", "quantity": 2}])

    def test_lost_delivery_reply_and_withdrawal_leave_independent_copy(self):
        c = self.candidate
        self.owner.approve(c.key, c.version, c.digest, "Supplier P", "Maya")
        with self.assertRaises(LostReply):
            self.shelf.accept(self.owner, c.key, c.version, "Supplier P", lose_reply=True)
        self.shelf = SupplierShelf(self.supplier_path)
        self.assertEqual(self.shelf.lookup(c.key, c.version, "Supplier P")[1], c.digest)
        self.owner.withdraw(c.key, c.version, "Maya")
        self.owner = OwnerLedger(self.owner_path)
        with self.assertRaises(ExportDenied):
            self.owner.approved_bytes(c.key, c.version, "Supplier P")
        with self.assertRaises(ExportDenied):
            self.shelf.accept(self.owner, c.key, c.version, "Supplier P")
        self.assertEqual(self.shelf.lookup(c.key, c.version, "Supplier P")[1], c.digest)

    def test_wrong_actor_and_private_field_are_rejected(self):
        c = self.candidate
        with self.assertRaises(ExportDenied):
            self.owner.approve(c.key, c.version, c.digest, "Supplier P", "Mallory")
        with self.assertRaises(ValueError):
            self.owner.stage("private", "v1", [{"part_number": "P-7", "quantity": 2,
                                                "address": "secret"}])

    def test_conflicting_concurrent_approvals_choose_one_supplier(self):
        c = self.candidate
        def attempt(supplier):
            try:
                return self.owner.approve(c.key, c.version, c.digest, supplier, "Maya")["supplier"]
            except ExportDenied:
                return "denied"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, ("Supplier P", "Supplier Q")))
        self.assertEqual(results.count("denied"), 1)
        self.assertEqual(len(set(results)), 2)

    def test_withdrawal_does_not_recall_in_flight_bytes(self):
        c = self.candidate
        self.owner.approve(c.key, c.version, c.digest, "Supplier P", "Maya")
        self.shelf.accept(self.owner, c.key, c.version, "Supplier P",
                          after_owner_read=lambda: self.owner.withdraw(c.key, c.version, "Maya"))
        self.assertEqual(self.shelf.lookup(c.key, c.version, "Supplier P")[1], c.digest)
        with self.assertRaises(ExportDenied):
            self.owner.approved_bytes(c.key, c.version, "Supplier P")


if __name__ == "__main__":
    unittest.main()
