"""Behavior checks for the local contract's meaningful failure boundaries."""

import unittest

from local_lab import ExportDenied, ExportLedger


class ExportContractTests(unittest.TestCase):
    def setUp(self):
        self.ledger = ExportLedger("Maya")
        self.v1 = self.ledger.stage("parts", "v1", [{"part_number": "P-7", "quantity": 2}])

    def test_private_field_or_invalid_quantity_is_not_exported(self):
        with self.assertRaises(ValueError):
            self.ledger.stage("parts", "bad", [{"part_number": "P-7", "quantity": 2,
                                                   "customer_address": "private"}])
        with self.assertRaises(ValueError):
            self.ledger.stage("parts", "bad", [{"part_number": "P-7", "quantity": True}])
        self.assertNotIn(("parts", "bad"), self.ledger.candidates)

    def test_approval_binds_digest_recipient_and_exact_version(self):
        with self.assertRaises(ExportDenied):
            self.ledger.approve("parts", "v1", "wrong", "Supplier P", "Maya")
        with self.assertRaises(ExportDenied):
            self.ledger.approve("parts", "v1", self.v1.digest, "Supplier P", "Supplier P")
        self.ledger.approve("parts", "v1", self.v1.digest, "Supplier P", "Maya")
        v2 = self.ledger.stage("parts", "v2", [{"part_number": "P-7", "quantity": 3}])
        self.assertEqual(self.ledger.owner_read_for_supplier("parts", "v1", "Supplier P"),
                         self.v1.payload)
        for key, version, supplier in [("parts", "v2", "Supplier P"),
                                       ("parts", "v1", "Supplier Q"),
                                       ("private-source", "v1", "Supplier P")]:
            with self.assertRaises(ExportDenied):
                self.ledger.owner_read_for_supplier(key, version, supplier)
        with self.assertRaises(ValueError):
            self.ledger.stage("parts", "v1", [{"part_number": "P-7", "quantity": 9}])
        self.assertNotEqual(v2.digest, self.v1.digest)

    def test_withdrawal_blocks_future_owner_read_but_not_delivered_copy(self):
        self.ledger.approve("parts", "v1", self.v1.digest, "Supplier P", "Maya")
        delivered = self.ledger.deliver_copy("parts", "v1", "Supplier P")
        with self.assertRaises(ExportDenied):
            self.ledger.withdraw("parts", "v1", "Supplier P")
        self.ledger.withdraw("parts", "v1", "Maya")
        with self.assertRaises(ExportDenied):
            self.ledger.owner_read_for_supplier("parts", "v1", "Supplier P")
        self.assertEqual(self.ledger.supplier_copy("parts", "v1", "Supplier P"), delivered)
        with self.assertRaises(ExportDenied):
            self.ledger.supplier_copy("parts", "v1", "Supplier Q")
        with self.assertRaises(ExportDenied):
            self.ledger.approve("parts", "v1", self.v1.digest, "Supplier Q", "Maya")


if __name__ == "__main__":
    unittest.main()
