import unittest

from schedule_diagnostic import CASES, classify, quiet_queue_shortcut


class ScheduleDiagnosticTests(unittest.TestCase):
    def test_authored_cases_have_narrow_outcomes(self):
        for case in CASES:
            with self.subTest(case=case["name"]):
                self.assertEqual(classify(case), case["expected"])

    def test_quiet_failure_queues_do_not_prove_completion(self):
        case = next(case for case in CASES if case["name"] == "quiet_queues_unknown_work")
        self.assertEqual(quiet_queue_shortcut(case), "all_clear")
        self.assertEqual(classify(case), "insufficient_evidence")

    def test_later_base_record_changes_observation(self):
        clear = next(case for case in CASES if case["name"] == "observed_clear_pass")
        self.assertEqual(classify(clear), "clear_at_observation")
        self.assertEqual(classify({**clear, "due_base_records": 1}), "reconcile_base_records")

    def test_page_cap_never_becomes_clear(self):
        clear = next(case for case in CASES if case["name"] == "observed_clear_pass")
        self.assertEqual(classify({**clear, "page_limit_reached": True}), "unfinished_backlog")

    def test_both_failure_records_need_both_investigations(self):
        case = next(case for case in CASES if case["name"] == "both_failure_records")
        self.assertEqual(classify(case), "investigate_both_paths")


if __name__ == "__main__":
    unittest.main()
