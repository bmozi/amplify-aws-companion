"""Changed-condition controls for local overdue contact ownership."""

import unittest

from deadline_lab import accept, inspect_due, read_open_worklist, record_contact
from operator_lab import operator_database, claim_open_contact, attest_first_contact


class OperatorLabTest(unittest.TestCase):
    def setUp(self):
        self.db = operator_database()
        self.connection = self.db.__enter__()
        accept(self.connection, "r1", 0)
        inspect_due(self.connection, 3601)

    def tearDown(self):
        self.db.__exit__(None, None, None)

    def test_claim_retry_rival_and_expiry(self):
        first = claim_open_contact(self.connection, "r1", "a", 3610, 20)
        self.assertEqual(claim_open_contact(self.connection, "r1", "a", 3620), first)
        with self.assertRaisesRegex(ValueError, "Another operator"):
            claim_open_contact(self.connection, "r1", "b", 3620)
        new = claim_open_contact(self.connection, "r1", "b", 3630, 20)
        self.assertEqual(new["generation"], 2)
        with self.assertRaisesRegex(ValueError, "No active matching"):
            attest_first_contact(self.connection, first, 3620, 3631)
        self.assertEqual(len(read_open_worklist(self.connection)["items"]), 1)

    def test_lost_attestation_reply_is_idempotent_and_late_stays_late(self):
        claim = claim_open_contact(self.connection, "r1", "a", 3610, 60)
        first = attest_first_contact(self.connection, claim, 3650, 3660)
        self.assertEqual(attest_first_contact(self.connection, claim, 3650, 4000), first)
        self.assertFalse(first["met_one_hour_promise"])
        self.assertEqual(read_open_worklist(self.connection)["items"], [])
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM attestations").fetchone()[0], 1)
        with self.assertRaisesRegex(ValueError, "cannot be rewritten"):
            attest_first_contact(self.connection, claim, 3599, 4001)
        with self.assertRaisesRegex(ValueError, "cannot precede"):
            attest_first_contact(self.connection, claim, 3650, 3649)

    def test_claim_alone_does_not_close_work_and_prior_contact_prevents_claim(self):
        claim_open_contact(self.connection, "r1", "a", 3610)
        self.assertEqual(len(read_open_worklist(self.connection)["items"]), 1)
        record_contact(self.connection, "r1", 3650)
        with self.assertRaisesRegex(ValueError, "not open"):
            claim_open_contact(self.connection, "r1", "b", 3700)

    def test_invalid_time_lease_and_attestation_fail_closed(self):
        for lease in (0, 901, True):
            with self.assertRaises(ValueError):
                claim_open_contact(self.connection, "r1", "a", 3610, lease)
        claim = claim_open_contact(self.connection, "r1", "a", 3610, 20)
        for contacted, recorded in ((3600, 3615), (3620, 3630)):
            with self.assertRaisesRegex(ValueError, "No active matching"):
                attest_first_contact(self.connection, claim, contacted, recorded)
        with self.assertRaisesRegex(ValueError, "cannot precede"):
            attest_first_contact(self.connection, claim, 3612, 3611)
        with self.assertRaises(ValueError):
            attest_first_contact(self.connection, {**claim, "generation": True}, 3612, 3613)
        self.assertEqual(len(read_open_worklist(self.connection)["items"]), 1)


if __name__ == "__main__":
    unittest.main()
