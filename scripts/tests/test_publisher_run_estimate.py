"""Offline checks for the publisher's reviewed run record."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import textwrap
import unittest
from unittest.mock import patch
from zipfile import ZipFile
import hashlib


ROOT = Path(__file__).resolve().parents[2]
source = ROOT / "scripts/publisher-run-estimate.py"
spec = importlib.util.spec_from_file_location("publisher_run_estimate", source)
estimate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(estimate)
template = json.loads((ROOT / "examples/costs/publisher-run-estimate.json").read_text())


class RunEstimateTests(unittest.TestCase):
    APP_TREE_SHA = "a" * 40
    OUTPUTS_SHA = "c" * 64

    def setUp(self):
        self.now = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)
        self.record = deepcopy(template)
        self.record.update({
            "review_status": "reviewed", "account_id": "123456789012",
            "reviewed_by": "Lab owner", "reviewed_at": (self.now - timedelta(days=1)).isoformat(),
            "rates_checked_at": (self.now - timedelta(days=1)).isoformat(),
            "planned_end": (self.now + timedelta(days=14)).isoformat(),
            "existing_resources_reviewed": True, "github_actions_reviewed": True,
            "app_tree_sha": self.APP_TREE_SHA,
            "amplify_outputs_sha256": self.OUTPUTS_SHA,
        })
        self.record["active_run_review"].update({
            "review_status": "reviewed", "checked_at": self.now.isoformat(),
            "other_active_runs": 0, "basis": "Synthetic active-run ledger review",
        })
        self.record["credit_terms"].update({
            "review_status": "reviewed",
            "checked_at": (self.now - timedelta(days=1)).isoformat(),
            "owner_receipt_sha256": "e" * 64,
            "applicability": {name: "eligible" for name in estimate.CREDIT_CHARGES},
        })
        self.record["audience"]["review_status"] = "reviewed"
        self.record["lifecycle_review"].update({
            "review_status": "reviewed",
            "owner": "Lab owner",
            "stop_new_publication": "Set this repository's publish flag false and inspect active jobs",
            "hosting_disposition": "remove_and_verify",
            "backend_disposition": "remove_and_verify",
            "resource_verification": "Inspect exact app, branch and backend resource inventory after cleanup",
            "billing_recheck_at": (self.now + timedelta(days=21)).isoformat(),
        })
        # A synthetic reviewed estimate for arithmetic tests, not a quote.
        for component in self.record["backend_components"].values():
            component["review_status"] = "reviewed"
            component["basis"] = "Synthetic zero usage, for validator arithmetic only"
        self.record["backend_components"]["appsync"]["estimated_usd"] = "0.01"
        self.record["backend_components"]["appsync"]["basis"] = "Synthetic priced GraphQL operation allowance"
        next(row for row in self.record["line_items"]
             if row["meter"] == "backend_and_logs_usd")["unit_price_usd"] = "0.01"

    def check(self):
        return estimate.assess(self.record, account_id="123456789012",
                               app_id="d000000000000", branch="lab",
                               scenario="static_5gb_30d", app_tree_sha=self.APP_TREE_SHA,
                               outputs_sha256=self.OUTPUTS_SHA,
                               built_archive_bytes=0, now=self.now)

    def test_template_is_deliberately_unreviewed(self):
        self.record["review_status"] = "review_needed"
        with self.assertRaisesRegex(ValueError, "not reviewed"):
            self.check()
        self.record["review_status"] = "reviewed"
        self.record["schema_version"] = 5
        with self.assertRaisesRegex(ValueError, "not reviewed"):
            self.check()

    def test_smoke_record_is_separate_and_needs_its_own_review(self):
        smoke = json.loads((ROOT / "examples/costs/publisher-smoke-run-estimate.json").read_text())
        self.assertEqual(smoke["review_status"], "review_needed")
        self.assertEqual(smoke["scenario"], "static_smoke_100_visit_1d")
        self.assertEqual(smoke["audience"]["visits"], "100")
        transfer = next(row for row in smoke["line_items"]
                        if row["meter"] == "hosting_transfer_gb")
        self.assertEqual(transfer["quantity"], "0.15")
        with self.assertRaisesRegex(ValueError, "not reviewed"):
            estimate.assess(smoke, account_id="123456789012",
                            app_id="d000000000000", branch="lab",
                            scenario="static_smoke_100_visit_1d",
                            app_tree_sha=self.APP_TREE_SHA, outputs_sha256=self.OUTPUTS_SHA,
                            built_archive_bytes=0, now=self.now)

        # An arithmetic-only fixture proves the alternate path is possible to
        # validate; its invented backend amount is not a live run forecast.
        self.record["scenario"] = smoke["scenario"]
        self.record["audience"] = smoke["audience"]
        self.record["audience"]["review_status"] = "reviewed"
        self.record["planned_end"] = (self.now + timedelta(hours=18)).isoformat()
        self.record["line_items"] = smoke["line_items"]
        next(row for row in self.record["line_items"]
             if row["meter"] == "backend_and_logs_usd")["unit_price_usd"] = "0.01"
        result = estimate.assess(self.record, account_id="123456789012",
                                 app_id="d000000000000", branch="lab",
                                 scenario="static_smoke_100_visit_1d",
                                 app_tree_sha=self.APP_TREE_SHA, outputs_sha256=self.OUTPUTS_SHA,
                                 built_archive_bytes=0, now=self.now)
        self.assertEqual(result["base_usd"], "0.03273")
        self.assertEqual(result["estimated_run_usd"], "0.28273")
        with self.assertRaisesRegex(ValueError, "below the exact built archive"):
            estimate.assess(self.record, account_id="123456789012",
                            app_id="d000000000000", branch="lab",
                            scenario="static_smoke_100_visit_1d",
                            app_tree_sha=self.APP_TREE_SHA, outputs_sha256=self.OUTPUTS_SHA,
                            built_archive_bytes=1500001, now=self.now)
        with self.assertRaisesRegex(ValueError, "target mismatch: scenario"):
            self.check()
        self.record["planned_end"] = (self.now + timedelta(days=2)).isoformat()
        with self.assertRaisesRegex(ValueError, "within 24 hours"):
            estimate.assess(self.record, account_id="123456789012",
                            app_id="d000000000000", branch="lab",
                            scenario="static_smoke_100_visit_1d",
                            app_tree_sha=self.APP_TREE_SHA, outputs_sha256=self.OUTPUTS_SHA,
                            built_archive_bytes=0, now=self.now)
        self.record["planned_end"] = (self.now + timedelta(hours=18)).isoformat()
        self.record["audience"]["visits"] = "101"
        with self.assertRaisesRegex(ValueError, "Smoke scenario audience"):
            estimate.assess(self.record, account_id="123456789012",
                            app_id="d000000000000", branch="lab",
                            scenario="static_smoke_100_visit_1d",
                            app_tree_sha=self.APP_TREE_SHA, outputs_sha256=self.OUTPUTS_SHA,
                            built_archive_bytes=0, now=self.now)

    def test_credit_terms_require_fresh_receipt_and_complete_disposition(self):
        terms = self.record["credit_terms"]
        terms["review_status"] = "pending"
        with self.assertRaisesRegex(ValueError, "owner review"):
            self.check()
        terms["review_status"] = "reviewed"
        terms["owner_receipt_sha256"] = ""
        with self.assertRaisesRegex(ValueError, "receipt digest"):
            self.check()
        terms["owner_receipt_sha256"] = "e" * 64
        terms["checked_at"] = (self.now - timedelta(days=8)).isoformat()
        with self.assertRaisesRegex(ValueError, "older than seven days"):
            self.check()
        terms["checked_at"] = self.now.isoformat()
        del terms["applicability"]["network"]
        with self.assertRaisesRegex(ValueError, "every selected service family"):
            self.check()
        terms["applicability"]["network"] = "unknown"
        with self.assertRaisesRegex(ValueError, "unknown"):
            self.check()
        terms["applicability"]["network"] = "budgeted_without_credit"
        self.assertEqual(self.check()["estimated_run_usd"], "1.01023")

    def test_each_backend_component_needs_explicit_review(self):
        self.record["backend_components"]["dynamodb"]["review_status"] = "pending"
        with self.assertRaisesRegex(ValueError, "Backend component still needs review: dynamodb"):
            self.check()

    def test_hosting_transfer_must_match_the_reviewed_audience(self):
        self.record["audience"]["visits"] = "100"
        with self.assertRaisesRegex(ValueError, "Hosting transfer does not match"):
            self.check()
        self.record["audience"]["visits"] = "10000"
        self.record["audience"]["review_status"] = "pending"
        with self.assertRaisesRegex(ValueError, "audience still needs review"):
            self.check()

    def test_audience_needs_positive_whole_counts_and_backend_basis(self):
        self.record["audience"]["visits"] = "0.5"
        with self.assertRaisesRegex(ValueError, "positive whole numbers"):
            self.check()
        self.record["audience"]["visits"] = "10000"
        self.record["audience"]["backend_usage_basis"] = ""
        with self.assertRaisesRegex(ValueError, "backend usage basis"):
            self.check()

    def test_reviewed_estimate_is_calculated_from_all_meters(self):
        result = self.check()
        self.assertEqual(result["base_usd"], "0.76023")
        self.assertEqual(result["estimated_run_usd"], "1.01023")
        self.assertEqual(result["planned_end_epoch"],
                         str(int((self.now + timedelta(days=14)).timestamp())))

    def test_lifecycle_review_cannot_be_skipped(self):
        lifecycle = self.record["lifecycle_review"]
        lifecycle["review_status"] = "pending"
        with self.assertRaisesRegex(ValueError, "lifecycle still needs owner review"):
            self.check()
        lifecycle["review_status"] = "reviewed"
        lifecycle["owner"] = ""
        with self.assertRaisesRegex(ValueError, "needs owner"):
            self.check()
        lifecycle["owner"] = "Lab owner"
        lifecycle["stop_new_publication"] = ""
        with self.assertRaisesRegex(ValueError, "stop_new_publication"):
            self.check()
        lifecycle["stop_new_publication"] = "Set the publish flag false and inspect jobs"
        lifecycle["resource_verification"] = ""
        with self.assertRaisesRegex(ValueError, "resource_verification"):
            self.check()

    def test_lifecycle_disposition_and_later_billing_date_are_bounded(self):
        lifecycle = self.record["lifecycle_review"]
        lifecycle["hosting_disposition"] = "unknown"
        with self.assertRaisesRegex(ValueError, "hosting_disposition"):
            self.check()
        lifecycle["hosting_disposition"] = "remove_and_verify"
        lifecycle["backend_disposition"] = []
        with self.assertRaisesRegex(ValueError, "backend_disposition"):
            self.check()
        lifecycle["backend_disposition"] = "remove_and_verify"
        lifecycle["billing_recheck_at"] = self.record["planned_end"]
        with self.assertRaisesRegex(ValueError, "Billing recheck must follow cleanup"):
            self.check()
        lifecycle["billing_recheck_at"] = (self.now + timedelta(days=61)).isoformat()
        with self.assertRaisesRegex(ValueError, "within 45 days"):
            self.check()
        lifecycle["billing_recheck_at"] = (self.now + timedelta(days=21)).isoformat()
        self.assertEqual(self.check()["retained_cost_usd"], "0")

    def test_retention_requires_deadline_basis_and_cost_inside_total(self):
        lifecycle = self.record["lifecycle_review"]
        lifecycle["hosting_disposition"] = "retain_with_next_budget"
        with self.assertRaisesRegex(ValueError, "retained_until"):
            self.check()
        lifecycle["retained_until"] = (self.now + timedelta(days=45)).isoformat()
        with self.assertRaisesRegex(ValueError, "within 30 days"):
            self.check()
        lifecycle["retained_until"] = (self.now + timedelta(days=28)).isoformat()
        with self.assertRaisesRegex(ValueError, "positive pre-allowance"):
            self.check()
        lifecycle["retained_cost_usd"] = "0.10"
        with self.assertRaisesRegex(ValueError, "usage and price basis"):
            self.check()
        lifecycle["retained_cost_basis"] = "Synthetic two-week post-window Hosting and backend estimate"
        lifecycle["billing_recheck_at"] = (self.now + timedelta(days=35)).isoformat()
        self.record["contingency_usd"] = "0.20"
        with self.assertRaisesRegex(ValueError, "at least 25%"):
            self.check()
        self.record["contingency_usd"] = "0.30"
        result = self.check()
        self.assertEqual(result["retained_cost_usd"], "0.10")
        self.assertEqual(result["estimated_run_usd"], "1.16023")
        self.assertEqual(result["planned_end_epoch"],
                         str(int((self.now + timedelta(days=28)).timestamp())))

    def test_remove_disposition_rejects_retention_cost_or_date(self):
        lifecycle = self.record["lifecycle_review"]
        lifecycle["retained_cost_usd"] = "0.10"
        with self.assertRaisesRegex(ValueError, "Removed resources cannot carry"):
            self.check()
        lifecycle["retained_cost_usd"] = "0"
        lifecycle["retained_until"] = (self.now + timedelta(days=20)).isoformat()
        with self.assertRaisesRegex(ValueError, "Removed resources cannot carry"):
            self.check()

    def test_retention_is_not_outside_the_usd_five_ceiling(self):
        lifecycle = self.record["lifecycle_review"]
        lifecycle["backend_disposition"] = "retain_with_next_budget"
        lifecycle["retained_until"] = (self.now + timedelta(days=28)).isoformat()
        lifecycle["retained_cost_usd"] = "4"
        lifecycle["retained_cost_basis"] = "Synthetic bounded extra backend month"
        lifecycle["billing_recheck_at"] = (self.now + timedelta(days=35)).isoformat()
        self.record["contingency_usd"] = "1.20"
        with self.assertRaisesRegex(ValueError, "exceeds USD 5"):
            self.check()

    def test_wrong_target_or_scenario_stops(self):
        for key, value in (("account_id", "wrong"), ("app_id", "wrong"),
                           ("branch", "main"), ("scenario", "different")):
            with self.subTest(key=key):
                changed = self.record[key]
                self.record[key] = value
                with self.assertRaisesRegex(ValueError, "target mismatch"):
                    self.check()
                self.record[key] = changed

    def test_changed_app_tree_requires_fresh_review(self):
        self.record["app_tree_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "differs from the reviewed source"):
            self.check()
        self.record["app_tree_sha"] = ""
        with self.assertRaisesRegex(ValueError, "differs from the reviewed source"):
            self.check()
        self.record["app_tree_sha"] = self.APP_TREE_SHA
        with self.assertRaisesRegex(ValueError, "missing or malformed"):
            estimate.assess(self.record, account_id="123456789012",
                            app_id="d000000000000", branch="lab",
                            scenario="static_5gb_30d", app_tree_sha="invalid",
                            outputs_sha256=self.OUTPUTS_SHA, built_archive_bytes=0, now=self.now)

    def test_changed_browser_configuration_requires_fresh_review(self):
        self.record["amplify_outputs_sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "browser configuration differs"):
            self.check()
        self.record["amplify_outputs_sha256"] = self.OUTPUTS_SHA
        with self.assertRaisesRegex(ValueError, "fingerprint is missing or malformed"):
            estimate.assess(self.record, account_id="123456789012",
                            app_id="d000000000000", branch="lab",
                            scenario="static_5gb_30d", app_tree_sha=self.APP_TREE_SHA,
                            outputs_sha256="", built_archive_bytes=0, now=self.now)

    def test_archive_fingerprint_is_bound_to_exact_zip(self):
        with TemporaryDirectory() as directory:
            archive = Path(directory) / "frontend.zip"
            with ZipFile(archive, "w") as bundle:
                bundle.writestr("index.html", "synthetic")
                bundle.writestr("config.sha256", self.OUTPUTS_SHA + "\n")
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(estimate.built_outputs_digest(archive, digest), self.OUTPUTS_SHA)
            self.assertEqual(estimate.built_archive_raw_bytes(archive), 9 + 65)
            with self.assertRaisesRegex(ValueError, "differs"):
                estimate.built_outputs_digest(archive, "0" * 64)
            with ZipFile(archive, "a") as bundle:
                bundle.writestr("config.sha256", "d" * 64 + "\n")
            changed_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "no single"):
                estimate.built_outputs_digest(archive, changed_digest)
            with self.assertRaisesRegex(ValueError, "unique files"):
                estimate.built_archive_raw_bytes(archive)

    def test_actual_workflow_package_binds_prebuild_browser_config(self):
        live = ROOT / ".github/workflows/reusable-amplify-publish.yml"
        example = ROOT / "examples/github-workflows/reusable-amplify-publish.yml"
        if live.is_file():
            self.assertEqual(live.read_bytes(), example.read_bytes())
        workflow = (live if live.is_file() else example).read_text()
        package_step = workflow.split("      - name: Package the built site\n", 1)[1].split(
            "      - name: Save the frontend artifact", 1)[0]
        match = re.search(r"python3 - <<'PY'\n(.*?)\n          PY", package_step, re.DOTALL)
        self.assertIsNotNone(match)
        script = textwrap.dedent(match.group(1))
        with TemporaryDirectory() as directory:
            root = Path(directory) / "app/frontend-publisher"
            (root / "dist").mkdir(parents=True)
            (root / "dist/index.html").write_text("synthetic page")
            config = root / "amplify_outputs.json"
            config.write_text('{"data":{"url":"https://example.invalid"}}')
            config_digest = hashlib.sha256(config.read_bytes()).hexdigest()
            (root / ".browser-config.sha256").write_text(config_digest + "\n")
            output = Path(directory) / "github-output"
            output.touch()
            environment = dict(os.environ, SOURCE_COMMIT=self.APP_TREE_SHA,
                               WORKFLOW_RUN_ID="19", GITHUB_OUTPUT=str(output))
            subprocess.run([sys.executable, "-c", script], cwd=directory,
                           env=environment, check=True, capture_output=True, text=True)
            archive = Path(directory) / "frontend.zip"
            archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(estimate.built_outputs_digest(archive, archive_digest), config_digest)
            self.assertIn("archive_sha256=" + archive_digest, output.read_text())
            (root / ".browser-config.sha256").write_text("0" * 64 + "\n")
            stopped = subprocess.run([sys.executable, "-c", script], cwd=directory,
                                     env=environment, capture_output=True, text=True)
            self.assertNotEqual(stopped.returncode, 0)
            self.assertIn("changed during the build", stopped.stderr)

    def test_stale_rates_and_unreviewed_resources_stop(self):
        self.record["rates_checked_at"] = (self.now - timedelta(days=8)).isoformat()
        with self.assertRaisesRegex(ValueError, "older than seven days"):
            self.check()
        self.record["rates_checked_at"] = self.now.isoformat()
        self.record["existing_resources_reviewed"] = False
        with self.assertRaisesRegex(ValueError, "Existing resources"):
            self.check()

    def test_other_active_or_unreviewed_runs_stop(self):
        review = self.record["active_run_review"]
        review["review_status"] = "pending"
        with self.assertRaisesRegex(ValueError, "active runs need"):
            self.check()
        review["review_status"] = "reviewed"
        review["other_active_runs"] = 1
        with self.assertRaisesRegex(ValueError, "Another active"):
            self.check()
        review["other_active_runs"] = None
        with self.assertRaisesRegex(ValueError, "Another active"):
            self.check()
        review["other_active_runs"] = False
        with self.assertRaisesRegex(ValueError, "Another active"):
            self.check()
        review["other_active_runs"] = 0
        review["checked_at"] = (self.now - timedelta(hours=2)).isoformat()
        with self.assertRaisesRegex(ValueError, "older than one hour"):
            self.check()
        review["checked_at"] = self.now.isoformat()
        review["basis"] = ""
        with self.assertRaisesRegex(ValueError, "evidence basis"):
            self.check()

    def test_missing_meter_and_understated_contingency_stop(self):
        self.record["line_items"].pop()
        with self.assertRaisesRegex(ValueError, "Missing required meters"):
            self.check()
        self.record["line_items"] = deepcopy(template["line_items"])
        next(row for row in self.record["line_items"]
             if row["meter"] == "backend_and_logs_usd")["unit_price_usd"] = "0.01"
        self.record["contingency_usd"] = "0"
        with self.assertRaisesRegex(ValueError, "at least 25%"):
            self.check()

    def test_zero_or_incomplete_backend_review_stops(self):
        row = next(row for row in self.record["line_items"]
                   if row["meter"] == "backend_and_logs_usd")
        row["unit_price_usd"] = "0"
        with self.assertRaisesRegex(ValueError, "nonzero"):
            self.check()
        row["unit_price_usd"] = "0.01"
        self.record["backend_components"]["appsync"]["estimated_usd"] = "0"
        with self.assertRaisesRegex(ValueError, "do not add up"):
            self.check()
        self.record["backend_components"]["appsync"]["estimated_usd"] = "0.01"
        del self.record["backend_components"]["cloudwatch"]
        with self.assertRaisesRegex(ValueError, "must cover"):
            self.check()

    def test_large_run_and_invalid_number_stop(self):
        self.record["line_items"][1]["quantity"] = "40"
        self.record["audience"]["visits"] = "80000"
        self.record["contingency_usd"] = "2"
        with self.assertRaisesRegex(ValueError, "exceeds USD 5"):
            self.check()
        self.record["line_items"][1]["quantity"] = "NaN"
        with self.assertRaisesRegex(ValueError, "finite"):
            self.check()

    def test_cli_writes_only_calculated_handoff_values(self):
        with TemporaryDirectory() as directory:
            record = Path(directory) / "record.json"
            output = Path(directory) / "github-output"
            archive = Path(directory) / "frontend.zip"
            output.touch()
            record.write_text(json.dumps(self.record))
            with ZipFile(archive, "w") as bundle:
                bundle.writestr("index.html", "synthetic")
                bundle.writestr("config.sha256", self.OUTPUTS_SHA + "\n")
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            args = [str(source), str(record), "--account-id", "123456789012",
                    "--app-id", "d000000000000", "--branch", "lab",
                    "--scenario", "static_5gb_30d", "--app-tree-sha", self.APP_TREE_SHA,
                    "--archive", str(archive), "--archive-sha256", digest]
            with patch.object(sys, "argv", args), \
                 patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}), \
                 patch.object(estimate, "datetime") as clock:
                clock.now.return_value = self.now
                clock.fromisoformat.side_effect = datetime.fromisoformat
                self.assertEqual(estimate.main(), 0)
            self.assertEqual(output.read_text().splitlines(), [
                "estimated_run_usd=1.01023",
                f"planned_end_epoch={int((self.now + timedelta(days=14)).timestamp())}",
            ])


if __name__ == "__main__":
    unittest.main()
