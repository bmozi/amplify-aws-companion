# When two helpers both retry

Maya's customer presses **Save repair request**. The website calls an intake worker, which calls a supplier. The supplier is slow. Both the website and the worker have been told to try three times. One customer's request can therefore cause **nine supplier calls**. That is like asking three staff members to repeat a three-call phone chain: nine rings do not mean nine repairs were accepted.

This local exercise counts calls and elapsed time without waiting, contacting AWS or charging money. It uses invented values: each supplier call takes **2 seconds**, retry waits are **1 then 2 seconds** inside each layer, the caller has a **10-second deadline**, and each supplier call costs **USD 0.001** solely for arithmetic practice. No AWS service has that price in this exercise.

## Predict before running

For **100** customer requests whose supplier calls all fail transiently, write down:

1. Supplier calls and sequential elapsed time for one request when both layers each permit three tries.
2. The fictional supplier-call subtotal for all 100 requests.
3. The same numbers when only the worker retries three times and respects a 10-second customer deadline.
4. Whether either failed plan produced a completed repair. If none completed, what is its cost per completed repair?

Run the model:

```sh
python3 examples/retry-budget/lab.py
python3 -m unittest discover -s examples/retry-budget -p 'test_*.py' -v
```

Read the output's `calls`, `elapsed_seconds` and `outcome` separately. The shared-budget policy also permits both layers to exist, but gives their combined supplier calls one limit of three. It stops before an unnecessary fourth call or wait. Compare it with one retrying layer. A real system also needs one owner for retry policy across SDK, queue, workflow and application layers; configuring one layer does not prove the others are disabled.

## Change one fact

The supplier succeeds on call **three**. Does removing *all* retries still help the customer? Next, the supplier says **permission denied** on call one. Should another attempt be made under the same identity? Use `simulate(SINGLE_LAYER, succeeds_on=3)` and `simulate(SINGLE_LAYER, failure="permanent")` from `lab.py` to check. Then shorten the deadline to eight seconds with `Policy(1, 3, 3, 8)`. The first two calls and their intervening wait consume five seconds. The model skips the next two-second wait and third two-second call because they would finish at nine seconds. A call that finishes exactly at the deadline is allowed by this fictional policy; a real caller needs its own timing and cancellation contract.

Finally change the symptom to **lost reply after the supplier might have acted**. Do not use this arithmetic model to authorize another charge or assignment. You need the supplier's operation identity, replay contract or authorized status lookup before a retry can safely settle the unknown effect. The [queue recovery exercise](../queue-recovery/README.md) models that separate boundary.

AWS's [reliability retry guidance](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_mitigate_interaction_failure_limit_retries.html) recommends limiting retries and using backoff with jitter; it warns about retrying at several layers. The [AWS SDK retry reference](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html) explains that SDK calls may already retry under configured modes. **This fixture deliberately uses fixed waits and no jitter** so its arithmetic is reproducible. Its nine-call and 30-second result predicts no AWS SDK, queue, workflow or real customer latency. A production decision needs measured service behavior, request identity, downstream capacity, real pricing, stop conditions and a customer-outcome check.

Ask Codex to list every retry owner in a proposed request path and mark each attempt limit, elapsed-time limit, billable meter and external-effect risk. Check the answer against the actual SDK/workflow configuration and the customer's deadline. Preserve your own first answer, then compare with the [assessor reasoning](ASSESSOR.md).

## Twenty customers retry at once

Imagine twenty people calling the same busy desk. Telling everybody “try again in two seconds” creates another rush. **Jitter** gives each caller a different waiting time. AWS explains why correlated retries can amplify overload in its [timeouts, retries and jitter lesson](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/), checked October 30, 2026.

The companion scheduler uses a new, separate fictional scenario: twenty clients start together, each call lasts one second, every call fails, and each client permits at most four calls before a twelve-second deadline. Retry wait caps grow from two to four seconds, then stay at four. Fixed waiting uses the whole cap. Full jitter chooses a wait uniformly between zero and that cap. A fixed random seed makes this demonstration replayable; it is not advice to give every production client the same seed.

Before running, predict whether spreading retries must also reduce total calls. Then run:

```sh
python3 examples/retry-budget/jitter.py
```

The default seed produces this comparison. A bucket counts retry **starts** during one second; it excludes the twenty initial starts at time zero. It does not measure concurrent requests or service capacity.

| Policy | Retry starts in the busiest one-second bucket | Total calls | Completed operations |
| --- | ---: | ---: | ---: |
| Fixed waits | 20 | 60 | 0 |
| Full jitter, seed 7 | 12 | 80 | 0 |

The fixed clients start at seconds 0, 3 and 8. Their next call would finish after the deadline. Shorter randomized waits let all twenty clients fit a fourth call in this particular run. The busiest retry bucket is smaller, but the work count is larger and nobody succeeds. That is why a graph showing smoother traffic cannot by itself justify a reliability or cost claim.

Try a different seed using `compare(seed=8)` in `jitter.py`. Then give two clients identical draws with `schedule([.5, .5, .5])`. Their schedules match: randomness does not guarantee that collisions disappear. Give one client `schedule([0, 0, 0], deadline=2)`; only starts at seconds zero and one fit. Even a zero wait does not remove call duration from the deadline.

Ask Codex to argue that the smaller peak proves the change is safe. Challenge that answer using the total call count, absence of successful operations and missing capacity model. For a real decision, independently inspect the SDK's existing retry behavior, operation replay safety, total attempt budget, actual latency and service recovery. This scheduler implements none of those service behaviors and is not an AWS SDK retry algorithm. It makes no network calls and requires no cloud cleanup. See the [assessor notes](ASSESSOR.md) after recording your prediction.
