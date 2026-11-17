"""A fictional operations handoff: customer recovery is not alarm recovery.

All observations are supplied local fixtures. Nothing calls AWS or sends alerts.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Probe:
    account: str
    region: str
    journey: str
    run_id: str
    measured_minute: int
    succeeded: bool


@dataclass(frozen=True)
class Work:
    account: str
    region: str
    request_id: str
    accepted_minute: int
    completed_minute: int | None


@dataclass(frozen=True)
class Delivery:
    transition_id: str
    acknowledged: bool


def unique_transitions(deliveries):
    """Collapse retries of one transition, never distinct transitions."""
    by_id = {}
    for item in deliveries:
        # A later acknowledged retry can repair an earlier failed attempt.
        by_id[item.transition_id] = by_id.get(item.transition_id, False) or item.acknowledged
    return by_id


def assess(*, now, account, region, journey, probes, work, deliveries,
           owner, current_alarm, accepted_ids):
    """Return separate customer and operations decisions with explicit gaps.

    The stipulated accepted_ids represent an independently checked intake ledger.
    The local model does not establish that a real intake ledger is complete.
    """
    gaps = []
    scoped = [p for p in probes if (p.account, p.region, p.journey) ==
              (account, region, journey) and p.measured_minute <= now]
    fresh = sorted((p for p in scoped if now - p.measured_minute <= 5),
                   key=lambda p: p.measured_minute)
    latest = fresh[-2:]
    if len(latest) != 2 or len({p.run_id for p in latest}) != 2 or not all(p.succeeded for p in latest):
        gaps.append('two_distinct_fresh_successful_customer_probes_missing')

    scoped_work = [w for w in work if (w.account, w.region) == (account, region)]
    recorded_ids = {w.request_id for w in scoped_work}
    if recorded_ids != set(accepted_ids) or len(scoped_work) != len(recorded_ids):
        gaps.append('accepted_work_inventory_unreconciled')
    if any(w.completed_minute is None or w.completed_minute > now for w in scoped_work):
        gaps.append('accepted_work_incomplete')

    customer_recovered = not gaps
    operations_gaps = []
    if not owner:
        operations_gaps.append('no_named_owner')
    if current_alarm != 'OK':
        operations_gaps.append('alarm_not_ok')
    transition_results = unique_transitions(deliveries)
    if not transition_results or not all(transition_results.values()):
        operations_gaps.append('notification_path_unverified')
    return {
        'customer_recovered': customer_recovered,
        'operations_handoff_complete': customer_recovered and not operations_gaps,
        'customer_gaps': gaps,
        'operations_gaps': operations_gaps,
        'unique_transitions': len(transition_results),
        'delivery_attempts': len(deliveries),
    }


def sample():
    return dict(now=20, account='111122223333', region='us-east-2', journey='confirm-booking',
                probes=[Probe('111122223333', 'us-east-2', 'confirm-booking', 'p1', 18, True),
                        Probe('111122223333', 'us-east-2', 'confirm-booking', 'p2', 20, True)],
                work=[Work('111122223333', 'us-east-2', 'booking-7', 3, 17)],
                accepted_ids={'booking-7'},
                deliveries=[Delivery('alarm-enter-1', False), Delivery('alarm-enter-1', True),
                            Delivery('alarm-ok-1', True)],
                owner='Maya', current_alarm='OK')


if __name__ == '__main__':
    import json
    base = sample()
    print('Recovered and handed off:', json.dumps(assess(**base), sort_keys=True))
    older = dict(base, work=[Work('111122223333', 'us-east-2', 'booking-7', 3, None)])
    print('Alarm green; booking unfinished:', json.dumps(assess(**older), sort_keys=True))
