"""Fictional Region shortlist; never queries AWS or authorizes a live run."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CarbonObservation:
    value: int  # Synthetic comparison units, not kilograms or measured emissions.
    method: str
    boundary: str
    period: str
    workload: str


@dataclass(frozen=True)
class Candidate:
    label: str  # Fictional labels; no actual AWS Region is evaluated here.
    residency_ok: bool | None
    services_ok: bool | None
    latency_ms: int | None
    transfer_included: bool | None
    estimated_run_cents: int | None
    projected_credit_reserve_cents: int | None
    carbon: CarbonObservation | None = None


def shortlist(candidate: Candidate, *, max_latency_ms=120,
              max_run_cents=500, min_reserve_cents=10_000):
    """Apply fictional case limits; callers choose their own for changed cases."""
    if max_latency_ms < 0 or max_run_cents < 0 or min_reserve_cents < 0:
        raise ValueError('Case limits must be nonnegative')
    rejected, pending = [], []
    for name, value in (('residency', candidate.residency_ok),
                        ('required services', candidate.services_ok)):
        if value is False:
            rejected.append(name)
        elif value is not True:
            pending.append(name)
    if candidate.latency_ms is None:
        pending.append('customer latency')
    elif candidate.latency_ms < 0 or candidate.latency_ms > max_latency_ms:
        rejected.append('customer latency')
    if candidate.estimated_run_cents is None:
        pending.append('complete run estimate')
    elif candidate.estimated_run_cents < 0 or candidate.estimated_run_cents > max_run_cents:
        rejected.append('run limit')
    if candidate.projected_credit_reserve_cents is None:
        pending.append('projected credit reserve')
    elif candidate.projected_credit_reserve_cents < min_reserve_cents:
        rejected.append('credit reserve')
    if candidate.transfer_included is not True:
        pending.append('transfer and replication in estimate')
    status = 'reject' if rejected else 'pending' if pending else 'paper_shortlist'
    return status, tuple(rejected), tuple(pending)


def compare_synthetic_carbon(first: Candidate, second: Candidate, *,
                             max_latency_ms=120, max_run_cents=500,
                             min_reserve_cents=10_000):
    """Only order supplied toy values when their declared bases match exactly."""
    left, right = first.carbon, second.carbon
    limits = dict(max_latency_ms=max_latency_ms, max_run_cents=max_run_cents,
                  min_reserve_cents=min_reserve_cents)
    if (shortlist(first, **limits)[0] != 'paper_shortlist' or
            shortlist(second, **limits)[0] != 'paper_shortlist' or
            left is None or right is None or
            left.value < 0 or right.value < 0 or
            not all((left.method, left.boundary, left.period, left.workload)) or
            (left.method, left.boundary, left.period, left.workload) !=
            (right.method, right.boundary, right.period, right.workload)):
        return None
    if left.value == right.value:
        return 'equal supplied toy values'
    return first.label if left.value < right.value else second.label


if __name__ == '__main__':
    same_basis = CarbonObservation(80, 'fictional-method-A', 'same-workload-whole-path',
                                   'one-month', 'shop-repairs-v1')
    candidates = (
        Candidate('region-alpha', True, True, 80, True, 420, 12_000, same_basis),
        Candidate('region-beta', False, True, 60, True, 380, 12_000,
                  CarbonObservation(50, 'fictional-method-A', 'same-workload-whole-path',
                                    'one-month', 'shop-repairs-v1')),
        Candidate('region-gamma', True, True, 75, False, 390, 12_000, None),
    )
    for candidate in candidates:
        print(candidate.label, shortlist(candidate))
    print('A Region choice still requires real evidence, current prices and account checks.')
