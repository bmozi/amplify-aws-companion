"""Changed routes that defeat a plausible green-path shortcut."""

import unittest

from path_lab import assess, owners_for, route_for


class PathLabTests(unittest.TestCase):
    def setUp(self):
        self.peers = {frozenset(("A", "B")), frozenset(("A", "C"))}
        self.routes = {
            "A": [("10.90.0.0/16", "B")],
            "B": [("10.80.0.0/16", "A")],
            "C": [("10.80.0.0/16", "A")],
        }

    def test_more_specific_wrong_hop_beats_broad_good_route(self):
        self.routes["A"].append(("10.90.1.0/24", "C"))
        self.assertEqual("C", route_for(self.routes, "A", "10.90.1.20"))
        self.assertEqual("peer_transit_not_supported",
                         assess("A", "10.80.1.10", "B", "10.90.1.20",
                                self.peers, self.routes))

    def test_forward_route_does_not_prove_reply(self):
        self.routes["B"] = []
        self.assertEqual("missing_return_route",
                         assess("A", "10.80.1.10", "B", "10.90.1.20",
                                self.peers, self.routes))

    def test_connecting_graph_does_not_make_peering_transitive(self):
        self.routes["B"].append(("10.100.0.0/16", "A"))
        self.assertEqual("peer_transit_not_supported",
                         assess("B", "10.90.1.10", "C", "10.100.1.20",
                                self.peers, self.routes))

    def test_partial_overlap_rejects_direct_vpc_pair(self):
        self.assertEqual("overlapping_vpc_cidrs",
                         assess("A", "10.80.1.10", "D", "10.80.129.20",
                                self.peers | {frozenset(("A", "D"))}, self.routes))

    def test_correct_name_answer_cannot_choose_between_duplicate_office_ranges(self):
        self.assertEqual(["one", "two"], owners_for(
            "10.20.8.9", {"one": "10.20.0.0/16", "two": "10.20.0.0/16"}))

    def test_endpoint_must_belong_to_its_named_vpc(self):
        with self.assertRaises(ValueError):
            assess("A", "10.90.1.10", "B", "10.90.1.20", self.peers, self.routes)


if __name__ == "__main__":
    unittest.main()
