# Select an EC2 instance size against the customer promise

This original design exercise supports SAA-C03 task 4.2 skill 06. It is not an AWS exam question, price quote or instance recommendation for a real workload. Do not launch instances for this paper lab.

## The measured test card

A booking API has already selected a compatible general-purpose family. The team runs the same application build against three sizes of that family in a controlled fictional benchmark. Each test includes the same database and request mix. The measurements are invented for this exercise; they are not AWS performance claims.

| Tested size profile | Peak completed requests/second before the latency goal is missed | p95 response time at 700 requests/second | CPU p95 | Observed application memory peak |
| --- | ---: | ---: | ---: | ---: |
| 2 vCPU, 8 GiB | 700 | 270 ms | 80% | 5.5 GiB |
| 4 vCPU, 16 GiB | 1,000 | 200 ms | 62% | 5.8 GiB |
| 8 vCPU, 32 GiB | 1,400 | 175 ms | 52% | 5.9 GiB |

The owner sets these fictional requirements:

- During normal peaks, handle 700 requests per second with p95 response time at or below 250 milliseconds.
- Continue meeting those targets if one of two Availability Zones becomes unavailable. Each zone has one application instance and the load balancer can send all traffic to the survivor.
- Keep 20% capacity headroom above the measured peak when operating on one surviving instance.
- The benchmark found the shared database and network path remained below their approved limits through 1,000 requests per second. It did not test above that rate.
- A separate deployment check confirms that the chosen family, architecture, operating system, AMI and software license can use all three size profiles. Their current AWS names, regional support and prices still need to be looked up.

## Your decision

1. Calculate the minimum one-instance throughput needed to meet the 700 requests/second peak with 20% headroom. Show the units and formula.
2. For each tested size, check both the p95 latency limit and the one-zone-loss capacity requirement. Select the smallest **tested** size that passes all requirements. State why the largest size is not automatically better.
3. Explain why the two-instance normal deployment does not let you size each instance for half of peak demand when one-zone loss must be tolerated.
4. Estimate the month in the current AWS Pricing Calculator for two instances at the candidate size, then model a one-instance outage and the business's chosen failover duration. Add EBS, addresses, logging/monitoring, load balancing, backups, transfer and scaling-related items that the design actually needs. Keep current price date, Region, OS and assumptions with the estimate. Do not invent prices for this lab.
5. The team changes the product cache. A new representative benchmark records 14.5 GiB application memory peak; the OS, agents and safety margin require an additional 2 GiB. Recheck each size and explain what the revised result says about selecting a larger size in the same family versus revisiting the family choice.
6. In a second changed case, p95 latency rises while CPU stays below 35% and EBS queue/latency is high. Explain why adding vCPU or choosing a bigger general-purpose size may not help. Name what new evidence would separate instance EBS bandwidth, volume limits and application behavior.
7. Ask Codex to recommend a smaller size and challenge it with the one-zone failure and 20% margin. Require the recommendation to show the calculation, all limits, price source, Region and what it did not measure. Check every current type or cost claim independently.

## Calculation worksheet

| Test profile | Throughput requirement with headroom | Latency passes? | Capacity passes after one-zone loss? | Size decision | Remaining risk |
| --- | --- | --- | --- | --- | --- |
| 2 vCPU, 8 GiB | | | | | |
| 4 vCPU, 16 GiB | | | | | |
| 8 vCPU, 32 GiB | | | | | |

## Monitoring caveat

Default EC2 metrics include CPU but do not automatically provide all guest memory and application measurements needed for sizing. A CloudWatch agent can report memory, logs and other in-guest signals; installing and configuring it adds work and can add metric charges. State which signal supports each conclusion. An average CPU value alone does not explain p95 latency, memory pressure, EBS queueing or database wait.

Compute Optimizer may be a useful input when the instance type is supported and enough history exists. It bases recommendations on observed history, which can miss seasonal peaks or a new customer promise. Review the metrics and compatibility, and validate the proposed size with representative load before acting.

## Cost and safety guardrail

This is a paper exercise. It does not query Compute Optimizer, inspect account metrics or estimate an account bill. Do not purchase a compute commitment for an untested size. A future benchmark needs a scoped non-root identity, a whole-run estimate against spending and reserve limits chosen for its account, and a stop time and cleanup list before launch.

## Evidence boundary

This worksheet tests the reasoning process using fictional benchmark data. It does not show that an AWS instance meets the target, that a month of traffic follows the test, that one-zone loss is operationally successful, or that a selected size is cheapest. Owner approval, regional type/price validation, live performance and recovery evidence, independent review and learner outcomes remain separate.
