"""Small CIDR and one-hop peering model; never reads or changes AWS routes."""

from ipaddress import ip_address, ip_network
import json


VPCS = {
    "A": ip_network("10.80.0.0/16"),
    "B": ip_network("10.90.0.0/16"),
    "C": ip_network("10.100.0.0/16"),
    "D": ip_network("10.80.128.0/17"),  # Deliberately overlaps A.
}


def route_for(routes, source, destination_ip):
    """Choose a matching route in this one-table-per-VPC teaching fixture."""
    matches = [(ip_network(destination), peer)
               for destination, peer in routes.get(source, [])
               if ip_address(destination_ip) in ip_network(destination)]
    if not matches:
        return None
    # Longest prefix wins. Equal-prefix conflicting targets are a bad fixture.
    matches.sort(key=lambda item: item[0].prefixlen, reverse=True)
    if len(matches) > 1 and matches[0][0].prefixlen == matches[1][0].prefixlen:
        raise ValueError("Ambiguous equal-prefix fixture routes")
    return matches[0][1]


def assess(source, source_ip, destination, destination_ip, peers, routes):
    """Check the modeled forward and reply hop, not security or real reachability."""
    if source == destination or source not in VPCS or destination not in VPCS:
        raise ValueError("Choose two known, distinct VPCs")
    if ip_address(source_ip) not in VPCS[source] or ip_address(destination_ip) not in VPCS[destination]:
        raise ValueError("The named endpoint must be inside its VPC")
    if VPCS[source].overlaps(VPCS[destination]):
        return "overlapping_vpc_cidrs"
    link = frozenset((source, destination))
    forward_target = route_for(routes, source, destination_ip)
    if forward_target is None:
        return "missing_forward_route"
    if forward_target != destination:
        return "peer_transit_not_supported" if frozenset((source, forward_target)) in peers else "invalid_forward_target"
    if link not in peers:
        return "missing_direct_peer"
    reply_target = route_for(routes, destination, source_ip)
    if reply_target is None:
        return "missing_return_route"
    if reply_target != source:
        return "wrong_return_target"
    return "modeled_route_pair_present"


def owners_for(address, networks):
    """An address alone cannot identify an office when CIDRs overlap."""
    value = ip_address(address)
    return sorted(name for name, cidr in networks.items() if value in ip_network(cidr))


def run():
    peers = {frozenset(("A", "B")), frozenset(("A", "C"))}
    full_routes = {
        "A": [("10.90.0.0/16", "B"), ("10.100.0.0/16", "C")],
        "B": [("10.80.0.0/16", "A")],
        "C": [("10.80.0.0/16", "A")],
    }
    baseline = assess("B", "10.90.1.10", "A", "10.80.1.20", peers, full_routes)
    no_return = {**full_routes, "A": [("10.100.0.0/16", "C")]}
    missing_reply = assess("B", "10.90.1.10", "A", "10.80.1.20", peers, no_return)
    through_a = {**full_routes, "B": full_routes["B"] + [("10.100.0.0/16", "A")]}
    false_transit = assess("B", "10.90.1.10", "C", "10.100.1.30", peers, through_a)
    direct_peers = peers | {frozenset(("B", "C"))}
    direct_routes = {**full_routes,
                     "B": full_routes["B"] + [("10.100.0.0/16", "C")],
                     "C": full_routes["C"] + [("10.90.0.0/16", "B")]}
    direct = assess("B", "10.90.1.10", "C", "10.100.1.30", direct_peers, direct_routes)
    overlap = assess("A", "10.80.1.20", "D", "10.80.129.10",
                     peers | {frozenset(("A", "D"))},
                     {**full_routes, "A": full_routes["A"] + [("10.80.128.0/17", "D")],
                      "D": [("10.80.0.0/16", "A")]})
    office_owners = owners_for("10.20.8.9", {"office-one": "10.20.0.0/16",
                                                "office-two": "10.20.0.0/16"})
    # A correct name answer selects an address, not a route or an owner.
    dns_without_route = assess("B", "10.90.1.10", "A", "10.80.1.20", peers,
                               {"A": full_routes["A"], "B": [], "C": full_routes["C"]})
    assert (baseline, missing_reply, false_transit, direct, overlap, dns_without_route) == (
        "modeled_route_pair_present", "missing_return_route", "peer_transit_not_supported",
        "modeled_route_pair_present", "overlapping_vpc_cidrs", "missing_forward_route")
    assert office_owners == ["office-one", "office-two"]
    return {
        "A_to_B_direct_pair": baseline,
        "B_to_A_without_reply_route": missing_reply,
        "B_to_C_through_A": false_transit,
        "B_to_C_with_direct_peer_and_two_routes": direct,
        "A_to_overlapping_D": overlap,
        "office_address_10_20_8_9_candidates": office_owners,
        "correct_DNS_answer_without_B_route": dns_without_route,
        "boundary": "One synthetic route table per VPC, full CIDR peers and one-hop model only; no SG, NACL, DNS resolver, VPN, TGW, TLS, IAM, application or AWS packet result",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
