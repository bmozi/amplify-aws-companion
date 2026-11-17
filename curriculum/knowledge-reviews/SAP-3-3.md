# SAP-C02 task 3.3 performance-improvement review

Internal editorial review, October 19, 2026, against the transitional [official task 3.3 guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain3.html#solutions-architect-professional-02-domain3-task3). Four knowledge points and five skills have **partial** teaching and authored changed-case evidence. This is neither a cloud benchmark nor SAP-C03 coverage.

| Point | Teaching and assessment evidence | Still needed |
| --- | --- | --- |
| Knowledge 1: high-performing architectures | Unit 02 follows the limiting stage before choosing a fleet, rightsize or cluster placement; cases 1, 4, 7 and 9 change CPU, downstream capacity, resource shape and inter-node wait. | Selected fleet and placement feasibility, measured peak/failure behavior and full cost. |
| Knowledge 2: global offerings | Unit 02 and Unit 05 separate CloudFront's HTTP content path from Global Accelerator's TCP/UDP endpoint path; case 8 changes the dominant wait to database work. | Selected protocol, geography, cache isolation, endpoint health, price and measured customer result. |
| Knowledge 3: monitoring tools | Unit 08 separates customer percentiles, logs, metrics and traces; case 1 contrasts flat CPU with rising connection wait and p99. | Configured telemetry, correlation, coverage and missing-data evidence. |
| Knowledge 4: SLAs and KPIs | Unit 02 and the packet define a fictional search target with population, window and correct completion while separating provider commitments. | Approved customer promise, current provider terms and measured workload. |
| Skill 1: requirements to metrics | The weekday-opening search target names eligible requests, clock, window, failures and correctness. | Real owner-approved target and representative measurement. |
| Skill 2: test remediation | The chapter and packet require same-mix baseline/candidate cohorts, disconfirming evidence, cost and rollback. | Bounded selected workload trial and independent interpretation. |
| Skill 3: new technology | Cases 8 and 9 force service proposals to answer a measured path, protocol and operating responsibility. | Regional eligibility, security, full price and observed performance. |
| Skill 4: rightsizing | Unit 02's peak/failure margin and case 7 challenge a memory-only conclusion with I/O evidence. | Representative family/size trial, runtime compatibility and price. |
| Skill 5: bottlenecks | The whole-path table and cases 1, 4, 8 and 9 separate app, store, network and inter-node waits. | Correlated real traces and service metrics under peak and failure. |

The [nine-case packet](../../examples/professional-performance-path/README.md) and [assessor](../../examples/professional-performance-path/ASSESSOR.md) are fictional. The existing [cold-cache local lab](../../examples/cold-cache-burst/README.md) tests one-process concurrency, not AWS performance. [AWS network-location guidance](https://docs.aws.amazon.com/wellarchitected/latest/framework/perf_networking_choose_workload_location_network_requirements.html) and [EC2 placement-group guidance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/placement-groups.html) were checked for service distinctions. No account resource, charge, benchmark or learner result was produced in this review.
