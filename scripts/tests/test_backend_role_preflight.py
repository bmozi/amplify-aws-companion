"""Synthetic AWS responses test the read-only CDK role-chain inventory."""

import importlib.util
from pathlib import Path
import unittest


path = Path(__file__).resolve().parents[1] / "backend-role-preflight.py"
spec = importlib.util.spec_from_file_location("backend_role_preflight", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ACCOUNT = "123456789012"
ROLES = {name: f"synthetic-{name}-role" for name in module.BOOTSTRAP_ROLE_IDS}


def responses(*, account=ACCOUNT, arn=None, denied_role=None,
              truncated_role=None, stack_role=None, bad_resource=None):
    arn = arn or f"arn:aws:sts::{ACCOUNT}:assumed-role/lab-deployer/session"
    calls = []

    def call(service, operation, *args, profile, region):
        calls.append((service, operation, args, profile, region))
        if (service, operation) == ("sts", "get-caller-identity"):
            return {"Account": account, "Arn": arn}
        if (service, operation) == ("cloudformation", "describe-stack-resource"):
            logical = args[-1]
            return {"StackResourceDetail": {
                "LogicalResourceId": logical, "ResourceType": "AWS::IAM::Role",
                "PhysicalResourceId": "bad/physical/id" if logical == bad_resource else ROLES[logical],
                "StackId": f"arn:aws:cloudformation:us-east-2:{ACCOUNT}:stack/CDKToolkit/id"}}
        if (service, operation) == ("cloudformation", "describe-stacks"):
            name = args[-1]
            return {"Stacks": [{"StackName": name,
                "StackId": f"arn:aws:cloudformation:us-east-2:{ACCOUNT}:stack/{name}/id",
                "StackStatus": "UPDATE_COMPLETE", "RoleARN": stack_role}]}
        if (service, operation) == ("iam", "get-role"):
            name = args[-1]
            if name == denied_role:
                return {"error": "access_denied"}
            return {"Role": {"Arn": f"arn:aws:iam::{ACCOUNT}:role/{name}",
                "RoleId": "synthetic", "AssumeRolePolicyDocument": {"Statement": []}}}
        if (service, operation) == ("iam", "list-attached-role-policies"):
            name = args[-1]
            return {"AttachedPolicies": (
                [{"PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess",
                  "PolicyName": "AdministratorAccess"}]
                if name == ROLES["CloudFormationExecutionRole"] else []),
                "IsTruncated": name == truncated_role}
        if (service, operation) == ("iam", "list-role-policies"):
            return {"PolicyNames": []}
        if (service, operation) == ("iam", "get-policy"):
            return {"Policy": {"DefaultVersionId": "v1"}}
        if (service, operation) == ("iam", "get-policy-version"):
            return {"PolicyVersion": {"Document": {"Statement": []}}}
        raise AssertionError((service, operation, args))

    return call, calls


class BackendRolePreflightTests(unittest.TestCase):
    def test_malformed_policy_is_not_accepted_as_evidence(self):
        for value in ({}, "{}", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.document(value)

    def test_wrong_account_stops_before_cloudformation(self):
        call, calls = responses(account="000000000000")
        result = module.inspect(ACCOUNT, profile="example", call=call)
        self.assertEqual([item[1] for item in calls], ["get-caller-identity"])
        self.assertIn("Wrong account; no further AWS calls made", result["review_required"])

    def test_all_five_roles_and_documents_are_collected(self):
        call, calls = responses()
        result = module.inspect(ACCOUNT, profile="example", call=call)
        for logical in module.BOOTSTRAP_ROLE_IDS:
            self.assertEqual(result["checks"]["bootstrap_" + logical]["arn"],
                             f"arn:aws:iam::{ACCOUNT}:role/{ROLES[logical]}")
        self.assertEqual(result["checks"]["bootstrap_CloudFormationExecutionRole_attached_0_version"]["version"], "v1")
        self.assertIn("bootstrap_CloudFormationExecutionRole: AdministratorAccess attached",
                      result["review_required"])
        self.assertTrue(all(item[3] == "example" for item in calls))

    def test_denied_role_read_is_unknown_and_other_roles_continue(self):
        name = ROLES["FilePublishingRole"]
        call, _ = responses(denied_role=name)
        result = module.inspect(ACCOUNT, call=call)
        self.assertIn("bootstrap_FilePublishingRole: read unavailable", result["review_required"])
        self.assertIn("bootstrap_ImagePublishingRole", result["checks"])

    def test_partial_policy_list_is_not_treated_as_complete(self):
        call, _ = responses(truncated_role=ROLES["CloudFormationExecutionRole"])
        result = module.inspect(ACCOUNT, call=call)
        self.assertIn("bootstrap_CloudFormationExecutionRole: attached-policy inventory incomplete",
                      result["review_required"])
        self.assertNotIn("bootstrap_CloudFormationExecutionRole_attached", result["checks"])

    def test_bad_physical_role_id_does_not_cause_iam_read(self):
        call, calls = responses(bad_resource="FilePublishingRole")
        result = module.inspect(ACCOUNT, call=call)
        self.assertIn("bootstrap_FilePublishingRole: resource identity unexpected; IAM read skipped",
                      result["review_required"])
        self.assertNotIn(ROLES["FilePublishingRole"],
                         [item[2][-1] for item in calls if item[1] == "get-role"])

    def test_root_is_reported_but_read_only_inventory_continues(self):
        call, _ = responses(arn=f"arn:aws:iam::{ACCOUNT}:root")
        result = module.inspect(ACCOUNT, call=call)
        self.assertIn("Caller is not an assumed-role session; no deployment", result["review_required"])
        self.assertIn("bootstrap_CloudFormationExecutionRole", result["checks"])

    def test_target_stack_role_matches_discovered_execution_role(self):
        role_arn = f"arn:aws:iam::{ACCOUNT}:role/{ROLES['CloudFormationExecutionRole']}"
        call, _ = responses(stack_role=role_arn)
        result = module.inspect(ACCOUNT, stack_name="AmplifyBackend", call=call)
        self.assertEqual(result["checks"]["target_stack"]["bootstrap_role_match"],
                         ["CloudFormationExecutionRole"])

    def test_foreign_stack_role_is_flagged_without_iam_read(self):
        call, calls = responses(stack_role="arn:aws:iam::000000000000:role/foreign")
        result = module.inspect(ACCOUNT, stack_name="AmplifyBackend", call=call)
        self.assertIn("Target stack service role is outside expected account", result["review_required"])
        self.assertNotIn("foreign", [item[2][-1] for item in calls if item[1] == "get-role"])


if __name__ == "__main__":
    unittest.main()
