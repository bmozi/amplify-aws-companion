"""A tiny fictional failover decision worksheet, not an AWS emulator."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Situation:
    primary_healthy: bool
    secondary_healthy: bool
    cached_primary_client: bool
    selected_target_health: tuple[bool, ...]
    arriving_bookings_per_minute: int
    useful_capacity_per_minute: int
    old_booking_verified: bool
    new_booking_verified: bool
    writer_authority_verified: bool
    tenant_denial_verified: bool


def review(s: Situation) -> dict[str, object]:
    if not s.selected_target_health:
        raise ValueError("Supply at least one registered target; no-target behavior is outside this model")
    if s.arriving_bookings_per_minute < 0 or s.useful_capacity_per_minute < 0:
        raise ValueError("Rates must be nonnegative")
    # Only the documented primary/secondary failover pair with both checked.
    dns_new_answer = "secondary" if not s.primary_healthy and s.secondary_healthy else "primary"
    healthy = tuple(i for i, value in enumerate(s.selected_target_health, start=1) if value)
    alb_selected = healthy or tuple(range(1, len(s.selected_target_health) + 1))
    fail_open = not healthy
    reasons = []
    if s.cached_primary_client:
        reasons.append("a cached client still has the primary answer")
    if dns_new_answer == "primary" and not s.primary_healthy:
        reasons.append("last-resort DNS answer is an unhealthy primary")
    if fail_open:
        reasons.append("ALB all-targets-unhealthy fail-open")
    if s.useful_capacity_per_minute < s.arriving_bookings_per_minute:
        reasons.append("useful surviving capacity is below arrivals")
    for passed, label in (
        (s.old_booking_verified, "old confirmed booking not verified"),
        (s.new_booking_verified, "new booking not verified"),
        (s.writer_authority_verified, "writer authority not verified"),
        (s.tenant_denial_verified, "cross-tenant denial not verified"),
    ):
        if not passed:
            reasons.append(label)
    return {"dns_new_answer": dns_new_answer, "alb_selected_target_numbers": alb_selected,
            "alb_fail_open": fail_open, "reopen_all_clients": not reasons, "reasons": tuple(reasons)}


if __name__ == "__main__":
    base = dict(primary_healthy=False, secondary_healthy=True, cached_primary_client=False,
                selected_target_health=(True, False), arriving_bookings_per_minute=80,
                useful_capacity_per_minute=55, old_booking_verified=True,
                new_booking_verified=True, writer_authority_verified=True,
                tenant_denial_verified=True)
    for label, changes in (
        ("survivor shortfall", {}),
        ("both DNS records unhealthy", {"secondary_healthy": False}),
        ("all ALB targets unhealthy", {"selected_target_health": (False, False)}),
        ("capacity restored", {"useful_capacity_per_minute": 90}),
    ):
        result = review(Situation(**(base | changes)))
        print(f"{label}: DNS={result['dns_new_answer']} ALB={result['alb_selected_target_numbers']} "
              f"reopen_all={result['reopen_all_clients']} reasons={result['reasons']}")
