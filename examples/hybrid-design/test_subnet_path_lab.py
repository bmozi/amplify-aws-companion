"""Changed-condition checks for the subnet and traffic-boundary teaching model."""

import unittest
from dataclasses import replace
from ipaddress import ip_address, ip_network

from subnet_path_lab import Route, base_case, diagnose, selected_target


class SubnetPathTests(unittest.TestCase):
    def test_base_has_all_modeled_conditions(self):
        network, flow = base_case()
        self.assertEqual(diagnose(network, flow), ())

    def test_explicit_subnet_association_overrides_a_useful_other_table(self):
        network, flow = base_case()
        changed = replace(network, subnet_to_table={**network.subnet_to_table, "b-worker": "b-main"})
        self.assertEqual(diagnose(changed, flow), ("source_subnet_route_missing",))

    def test_return_uses_destination_subnet_association(self):
        network, flow = base_case()
        changed = replace(network, subnet_to_table={**network.subnet_to_table, "a-api": "a-main"})
        self.assertEqual(diagnose(changed, flow), ("destination_subnet_return_route_missing",))

    def test_more_specific_wrong_target_beats_broad_peer_route(self):
        network, flow = base_case()
        changed_tables = dict(network.tables)
        changed_tables["b-peer"] += (Route(ip_network("10.80.2.0/24"), "wrong-target"),)
        changed = replace(network, tables=changed_tables)
        self.assertEqual(selected_target(changed, "b-worker", flow.destination.address), "wrong-target")
        self.assertEqual(diagnose(changed, flow), ("source_subnet_route_missing",))

    def test_dns_answer_does_not_supply_route(self):
        network, flow = base_case()
        changed = replace(network, subnet_to_table={**network.subnet_to_table, "b-worker": "b-main"})
        self.assertEqual(flow.dns_answer, flow.destination.address)
        self.assertEqual(diagnose(changed, flow), ("source_subnet_route_missing",))

    def test_security_group_request_denial_is_separate_from_routes(self):
        network, flow = base_case()
        self.assertEqual(diagnose(network, replace(flow, destination_inbound_443=False)),
                         ("destination_security_group_inbound_denied",))

    def test_source_security_group_outbound_is_a_separate_gate(self):
        network, flow = base_case()
        self.assertEqual(diagnose(network, replace(flow, source_outbound_443=False)),
                         ("source_security_group_outbound_denied",))

    def test_stateless_nacl_needs_reply_rules_on_both_subnets(self):
        network, flow = base_case()
        changed = replace(flow, destination_nacl_outbound_ephemeral=False,
                          source_nacl_inbound_ephemeral=False)
        self.assertEqual(diagnose(network, changed),
                         ("destination_nacl_reply_denied", "source_nacl_reply_denied"))

    def test_application_denial_remains_after_network_conditions_pass(self):
        network, flow = base_case()
        self.assertEqual(diagnose(network, replace(flow, application_authorized=False)),
                         ("application_denied",))

    def test_changed_dns_answer_is_not_silently_treated_as_api(self):
        network, flow = base_case()
        self.assertEqual(diagnose(network, replace(flow, dns_answer=ip_address("10.80.2.99"))),
                         ("dns_wrong_destination",))

    def test_multiple_independent_denials_are_reported_together(self):
        network, flow = base_case()
        changed = replace(flow, source_outbound_443=False,
                          destination_nacl_outbound_ephemeral=False,
                          source_nacl_inbound_ephemeral=False)
        self.assertEqual(diagnose(network, changed),
                         ("source_security_group_outbound_denied",
                          "destination_nacl_reply_denied", "source_nacl_reply_denied"))


if __name__ == "__main__":
    unittest.main()
