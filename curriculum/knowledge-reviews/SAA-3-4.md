# Networking knowledge review: SAA-C03 task 3.4

Internal editorial review, October 18, 2026. Compared all four current knowledge bullets in the [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain3.html#solutions-architect-associate-03-domain3-task4) with the stored bullet hashes; all matched. Ordinals below are our inventory positions, not AWS-issued objective identifiers. All four entries now have partial teaching and assessment evidence.

## Knowledge 01 — Edge service use cases

Unit 05's “Choose what the entry point must do” distinguishes reusable web delivery from static global entry addresses and regional endpoint routing. Its adjacent sections address private-cache isolation and why moving traffic does not move authoritative business state. Network-selection cases 2, 5 and 6 require a reader to apply those distinctions, reject an unsuitable alternative and specify missing observations. The separate assessor notes identify the expected reasoning without requiring one universal architecture.

This supports service-selection understanding. It does not establish a configured distribution, safe private-cache implementation, supported endpoint combination, improved latency or regional recovery. Those require service-specific configuration and tests. No learner result is recorded.

## Knowledge 02 — Network architecture

Unit 05 explains IP ranges, longest-prefix selection, per-subnet address headroom, routes versus permissions, return traffic and public/private configuration. Its local growth lab checks fictional address plans, including deployment overlap. Unit 18 adds application and DNS flow ownership and overlapping office addresses. Skill-review cases 01 and 02 require a topology drawing and growth reasoning; the hybrid exercise challenges a drawing with ambiguous addresses, failed DNS and uncertain response delivery.

A satisfactory response must identify actual source/destination ranges, the route and return path, the boundary permitting traffic and the capacity assumption. A subnet label or successful application response is insufficient. The local arithmetic and authored design assessments remain partial evidence: no deployed multi-tier topology, endpoint configuration, migration or route-propagation test is supplied.

## Knowledge 03 — Load-balancing concepts

Unit 05's “Distributing work does not create workers” distinguishes HTTP host/path selection from transport-flow selection. It explains connection lifetime, surviving worker capacity and health-check limits. Network-selection cases 1, 3, 4 and 5 test DNS-versus-request distribution, ALB/NLB fit, capacity after losing a worker and a non-HTTP global entry requirement. Their assessor notes require both the candidate and its limits.

This is conceptual selection evidence. Installed listeners, certificate/TLS configuration, target registration, draining, cross-zone behavior and measured load distribution remain untested. The arithmetic fixture is not a performance benchmark, and no independent learner assessment exists.

## Knowledge 04 — Connection options

Unit 18 now adds “Connect a network or expose a service,” comparing VPN, Direct Connect and the PrivateLink interface endpoint/service pattern. The text and request-path diagram explain why office connectivity and service exposure can coexist. It separates connection permission from application authorization and addresses initiation direction, DNS, encryption, shared dependencies and provisioned costs. Current AWS primary references support the service boundaries; the teaching example is not a deployed topology.

The hybrid exercise's six connection-selection cases and separate assessor notes test the comparison, office access, callback assumptions, wrong DNS answers, shared zonal dependencies and idle costs. Answers must identify a rejected alternative, changed requirement and future operation/denial checks. This closes the previously identified missing conceptual comparison and dedicated assessment, not the implementation gap. Detailed configuration, protocol/endpoint compatibility, live security/failover/cost evidence and independent learner results remain outstanding.

## Evidence locations

- [Network lesson](../../reader/BOOK-LOCATORS.md#book-6948135871204c55)
- [Hybrid lesson](../../reader/BOOK-LOCATORS.md#book-0b54b52a3c811230)
- [Network-selection cases](../../examples/network-selection/README.md) and [assessor notes](../../examples/network-selection/ASSESSOR.md)
- [Skill-review topology and growth assessments](../skill-reviews/SAA-3-4.md)
- [Hybrid cases](../../examples/hybrid-design/README.md)
- [Knowledge evidence ledger](../knowledge-evidence.csv)

These mappings record an internal review of existing material, not new execution evidence or complete task coverage.
