"""Deterministic DNS-cache teaching model; no network or AWS calls."""

from dataclasses import dataclass
import json


@dataclass
class Resolver:
    answer: str | None = None
    expires_at: int = -1
    last_query_at: int = -1


def lookup(resolver: Resolver, at: int, *, authority_switch_at: int,
           ttl_change_at: int, old_ttl: int, new_ttl: int) -> dict:
    """Return one fictional resolver observation with ideal TTL compliance."""
    if any(type(value) is not int for value in
           (at, authority_switch_at, ttl_change_at, old_ttl, new_ttl)):
        raise ValueError("Times and TTLs must be integer seconds")
    if at < 0 or authority_switch_at < 0 or ttl_change_at < 0 or old_ttl <= 0 or new_ttl <= 0:
        raise ValueError("Times must be nonnegative and TTLs positive")
    if at < resolver.last_query_at:
        raise ValueError("A resolver's observations must move forward in time")
    resolver.last_query_at = at
    if resolver.answer is not None and at < resolver.expires_at:
        return {"at": at, "answer": resolver.answer, "source": "cache",
                "expires_at": resolver.expires_at}
    # The switch is a supplied point when the authoritative answer has changed.
    # It does not model health-check detection or DNS propagation.
    resolver.answer = "standby" if at >= authority_switch_at else "primary"
    ttl = new_ttl if at >= ttl_change_at else old_ttl
    resolver.expires_at = at + ttl
    return {"at": at, "answer": resolver.answer, "source": "authority",
            "expires_at": resolver.expires_at}


def example() -> dict:
    resolvers = {name: Resolver() for name in ("A", "B", "C")}
    settings = {"authority_switch_at": 100, "ttl_change_at": 120,
                "old_ttl": 300, "new_ttl": 30}
    observations = []
    for name, at in (("A", 0), ("B", 80), ("A", 110), ("B", 110),
                     ("C", 110), ("B", 121), ("A", 300), ("B", 379),
                     ("B", 380)):
        observations.append({"resolver": name,
                             **lookup(resolvers[name], at, **settings)})
    return {"settings": settings, "observations": observations,
            "scope": "Fictional compliant resolver caches; no DNS traffic, health-check timing, client connections, AWS failover or customer recovery proof"}


if __name__ == "__main__":
    print(json.dumps(example(), indent=2))
