# Assessor guide — bandwidth selection

## Arithmetic

For a binary GiB input, the model converts `GiB × 2^30 × 8` bits, divides by the deadline in seconds, applies the stated overhead factor, and divides by the target utilization fraction. For the nightly 480 GiB in 120 minutes case, 20% overhead and 70% target utilization yield approximately **0.982 Gbps** of planning capacity. This estimate is not measured goodput. The exercise does not include external-office traffic, other VIFs, route convergence time, packet-rate ceilings, queuing delay or actual retransmissions unless learners add them.

For the 2.4 TiB migration case, 2.4 TiB equals 2,457.6 GiB. Under the same 120-minute, 1.2-overhead and 0.7-utilization assumptions, the planning rate is approximately **5.026 Gbps**. Sustained production traffic must be added before candidate capacity is judged. A standard VPN tunnel's documented ceiling is below this number; large-bandwidth VPN tunnels have different attachment and Region requirements. A Direct Connect port choice is a candidate for evaluation, not proof of end-to-end capacity. The capacity that matters is verified useful throughput across all bottlenecks and during the required failure state.

## Decision quality

- Require a directional demand profile, not only monthly transferred bytes. Bulk volume, short bursts, packet rate, concurrent flows and latency-sensitive calls can favor different mechanisms.
- For the nightly recovery case, test whether a single surviving path can carry the protected workload. Do not add both VPN tunnel ceilings as if they were automatically available as one pipe. Check actual routing, eligible attachment, Region, customer gateway, provider path and failover traffic distribution.
- For the migration case, add production traffic and any competing workload before comparing to a nominal interface speed. Verify sustainable end-to-end throughput under representative encryption, packet sizes, file counts and application behavior.
- For the shared Direct Connect case, a VIF rate limiter on a supported Dedicated connection can cap one VIF; excess traffic is dropped. It is static and can be oversubscribed against physical capacity. AWS documents direction-specific behavior: ingress may congest the physical port before AWS applies the limiter, so customer-side policing may also be necessary. Monitor both utilization and policed bytes/packets.
- For interactive plus bulk traffic, identify queue and buffer behavior, application timeouts, bounded retries, priority and fairness. A higher line rate can defer congestion without correcting uncontrolled queues or a slow database.
- Include port, provider, cross-connect, VPN, transfer, transit/data-processing, router, operations and failure-capacity costs that apply. No prices are present here.

AWS currently documents standard VPN tunnels up to 1.25 Gbps, Large Bandwidth Tunnels up to 5 Gbps for supported Transit Gateway or Cloud WAN attachments, and Direct Connect VIF Rate Limiters for Dedicated connections. These are changing service details and upper bounds/controls, not promises that a particular workload will attain its calculated rate. See the official sources linked from Unit 18 before real use. This exercise demonstrates no AWS capacity, failover, pricing or learner outcome.

