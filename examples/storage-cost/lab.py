"""Fictional uniform-object cost model, not an AWS bill estimator. No network calls."""
from dataclasses import dataclass
from decimal import Decimal as D
import json

GIB = D(2**30)

@dataclass(frozen=True)
class Offer:
    rate: D
    minimum_days: int
    minimum_bytes: int
    transition_per_object: D
    retrieval_per_gib: D
    ready_minutes: int

# Invented offers; none corresponds to a named AWS storage class.
READY = Offer(D('.02'), 0, 0, D('0'), D('0'), 1)
SHELF = Offer(D('.005'), 90, 65536, D('.001'), D('.04'), 120)

def compare(offer, *, objects, bytes_each, days, retrieved_gib, deadline_minutes):
    for name, value in [('objects', objects), ('bytes_each', bytes_each),
                        ('days', days), ('deadline_minutes', deadline_minutes)]:
        if type(value) is not int or value <= 0:
            raise ValueError(name + ' must be a positive integer')
    retrieval = D(str(retrieved_gib))
    if not retrieval.is_finite() or retrieval < 0:
        raise ValueError('retrieved_gib must be finite and nonnegative')
    billed_gib = D(objects * max(bytes_each, offer.minimum_bytes)) / GIB
    billed_days = max(days, offer.minimum_days)
    parts = {
        'storage': billed_gib * D(billed_days) / 30 * offer.rate,
        'transition': D(objects) * offer.transition_per_object,
        'retrieval': retrieval * offer.retrieval_per_gib,
    }
    return {**parts, 'total': sum(parts.values()), 'billed_gib': billed_gib,
            'billed_days': billed_days,
            'meets_deadline': offer.ready_minutes <= deadline_minutes}

def main():
    cases = {
        'quiet_90_days': dict(objects=100, bytes_each=2**30, days=90, retrieved_gib=10, deadline_minutes=180),
        'frequent_reads': dict(objects=100, bytes_each=2**30, days=90, retrieved_gib=150, deadline_minutes=180),
        'delete_day_10': dict(objects=100, bytes_each=2**30, days=10, retrieved_gib=0, deadline_minutes=180),
        'many_small': dict(objects=1024, bytes_each=1024, days=90, retrieved_gib=0, deadline_minutes=180),
        'urgent': dict(objects=100, bytes_each=2**30, days=90, retrieved_gib=10, deadline_minutes=30),
    }
    result = {name: {label: compare(offer, **inputs) for label, offer in [('Ready', READY), ('Shelf', SHELF)]}
              for name, inputs in cases.items()}
    # Hand-calculated cases exercise ranking reversal, minimums and suitability.
    assert result['quiet_90_days']['Ready']['total'] == D('6')
    assert result['quiet_90_days']['Shelf']['total'] == D('2')
    assert result['frequent_reads']['Shelf']['total'] == D('7.6')
    assert result['delete_day_10']['Shelf']['total'] == D('1.6')
    assert result['delete_day_10']['Ready']['total'] < D('0.67')
    assert result['many_small']['Shelf']['billed_gib'] == D('.0625')
    assert result['many_small']['Shelf']['total'] == D('1.0249375')
    assert not result['urgent']['Shelf']['meets_deadline']
    assert result['urgent']['Ready']['meets_deadline']
    # Repeat reads are valid: retrieved bytes may exceed bytes stored.
    same = cases['quiet_90_days'] | {'retrieved_gib': '110'}
    assert compare(SHELF, **same)['total'] == compare(READY, **same)['total'] == D('6')
    for patch in [{'objects': 0}, {'days': -1}, {'bytes_each': True},
                  {'retrieved_gib': 'NaN'}, {'retrieved_gib': '-1'}]:
        try:
            compare(SHELF, **(cases['quiet_90_days'] | patch))
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid workload accepted: ' + str(patch))
    print(json.dumps({'scope': 'fictional cost units; simplified model; no AWS pricing', 'cases': result}, default=str, indent=2))

if __name__ == '__main__':
    main()
