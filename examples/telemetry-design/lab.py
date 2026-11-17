"""Complete versus incomplete fixed-cadence gauge windows; no AWS emulation."""
from fractions import Fraction
import json


def ingest(records, events):
    """One trusted synthetic sensor; integer event second is its unique identity."""
    for second, depth in events:
        if type(second) is not int or second < 0 or type(depth) is not int or depth < 0:
            raise ValueError('Expected nonnegative integer second and queue depth')
        if second in records and records[second] != depth:
            raise ValueError('Conflicting observation at the same sensor second')
        records[second] = depth


def window(records, start, length=60):
    """Expected one reading per second in [start, start + length). No interpolation."""
    if type(start) is not int or start < 0 or type(length) is not int or length <= 0:
        raise ValueError('Invalid window')
    observed = [records[t] for t in range(start, start + length) if t in records]
    missing = [t for t in range(start, start + length) if t not in records]
    return {
        'start_inclusive': start, 'end_exclusive': start + length,
        'observed_count': len(observed), 'expected_count': length,
        'coverage': str(Fraction(len(observed), length)),
        'missing_seconds': missing,
        'observed_average': str(Fraction(sum(observed), len(observed))) if observed else None,
        'observed_maximum': max(observed) if observed else None,
        'observed_sum': sum(observed) if observed else None,
        'whole_window_average': str(Fraction(sum(observed), length)) if not missing else None,
        'status': 'complete' if not missing else 'incomplete',
    }


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    records = {}
    quiet = [(t, 0) for t in range(10, 60)]
    burst = [(t, 60) for t in range(10)]
    ingest(records, quiet)
    before = window(records, 0)
    assert before['observed_average'] == '0' and before['observed_maximum'] == 0
    assert before['coverage'] == '5/6' and before['missing_seconds'] == list(range(10))
    assert before['whole_window_average'] is None and before['status'] == 'incomplete'
    # Arrival order differs from event time. Late readings revise the same event-time window.
    ingest(records, reversed(burst))
    after = window(records, 0)
    assert after['whole_window_average'] == '10' and after['observed_maximum'] == 60
    assert after['observed_sum'] == 600 and after['status'] == 'complete'
    ingest(records, quiet + burst)  # Exact retransmissions must not double-count samples.
    assert window(records, 0) == after
    try:
        ingest(records, [(0, 0)])
    except ValueError:
        pass
    else:
        raise AssertionError('Conflicting duplicate accepted')
    assert records[0] == 60 and window(records, 0) == after
    ingest(records, [(60, 99)])
    assert window(records, 0) == after
    next_window = window(records, 60)
    assert next_window['observed_count'] == 1 and next_window['observed_maximum'] == 99
    assert next_window['whole_window_average'] is None
    empty = window(records, 120)
    assert empty['coverage'] == '0' and empty['observed_average'] is None
    assert empty['observed_maximum'] is None and empty['observed_sum'] is None
    # Group summaries can be merged with counts, not by averaging their means.
    wrong_mean = (Fraction(60) + Fraction(0)) / 2
    merged_mean = Fraction(60 * 10 + 0 * 50, 10 + 50)
    assert wrong_mean == 30 and merged_mean == 10
    invalid = [(-1, 0), (0, -1), (True, 0), (0, 1.5)]
    for item in invalid:
        try:
            ingest({}, [item])
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid observation accepted')
    print(json.dumps({
        'scope': 'synthetic single-sensor fixed-cadence arithmetic; not CloudWatch behavior',
        'before_late_arrival': before, 'after_late_arrival': after,
        'duplicate_replay_preserved_window': True, 'conflicting_duplicate_rejected': True,
        'boundary_observation_only_in_next_window': next_window,
        'empty_window': empty, 'incorrect_average_of_group_means': str(wrong_mean),
        'count_weighted_group_mean': str(merged_mean), 'invalid_observations_rejected': len(invalid),
    }, indent=2))


if __name__ == '__main__':
    main()
