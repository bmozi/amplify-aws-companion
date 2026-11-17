"""Offline retry-start schedule; no service, capacity or SDK simulation."""
from collections import Counter
import json
import math
import random


def schedule(draws, *, jitter=True, deadline=12.0, call_seconds=1.0):
    """Initial call plus up to three retries, using caps of 2, 4, 4 seconds.

    Inputs are explicit draws in [0, 1], so timing decisions can be replayed.
    All calls fail. A retry is admitted only if it can finish by the deadline.
    """
    if not math.isfinite(deadline) or deadline < 0:
        raise ValueError('deadline must be finite and nonnegative')
    if not math.isfinite(call_seconds) or call_seconds <= 0:
        raise ValueError('call duration must be finite and positive')
    draws = tuple(draws)
    if len(draws) != 3 or any(not math.isfinite(x) or not 0 <= x <= 1 for x in draws):
        raise ValueError('provide three draws between zero and one')
    if call_seconds > deadline:
        return []
    starts = [0.0]
    end = call_seconds
    for cap, draw in zip((2, 4, 4), draws):
        start = end + cap * (draw if jitter else 1)
        if start + call_seconds > deadline:
            break
        starts.append(start)
        end = start + call_seconds
    return starts


def compare(clients=20, seed=7):
    rng = random.Random(seed)
    draws = [[rng.random() for _ in range(3)] for _ in range(clients)]
    results = {}
    for label, jitter in [('fixed', False), ('full_jitter', True)]:
        paths = [schedule(d, jitter=jitter) for d in draws]
        bins = Counter(math.floor(t) for path in paths for t in path[1:])
        results[label] = {
            'total_calls': sum(map(len, paths)),
            'retry_starts_per_one_second_bucket': dict(sorted(bins.items())),
            'peak_retry_bucket': max(bins.values(), default=0),
            'completed_customer_operations': 0,
        }
    return results


if __name__ == '__main__':
    print(json.dumps(compare(), indent=2))
