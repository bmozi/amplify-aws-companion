import unittest

from lab import (ALLOWED_ACCOUNT, ALLOWED_REGION, ALLOWED_RESOURCE, fixtures,
                 matches_pattern, response_workflow, route_event, run_packet,
                 scoped_identity)


class IncidentEventWorkflowTests(unittest.TestCase):
    def test_packet_expected_routing_and_gates(self):
        self.assertEqual(run_packet(), {
            "routing": ["NOTICE_AND_REVIEW", "NOTICE_ONLY", "NOTICE_AND_REVIEW",
                        "OUT_OF_SCOPE", "DUPLICATE"],
            "notifications": 3,
            "response_queue": 2,
            "workflow": ["WAIT_FOR_EVIDENCE", "WAIT_FOR_APPROVAL", "VERIFIED",
                         "ALREADY_VERIFIED_IN_FIXTURE"],
        })

    def test_health_impact_region_is_distinct_from_delivery_region(self):
        health = fixtures()[0]
        identity = scoped_identity(health)
        self.assertIn(ALLOWED_REGION, identity)
        self.assertNotEqual(health["region"], health["detail"]["eventRegion"])
        notifications, work, seen = [], [], set()
        self.assertEqual(route_event(health, seen, notifications, work), "NOTICE_AND_REVIEW")
        self.assertEqual(work[0]["region"], health["detail"]["eventRegion"])

    def test_public_health_notice_does_not_create_response_work(self):
        notifications, work, seen = [], [], set()
        self.assertEqual(route_event(fixtures()[1], seen, notifications, work), "NOTICE_ONLY")
        self.assertEqual(len(notifications), 1)
        self.assertEqual(work, [])

    def test_wrong_account_cannot_enter_response_queue(self):
        notifications, work, seen = [], [], set()
        self.assertEqual(route_event(fixtures()[3], seen, notifications, work), "OUT_OF_SCOPE")
        self.assertEqual(notifications, [])
        self.assertEqual(work, [])

    def test_each_matching_event_has_separate_notification_and_work_record(self):
        notifications, work, seen = [], [], set()
        self.assertEqual(route_event(fixtures()[2], seen, notifications, work), "NOTICE_AND_REVIEW")
        self.assertEqual(len(notifications), 1)
        self.assertEqual(len(work), 1)
        self.assertNotEqual(notifications[0], work[0])

    def test_response_requires_exact_scope_evidence_and_approval(self):
        work = {"identity": "fixture-1", "account": ALLOWED_ACCOUNT,
                "region": ALLOWED_REGION, "resource": ALLOWED_RESOURCE}
        attempted, verified = set(), set()
        self.assertEqual(response_workflow(work, evidence_complete=False, approved_by=None,
                                           action_outcome="SUCCEEDED", verification_succeeded=True,
                                           attempted_effects=attempted,
                                           verified_effects=verified), "WAIT_FOR_EVIDENCE")
        self.assertEqual(response_workflow(work, evidence_complete=True, approved_by=None,
                                           action_outcome="SUCCEEDED", verification_succeeded=True,
                                           attempted_effects=attempted,
                                           verified_effects=verified), "WAIT_FOR_APPROVAL")

    def test_action_is_not_closed_until_independent_verification(self):
        work = {"identity": "fixture-2", "account": ALLOWED_ACCOUNT,
                "region": ALLOWED_REGION, "resource": ALLOWED_RESOURCE}
        attempted, verified = set(), set()
        self.assertEqual(response_workflow(work, evidence_complete=True,
                                           approved_by="reviewer-fixture",
                                           action_outcome="SUCCEEDED", verification_succeeded=False,
                                           attempted_effects=attempted,
                                           verified_effects=verified), "UNVERIFIED_STOP")
        self.assertEqual(response_workflow(work, evidence_complete=True,
                                           approved_by="reviewer-fixture",
                                           action_outcome="SUCCEEDED", verification_succeeded=True,
                                           attempted_effects=attempted,
                                           verified_effects=verified), "INSPECT_PREVIOUS_ATTEMPT")
        self.assertNotIn("fixture-2", verified)

    def test_successful_effect_is_not_repeated(self):
        work = {"identity": "fixture-3", "account": ALLOWED_ACCOUNT,
                "region": ALLOWED_REGION, "resource": ALLOWED_RESOURCE}
        attempted, verified = set(), set()
        kwargs = dict(evidence_complete=True, approved_by="reviewer-fixture",
                      action_outcome="SUCCEEDED", verification_succeeded=True,
                      attempted_effects=attempted, verified_effects=verified)
        self.assertEqual(response_workflow(work, **kwargs), "VERIFIED")
        self.assertEqual(response_workflow(work, **kwargs), "ALREADY_VERIFIED_IN_FIXTURE")

    def test_unknown_effect_is_inspected_before_any_retry(self):
        work = {"identity": "fixture-4", "account": ALLOWED_ACCOUNT,
                "region": ALLOWED_REGION, "resource": ALLOWED_RESOURCE}
        attempted, verified = set(), set()
        kwargs = dict(evidence_complete=True, approved_by="reviewer-fixture",
                      action_outcome="UNKNOWN", verification_succeeded=True,
                      attempted_effects=attempted, verified_effects=verified)
        self.assertEqual(response_workflow(work, **kwargs), "INSPECT_PREVIOUS_ATTEMPT")
        self.assertEqual(response_workflow(work, **kwargs), "INSPECT_PREVIOUS_ATTEMPT")
        self.assertNotIn("fixture-4", verified)

    def test_pattern_requires_source_and_account(self):
        event = fixtures()[2]
        self.assertTrue(matches_pattern(event, {
            "source": ["aws.ec2"], "account": [ALLOWED_ACCOUNT],
            "detail": {"eventName": ["AuthorizeSecurityGroupIngress"]}}))
        self.assertFalse(matches_pattern(event, {
            "source": ["aws.health"], "account": [ALLOWED_ACCOUNT]}))


if __name__ == "__main__":
    unittest.main()
