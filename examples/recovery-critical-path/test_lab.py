import unittest
from dataclasses import replace

from lab import Evidence, Step, evaluate, plan, schedule


class RecoveryCriticalPathTests(unittest.TestCase):
    def setUp(self):
        self.evidence = Evidence(confirmation_inventory_complete=True, copy_complete=True,
                                 destination_key_usable=True, old_writer_fenced=True,
                                 customer_check_passed=True)

    def test_unset_claims_hold_the_plan(self):
        answer = evaluate(plan(2, 3), Evidence())
        self.assertEqual(answer['decision'], 'NO_GO')
        self.assertIn('confirmation inventory completeness is not established', answer['blockers'])
        self.assertEqual(len(answer['blockers']), 5)

    def test_warming_only_workers_does_not_shorten_data_critical_path(self):
        pilot = evaluate(plan(), self.evidence)
        warm = evaluate(plan(worker_minutes=2), self.evidence)
        self.assertEqual((pilot["projected_customer_minute"], warm["projected_customer_minute"]), (25, 25))
        self.assertEqual(pilot["decision"], "NO_GO")
        self.assertIn("reconcile_confirmations", warm["critical_chain"])

    def test_both_paths_need_improvement_for_exact_target(self):
        self.assertEqual(evaluate(plan(restore_minutes=3), self.evidence)["projected_customer_minute"], 23)
        answer = evaluate(plan(worker_minutes=2, restore_minutes=3), self.evidence)
        self.assertEqual(answer["projected_customer_minute"], 20)
        self.assertEqual(answer["decision"], "PLAN_FITS_ASSUMPTIONS")

    def test_fast_schedule_does_not_replace_destination_key_receipt(self):
        answer = evaluate(plan(2, 3), replace(self.evidence, destination_key_usable=False))
        self.assertEqual(answer["projected_customer_minute"], 20)
        self.assertEqual(answer["decision"], "NO_GO")
        self.assertIn("destination recovery role", answer["blockers"][0])

    def test_missing_or_unexpected_confirmation_blocks_reopening(self):
        missing = evaluate(plan(2, 3), replace(self.evidence, journal=()))
        unexpected = evaluate(plan(2, 3), replace(self.evidence, journal=(("B111", 2300), ("B999", 900))))
        self.assertIn("B111", " ".join(missing["blockers"]))
        self.assertIn("B999", " ".join(unexpected["blockers"]))

    def test_same_ids_with_wrong_amount_or_conflicting_sources_block_reopening(self):
        wrong = evaluate(plan(2, 3), replace(self.evidence, candidate=(("B110", 1300),)))
        conflict = evaluate(plan(2, 3), replace(
            self.evidence, candidate=(("B110", 1200), ("B111", 2500))))
        self.assertEqual(wrong["decision"], "NO_GO")
        self.assertIn("changed=['B110']", " ".join(wrong["blockers"]))
        self.assertEqual(conflict["decision"], "NO_GO")
        self.assertIn("source_conflicts=['B111']", " ".join(conflict["blockers"]))

    def test_duplicate_or_malformed_receipts_cannot_become_a_green_plan(self):
        cases = (
            replace(self.evidence, candidate=(("B110", 1200), ("B110", 1200))),
            replace(self.evidence, journal=(("B111", True),)),
        )
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                evaluate(plan(2, 3), case)

    def test_capacity_old_writer_and_customer_check_are_independent(self):
        changes = (
            replace(self.evidence, capacity_per_minute=79),
            replace(self.evidence, old_writer_fenced=False),
            replace(self.evidence, customer_check_passed=False),
        )
        for case in changes:
            with self.subTest(case=case):
                self.assertEqual(evaluate(plan(2, 3), case)["decision"], "NO_GO")

    def test_unknown_evidence_and_invalid_capacity_do_not_pass(self):
        for field in ('confirmation_inventory_complete', 'copy_complete', 'destination_key_usable', 'old_writer_fenced', 'customer_check_passed'):
            for value in ('unknown', None, 1):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    evaluate(plan(2, 3), replace(self.evidence, **{field: value}))
        for field, value in (('capacity_per_minute', True), ('capacity_per_minute', float('nan')),
                             ('demand_per_minute', 80.5)):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                evaluate(plan(2, 3), replace(self.evidence, **{field: value}))
        with self.assertRaises(ValueError):
            evaluate(plan(2, 3), self.evidence, True)

    def test_matching_empty_or_partial_inventory_does_not_prove_completeness(self):
        for rows in ((), (("B110", 1200),)):
            evidence = replace(self.evidence, confirmed=rows, candidate=rows, journal=(),
                               confirmation_inventory_complete=False)
            answer = evaluate(plan(2, 3), evidence)
            self.assertEqual(answer['decision'], 'NO_GO')
            self.assertIn('confirmation inventory completeness is not established', answer['blockers'])

    def test_dependency_omission_can_make_an_unsafe_plan_look_early(self):
        good = plan(worker_minutes=2, restore_minutes=8)
        bad = tuple(replace(s, after=("prove_capacity", "fence_old_writer"))
                    if s.name == "customer_read_and_write" else s for s in good)
        self.assertEqual(evaluate(good, self.evidence)["projected_customer_minute"], 25)
        self.assertEqual(evaluate(bad, self.evidence)["projected_customer_minute"], 13)
        self.assertNotIn("reconcile_confirmations", evaluate(bad, self.evidence)["critical_chain"])

    def test_invalid_dependency_graph_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, "invalid dependency"):
            schedule((Step("a", 1, ("missing",)),))
        with self.assertRaisesRegex(ValueError, "cycle"):
            schedule((Step("a", 1, ("b",)), Step("b", 1, ("a",))))
        with self.assertRaisesRegex(ValueError, "distinct"):
            schedule((Step("a", 1), Step("a", 2)))


if __name__ == "__main__":
    unittest.main()
