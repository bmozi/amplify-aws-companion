"""Negative controls for the read-only publisher account snapshot."""

import importlib.util
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess
from urllib.parse import quote


SOURCE = Path(__file__).resolve().parents[1] / "publisher-account-preflight.py"
spec = importlib.util.spec_from_file_location("publisher_account_preflight", SOURCE)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)
ACCOUNT = "123456789012"
APP = "dexample123"
BRANCH = "lab"


def fixture(service, operation, *args, profile=None, region=None):
    if (service, operation) == ("sts", "get-caller-identity"):
        return {"Account": ACCOUNT, "Arn": f"arn:aws:sts::{ACCOUNT}:assumed-role/ReadOnly/session"}
    if (service, operation) == ("freetier", "get-account-plan-state"):
        return {"accountId": ACCOUNT, "accountPlanType": "FREE", "accountPlanStatus": "ACTIVE",
                "accountPlanRemainingCredits": {"amount": 150, "unit": "USD"},
                "accountPlanExpirationDate": "2099-01-01T00:00:00Z"}
    if (service, operation) == ("billing", "get-credits"):
        return {"credits": [{"accountId": ACCOUNT, "creditId": "42", "creditStatus": "ENABLED",
                             "remainingAmount": {"currencyCode": "USD", "currencyAmount": "125.00"},
                             "applicableProductNames": ["AWS Amplify"], "endDate": 4070908800}]}
    if (service, operation) == ("amplify", "get-app"):
        return {"app": {"appId": APP,
                        "appArn": f"arn:aws:amplify:us-east-2:{ACCOUNT}:apps/{APP}",
                        "repository": None, "enableAutoBranchCreation": False}}
    if (service, operation) == ("amplify", "get-branch"):
        return {"branch": {"branchName": BRANCH,
                           "branchArn": f"arn:aws:amplify:us-east-2:{ACCOUNT}:apps/{APP}/branches/{BRANCH}",
                           "enableAutoBuild": False, "enablePullRequestPreview": False}}
    if (service, operation) == ("iam", "list-open-id-connect-providers"):
        return {"OpenIDConnectProviderList": []}
    if (service, operation) == ("iam", "get-role"):
        return {"error": "not_found"}
    if (service, operation) == ("budgets", "describe-budget"):
        return {"Budget": {"BudgetName": "AWS-Learning-Monthly-Cost",
                           "BudgetLimit": {"Amount": "50", "Unit": "USD"},
                           "BudgetType": "COST", "TimeUnit": "MONTHLY",
                           "CalculatedSpend": {"ActualSpend": {"Amount": "10", "Unit": "USD"}},
                           "CostTypes": {"IncludeCredit": False, "IncludeRefund": False}}}
    raise AssertionError((service, operation, args, profile, region))


class PublisherAccountPreflightTests(unittest.TestCase):
    def test_expired_cli_session_is_reported_as_unavailable_credentials(self):
        expired = CompletedProcess([], 255, "", "aws: [ERROR]: Your session has expired. Please reauthenticate using 'aws login'.")
        with patch.object(preflight.subprocess, "run", return_value=expired):
            self.assertEqual(preflight.aws_json("sts", "get-caller-identity", profile="wgu"),
                             {"error": "credentials_unavailable"})

    def test_complete_read_only_snapshot_is_still_not_deployment_approval(self):
        calls = []

        def call(*args, **kwargs):
            calls.append((args[0], args[1], kwargs["region"]))
            return fixture(*args, **kwargs)

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        self.assertEqual(set(report["checks"]), {"identity", "free_plan", "credit_terms", "app", "branch",
                                                 "github_provider", "publisher_role", "budget"})
        self.assertEqual(calls[1], ("freetier", "get-account-plan-state", "us-east-1"))
        self.assertEqual(calls[2], ("billing", "get-credits", "us-east-1"))
        self.assertEqual(calls[-1], ("budgets", "describe-budget", "us-east-1"))
        self.assertIn("publisher_role: not_found", report["review_required"])
        self.assertTrue(any("full run estimate" in reason for reason in report["review_required"]))
        self.assertTrue(any("applicable products" in reason for reason in report["review_required"]))

    def test_credit_terms_query_is_account_scoped_and_within_api_date_window(self):
        from datetime import datetime, timezone
        seen = []

        def call(service, operation, *args, **kwargs):
            if (service, operation) == ("billing", "get-credits"):
                seen.append((args, kwargs["region"]))
            return fixture(service, operation, *args, **kwargs)

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        arguments, region = seen[0]
        self.assertEqual(region, "us-east-1")
        self.assertEqual(arguments[:2], ("--account-id", ACCOUNT))
        self.assertEqual(arguments[-1], "--no-payer-account-flag")
        age = datetime.now(timezone.utc).timestamp() - int(arguments[3])
        self.assertGreater(age, 363 * 86400)
        self.assertLess(age, 365 * 86400)
        self.assertEqual(report["checks"]["credit_terms"]["credits"][0]["creditId"], "42")

    def test_denied_or_mismatched_credit_terms_never_confirm_eligibility(self):
        def denied(service, operation, *args, **kwargs):
            if (service, operation) == ("billing", "get-credits"):
                return {"error": "access_denied"}
            return fixture(service, operation, *args, **kwargs)

        denied_report = preflight.inspect(ACCOUNT, APP, BRANCH, call=denied)
        self.assertEqual(denied_report["checks"]["credit_terms"], {"error": "access_denied"})
        self.assertIn("credit_terms: access_denied", denied_report["review_required"])

        def mismatched(service, operation, *args, **kwargs):
            if (service, operation) == ("billing", "get-credits"):
                return {"credits": [{"accountId": "999999999999", "creditId": "42"}]}
            return fixture(service, operation, *args, **kwargs)

        mismatch_report = preflight.inspect(ACCOUNT, APP, BRANCH, call=mismatched)
        self.assertEqual(mismatch_report["checks"]["credit_terms"], {"error": "credit_account_mismatch"})
        self.assertTrue(any("different or missing account" in reason for reason in mismatch_report["review_required"]))

        def empty(service, operation, *args, **kwargs):
            if (service, operation) == ("billing", "get-credits"):
                return {"credits": []}
            return fixture(service, operation, *args, **kwargs)

        empty_report = preflight.inspect(ACCOUNT, APP, BRANCH, call=empty)
        self.assertEqual(empty_report["checks"]["credit_terms"]["credits"], [])
        self.assertTrue(any("do not infer service eligibility" in reason for reason in empty_report["review_required"]))

    def test_wrong_account_stops_before_plan_or_app_queries(self):
        calls = []

        def call(service, operation, *args, **kwargs):
            calls.append((service, operation))
            return {"Account": "999999999999", "Arn": "arn:aws:iam::999999999999:root"}

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        self.assertEqual(calls, [("sts", "get-caller-identity")])
        self.assertIn("Wrong account; no further AWS calls made", report["review_required"])

    def test_denied_provider_is_unknown_not_absent(self):
        def call(service, operation, *args, **kwargs):
            if (service, operation) == ("iam", "list-open-id-connect-providers"):
                return {"error": "access_denied"}
            return fixture(service, operation, *args, **kwargs)

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        self.assertEqual(report["checks"]["github_provider"], {"error": "access_denied"})
        self.assertIn("github_provider: access_denied", report["review_required"])

    def test_connected_app_and_low_credit_are_flagged(self):
        def call(service, operation, *args, **kwargs):
            value = fixture(service, operation, *args, **kwargs)
            if (service, operation) == ("freetier", "get-account-plan-state"):
                value["accountPlanRemainingCredits"]["amount"] = 99
            if (service, operation) == ("amplify", "get-app"):
                value["app"]["repository"] = "https://github.com/example/repo"
            return value

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        self.assertTrue(any("USD 100" in reason for reason in report["review_required"]))
        self.assertTrue(any("repository connection" in reason for reason in report["review_required"]))

    def test_budget_room_holds_a_run_when_gross_spend_nears_limit(self):
        def call(service, operation, *args, **kwargs):
            value = fixture(service, operation, *args, **kwargs)
            if (service, operation) == ("budgets", "describe-budget"):
                value["Budget"]["CalculatedSpend"]["ActualSpend"]["Amount"] = "43.97"
            return value

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        self.assertEqual(report["checks"]["budget"]["gross_room_usd"], "6.03")
        self.assertEqual(report["checks"]["budget"]["room_after_usd_5_buffer_usd"], "1.03")
        self.assertTrue(any("hold new cloud runs" in reason for reason in report["review_required"]))
        self.assertTrue(any("can lag" in reason for reason in report["review_required"]))

    def test_missing_or_incomparable_budget_actual_never_becomes_headroom(self):
        for actual in (None, {"Amount": "10", "Unit": "EUR"}, {"Amount": "NaN", "Unit": "USD"}):
            with self.subTest(actual=actual):
                def call(service, operation, *args, **kwargs):
                    value = fixture(service, operation, *args, **kwargs)
                    if (service, operation) == ("budgets", "describe-budget"):
                        value["Budget"]["CalculatedSpend"]["ActualSpend"] = actual
                    return value

                report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
                self.assertNotIn("gross_room_usd", report["checks"]["budget"])
                self.assertTrue(any("unavailable; hold new cloud runs" in reason for reason in report["review_required"]))

    def test_malformed_budget_limit_is_a_hold_not_a_crash(self):
        def call(service, operation, *args, **kwargs):
            value = fixture(service, operation, *args, **kwargs)
            if (service, operation) == ("budgets", "describe-budget"):
                value["Budget"]["BudgetLimit"] = None
            return value

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        self.assertNotIn("gross_room_usd", report["checks"]["budget"])
        self.assertIn("Budget limit is unavailable", report["review_required"])
        self.assertTrue(any("unavailable; hold new cloud runs" in reason for reason in report["review_required"]))

    def test_existing_provider_is_inspected_for_audience(self):
        def call(service, operation, *args, **kwargs):
            if (service, operation) == ("iam", "list-open-id-connect-providers"):
                return {"OpenIDConnectProviderList": [{"Arn": f"arn:aws:iam::{ACCOUNT}:oidc-provider/token.actions.githubusercontent.com"}]}
            if (service, operation) == ("iam", "get-open-id-connect-provider"):
                return {"Url": "token.actions.githubusercontent.com", "ClientIDList": ["wrong-audience"]}
            return fixture(service, operation, *args, **kwargs)

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        self.assertTrue(report["checks"]["github_provider"]["exists"])
        self.assertTrue(any("URL/audience" in reason for reason in report["review_required"]))

    def test_existing_role_collects_trust_and_every_policy_source(self):
        document = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "amplify:GetJob", "Resource": "*"}]}
        managed_arn = f"arn:aws:iam::{ACCOUNT}:policy/ExtraPublisher"
        boundary_arn = f"arn:aws:iam::{ACCOUNT}:policy/PublisherBoundary"
        calls = []

        def call(service, operation, *args, **kwargs):
            calls.append((service, operation, args))
            if (service, operation) == ("iam", "get-role"):
                return {"Role": {"Arn": f"arn:aws:iam::{ACCOUNT}:role/AmplifyLabGitHubPublisher",
                                 "RoleId": "AROAEXAMPLE", "MaxSessionDuration": 3600,
                                 "AssumeRolePolicyDocument": quote(json.dumps(document)),
                                 "PermissionsBoundary": {"PermissionsBoundaryArn": boundary_arn}}}
            if (service, operation) == ("iam", "list-role-policies"):
                return {"PolicyNames": ["PublishOneBranch"]}
            if (service, operation) == ("iam", "get-role-policy"):
                return {"PolicyDocument": document}
            if (service, operation) == ("iam", "list-attached-role-policies"):
                return {"AttachedPolicies": [{"PolicyName": "ExtraPublisher", "PolicyArn": managed_arn}]}
            if (service, operation) == ("iam", "get-policy"):
                return {"Policy": {"DefaultVersionId": "v2"}}
            if (service, operation) == ("iam", "get-policy-version"):
                return {"PolicyVersion": {"Document": quote(json.dumps(document))}}
            return fixture(service, operation, *args, **kwargs)

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        checks = report["checks"]
        self.assertEqual(checks["publisher_role"]["trust_document"], document)
        self.assertEqual(checks["publisher_inline_PublishOneBranch"], document)
        self.assertEqual(checks["publisher_managed_0_version"]["document"], document)
        self.assertEqual(checks["publisher_boundary_version"]["document"], document)
        self.assertEqual(sum(operation == "get-policy-version" for _, operation, _ in calls), 2)
        self.assertTrue(any("other applicable controls" in reason for reason in report["review_required"]))

    def test_denied_policy_inventory_is_unknown_not_empty(self):
        def call(service, operation, *args, **kwargs):
            if (service, operation) == ("iam", "get-role"):
                return {"Role": {"Arn": f"arn:aws:iam::{ACCOUNT}:role/AmplifyLabGitHubPublisher",
                                 "AssumeRolePolicyDocument": {"Statement": []}}}
            if (service, operation) in {("iam", "list-role-policies"), ("iam", "list-attached-role-policies")}:
                return {"error": "access_denied"}
            return fixture(service, operation, *args, **kwargs)

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        self.assertIn("publisher_inline_names: access_denied", report["review_required"])
        self.assertIn("publisher_attached_names: access_denied", report["review_required"])
        self.assertNotIn("publisher_inline_names", {name for name, value in report["checks"].items() if value == []})

    def test_truncated_inventory_is_refused(self):
        def call(service, operation, *args, **kwargs):
            if (service, operation) == ("iam", "get-role"):
                return {"Role": {"AssumeRolePolicyDocument": {"Statement": []}}}
            if (service, operation) == ("iam", "list-role-policies"):
                return {"PolicyNames": ["One"], "IsTruncated": True}
            if (service, operation) == ("iam", "list-attached-role-policies"):
                return {"AttachedPolicies": [], "NextToken": "more"}
            return fixture(service, operation, *args, **kwargs)

        report = preflight.inspect(ACCOUNT, APP, BRANCH, call=call)
        self.assertIn("Publisher inline-policy inventory is incomplete", report["review_required"])
        self.assertIn("Publisher attached-policy inventory is incomplete", report["review_required"])
        self.assertNotIn("publisher_inline_One", report["checks"])

    def test_saved_security_receipt_is_owner_only(self):
        with TemporaryDirectory() as directory:
            args = ["publisher-account-preflight.py", "--account-id", ACCOUNT,
                    "--app-id", APP, "--branch", BRANCH, "--output-dir", directory]
            fake = {"checks": {"identity": {"account_id": ACCOUNT},
                               "publisher_role": {"trust_document": {"Statement": []}}},
                    "review_required": []}
            with patch.object(sys, "argv", args), patch.object(preflight, "inspect", return_value=fake):
                self.assertEqual(preflight.main(), 0)
            saved = list(Path(directory).glob("*-read-only.json"))
            self.assertEqual(len(saved), 1)
            self.assertEqual(os.stat(saved[0]).st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(saved[0].read_text()), fake)


if __name__ == "__main__":
    unittest.main()
