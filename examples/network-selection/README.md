# Choose an entry point from the requirement

Read [the networking lesson](../../reader/BOOK-LOCATORS.md#book-6948135871204c55). These are fictional design cases, not deployment commands or certification questions. No cloud resources are needed. Write your answer before opening [the assessor notes](ASSESSOR.md).

For each case identify the requirement, the relevant layer, one bounded design choice, one rejected alternative, and the observation needed to test the claim. A service name without reasoning is insufficient.

1. **A DNS canary.** The team assigns a candidate ten percent of the DNS weight. It promises exactly ten candidate requests in the next hundred HTTP requests from one browser. Explain why the promise is unsupported and propose what to measure instead.
2. **A private cache.** The public guide and a customer invoice share the same edge distribution. Two customers request `/invoice/current`, and the proposed cache key distinguishes only the URL. The team wants the same shared caching rule for both kinds of content. Identify the risk and a conservative initial design.
3. **Two web services.** A hypothetical container application needs `/bookings` and `/invoices` to reach different groups of workers behind one web entry point. The proposal selects a Network Load Balancer because “network means everything.” Choose a more directly relevant candidate and explain the authorization work that remains.
4. **One worker disappears.** Each of two fictional workers sustains 40 requests per second within the required latency. Demand is 60. A reviewer says load balancing proves this architecture survives losing one worker. Calculate the remaining capacity and explain the missing evidence.
5. **Global equipment traffic.** Suppliers use a custom TCP protocol and require stable global destination IP addresses. The team proposes CloudFront because its public website uses it. Give a candidate path to investigate and name at least three requirements that still need verification. Do not claim measured acceleration.
6. **A reachable second Region.** The second endpoint passes a health check, but the team has not defined replication lag, write ownership or duplicate-request handling for appointment records. It proposes automatic regional traffic failover. Explain why this is not yet a complete recovery design and give a test that would challenge it.

Afterward, change one requirement and reconsider your choice: remove the global-IP requirement, make the guide private, or replace HTTP with a different protocol. Ask Codex to criticize your reasoning using official documentation, then record which claims you verified yourself. Keep proposed behavior separate from observed results.

## A21 extension: the guide loads but the booking is uncertain

Maya's public repair guide may be cached for five minutes. A booking confirmation is different: it promises a particular appointment to a particular customer. The business requires no duplicate bookings when customers retry. It has not yet approved a loss window for confirmed writes. Consider two designs before adding another Region:

```text
Option A
Public guide -> edge cache -> guide origin
Booking      -> one regional authority

Option B
Public guide -> edge cache -> guide origins
Booking      -> selected write authority
                  A or B
               -> reconciled records
```

Option A has less regional coordination work but needs an explicit regional-outage response. Option B adds another serving location and its recovery dependencies; the diagram does not supply replication, exclusive write authority or a shared duplicate-request record. Compare the actual customer requirements, recurring capacity and transfer costs before choosing. These are fictional design options, not deployed AWS architectures.

### Packet 7: cached success during an outage

The public guide loads from a previously cached copy. A new uncached page fails because its origin is unreachable. A dashboard counts only successful guide requests and reports healthy service. Decide what the evidence proves about the guide, its origin and the booking API. Propose separate observations for cached content, uncached origin retrieval and an authorized booking journey. Do not use a destructive customer booking as a casual health probe.

After your first answer, run the [loopback cache exercise](../global-web/README.md). Its warm public page and failed origin-dependent paths give local HTTP observations; its intentionally unsafe invoice cache supplies a cross-customer negative control. It does not emulate CloudFront or establish a real authorization boundary.

### Packet 8: a response disappears

At 10:00:00, Region A accepts logical request `booking-42` and commits appointment `appointment-19`. Its response does not reach the browser. The browser reports a timeout. At 10:00:02, Region B's copied records still end before that request, and B's health endpoint returns 200. A proposed client retry would send the same logical request ID to B.

Decide whether B's failure to find the ID proves the booking never happened. Explain why retaining a request ID is necessary but insufficient when each Region consults an incomplete independent duplicate-request record. Write the customer-facing pending message and the evidence required to turn it into a confirmed or rejected outcome. Keep the retry count and overall resolution deadline bounded; escalating unresolved work is different from retrying forever.

The desired record is one accepted logical request, one appointment and a stable result for later retries. Name the authority that can establish that result. If the available evidence cannot do so, preserve the uncertainty. A plausible answer generated by AI is not a booking receipt.

### Packet 9: choose the actual failover mechanism

The team proposes CloudFront origin failover for both public guide requests and booking `POST` requests. Check the official method restrictions before approving that claim. CloudFront's documented origin failover applies to `GET`, `HEAD` and qualifying `OPTIONS` requests, not `POST` or `PUT`. For `OPTIONS`, the cache behavior must also enable it as a cached method. A cache hit can be served without contacting the origin; origin selection and failover criteria matter when a request goes to an origin. [AWS origin failover guidance](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/high_availability_origin_failover.html).

Explain why enabling allowed HTTP methods is a different setting from obtaining failover for those methods. Do not change a booking mutation to `GET` to fit the failover feature: that would change HTTP operation semantics without solving data authority or duplicate effects. Propose a separate application recovery design, then use the [regional recovery exercise](../regional-recovery/README.md) to review its missing state and write-control evidence.

For a future implementation, include TLS, authenticated record access, request-size/rate controls, and protected access/incident logs in the design. Investigate appropriately scoped WAF rules and monitoring before public exposure, with current service eligibility and pricing; do not assume this worksheet installs them or makes them free. Keep private booking responses outside shared caching unless a tested access/cache policy establishes isolation. Compare build, edge requests, transfer, duplicated capacity and retained logs against spending and reserve limits chosen for the account. No live deployment is part of these packets.

Ask Codex to challenge your response: “Separate cached availability, origin availability, write acceptance and client knowledge. Identify which supplied fact changes each decision. Do not invent replication or a successful receipt.” Then remove the requirement for regional write recovery and reassess whether Option B is still justified.

## Observe a committed booking with no response

From the repository root, run Python 3 without optimization:

```sh
python3 examples/network-selection/lost_response.py
```

Predict the result before running. If the worker exits without printing a response, should a fresh process retry create another appointment? What changes when that retry uses an independent empty database?

The harness starts a separate worker process. The worker stores request `booking-42`, its full fixture content and a generated appointment ID in one SQLite transaction, commits, then exits immediately without printing its result. The parent observes the specific exit status and empty output, then opens the database independently and finds the committed appointment. Two new worker processes retry against that same authority and return the original appointment ID without changing the row. Reusing the ID with a different appointment time is rejected.

The counterexample sends the original request ID and content to a second, initially empty database. That store accepts it as new and creates a different appointment ID. Each database has a unique request key, yet together they contain two appointments for one logical request. This is a deliberately demonstrated defect in the proposed two-authority design, not a successful regional recovery.

The second database models the decision made without the first store's request history; it is **not** an implemented replica or a measured replication delay. The local transaction combines the booking and receipt in one row. It does not coordinate payments, notifications or another database. Input identity is trusted; there is no authentication, HTTP connection, global writer fence, actual region, concurrent-writer test or machine power-loss test. The forced exit demonstrates a process boundary after commit, not every transport failure. Temporary files are removed after the drill.

Inspect the output and explain why the same request ID works at the original authority but fails to deduplicate across independent authorities. Ask Codex to identify what would be needed to keep the guarantee if the receipt and booking were stored in separate systems. Do not infer that the program implements that change.
