# Assessor guide — network workload evidence review

## What the exercise can establish

The local script sums only the synthetic `OK` rows. `app-a` has 80,000,000,000 accepted bytes plus 2,000,000 rejected bytes; `app-b` has 12,000,000,000 accepted bytes plus 1,000,000 rejected bytes. The `SKIPDATA` marker has **no measured bytes or action** in this fixture. The missing interval is neither zero traffic nor an estimate of `app-b` traffic. The sample does not establish full workload volume. Its `source_group` labels are analyst additions, not VPC Flow Logs fields.

The independent synthetic NAT metric states 920 GiB from source. The fictional bill lists 900 GiB of NAT processing and 120 GiB of regional transfer. These aggregate figures cannot be directly joined to individual flow rows. AWS Flow Logs may be delayed, omit traffic and contain skipped data; byte counts and aggregation boundaries need scrutiny. NAT metrics show directional gateway totals, not per-application ownership. CUR usage types and product codes identify billed categories at their own grain, not individual requests.

## Strong response characteristics

- Separates observations from hypotheses. The increased p95 and retries are observed; the cause is unknown.
- Treats the high `app-a` sample traffic, NAT metric and billing rows as clues with different coverage, not a reconciled equality.
- Checks flow time windows, interfaces, directions, action/status and missing records, then verifies analyst-added identities independently.
- Inspects the actual route table association, destination/service, DNS, endpoint support, security rules, workload placement and account that owns each charge.
- Uses application traces/logs or measured request timing to connect a slow operation to a dependency. Flow Logs do not show application request latency.
- Preserves two-AZ availability. If proposing a route or endpoint change, checks permissions, failure behavior and path eligibility first.
- Defines a bounded canary/test, before-and-after windows, latency/error/availability/cost indicators and a rollback trigger.

## Common overclaims to reject

For the changed facts, a public software vendor is outside an S3 gateway endpoint's purpose; the proposal loses its destination premise. A verified same-Region S3 destination plus an attached NAT route makes a gateway endpoint a candidate, not an approved change or a quantified saving. Check the endpoint's service/Region and route-table fit, S3 bucket and endpoint policies, the application's actual destination and request behavior, multi-AZ path, and the traffic window. Canary one bounded source or path, preserve its customer outcome and rollback condition, and compare the resulting route, service metrics and later bill at their own grains. The 900 GiB NAT line includes unassigned traffic and cannot all be credited to S3.

- “The Flow Logs show the bill exactly.” Different capture and billing boundaries prevent that inference.
- “The endpoint will save 900 GiB of NAT.” No destination mapping or route proof establishes that all bytes are eligible.
- “The app with the most recorded bytes caused latency.” Volume and latency are separate observations without request correlation.
- “The data-transfer row proves cross-AZ traffic between these two app groups.” A billing usage type alone does not identify a specific packet path.

This synthetic exercise is partial design evidence only. It is not a live account review, cost reconciliation, pricing estimate, network test, certification item, or learner outcome measurement.
