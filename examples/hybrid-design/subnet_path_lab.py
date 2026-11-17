"""Small, cloud-free teaching model for one HTTPS request across a VPC peer.

This is a decision fixture, not an AWS network emulator or packet capture.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from ipaddress import IPv4Address, IPv4Network, ip_address, ip_network


@dataclass(frozen=True)
class Route:
    destination: IPv4Network
    target: str


@dataclass(frozen=True)
class Endpoint:
    name: str
    address: IPv4Address
    subnet: str


@dataclass(frozen=True)
class Flow:
    source: Endpoint
    destination: Endpoint
    dns_answer: IPv4Address
    source_outbound_443: bool = True
    destination_inbound_443: bool = True
    source_nacl_outbound_443: bool = True
    destination_nacl_inbound_443: bool = True
    destination_nacl_outbound_ephemeral: bool = True
    source_nacl_inbound_ephemeral: bool = True
    application_authorized: bool = True


@dataclass(frozen=True)
class Network:
    subnet_to_table: dict[str, str]
    tables: dict[str, tuple[Route, ...]]
    peer_target: str = "pcx-ab"


def selected_target(network: Network, subnet: str, destination: IPv4Address) -> str | None:
    """Select longest-prefix match in the named fixture table only.

    AWS has additional route-priority rules that this fixture does not model.
    """
    table = network.subnet_to_table.get(subnet)
    if table is None or table not in network.tables:
        return None
    matching = [route for route in network.tables[table] if destination in route.destination]
    if not matching:
        return None
    best = max(matching, key=lambda route: route.destination.prefixlen)
    return best.target


def diagnose(network: Network, flow: Flow) -> tuple[str, ...]:
    """Return independent missing conditions; ordering is not packet-processing order."""
    blockers: list[str] = []
    if flow.dns_answer != flow.destination.address:
        blockers.append("dns_wrong_destination")
    if selected_target(network, flow.source.subnet, flow.destination.address) != network.peer_target:
        blockers.append("source_subnet_route_missing")
    if selected_target(network, flow.destination.subnet, flow.source.address) != network.peer_target:
        blockers.append("destination_subnet_return_route_missing")
    if not flow.source_outbound_443:
        blockers.append("source_security_group_outbound_denied")
    if not flow.destination_inbound_443:
        blockers.append("destination_security_group_inbound_denied")
    if not flow.source_nacl_outbound_443:
        blockers.append("source_nacl_request_denied")
    if not flow.destination_nacl_inbound_443:
        blockers.append("destination_nacl_request_denied")
    if not flow.destination_nacl_outbound_ephemeral:
        blockers.append("destination_nacl_reply_denied")
    if not flow.source_nacl_inbound_ephemeral:
        blockers.append("source_nacl_reply_denied")
    if not flow.application_authorized:
        blockers.append("application_denied")
    return tuple(blockers)


def base_case() -> tuple[Network, Flow]:
    network = Network(
        subnet_to_table={"b-worker": "b-peer", "a-api": "a-peer"},
        tables={
            "b-peer": (
                Route(ip_network("10.90.0.0/16"), "local"),
                Route(ip_network("10.80.0.0/16"), "pcx-ab"),
            ),
            "b-main": (Route(ip_network("10.90.0.0/16"), "local"),),
            "a-peer": (
                Route(ip_network("10.80.0.0/16"), "local"),
                Route(ip_network("10.90.0.0/16"), "pcx-ab"),
            ),
            "a-main": (Route(ip_network("10.80.0.0/16"), "local"),),
        },
    )
    flow = Flow(
        source=Endpoint("reporting worker", ip_address("10.90.1.10"), "b-worker"),
        destination=Endpoint("booking API", ip_address("10.80.2.10"), "a-api"),
        dns_answer=ip_address("10.80.2.10"),
    )
    return network, flow


def cases() -> tuple[tuple[str, Network, Flow], ...]:
    network, flow = base_case()
    wrong_b_table = replace(network, subnet_to_table={**network.subnet_to_table, "b-worker": "b-main"})
    wrong_a_table = replace(network, subnet_to_table={**network.subnet_to_table, "a-api": "a-main"})
    return (
        ("baseline", network, flow),
        ("correct DNS, wrong B subnet table", wrong_b_table, flow),
        ("A reply uses its main table", wrong_a_table, flow),
        ("API security group refuses 443", network, replace(flow, destination_inbound_443=False)),
        ("API subnet NACL blocks reply port", network, replace(flow, destination_nacl_outbound_ephemeral=False)),
        ("worker subnet NACL blocks reply port", network, replace(flow, source_nacl_inbound_ephemeral=False)),
        ("network path works; API refuses identity", network, replace(flow, application_authorized=False)),
    )


if __name__ == "__main__":
    for name, network, flow in cases():
        print(f"{name}: {', '.join(diagnose(network, flow)) or 'modeled_conditions_present'}")
