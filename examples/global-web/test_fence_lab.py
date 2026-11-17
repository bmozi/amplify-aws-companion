"""Changed-order and stale-token checks for the local A21 authority exercise."""

import tempfile
import unittest
from pathlib import Path

from fence_lab import Authority, run


class FenceTests(unittest.TestCase):
    def test_local_negative_controls_and_atomic_guard(self):
        result = run()
        self.assertEqual(result["flag_only"], {"old_writer_after_move": "ACCEPTED", "new_writer_after_move": "ACCEPTED"})
        self.assertEqual(result["precheck_only"], {"old_precheck": True, "move": "TRANSFERRED", "old_write_after_move": "ACCEPTED"})
        self.assertEqual(result["atomic_local_authority"], {
            "old_token_after_move": "STALE_WRITER", "new_token": "ACCEPTED",
            "old_token_other_slot": "STALE_WRITER", "visible_receipts": ["r-new"]})

    def test_stale_transfer_cannot_reopen_first_writer(self):
        with tempfile.TemporaryDirectory() as folder:
            gate = Authority(Path(folder) / "gate.sqlite")
            try:
                self.assertEqual(gate.transfer(1, "first", "second"), "TRANSFERRED")
                self.assertEqual(gate.transfer(1, "second", "first"), "STALE_TRANSFER")
                self.assertEqual(gate.current(), (2, "second"))
            finally:
                gate.close()

    def test_same_slot_conflict_does_not_advance_receipts(self):
        with tempfile.TemporaryDirectory() as folder:
            gate = Authority(Path(folder) / "gate.sqlite")
            try:
                self.assertEqual(gate.book(1, "first", "r-a", "09:00", "Alice"), "ACCEPTED")
                self.assertEqual(gate.book(1, "first", "r-b", "09:00", "Bob"), "CONFLICT")
                self.assertEqual(gate.rows(), [("r-a", "09:00", "Alice")])
            finally:
                gate.close()

    def test_old_token_rejected_before_and_after_new_booking(self):
        with tempfile.TemporaryDirectory() as folder:
            gate = Authority(Path(folder) / "gate.sqlite")
            try:
                self.assertEqual(gate.transfer(1, "first", "second"), "TRANSFERRED")
                self.assertEqual(gate.book(1, "first", "r-a", "08:00", "Alice"), "STALE_WRITER")
                self.assertEqual(gate.book(2, "second", "r-b", "09:00", "Bob"), "ACCEPTED")
                self.assertEqual(gate.book(1, "first", "r-c", "10:00", "Cara"), "STALE_WRITER")
                self.assertEqual(gate.rows(), [("r-b", "09:00", "Bob")])
            finally:
                gate.close()

    def test_invalid_owner_does_not_change_authority(self):
        with tempfile.TemporaryDirectory() as folder:
            gate = Authority(Path(folder) / "gate.sqlite")
            try:
                self.assertEqual(gate.transfer(1, "first", "stranger"), "INVALID_OWNER")
                self.assertEqual(gate.current(), (1, "first"))
            finally:
                gate.close()
