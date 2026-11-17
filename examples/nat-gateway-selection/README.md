# NAT gateway selection worksheet

This paper exercise practices SAA-C03 task 4.4 skill 01. It creates no VPC, routes, NAT gateways, endpoints, addresses or charges. Read [Unit 05](../../reader/BOOK-LOCATORS.md#book-32679e6fc448bd47), write the routing/cost decision first, then compare with the [assessor notes](ASSESSOR.md).

The unit also compares a managed NAT gateway with an owner-operated NAT instance. For an additional case, assume a small training system has low but unpredictable egress and can tolerate a documented short outage. One engineer proposes a small NAT instance because its EC2 hourly price appears lower. Compare the complete monthly bill and the owner work/failure responsibilities with an AWS-managed NAT gateway; change the scenario to a customer payment workload and explain which new capacity and availability evidence matters. Use current prices and explicit labor/capacity assumptions only for real planning; this worksheet contains no rate or quote.

## Scenario

A fictional service runs private workers in two Availability Zones. Each sends software updates and calls two AWS APIs. The service can accept a one-hour loss of outbound access in its training environment. Its customer workload cannot lose access to a payment provider for more than five minutes. Workers send 600 GB/month to the payment provider and 900 GB/month to the two AWS APIs. These volumes and outage promises are scenario inputs, not observed AWS measurements.

Compare four paths:

1. One shared zonal NAT gateway.
2. One zonal NAT gateway in each workload AZ, with each subnet routed locally.
3. One regional NAT gateway, after checking support and current behavior in the selected Region.
4. Private VPC endpoints for the AWS APIs where supported, plus a suitable outbound path for the payment provider.

## Workcard

For each path, draw subnet-to-route-to-destination flow and state:

- What happens when the NAT gateway's AZ or a workload AZ fails?
- Which traffic crosses AZ boundaries? Which traffic must reach the public internet?
- What destinations and protocols are covered? What remains without a route?
- What does the path cost in a quiet month and at the stated traffic volume?
- What assumption or business promise would make you change your recommendation?

Estimate using current regional pricing. Keep the cost equation visible:

```text
NAT cost = gateway hours + processed GB + applicable cross-AZ/data-transfer charges
Endpoint cost = endpoint hours (where charged) + processed GB (where charged)
```

Do not invent unit prices. Record the pricing-page/calculator date, NAT mode, workload AZs, hours, expected processed data, endpoint services, traffic direction and any transfer charges. Compare the whole path with equal availability assumptions. Gateway endpoints, interface endpoints and NAT are not interchangeable.

## Changed-case transfer

Reassess when the training workload becomes customer-facing; AWS API traffic grows to 95% of all bytes; the payment provider accepts traffic only from a fixed public IP; the required Region lacks regional NAT; workloads span three AZs; the team adds TLS inspection; or egress is no longer required. Explain the routing, availability, allowlist, security and cost term that changes. Verify product availability and pricing before any live lab. This worksheet is not implementation evidence.
