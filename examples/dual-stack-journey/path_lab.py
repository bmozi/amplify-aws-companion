"""Offline path decision exercise; this does not probe or simulate AWS networking."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class RepairSite:
    ipv4_dns: bool = True
    ipv6_dns: bool = True
    ipv4_internet_route: bool = True
    ipv4_listener_allowed: bool = True
    alb_dualstack: bool = True
    alb_subnets_ipv6: bool = True
    ipv6_internet_route: bool = True
    ipv6_listener_allowed: bool = True
    ipv4_target_healthy: bool = True
    ipv4_target_allowed: bool = True


def customer_path(site: RepairSite, family: str) -> tuple[bool, str]:
    """Return the first failed design gate for one independently chosen family."""
    if family == "IPv4":
        gates = ((site.ipv4_dns, "A record missing"),
                 (site.ipv4_internet_route, "IPv4 internet route missing"),
                 (site.ipv4_listener_allowed, "IPv4 listener path denied"),
                 (site.ipv4_target_healthy, "IPv4 target unhealthy"),
                 (site.ipv4_target_allowed, "IPv4 target path denied"))
    elif family == "IPv6":
        gates = ((site.ipv6_dns, "AAAA record missing"),
                 (site.alb_dualstack, "load balancer not dualstack"),
                 (site.alb_subnets_ipv6, "load balancer subnet has no IPv6 range"),
                 (site.ipv6_internet_route, "IPv6 internet route missing"),
                 (site.ipv6_listener_allowed, "IPv6 listener path denied"),
                 (site.ipv4_target_healthy, "IPv4 target unhealthy"),
                 (site.ipv4_target_allowed, "IPv4 target path denied"))
    else:
        raise ValueError("Choose IPv4 or IPv6")
    for allowed, reason in gates:
        if not allowed:
            return False, reason
    return True, "design gates passed; live delivery unverified"


def supplier_path(worker_family: str, supplier_family: str,
                  dns64: bool = False, nat64_route: bool = False) -> tuple[bool, str]:
    """Classify an outbound family mismatch without inventing a working VPC."""
    if worker_family not in ("IPv4", "IPv6", "dualstack"):
        raise ValueError("Unknown worker family")
    if supplier_family not in ("IPv4", "IPv6"):
        raise ValueError("Unknown supplier family")
    if worker_family == "dualstack" or worker_family == supplier_family:
        return True, "matching address family; route and policy still need review"
    if worker_family == "IPv6" and supplier_family == "IPv4":
        if dns64 and nat64_route:
            return True, "DNS64/NAT64 candidate; verify NAT gateway path, policy and price"
        return False, "IPv6-only worker needs an IPv4 path or DNS64 and NAT64"
    return False, "IPv4-only worker cannot directly reach an IPv6-only destination"


def demonstration() -> None:
    base = RepairSite()
    cases = (
        ("baseline", base),
        ("AAAA added before IPv6 route", replace(base, ipv6_internet_route=False)),
        ("IPv6 rule missing", replace(base, ipv6_listener_allowed=False)),
        ("target fails", replace(base, ipv4_target_healthy=False)),
    )
    for label, site in cases:
        print(label)
        for family in ("IPv4", "IPv6"):
            ok, reason = customer_path(site, family)
            print(f"  {family}: {'candidate' if ok else 'blocked'} — {reason}")
    print("IPv6-only worker to IPv4-only supplier:", supplier_path("IPv6", "IPv4"))


if __name__ == "__main__":
    demonstration()
