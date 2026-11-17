# Individual-skill review: SAA-C03 task 3.4

Internal editorial review, October 18, 2026, with a focused Skill 01 evidence recheck on October 26. The [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain3.html#solutions-architect-associate-03-domain3-task4) has four skills. This review maps partial teaching and assessment for all four editorial ordinals. The growth review has a local address-plan lab; neither local model establishes a deployed scalable network configuration.

## Skill 01 — Draw the topology from required flows

A company has an office parts API and a cloud booking service. Draw the request and return paths for office staff, the cloud worker's parts lookup, and both directions of private name resolution. Add a newly acquired office that overlaps the original private address range. Explain what is ambiguous and compare renumbering with a narrowly scoped application-access boundary.

Look for distinct application and DNS flows, explicit direction and ownership, both return paths, an address plan and no claim that a name alias resolves overlapping destination addresses. The reader must extend the drawing with actual subnets, routes and controls before implementation. Teaching: unit 18, “Inventory before connecting” and “Resolve address ambiguity explicitly”; unit 05's web entry diagram adds the distinction between DNS lookup and HTTP forwarding. The [hybrid cases](../../examples/hybrid-design/README.md) and their assessor notes supply further failure variants.

The authored office topology prompt is design-only. A separate [subnet and return-path exercise](../../examples/hybrid-design/README.md#use-the-subnets-actual-map) now runs seven fictional changed cases and an eleven-test local model. It distinguishes a correct DNS answer from the worker subnet's *selected* route table, the API subnet's return table, a security-group request denial, two network-ACL reply denials and application denial. The model also catches a more-specific wrong route and independent simultaneous denials. This is executable evidence about the supplied model, not a packet sent through AWS.

AWS's current [subnet route-table guide](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-route-tables.html) confirms that an explicit association selects a subnet's table and an otherwise unassociated subnet uses the main table. The [network ACL guide](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html) distinguishes stateless request/reply rules from stateful security groups; the [security-group guide](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) confirms tracked replies. These sources support the teaching boundary, not the fixture's invented address plan or an effective rule in the user's account.

Address allocation and propagation, selected endpoint configuration, actual subnet associations and traffic controls, live multi-tier reachability, customer authorization and independent topology assessment remain open. Organizational designs remain unprovisioned in the personal trial account.

## Skill 02 — Plan for growth during transitions

Use [the growth-planning lab](../../examples/network-growth/README.md). Predict ordinary, deployment-overlap and recovery allocations before running it. Explain why three free addresses fail a ten-address reserve, why another subnet is not a shared address pool, and why two adjacent `/25` allocations cannot coexist with one expanded to the encompassing `/24`.

Teaching: unit 05, “Leave address space for the busiest transition.” The local program checks private IPv4 range containment/overlap and fictional demand, including exact-fit and one-over boundaries. A deliberately wrong two-address reservation rule fails the known AWS five-address fixture. These are calculations and input validation, not live resource allocation. Actual service-specific allocation, quotas, throughput, connection behavior and a migration/configuration exercise remain open. The assessment must require these limitations as well as the correct arithmetic.

## Skill 03 — Place resources using the complete operation

A booking performs six sequential parts lookups across a fictional 40-millisecond round-trip path. A proposed change moves only the web server nearer the browser. Explain the unmeasured assumption in claiming that booking becomes fast. Calculate the network contribution from those lookups; compare a semantically equivalent batch. Then change the requirement: one Availability Zone must be lost without violating the business response objective.

Expected reasoning: six times 40 equals 240 milliseconds; one equivalent lookup contributes 40, a hypothetical reduction of 200. Processing and other calls remain outside those numbers. Batching or parallelism must preserve correctness; neither is established by arithmetic. Draw service targets and their data/control dependencies, cross out one zone, and identify surviving capacity and shared dependencies. Include private-data placement, logs, backups and service availability in the decision. Reject “nearest to users” as a complete placement argument.

Teaching: unit 05, “Place resources around the work they perform.” A strong answer compares two placements and names an observation or changed requirement that would reverse the recommendation. No measured network latency, residency determination, deployed zonal topology or failover test is established.

## Skill 04 — Select the load-balancing strategy

Use [network selection cases 1, 3, 4 and 5](../../examples/network-selection/README.md), then consult [assessor reasoning](../../examples/network-selection/ASSESSOR.md). Distinguish DNS answer selection, HTTP host/path routing and transport-flow routing. Explain why a DNS weight is not an exact per-request traffic allocation, a long TCP connection matters to work distribution, and load balancing cannot replace missing worker capacity.

Teaching: unit 05, “Distributing work does not create workers,” supported by the adjacent DNS and regional-entry sections. The candidate service must match protocol and routing requirements. Include target health limitations and the documented ALB all-unhealthy behavior; a health check does not prove business correctness or enforce record ownership.

This supports a partial selection review, not installed listeners, TLS policies, target registration, connection-draining tests, cross-zone configuration or measured load distribution. The original cases are editorial assessments, not AWS exam questions. No independent learner result is recorded.

## Remaining task work

All four mapped skills remain partial. Growth teaching now covers bounded address planning, but service-specific limits and configuration evidence remain outstanding. All four separate knowledge bullets now have partial individual reviews in [the knowledge review](../knowledge-reviews/SAA-3-4.md), including the added connection-options comparison and design assessment. Actual service configuration and learner evidence remain open. Skill coverage does not establish knowledge coverage automatically. Do not infer task completion from four partial ledger rows.
