# EBS volume selection case

This case is a paper design exercise. It creates no EC2 instance or EBS volume and contains no AWS price estimate. Write your choice and the evidence you still need before reading the [assessor notes](ASSESSOR.md).

## Three jobs, three shapes

An analytics team has three EC2-backed jobs:

1. A small transactional database reads and updates many small records in unpredictable locations. Its customer-facing response time has a strict measured target.
2. A frequently used log-processing job scans large files in order and must finish each scan inside a fixed window.
3. A historical archive is read only a few times each quarter, when analysts scan it sequentially. The business values low storage cost but has not stated its retrieval deadline.

For each job, propose an EBS family to evaluate. Explain why the alternative SSD/HDD pattern is a poor fit. State which workload measurement, instance limit, price input, backup decision and acceptance test must be checked before deployment. Do not invent a numeric price or claim that one type is universally cheapest.

## Changed constraints

- The database's measured IOPS doubles while its volume capacity stays the same. What should be remeasured before increasing a performance setting?
- The sequential scan now needs to boot the instance from the same volume. Which candidate becomes invalid?
- The archive must be readable within five minutes after an incident. Does “infrequent” alone settle the volume choice?

Ask Codex to challenge your volume choice, then verify its claims against current AWS documentation and regional prices. Record unaided and assisted reasoning separately.
