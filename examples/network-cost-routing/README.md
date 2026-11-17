# Compare routes by their full path cost

Run from the repository root:

```sh
python3 examples/network-cost-routing/lab.py
```

This exercise has no AWS credentials, internet access, package installs or persistent resources. It computes **teaching points**, not dollars. The rates below are invented so you can see how fixed hourly cost and per-GiB cost can reverse which path looks cheaper. They are not AWS prices and must never be copied into a budget.

## Before running

Predict each result, then run the calculator and explain why:

| Case | Path A | Path B | What changes |
| --- | --- | --- | --- |
| 800 GiB from a VPC workload to same-Region S3 | S3 gateway endpoint: 0 fixed points and 0 processing points in this model | NAT: 730 hours × 0.045 points/hour plus 800 GiB × 0.045 points/GiB | The endpoint route is eligible only for the stated same-Region VPC-to-S3 case; the NAT path also works as general egress but adds modeled fixed and data charges. |
| 100 GiB to another supported AWS API | One NAT gateway: 730 × 0.045 + 100 × 0.045 | Two interface endpoint Availability Zones: 2 × 730 × 0.030 + 100 × 0.010 | Low traffic leaves the interface endpoints' fixed hourly footprint spread over fewer GiB. |
| 500 GiB to the same API | Same formula as above | Same formula as above | More processed data changes the variable-cost balance; the model's cheaper result can reverse. |

The same-Region S3 route must still be associated with the right subnet route table and its identity/resource policies must allow the intended request. It is not a general internet route. Interface endpoint choices need supported-service, DNS, security-group, Availability Zone and redundancy checks. Either route may also have transfer charges outside this deliberately small model.

## Inspect the result

The program calculates each hourly and data-processing component separately. It checks that the S3 gateway endpoint comparison rejects a workload in another Region, and that the fictional API comparison is more expensive on the two-AZ interface-endpoint path at low volume but reverses at higher volume under the supplied sample rates.

The model deliberately omits service-specific data-transfer exceptions, taxes, free allowances, changes over time, request charges, NAT address costs, redundancy/capacity requirements, cross-AZ traffic, Transit Gateway, peering, internet egress and engineering/operations costs. Those omissions are prompts for an estimate, not zero-cost claims. A real comparison needs current AWS Pricing Calculator/service rates, the actual routes and usage measurements, and the business's security and failure requirements. Never remove an Availability Zone or security path just to improve one arithmetic line.

## Change the case

1. Recalculate for a 30-GiB and 2,000-GiB month. Find the sample model's crossover and explain why the crossover is not an AWS design recommendation.
2. Add a separately named cross-AZ traffic component. Explain which design can reduce it and what availability, duplicated capacity or recovery promise might be weakened.
3. Change the S3 destination to another Region. Explain why the gateway endpoint result is no longer eligible and list the transfer and endpoint choices you must price.
4. Add Transit Gateway to a three-VPC design. Include attachment hours, processed bytes and the charge owner; compare with the operational and routing limits of direct VPC peering.

Ask Codex to audit your units, omitted line items and changed assumptions. Give it fictional traffic values only. Ask it to return competing designs and evidence needed, not an AWS apply plan. The arithmetic is a local teaching fixture, not live network or billing evidence.
