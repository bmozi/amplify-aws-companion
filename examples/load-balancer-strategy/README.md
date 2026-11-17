# Load-balancer strategy: match the traffic, then price the whole path

This fictional design case supports SAA-C03 Domain 4, task 4.2: choose a cost-optimized load-balancing strategy. It is original study material, not an AWS exam question. Requirements are deliberately split so the reader must match the service to the job before comparing prices.

## Brief

Maya's company runs three separate workloads:

1. A public HTTP application sends `/orders` and `/returns` to different service groups. It uses host and path rules and needs targets in at least two Availability Zones.
2. A supplier sends a proprietary UDP protocol. The supplier accepts one stable destination address per enabled Availability Zone and does not send HTTP requests.
3. A regulated internal segment must inspect selected traffic with the company's licensed virtual firewall appliances before it reaches the application. The security team owns appliance selection and patching. It can make subnet route changes and needs flow stickiness to an appliance.

The finance team asks which design costs least. Do not answer until each requirement has a viable design. Compare ALB for application-aware HTTP routing, NLB for transport flows and stable zonal addresses, and GWLB for inserting and scaling the virtual appliance fleet. A GWLB path also needs route-table decisions and GWLB endpoints where traffic crosses VPC boundaries. NLB is not an HTTP path router; ALB does not insert a packet-inspection fleet; GWLB is not a general web load balancer.

```text
HTTP clients --> ALB rules --> orders and returns targets
Supplier UDP --> NLB -------> protocol targets
Internal subnet --> GWLB endpoint --> GWLB --> firewall fleet
       ^______________________________________________|
```

The drawing is a responsibility map, not an implementation diagram. For the real design, draw both directions of traffic and verify routes, security controls, target health, Availability Zone placement and return paths. AWS requires ALB in at least two Availability Zones. NLB/GWLB cross-zone behavior and target placement are explicit design choices; verify current defaults and data-transfer implications before estimating.

For a calculator practice run, assume each service stays available for 730 hours in an illustrative billing month across two Availability Zones. These invented numbers are practice inputs only, not measurements or a forecast:

| Workload | Fictional monthly planning inputs |
| --- | --- |
| ALB web app | 4 listener rules; 20 requests/second on average, 60 at peak; average 2-minute client connections; 100 KB processed per request across both directions |
| NLB partner protocol | 10 new UDP flows/second on average, 40 at peak; average flow lasts 2 minutes; 50 KB processed per flow across both directions; one static address per enabled zone |
| GWLB inspection path | 2 consumer endpoints, one per zone; 5 new flows/second on average, 20 at peak; average flow lasts 3 minutes; 2 GB/hour processed across the load balancer; at least one licensed appliance target per zone |

State which usage inputs are needed by each capacity-unit dimension and which of average or peak drives your assumption. If a product calculator asks for a value this brief does not define, write down your assumption instead of presenting it as fact. The three monthly totals answer different jobs; do not rank them as interchangeable designs. Compare candidates only within the same requirement, after removing designs that cannot meet it.

## Work to submit

For each workload, write:

- The protocol and decision the load balancer must make.
- The candidate that satisfies it and why each other type is ineligible or adds no needed function.
- A request/packet-flow sketch, including return traffic and any target or appliance dependency.
- A full monthly cost model with the current AWS Pricing Calculator for the intended Region and realistic usage. Record inputs and date, not just the total.
- One observation that would change the choice.

Keep these cost inputs separate so a low load-balancer line item does not hide the operating bill:

| Cost area | Inputs to collect |
| --- | --- |
| Load balancer | Hours running; ALB LCU, NLB NLCU or GWLB GLCU traffic dimensions; rules and connections where applicable |
| Network path | Bytes processed, cross-zone behavior, endpoint count and endpoint data, inter-AZ/Region transfer, internet egress |
| Targets | EC2/ECS/EKS/Lambda capacity, health-check and failover headroom, scaling floor |
| Inspection | Appliance instances or vendor service, licenses, support, patching, logs and redundant capacity |
| Operations | Monitoring retention, testing, deployment, incident response and architecture-specific maintenance |

No rates are embedded because prices vary by Region, time and workload. Do not treat the provider's license or target compute as included in a load-balancer price. Do not assume the lowest per-hour example is the lowest full-path cost.

## Changed constraints

1. The web app no longer uses host/path rules and serves one HTTP target group. Which requirement disappeared, and what should be re-evaluated before paying for ALB rules?
2. The supplier changes from UDP to HTTPS and now requires `/device/*` routing to separate target groups. Which load-balancing function is needed now, and can the stable-address requirement still be met by the chosen design?
3. Security removes mandatory inline inspection and accepts a managed, out-of-band detection service. What GWLB, endpoint, appliance and route costs may no longer be justified? Identify the security evidence still required before removing the path.
4. Inspection must span four consumer VPCs in two Availability Zones. Recount endpoints, appliance capacity, routes and data transfer rather than copying the single-path estimate.
5. Demand is nearly zero overnight but the service must remain reachable. Which hourly charges remain, which usage charges vary, and which target capacity can safely scale down?

Use the official current pricing pages and calculator for estimation. AWS pricing documentation describes load-balancer usage units and separate GWLB endpoint charges; this exercise includes no quoted rate and no live account bill.

## AI-assisted study

Ask Codex to challenge the requirements before it recommends a product: “List the packet or request facts that justify each load balancer. Flag any service that cannot satisfy a stated requirement. Build a cost-input checklist without inventing prices. Then change one requirement at a time and show what design evidence must be rechecked.” Verify every service behavior and price against current AWS documentation. AI output is a draft explanation, not a tested topology or a bill estimate.

Sources: [official SAA-C03 Domain 4 objective](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain4.html#solutions-architect-associate-03-domain4-task2), [ELB routing behavior](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/how-elastic-load-balancing-works.html), [GWLB overview](https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/introduction.html), and [ELB pricing](https://aws.amazon.com/elasticloadbalancing/pricing/).

See [assessor notes](ASSESSOR.md) after completing the case.
