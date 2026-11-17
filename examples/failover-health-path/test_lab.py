import unittest
from lab import Situation, review


class FailoverReviewTests(unittest.TestCase):
    def setUp(self):
        self.base = dict(primary_healthy=False, secondary_healthy=True, cached_primary_client=False,
                         selected_target_health=(True, False), arriving_bookings_per_minute=80,
                         useful_capacity_per_minute=90, old_booking_verified=True,
                         new_booking_verified=True, writer_authority_verified=True,
                         tenant_denial_verified=True)

    def case(self, **changes):
        return review(Situation(**(self.base | changes)))

    def test_secondary_answer_requires_healthy_secondary(self):
        self.assertEqual(self.case()["dns_new_answer"], "secondary")
        both_failed = self.case(secondary_healthy=False)
        self.assertEqual(both_failed["dns_new_answer"], "primary")
        self.assertFalse(both_failed["reopen_all_clients"])

    def test_all_unhealthy_alb_targets_are_still_selected(self):
        result = self.case(selected_target_health=(False, False))
        self.assertTrue(result["alb_fail_open"])
        self.assertEqual(result["alb_selected_target_numbers"], (1, 2))
        self.assertFalse(result["reopen_all_clients"])

    def test_route_and_capacity_do_not_replace_customer_evidence(self):
        self.assertFalse(self.case(useful_capacity_per_minute=55)["reopen_all_clients"])
        self.assertFalse(self.case(old_booking_verified=False)["reopen_all_clients"])
        self.assertFalse(self.case(tenant_denial_verified=False)["reopen_all_clients"])
        self.assertFalse(self.case(cached_primary_client=True)["reopen_all_clients"])
        self.assertTrue(self.case()["reopen_all_clients"])

    def test_no_targets_is_outside_model(self):
        with self.assertRaises(ValueError):
            self.case(selected_target_health=())


if __name__ == "__main__":
    unittest.main()
