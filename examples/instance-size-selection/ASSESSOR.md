# Assessor notes: instance-size selection

The fictional data is intentionally sufficient for a bounded decision, but not for a real AWS recommendation. Score whether the learner used the target and failure requirement, not whether they memorize a common size name.

## Calculation and intended decision

The 20% headroom requirement is interpreted as requested capacity being 20% above the observed peak: 700 × 1.20 = **840 requests/second** from the single surviving instance. Under that explicit assumption, the 2-vCPU/8-GiB size has only 700 requests/second of measured capacity and misses the 250-ms response target at that load. The 4-vCPU/16-GiB size handles 1,000 requests/second at the target benchmark and has p95 latency of 200 ms at 700 requests/second, so it is the smallest tested size that meets both requirements. The 8-vCPU/32-GiB size also passes, but its additional capacity has not been tied to a business need in this workload card.

The learner should state that the equation assumes the benchmark holds with all requests sent to the one survivor, the data path remains below its limits, and the two-zone load balancer/deployment behave as described. In real architecture, a 20% margin is a business or engineering choice, not a universal AWS rule. Different definitions are possible; require the learner to state theirs.

In the changed memory case, 14.5 GiB application memory plus 2 GiB of OS/agent/headroom gives 16.5 GiB. The 16-GiB candidate no longer satisfies the modeled memory requirement. The 32-GiB candidate is the next tested candidate in this family, but it must still be tested against the business promise and priced. If the memory-to-CPU mix is poor, reconsider the family rather than automatically buying more of a balanced configuration.

## Strong answer characteristics

- Keeps the already-selected family separate from the amount of compute/memory represented by size.
- Uses the benchmark rate and response-time goal, then checks the failover assumption when one zone disappears.
- Describes the measurement's coverage and gaps: representative input, concurrency, seasonality, cold start, retry and failure behavior, database, network, storage, and deployment version.
- Notes that CPU telemetry is not guest-memory telemetry by default. Additional memory metrics need the configured CloudWatch agent or another source; custom metrics and operations have their own costs and permissions.
- Reviews the whole operating bill for the candidate and current region, not only the hourly instance line. If more instances are needed for availability or peak load, include their minimum and failure-state capacity.
- Treats Compute Optimizer as historical evidence for supported resources, not a forecast or a substitute for current requirements and load testing.
- Uses the changed EBS-wait case to challenge vertical scaling: first measure the instance-to-volume path, volume characteristics, queue and application I/O behavior.
- Makes a provisional choice, records the test and review owner, and states an observation that would reverse it.

## Common errors

| Error | Why it fails | Correction |
| --- | --- | --- |
| Divide peak traffic by two instances, then size each for half | The remaining instance must handle the whole peak after a zone loss | Test the failure-state capacity explicitly |
| Choose the smallest size that passes normal traffic only | It misses the customer's failure margin or latency requirement | Check all stated conditions using the same benchmark |
| Select the largest size for “safety” without a requirement | It raises cost without demonstrating customer value | Find the smallest tested candidate that meets approved targets, then challenge its margin |
| Use average CPU to decide | Averages hide CPU peaks, memory pressure, I/O wait and downstream bottlenecks | Compare time-series and customer outcomes across relevant load and failure cases |
| Treat Compute Optimizer as a command | Historical metrics can omit future usage and selected types may be unsupported | Evaluate its evidence, current compatibility and representative performance before action |
| Assume CloudWatch already has EC2 memory percentages | Default EC2 metrics do not expose all in-guest resource data | Install/configure a metric source and include its operational and cost effect |

## Evidence boundary

No EC2 size, price, account, CloudWatch metric or Compute Optimizer recommendation was inspected. The arithmetic is reviewable because inputs are stated; the AWS performance and cost claims remain untested. No live availability, failover or learner result is established.
