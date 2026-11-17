# Size and allocate network bandwidth

## Start with the promise

A design team is comparing VPN and Direct Connect for a hybrid workload. The link label is not enough: learners must estimate the rate needed for a transfer deadline, preserve useful capacity after a failure, and protect shared traffic without assuming that a configured ceiling is the same as measured throughput.

Run the standard-library model from the repository root:

```sh
python3 examples/network-bandwidth-selection/lab.py
```

The model converts fictional GiB/deadline values to a lower-bound link rate and applies explicit overhead and target-utilization assumptions. It is arithmetic, not a network benchmark, AWS quota oracle or quote. Change the inputs only when you can explain their source.

## Four design cases

| Case | Fictional facts | Decision to explain |
|---|---|---|
| Nightly recovery copy | Move 480 GiB within two hours. The model assumes 20% protocol/retry overhead and 70% target utilization. A second path must carry the protected recovery copy if the primary path fails. | Which VPN or Direct Connect candidate can meet the useful-throughput target on the surviving path? Which measurements are required before relying on it? |
| Regional migration | Move 2.4 TiB in two hours while production continues. | Does one path meet the calculated planning rate with production traffic included? If considering larger VPN tunnels, are attachment type, Region, customer gateway and failover behavior eligible? |
| Shared Direct Connect | Production, analytics and backup VIFs share one dedicated connection. Analytics can burst and starve time-sensitive production traffic. | Should VIF rate limiters or customer-side shaping be evaluated? Show that static allocations fit the physical link in the failure state, and account for packets dropped by a cap. |
| Interactive operations plus bulk copy | Operators need low-latency database calls while a backup transfer can fill the same path. | Bandwidth alone may not protect latency. Which queueing, shaping, priority, packet-rate, loss and application measurements matter, and how will the backup yield without losing required work? |

Use the [assessor guide](ASSESSOR.md) after writing your calculations and design. Include both traffic directions, units, peak and steady demand, overhead assumptions, headroom, single-failure capacity, route convergence, queueing and complete cost ownership. Distinguish a nominal service/port ceiling, a configured cap, measured path throughput and application completion rate.

## Guardrails

- The VPN and Direct Connect cases remain design-only. Do not create tunnels, circuits, transit gateways or VIFs for this worksheet.
- The workload values and utilization assumptions are fictional; the model uses no AWS credentials or prices.
- The remaining path must meet the stated promise during failover. If it cannot, explicitly revise the service promise or design; do not label a redundant diagram “resilient.”
- Confirm current AWS service limits, feature/Region eligibility, provider capacity and pricing before any real design.

