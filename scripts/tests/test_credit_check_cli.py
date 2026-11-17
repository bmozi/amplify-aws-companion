"""Mocked CLI checks for the inspection-only credit-gate specimen; no AWS calls."""

from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
import importlib.util
from io import StringIO
import json
import os
import stat
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "credit-check.py"
spec = importlib.util.spec_from_file_location("credit_check", SOURCE)
credit_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(credit_check)
ACCOUNT = "123456789012"


class PublisherCreditGateTests(unittest.TestCase):
    def test_receipt_private_at_creation_under_permissive_umask(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / 'receipt.json'
            original = credit_check.os.fdopen
            def inspect_before_write(descriptor, *args):
                self.assertEqual(stat.S_IMODE(os.fstat(descriptor).st_mode), 0o600)
                return original(descriptor, *args)
            old = os.umask(0)
            try:
                with patch.object(credit_check.os, 'fdopen', side_effect=inspect_before_write):
                    credit_check.write_private_receipt(target, {'fixture': True})
            finally:
                os.umask(old)
            self.assertEqual(json.loads(target.read_text()), {'fixture': True})

    def test_existing_receipt_and_symlink_are_not_overwritten(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / 'original.json'
            target.write_text('retain original')
            link = Path(directory) / 'link.json'
            link.symlink_to(target)
            for path in (target, link):
                with self.assertRaises(FileExistsError):
                    credit_check.write_private_receipt(path, {'replacement': True})
                self.assertEqual(target.read_text(), 'retain original')

    def invoke(self, *, credits="150", returned_account=ACCOUNT):
        future = datetime.now(timezone.utc) + timedelta(days=40)
        end = datetime.now(timezone.utc) + timedelta(days=30)
        plan = {"accountId": returned_account, "accountPlanType": "FREE",
                "accountPlanStatus": "ACTIVE",
                "accountPlanRemainingCredits": {"amount": credits, "unit": "USD"},
                "accountPlanExpirationDate": future.isoformat()}
        commands = []

        def fake_call(command):
            commands.append(command)
            if command[1:3] == ["sts", "get-caller-identity"]:
                return json.dumps({"Account": ACCOUNT, "Arn": "arn:aws:sts::123456789012:assumed-role/Publisher/run"}).encode()
            if command[1:3] == ["freetier", "get-account-plan-state"]:
                return json.dumps(plan).encode()
            raise AssertionError(command)

        with TemporaryDirectory() as directory:
            args = [str(SOURCE), "--account-id", ACCOUNT, "--estimated-run-usd", "1",
                    "--reserve-usd", "100", "--run-limit-usd", "5",
                    "--planned-end-epoch", str(int(end.timestamp())),
                    "--output-dir", directory, "--quiet"]
            output = StringIO()
            with patch.object(sys, "argv", args), patch.object(credit_check.subprocess, "check_output", side_effect=fake_call), redirect_stdout(output):
                result = credit_check.main()
            receipts = list(Path(directory).glob("*-credits.json"))
            self.assertEqual(len(receipts), 1)
            private = json.loads(receipts[0].read_text())
            self.assertNotIn(credits, output.getvalue())
            self.assertTrue(all("--profile" not in command for command in commands))
            return result, output.getvalue(), private

    def test_no_profile_oidc_session_passes_only_with_reserve(self):
        code, output, private = self.invoke()
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), "Free-plan credit gate: within_credit_policy")
        self.assertEqual(private["summary"]["headroom_after_estimate_usd"], "49")

    def test_reserve_shortfall_stops_publication(self):
        code, output, private = self.invoke(credits="100")
        self.assertEqual(code, 2)
        self.assertEqual(output.strip(), "Free-plan credit gate: review_required")
        self.assertIn("Estimate would breach reserved credits", private["summary"]["reasons"])

    def test_plan_from_another_account_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Plan belongs to different account"):
            self.invoke(returned_account="999999999999")


if __name__ == "__main__":
    unittest.main()
