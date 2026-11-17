import unittest

from lab import ALLOWED_ACCOUNT, ALLOWED_REGION, fixtures, plan_change, run_packet


def event(**overrides):
    value = {"event_id": "event-test", "account": ALLOWED_ACCOUNT,
             "region": ALLOWED_REGION, "resource_id": "node-lab-01",
             "evaluation_age_minutes": 1, "max_age_minutes": 10,
             "compliance": "NON_COMPLIANT", "observed_revision": "rev-18",
             "desired_revision": "rev-18", "deployment_active": False,
             "previous_attempt_unknown": False, "attempts": 0, "max_attempts": 2,
             "error_count": 0, "max_errors": 1, "active_targets": 0,
             "max_concurrent_targets": 1, "approval_required": False,
             "approval_present": False, "desired_state_owner": "STATE_MANAGER",
             "target_kind": "MANAGED_NODE", "ssm_managed": True,
             "agent_online": True}
    value.update(overrides)
    return value


class ConfigurationChangeControlTests(unittest.TestCase):
    def test_packet_selects_owner_and_stops_stale_wrong_account_and_revision(self):
        self.assertEqual(run_packet()["change_plan"], [
            "UPDATE_TEMPLATE_AND_REFRESH", "STOP_STALE", "STOP_SCOPE",
            "STOP_REVISION", "UPDATE_TEMPLATE_AND_REFRESH", "INSPECT_PRIOR_PLAN"])

    def test_managed_node_uses_state_manager_only_when_online(self):
        e = event()
        self.assertEqual(plan_change(e, {}), "APPLY_VERSIONED_ASSOCIATION")
        e["event_id"] = "offline"
        e["agent_online"] = False
        self.assertEqual(plan_change(e, {}), "STOP_SSM_READINESS")

    def test_terraform_owned_resource_requires_reviewed_iac_plan(self):
        self.assertEqual(plan_change(event(event_id="tf", target_kind="AWS_RESOURCE",
                                           resource_id="bucket-lab-01",
                                           desired_state_owner="TERRAFORM"), {}),
                         "REVIEW_IAC_PLAN")

    def test_revision_change_and_active_deployment_stop_repair(self):
        self.assertEqual(plan_change(event(event_id="new-rev", desired_revision="rev-19"), {}),
                         "STOP_REVISION")
        self.assertEqual(plan_change(event(event_id="deploying", deployment_active=True), {}),
                         "STOP_DEPLOYMENT")

    def test_approval_and_uncertain_effect_are_not_blindly_retried(self):
        self.assertEqual(plan_change(event(event_id="approve", approval_required=True), {}),
                         "WAIT_APPROVAL")
        self.assertEqual(plan_change(event(event_id="unknown", previous_attempt_unknown=True), {}),
                         "INSPECT_PREVIOUS_ATTEMPT")

    def test_concurrency_retry_and_error_caps_are_enforced(self):
        self.assertEqual(plan_change(event(event_id="busy", active_targets=1), {}),
                         "WAIT_CONCURRENCY")
        self.assertEqual(plan_change(event(event_id="tries", attempts=2), {}),
                         "STOP_RETRIES")
        self.assertEqual(plan_change(event(event_id="errors", error_count=1), {}),
                         "STOP_ERROR_BUDGET")

    def test_unknown_owner_and_incompatible_target_stop(self):
        self.assertEqual(plan_change(event(event_id="unknown-owner",
                                           desired_state_owner="NONE"), {}), "STOP_OWNER")
        self.assertEqual(plan_change(event(event_id="wrong-pair", target_kind="ASG"), {}),
                         "STOP_TARGET_KIND")

    def test_allowed_identifier_cannot_impersonate_another_resource_kind(self):
        for resource, owner, target in (
            ("bucket-lab-01", "STATE_MANAGER", "MANAGED_NODE"),
            ("node-lab-01", "LAUNCH_TEMPLATE", "ASG"),
            ("asg-lab-01", "STATE_MANAGER", "MANAGED_NODE"),
        ):
            with self.subTest(resource=resource, target=target):
                planned = {}
                self.assertEqual(plan_change(event(resource_id=resource,
                    desired_state_owner=owner, target_kind=target), planned), "STOP_TARGET_KIND")
                self.assertEqual(planned, {})
        self.assertEqual(plan_change(event(resource_id="asg-lab-01",
            desired_state_owner="TERRAFORM", target_kind="AWS_RESOURCE"), {}), "REVIEW_IAC_PLAN")

    def test_missing_identity_and_noncompliant_state_stop(self):
        e = event(event_id="")
        self.assertEqual(plan_change(e, {}), "STOP_IDENTITY")
        self.assertEqual(plan_change(event(event_id="compliant", compliance="COMPLIANT"), {}),
                         "STOP_NOT_NONCOMPLIANT")

    def test_missing_revision_and_invalid_bounds_fail_closed(self):
        self.assertEqual(plan_change(event(event_id="missing-revision",
                                           observed_revision=None,
                                           desired_revision=None), {}), "STOP_EVIDENCE")
        self.assertEqual(plan_change(event(event_id="negative-age",
                                           evaluation_age_minutes=-1), {}), "STOP_EVIDENCE")
        self.assertEqual(plan_change(event(event_id="zero-concurrency",
                                           max_concurrent_targets=0), {}), "STOP_EVIDENCE")

    def test_missing_or_non_boolean_safety_evidence_never_selects_a_plan(self):
        for name in ("deployment_active", "previous_attempt_unknown", "approval_required",
                     "approval_present", "ssm_managed", "agent_online"):
            for value in (None, "false", 0, 1):
                with self.subTest(field=name, value=value):
                    e = event(**{name: value})
                    planned = {}
                    self.assertEqual(plan_change(e, planned), "STOP_EVIDENCE")
                    self.assertEqual(planned, {})
            with self.subTest(field=name, value="missing"):
                e = event()
                del e[name]
                self.assertEqual(plan_change(e, {}), "STOP_EVIDENCE")

    def test_scope_includes_account_region_and_explicit_resource(self):
        self.assertEqual(plan_change(event(event_id="region", region="us-west-2"), {}),
                         "STOP_SCOPE")
        self.assertEqual(plan_change(event(event_id="resource", resource_id="prod-1"), {}),
                         "STOP_SCOPE")

    def test_repeat_requires_prior_plan_reconciliation(self):
        e = event(event_id="once")
        planned = {}
        self.assertEqual(plan_change(e, planned), "APPLY_VERSIONED_ASSOCIATION")
        self.assertEqual(plan_change(e, planned), "INSPECT_PRIOR_PLAN")
        self.assertEqual(plan_change(event(event_id="once", resource_id="bucket-lab-01",
                                           desired_state_owner="TERRAFORM",
                                           target_kind="AWS_RESOURCE"), planned), "STOP_ID_REUSE")
        self.assertEqual(plan_change(event(event_id="once", observed_revision="rev-19",
                                           desired_revision="rev-19"), planned), "STOP_ID_REUSE")
        self.assertEqual(plan_change(event(event_id="once", account="222222222222"),
                                     planned), "STOP_SCOPE")

    def test_repeat_still_checks_current_safety_evidence(self):
        planned = {}
        self.assertEqual(plan_change(event(event_id="once"), planned),
                         "APPLY_VERSIONED_ASSOCIATION")
        self.assertEqual(plan_change(event(event_id="once", deployment_active=True),
                                     planned), "STOP_DEPLOYMENT")
        self.assertEqual(plan_change(event(event_id="once", evaluation_age_minutes=42),
                                     planned), "STOP_STALE")

    def test_fixture_set_is_local_and_explicitly_synthetic(self):
        self.assertEqual(len(fixtures()), 5)
        self.assertTrue(all("event_id" in item for item in fixtures()))


if __name__ == "__main__":
    unittest.main()
