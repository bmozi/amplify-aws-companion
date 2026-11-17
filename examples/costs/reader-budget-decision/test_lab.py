"""Counterexamples for the reader's three independent cost questions."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("reader_budget_lab", Path(__file__).with_name("lab.py"))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.case = dict(run_estimate_usd="3", chosen_run_limit_usd="4",
                         credit_balance_usd="85", chosen_credit_reserve_usd="75",
                         gross_monthly_used_usd="46", gross_monthly_budget_usd="50",
                         chosen_budget_margin_usd="2", credit_applicability_checked=True,
                         usage_snapshot_current=True)

    def test_credits_can_pass_when_gross_headroom_fails(self):
        result = lab.assess(self.case)
        self.assertEqual(result["projected_credit_balance_usd"], "82")
        self.assertEqual(result["gross_headroom_after_run_and_margin_usd"], "-1")
        self.assertEqual(result["decision"], "hold")

    def test_individually_plausible_runs_do_not_reserve_shared_headroom(self):
        self.case.update(credit_balance_usd="80", gross_monthly_used_usd="40")
        self.assertEqual(lab.assess(self.case)["decision"], "review_candidate")
        self.case["run_estimate_usd"] = "6"  # combined forecast for two USD 3 runs
        self.case["chosen_run_limit_usd"] = "8"  # isolate credit-reserve failure
        result = lab.assess(self.case)
        self.assertIn("Projected credits fall below the chosen reserve", result["reasons"])

    def test_missing_or_stale_evidence_holds_even_with_favorable_arithmetic(self):
        self.case["credit_applicability_checked"] = False
        self.assertEqual(lab.assess(self.case)["decision"], "hold")
        self.case["credit_applicability_checked"] = True
        self.case["usage_snapshot_current"] = False
        self.assertEqual(lab.assess(self.case)["decision"], "hold")

    def test_both_missing_evidence_items_are_reported(self):
        self.case.update(credit_applicability_checked=False, usage_snapshot_current=False)
        result = lab.assess(self.case)
        self.assertEqual(result["decision"], "hold")
        self.assertEqual(result["reasons"], ["Credit applicability is unverified",
                                             "Gross usage snapshot is unverified or stale"])

    def test_invalid_money_cannot_become_a_safe_decision(self):
        self.case["run_estimate_usd"] = "NaN"
        with self.assertRaises(ValueError):
            lab.assess(self.case)

    def test_command_reads_the_changed_case_file(self):
        self.case.update(name="changed", gross_monthly_used_usd="40")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cases.json"
            path.write_text(json.dumps([self.case]), encoding="utf-8")
            run = subprocess.run([sys.executable, str(Path(__file__).with_name("lab.py")), str(path)],
                                 check=True, text=True, capture_output=True)
        result = json.loads(run.stdout)
        self.assertEqual(result["case"], "changed")
        self.assertEqual(result["decision"], "review_candidate")


if __name__ == "__main__":
    unittest.main()
