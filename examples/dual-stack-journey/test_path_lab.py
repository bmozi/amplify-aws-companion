import unittest
from dataclasses import replace

from path_lab import RepairSite, customer_path, supplier_path


class JourneyTests(unittest.TestCase):
    def test_missing_ipv6_route_breaks_only_ipv6_client(self):
        site = replace(RepairSite(), ipv6_internet_route=False)
        self.assertTrue(customer_path(site, "IPv4")[0])
        self.assertEqual(customer_path(site, "IPv6"), (False, "IPv6 internet route missing"))

    def test_missing_ipv4_route_breaks_only_ipv4_client(self):
        site = replace(RepairSite(), ipv4_internet_route=False)
        self.assertTrue(customer_path(site, "IPv6")[0])
        self.assertEqual(customer_path(site, "IPv4"), (False, "IPv4 internet route missing"))

    def test_ipv4_target_can_serve_ipv6_client_through_dualstack_front(self):
        self.assertTrue(customer_path(RepairSite(), "IPv6")[0])
        self.assertEqual(customer_path(replace(RepairSite(), ipv4_target_healthy=False), "IPv6"),
                         (False, "IPv4 target unhealthy"))

    def test_rollback_aaaa_restores_old_client_path_but_not_new_client_access(self):
        site = replace(RepairSite(), ipv6_listener_allowed=False, ipv6_dns=False)
        self.assertTrue(customer_path(site, "IPv4")[0])
        self.assertEqual(customer_path(site, "IPv6"), (False, "AAAA record missing"))

    def test_ipv6_egress_is_not_ipv4_translation(self):
        self.assertFalse(supplier_path("IPv6", "IPv4")[0])
        self.assertFalse(supplier_path("IPv6", "IPv4", dns64=True)[0])
        self.assertTrue(supplier_path("IPv6", "IPv4", dns64=True, nat64_route=True)[0])
        self.assertTrue(supplier_path("dualstack", "IPv4")[0])

    def test_invalid_family_is_rejected(self):
        with self.assertRaises(ValueError):
            customer_path(RepairSite(), "maybe")


if __name__ == "__main__":
    unittest.main()
