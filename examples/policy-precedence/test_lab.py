import unittest

from lab import BULLETIN, decide, digest, discover, setup


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.db = setup()
        self.ranked = discover(self.db, "alice")

    def tearDown(self):
        self.db.close()

    def choice(self, kind="household", day="2026-10-02", receipt=True, candidates=None):
        return decide(self.db, "alice", kind, day, receipt,
                      self.ranked if candidates is None else candidates)

    def test_relevance_does_not_choose_policy(self):
        self.assertEqual(self.ranked[0]["id"], "general")
        self.assertEqual(self.choice(), {"status": "answer", "days": 60, "source": "bulletin"})
        self.assertEqual(self.choice(day="2026-09-30"), {"status": "answer", "days": 45, "source": "general"})

    def test_missing_fact_and_receipt_abstain(self):
        self.assertEqual(self.choice(day=None)["reason"], "missing_or_invalid_acceptance_date")
        self.assertEqual(self.choice(receipt=False)["reason"], "receipt_required")

    def test_commercial_exclusion_is_separate(self):
        self.assertEqual(self.choice(kind="commercial", receipt=False),
                         {"status": "excluded", "source": "exclusion"})

    def test_missing_or_revoked_bulletin_does_not_fall_back(self):
        without = [c for c in self.ranked if c["id"] != "bulletin"]
        self.assertEqual(self.choice(candidates=without)["reason"], "missing_applicable_source")
        self.db.execute("DELETE FROM grants WHERE actor='alice' AND document='bulletin'")
        self.assertEqual(self.choice()["reason"], "source_not_currently_authorized")

    def test_changed_source_or_approval_mapping_abstains(self):
        self.db.execute("UPDATE documents SET version=2,body=? WHERE id='bulletin'", (BULLETIN + " Revised.",))
        self.assertEqual(self.choice()["reason"], "source_or_rule_mapping_stale")
        self.db.execute("UPDATE approved_rules SET source_version=2,source_digest=? WHERE id='bulletin-rule'",
                        (digest(BULLETIN + " Revised."),))
        self.assertEqual(self.choice()["days"], 60)

    def test_equal_priority_conflict_abstains(self):
        self.db.execute("""INSERT INTO approved_rules VALUES
            ('conflict','shop-a','general',1,?,'household','2026-10-01',90,2,1)""", (digest("Household repair coverage is 45 days with a receipt."),))
        self.assertEqual(self.choice()["reason"], "conflicting_top_priority_rules")

    def test_wrong_actor_or_packet_cannot_select_policy(self):
        self.assertEqual(decide(self.db, "bob", "household", "2026-10-02", True, self.ranked)["reason"],
                         "no_approved_applicable_rule")
        self.assertEqual(decide(self.db, "unknown", "household", "2026-10-02", True, self.ranked)["status"], "deny")
        self.assertEqual(self.choice(candidates=[{"id": 5}])["reason"], "invalid_candidate_packet")


if __name__ == "__main__":
    unittest.main()
