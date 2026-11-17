"""Fictional per-key capacity and backlog arithmetic; no AWS client or quota model."""
import json


def assess(rates, key_limit, aggregate_limit, consumer_rate, seconds):
    if not rates or any(type(v) is not int or v < 0 for v in rates.values()):
        raise ValueError('Rates must be nonnegative integers')
    if any(type(v) is not int or v <= 0 for v in (key_limit, aggregate_limit, consumer_rate, seconds)):
        raise ValueError('Limits and duration must be positive integers')
    total = sum(rates.values())
    hot = sorted(key for key, rate in rates.items() if rate > key_limit)
    admitted = min(aggregate_limit, sum(min(rate, key_limit) for rate in rates.values()))
    return {
        'total_per_second': total,
        'aggregate_within_model_limit': total <= aggregate_limit,
        'hot_keys': hot,
        'offered_over_interval': total * seconds,
        'admitted_by_toy_limits_over_interval': admitted * seconds,
        'unadmitted_upstream_over_interval': (total - admitted) * seconds,
        'consumer_capacity_over_interval': consumer_rate * seconds,
        'consumer_backlog_added_from_admitted': max(0, admitted - consumer_rate) * seconds,
    }


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    burst = assess({'van-17': 70, 'van-18': 10, 'van-19': 10}, 50, 100, 60, 120)
    assert burst['aggregate_within_model_limit']
    assert burst['hot_keys'] == ['van-17']
    assert burst['unadmitted_upstream_over_interval'] == 2400
    assert burst['consumer_backlog_added_from_admitted'] == 1200
    quiet = assess({'van-17': 10, 'van-18': 10, 'van-19': 10}, 50, 100, 60, 120)
    assert quiet['hot_keys'] == [] and quiet['consumer_backlog_added_from_admitted'] == 0
    for bad in ({'van-17': -1}, {'van-17': 1.5}, {}):
        try:
            assess(bad, 50, 100, 60, 120)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid input accepted')
    print(json.dumps({'scope': 'fictional arithmetic, not Kinesis shard placement, throughput or AWS evidence',
                      'burst': burst, 'quiet': quiet, 'invalid_inputs_rejected': 3}, indent=2))


if __name__ == '__main__':
    main()
