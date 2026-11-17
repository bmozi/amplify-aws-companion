import copy
import json
from pathlib import Path
import unittest

from impact import FOUNDATION_QUESTIONS, review_foundations, worklist

CASES = json.loads(Path(__file__).with_name("cases.json").read_text())


class ChangedPromiseTests(unittest.TestCase):
    def test_restore_traces_external_effect_and_neighbor_preservation(self):
        rows = worklist(CASES["shop-restore"])
        by_id = {row["decision_id"]: row for row in rows}
        self.assertIn("workflow", by_id["outside_effect"]["path_from_change"])
        self.assertIn("other_shop", by_id)
        self.assertIn("photos", by_id)
        self.assertIn("cost", by_id)
        self.assertIn("customer_route", by_id)

    def test_two_reviewers_reaches_old_link_and_duplicate_event(self):
        ids = {row["decision_id"] for row in worklist(CASES["school-two-reviewers"])}
        self.assertTrue({"identity", "retry", "direct_link", "audit"} <= ids)

    def test_tenant_burst_reaches_shared_bottleneck_and_per_tenant_result(self):
        ids = {row["decision_id"] for row in worklist(CASES["tenant-burst"])}
        self.assertTrue({"workers", "database", "queue", "observability", "cost", "change_rollout"} <= ids)

    def test_every_case_maps_all_seven_shared_questions_to_reachable_decisions(self):
        for name, case in CASES.items():
            with self.subTest(case=name):
                rows = worklist(case)
                mapped = review_foundations(case, rows)
                self.assertEqual([row["foundation"] for row in mapped], list(FOUNDATION_QUESTIONS))

    def test_orphan_link_fails_instead_of_silently_dropping_question(self):
        case = copy.deepcopy(CASES["shop-restore"])
        case["nodes"]["workflow"]["leads_to"].remove("outside_effect")
        with self.assertRaisesRegex(ValueError, "reachable"):
            worklist(case)

    def test_graph_misses_deleted_concept_but_separate_foundation_map_catches_it(self):
        case = copy.deepcopy(CASES["shop-restore"])
        case["nodes"]["workflow"]["leads_to"].remove("outside_effect")
        del case["nodes"]["outside_effect"]
        rows = worklist(case)
        ids = {row["decision_id"] for row in rows}
        self.assertNotIn("outside_effect", ids)
        with self.assertRaisesRegex(ValueError, "foundation work names a missing"):
            review_foundations(case, rows)

    def test_missing_foundation_question_is_rejected(self):
        case = copy.deepcopy(CASES["tenant-burst"])
        del case["foundation_review"]["delivery"]
        with self.assertRaisesRegex(ValueError, "exactly the seven"):
            review_foundations(case, worklist(case))

    def test_passing_mappings_still_cannot_check_semantic_truth(self):
        case = copy.deepcopy(CASES["shop-restore"])
        case["nodes"]["workflow"]["leads_to"].remove("outside_effect")
        del case["nodes"]["outside_effect"]
        case["foundation_review"]["work"] = ["workflow"]
        case["foundation_review"]["recovery"] = ["runbook"]
        # The machine sees seven nonempty mappings, yet no longer asks about
        # the technician scheduler's uncertain effect.
        self.assertEqual(len(review_foundations(case, worklist(case))), 7)


if __name__ == "__main__":
    unittest.main()
