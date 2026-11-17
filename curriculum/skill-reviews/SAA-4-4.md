# Individual-skill review: SAA-C03 task 4.4

Internal editorial review, October 18, 2026. The official [Domain 4 objective](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain4.html#solutions-architect-associate-03-domain4-task4) includes seven network skills. All seven now have separate partial mappings; individual mappings do not establish full task or exam readiness.

## Skill 01 — Configure appropriate NAT gateway types

Unit 05, “Choose NAT egress from failure boundaries and traffic paths,” compares one shared zonal NAT gateway, one zonal gateway per AZ and the newer regional NAT gateway mode, while distinguishing a private endpoint from internet egress. The [no-cloud worksheet](../../examples/nat-gateway-selection/README.md) contrasts two-AZ training and customer workloads, makes failure boundaries visible, records processed traffic and asks for current regional price inputs.

Checked current AWS Domain 4 skill wording, NAT gateway basics, regional NAT launch/availability information and the regional-mode guide on October 18, 2026. Regional NAT mode was announced November 19, 2025 for commercial Regions, excluding GovCloud and China. Its exact feature support, route/address behavior and pricing must be verified for any implementation.

This is partial design evidence. Workload volumes and interruption budgets are fictional. No NAT gateway, route, VPC endpoint, regional price or route-failure behavior was tested. Independent technical review and learner response remain open.

## Skill 02 — Configure appropriate network connections

Unit 18, “Compare internet, VPN and Direct Connect as different paths,” starts from the destination, privacy, encryption, route and failure needs. The [hybrid design exercise](../../examples/hybrid-design/README.md#connection-selection-extension) adds four cases: public HTTPS access, near-term private VPN access, dedicated connectivity with a documented business need, and an unsupported claim that Direct Connect is automatically encrypted. The response rubric covers provider dependency, circuit diversity, encryption, throughput evidence, lead time and whole-path cost.

Current AWS primary documentation was checked October 18, 2026 for internet-gateway behavior/pricing, Site-to-Site VPN pricing and Direct Connect standard/flat-rate billing. This is a partial design mapping. No circuit, VPN tunnel, internet route or hybrid test was created. Workload volumes and outage requirements remain fictional. Selected provider/current prices, measured performance, independent technical review, learner response and broader exam readiness remain open.

## Skill 03 — Configure appropriate network routes to minimize transfer costs

Unit 05, “Choose routes with the whole bill in view,” starts with a private worker's destination and follows the matching route to its next hop. It distinguishes same-Region S3/DynamoDB gateway endpoints, billed interface endpoints for many other AWS APIs, and general NAT egress. A route-cost figure shows three distinct paths. The [local worksheet](../../examples/network-cost-routing/README.md) calculates fictional fixed-hourly and per-GiB components, demonstrates that a modeled preference can change with volume, rejects an ineligible cross-Region gateway-endpoint comparison and asks learners to include resilience, omitted transfer items and charge ownership.

The current AWS exam guide wording and primary endpoint, data-transfer, peering and Transit Gateway sources were checked October 18, 2026. No service rate is embedded as a current quote. This is partial evidence: no live route, endpoint, DNS policy, byte count or bill was inspected; model rates are fictional teaching points. Real workload eligibility, current complete regional pricing, charge allocation, failure testing, independent technical review, learner response and broader exam readiness remain open.

## Skill 04 — Determine strategic needs for CDNs and edge caching

Unit 05 already contains CloudFront-versus-DNS/load-balancer/Global Accelerator role distinctions, a private-response cache warning, versioned public publication, cache freshness/withdrawal reasoning, origin outage evidence and the write-versus-read boundary. Its new “Decide whether an edge cache earns its place” section adds the strategic gate: reusable content and distributed audience, measured latency or origin load, authorization and freshness, full cost, and a reason to retain or reject the added service.

The [CDN strategy assessment](../../examples/cdn-strategy/README.md) has five fictional cases and separate assessor notes spanning public content, customer invoices, a local dashboard, booking writes and an urgent safety notice. Current CloudFront cache-key, stale-response and pricing material was checked on October 18, 2026. CloudFront currently presents pay-as-you-go and flat-rate offerings; no live rate or plan is asserted in the lesson. This is partial evidence: there are no geographic measurements, distribution configuration, warm-cache tests, withdrawal test, complete workload bill, independent technical review, learner response or full exam-readiness evidence.

## Skill 05 — Review existing workloads for network optimizations

Unit 05 now teaches an evidence-first review: begin with customer, security, resilience and performance promises; map the actual attached routes and path; compare a relevant problem window with a normal baseline; and keep measured facts separate from hypotheses. A table distinguishes what route configuration, Flow Logs, NAT CloudWatch metrics, application/DNS/load-balancer telemetry and CUR/Data Exports can each establish. The [synthetic evidence packet](../../examples/network-workload-review/README.md) aggregates a small set of fictional flow observations while preserving an independent NAT metric, latency signal and billing view. Its local script intentionally does not join datasets or claim a cause. The October 26 correction leaves a `SKIPDATA` interval unmeasured rather than assigning it 8 billion bytes; two changed destination cases reject a premature S3 endpoint or savings claim. Two local negative/positive checks exercise that boundary. A separate assessor guide gives answer boundaries, disconfirming evidence and safe canary/rollback criteria.

Checked AWS primary Flow Logs field, delay, omission and limitation documentation; NAT directional metric descriptions; Cost and Usage report grain; data-transfer usage-type guidance; and Well-Architected data-transfer modeling on October 18, 2026. This is partial design and local-arithmetic evidence only. No live workload, AWS metric, bill or route was inspected; no real optimization or savings was demonstrated. Flow Logs, NAT metrics and billing have different collection and attribution boundaries. Independent technical review, learner response and broader exam readiness remain open.

## Skill 06 — Select an appropriate throttling strategy

Unit 05 distinguishes API Gateway rate/burst targets, AWS WAF application-request rate rules, shared application admission control or bounded queues, and billing alerts. The [four-case assessment](../../examples/throttling-strategy/README.md) varies burst traffic, shared source IPs, rotating IPs, replica count and a paid workload's budget promise. Its assessor guide distinguishes customer identification from authorization, edge protection from downstream capacity, approximate throttling targets from a hard business quota, and monitoring from prevention.

Checked current AWS primary API Gateway token-bucket and usage-plan guidance and AWS WAF evaluation-window, aggregation and caveat documentation on October 18, 2026. This is a partial design mapping; no rate, web ACL, API, budget or database control was configured or tested. No abuse pattern, production threshold, price, customer impact, independent technical review, learner response or full exam-readiness evidence is established.

## Skill 07 — Select appropriate bandwidth allocation for a network device

Unit 18, “Size network bandwidth from the deadline and the failure case,” teaches directional workload measurement, packet rate and mix, overhead, utilization headroom, transfer-deadline arithmetic and the surviving-path capacity requirement. It distinguishes Site-to-Site VPN tunnel ceilings, Direct Connect physical/LAG capacity, and Direct Connect VIF rate limiters. The [local planning worksheet](../../examples/network-bandwidth-selection/README.md) computes fictional required Gbps from volume/deadline assumptions and gives four design cases for a recovery transfer, large migration, shared VIFs and latency-sensitive traffic. The assessor keeps a configured ceiling, nominal service/port capacity, measured path throughput and application completion rate distinct.

Checked AWS primary Site-to-Site VPN limit, Large Bandwidth Tunnel and Direct Connect dedicated-connection, LAG and VIF rate-limiter documentation on October 18, 2026. This is partial mathematical and design evidence: all demand values are fictional; no device, tunnel, connection, VIF, price, failover or throughput was measured. Service features and regional eligibility change, so verify them for a real design. Independent technical review and learner response remain open.
