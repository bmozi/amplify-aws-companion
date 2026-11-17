# Hybrid-network design exercise

This is a fictional design review for [unit 18](../../reader/BOOK-LOCATORS.md#book-0b54b52a3c811230), not an executable VPN lab. Do not change local routes, DNS settings or AWS resources. An organization-dependent network design stays on paper until its account, authority, cost and governance requirements have been reviewed separately.

Maya has two offices and an AWS booking application. The offices currently share `10.20.0.0/16`; the proposed AWS VPC is `10.80.0.0/16`. The office parts API uses `parts.office.example`; the AWS application uses `booking.cloud.example`. These are illustrative names, not live endpoints. Staff need booking access, and an AWS worker needs the parts API. Both VPN tunnels terminate through one office router and internet connection in the initial proposal.

For each case, separate observation from hypothesis, propose one discriminating read-only check, name the smallest justified correction, and specify the business operation to repeat. Do not read [assessor reasoning](ASSESSOR.md) until you have written your own answer.

| Case | Fictional observation or changed requirement |
| --- | --- |
| 1 | Both offices claim that `10.20.8.9` is their parts server. A proposed route advertises only `10.20.0.0/16`. |
| 2 | A controlled HTTPS test preserving the correct hostname reaches the AWS app through its expected private address. A normal client lookup of the name fails. |
| 3 | The app records an incoming request, but the office client times out. No response arrival has been demonstrated. |
| 4 | Both tunnels report healthy before the shared office router loses power. The design document calls this two independent paths. |
| 5 | The backup link carries a small probe successfully, but the parts backlog grows during a full office workload. |
| 6 | DNS resolves and the application returns a correlated 403 for one employee. Another employee succeeds through the same office path. |

Now propose a revised architecture. Draw application requests/responses separately from DNS queries. Identify address-overlap treatment, authoritative namespaces, encryption scope, routing ownership, shared failure points and application permissions. Compare at least two feasible options; state which changed requirement would reverse the choice.

Supply a future test card for one failure: baseline, authorized target, exact fault, expected observation, stop conditions, recovery command/procedure owner, customer acceptance check, denial check and retained-resource inventory. Leave actual prices blank until verified for the selected design and date. This design exercise does not authorize the test card's execution.

Assessment is provisional: an answer is useful when it identifies a plausible distinguishing observation and preserves the business/access constraints. There is no uniquely correct complete architecture from the limited facts given. Missing evidence should remain explicitly unknown. No learner has yet been assessed against this exercise.

## Network-evidence review

The office booking request at 14:02 returns HTTP 403. The VPN dashboard reports a healthy tunnel. The affected client got the expected private address for `booking.cloud.example` at 13:55. A VPC Flow Log row for an application interface shows `ACCEPT` near 14:02, but the row has not been tied to the client's translated address and port. A teammate ran Reachability Analyzer from one AWS interface to the application interface and saw a reachable modeled path. No application request ID, employee identity decision, office firewall record or return-path trace has been supplied. These are fictional observations, not AWS telemetry.

Write a three-column **claim / evidence / still unknown** table. Explain which observations could refer to the same request and which have not been correlated. Identify the first two read-only checks you would ask the owners to make, in order, and what result would change your hypothesis. Include one reason an absent Flow Log record might not mean a network block. Preserve the intended hostname and TLS verification in any proposed client check.

**Change:** the employee's request now returns HTTP 200, but the booking confirmation never appears. Explain why the earlier network indicators still do not prove that the business operation finished. Name the application or data evidence needed to distinguish a delayed worker, rejected write, and missing confirmation delivery. Do not create resources to answer this paper exercise.

Ask Codex to challenge your first table and name a source it may be overinterpreting. Record its revision separately and check AWS-specific claims against the lesson's linked documentation. Use the [assessor notes](ASSESSOR.md#network-evidence-reasoning) after writing your own answer.

## Multi-VPC topology decision

This is a paper design packet for the [two-VPC lesson](../../reader/BOOK-LOCATORS.md#book-f1469fb7e08753a4). Do not create a peer, Transit Gateway, tunnel, endpoint or DNS resource. Keep the original offices' shared `10.20.0.0/16` distinct from AWS VPC A (`10.80.0.0/16`) and VPC B (`10.90.0.0/16`). The fictional parts-reporting worker in B needs only an authenticated booking-status API in A. A contractor in a co-location facility needs only the same read-only service, not general access to either VPC.

For each packet, draw the **forward and return** application path, the DNS query and answer, and the authorization boundary. Make a decision record with: business need; address ownership; selected connection; one rejected alternative; Region/AZ rationale; route-table/traffic-rule owners; encryption scope; failure test; idle and traffic cost; and the observation that would change your choice. Prices must be verified on the chosen date and Region before any live proposal. Read [assessor reasoning](ASSESSOR.md#multi-vpc-topology-reasoning) only after writing your own decisions.

| Packet | Changed fact to reason through |
| --- | --- |
| 1 — Two VPCs | A and B are the only AWS VPCs. B initiates HTTPS calls to A's private API. Decide whether a direct peer or Transit Gateway is justified. State the CIDR, subnet routes, return route, traffic permissions, DNS and API authorization checks. |
| 2 — Third VPC | Development VPC C (`10.100.0.0/16`) peers with A. A teammate says B can now reach C through A. Decide whether that works and whether B should reach C at all. Compare another direct peer with a segmented hub if more VPCs are expected. |
| 3 — Same office addresses | The acquired office must call the API but shares `10.20.0.0/16` with the first office. Compare renumbering, a documented translation boundary and service-scoped access. Explain why a hub or DNS alias alone is insufficient. |
| 4 — Co-location | A partner runs a client in a co-location facility and asks for a dedicated line into every VPC. The required operation is one read-only booking-status lookup. Compare public HTTPS if exposure is permitted, VPN, provider-arranged Direct Connect and a service endpoint pattern. Name the missing path from the co-location client to any private endpoint and distinguish connection permission from API authorization. |
| 5 — Region and zone | Candidate Region East is nearer most customers but farther from the office parts API; Region West reverses that relationship. No measured end-to-end timings or data-location approval are supplied. The proposal places two web workers in separate AZs but one required database writer and one office router remain single dependencies. State what measurements and requirements would choose the Region, what two AZs help, and which failure promises remain unsupported. |

**Change:** the reporting worker becomes an ECS task rather than a VM. Explain which network and identity facts must be redrawn; do not assume its container label creates a route or permission. Ask Codex to challenge the transitive-peering claim, identify an unintended development path, and list cost dimensions. Check its AWS claims against the lesson's linked primary sources. Record your unaided answer and assisted revision separately; the exercise does not deploy a network.

### Trace a request and its reply locally

Before reading the output, draw A (`10.80.0.0/16`), B (`10.90.0.0/16`) and C (`10.100.0.0/16`). Draw direct peers A–B and A–C. B wants A's booking API. Predict what happens if A has no return route, if B tries to reach C *through* A, and if B–C instead get their own direct peer and two routes. D (`10.80.128.0/17`) deliberately overlaps A. Both offices still claim `10.20.8.9`. Decide which of those problems a DNS alias could fix.

Run `python3 examples/hybrid-design/path_lab.py` from the repository root, then `python3 -m unittest discover -s examples/hybrid-design -p 'test_path_lab.py' -v`. The first program prints seven outcomes. The focused tests change a return route, insert a more-specific wrong hop, try transitive peering, and check partial overlap. The code uses Python's address math and one synthetic route table per VPC. It does not open a tunnel, create a peer or read AWS configuration.

`modeled_route_pair_present` is deliberately a modest result. It means the fixture found a one-hop peer and a matching route for each direction. It does **not** mean the selected subnets use those tables, a security group allows the request, TLS names match, the API authorizes the worker, or the customer receives a booking. `peer_transit_not_supported` follows the current [AWS peering rule](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-basics.html); the exercise is not an emulator of all route-table priorities or Transit Gateway. AWS describes [routes on both sides](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-routing.html) and [longest-prefix selection with additional priority rules](https://docs.aws.amazon.com/vpc/latest/userguide/route-tables-priority.html). The [assessor notes](ASSESSOR.md#local-path-model) explain the boundaries after your prediction.

For a changed case, remove B's route to A but leave DNS returning A's correct private address. Show why name lookup is no packet path. Then change the business promise: B may call only one read-only booking endpoint. Draw the traffic rule and application authorization checks missing from this route model. A later cloud experiment would need exact Regions, route-table owners, flow-log cost and retention, peering or hub charges, a complete estimate against the operator's chosen limit, applicable credit terms, a stop owner and cleanup evidence. This exercise does not authorize organization-wide network work.

## Connection-selection extension

Read unit 18's “Connect a network or expose a service.” These additional fictional cases require a design decision, not resource creation. For each, state the initiating caller, destination, candidate path, rejected alternative, encryption and authorization boundaries, DNS dependency, failure test and cost inventory.

First select a path for each brief:

| Brief | Workload fact |
| --- | --- |
| A | Public customers visit an HTTPS Amplify application; there is no private office-to-VPC requirement. |
| B | The main office needs access to private AWS application prefixes this week. Its existing device supports IPsec VPN, and the business accepts measured internet-path variation. |
| C | A distributed finance system moves a high volume to private AWS prefixes and has a documented path-variation and outage objective. The business is willing to arrange provider connectivity and fund a resilient design. |
| D | The team proposes Direct Connect because “private is always encrypted,” but cannot name a supported location, provider or second path. |

For each, decide whether an internet path, Site-to-Site VPN, Direct Connect, or a combination is justified. Record the security, route, availability and cost evidence needed before implementing it. A public HTTPS path is not automatically unencrypted; Direct Connect is not automatically encrypted; VPN tunnels can still share one customer router or ISP.

Then answer the existing six connection-selection cases below.

1. An office needs several AWS application flows. It has a compatible VPN device and internet access, but no dedicated circuit. Compare a VPN starting proposal with Direct Connect. Name the evidence that would justify changing the choice; do not invent throughput or availability guarantees.
2. A supplier workload already in a VPC needs only the parts API. General access to Maya's network is unwanted. Evaluate the interface endpoint/service pattern. Identify who operates the endpoint, load balancer and API and who authorizes the employee's request.
3. The supplier moves the calling client to its office. It deletes its office-to-AWS connection because “PrivateLink is private.” Explain the missing path and draw a design combining the mechanisms where justified.
4. The parts API must now initiate a new connection to a supplier webhook. A reviewer says existing API replies prove the callback works. Challenge that claim and compare a separate callback route with consumer polling.
5. The endpoint exists, but the office's hostname lookup returns an unintended public destination. Propose a read-only investigation preserving TLS validation. Explain why creating another endpoint is premature.
6. Two endpoint zones are configured, but all provider targets depend on one zonal component. No customers use the system overnight. Evaluate the claims “zone failure is covered” and “overnight cost is zero.”

Submit a diagram and a one-page decision record. Include one changed requirement that reverses your choice, one unanswered question, and an operation plus denial check that a future authorized test must pass. Read the corresponding assessor notes afterward. Record AI-assisted revisions separately from your first answer.

## Storage extension: working during an outage

Read the worked design in [storage unit 20](../../reader/BOOK-LOCATORS.md#book-316ad1ab1452bb2f). This extension is also design-only.

1. The office can open one cached manual, but a second technician needs an uncached manual. State what the first success proves and which dependency the second request adds.
2. A local photograph save succeeds immediately before the office disk fails. No upload confirmation exists. State what is known about the AWS copy and what evidence could resolve the uncertainty.
3. Use the chapter's 24 GiB allowance and 3 GiB/hour arrival rate. Calculate time to fill and time to the 18 GiB operating threshold. After six hours offline, compare recovery at upload rates of 5, 3 and 2 GiB/hour while arrivals continue.
4. Two offices edit the same instruction independently. Compare single-writer ownership, explicit review of competing revisions and unrestricted last-write-wins. Explain the business consequence of losing either edit.
5. All required files are local, but the identity provider is unavailable after a workstation restart. Define the missing acceptance test without disabling authentication.

Draw the selected design, separate local-save evidence from cloud-availability evidence, name a stop/degradation threshold and explain its cost. Ask Codex to challenge the design only after recording your first answer. Keep original and assisted reasoning separate; neither is a live outage test.

## Use the subnet's actual map

The earlier path model asks whether VPC A and B have a peer and broad routes. This continuation asks a more precise question: **does the specific worker subnet use the table with that route, and can the reply get home?** First read [unit 18's subnet lesson](../../reader/BOOK-LOCATORS.md#book-4e165baece9e0bf9) and inspect its [diagram](../../book/figures/hybrid-subnet-return-boundary.svg). The addresses, tables and permissions below are invented. No AWS API is called.

Before running anything, predict the first missing condition in each case. Draw the request and reply separately. Mark which check is DNS, subnet routing, security group, network ACL or application authorization.

| Case | One changed condition |
| --- | --- |
| Baseline | B worker `10.90.1.10` uses table `b-peer`; A API `10.80.2.10` uses `a-peer`. Each has a direct route through `pcx-ab`, request/reply traffic rules and application access. |
| Wrong B table | DNS still answers `10.80.2.10`, but the worker subnet is associated with `b-main`, whose only route is local. The useful `b-peer` table still exists. |
| Wrong A table | B can send, but the API subnet is associated with `a-main`, which lacks a route back to B. |
| API security group | Both subnet routes exist; the API inbound rule does not allow this HTTPS request. |
| API ACL reply | Request rules and routes exist; the API subnet's outbound ACL blocks the reply to the worker's client port. |
| Worker ACL reply | The API can send its reply, but the worker subnet's inbound ACL blocks that return port. |
| Application denial | DNS, routes and modeled traffic rules permit the flow, but the API does not authorize the worker identity. |

From the repository root, run:

```sh
python3 examples/hybrid-design/subnet_path_lab.py
python3 -m unittest discover -s examples/hybrid-design -p 'test_subnet_path_lab.py' -v
```

The program prints **all** missing modeled conditions, not a literal AWS packet-processing order. Eleven focused tests include a correctly resolved name with a wrong subnet table, a more-specific route to a wrong target and a combination of three independent denials. Compare your predictions with the [separate assessor](ASSESSOR.md#subnet-and-return-path-reasoning) only after the run. Then change the baseline so the worker security group blocks outbound 443 and both reply ACL rules are missing. Explain why adding a broader peer route alone repairs none of those denials.

This is a small Python decision model. Its booleans stand in for selected traffic-rule outcomes; it does not evaluate ordered ACL entries, all AWS route priorities, real security-group connection tracking, DNS resolver behavior, TLS, IAM or application code. It sends no packet and creates no AWS resource. A future cloud test would require the actual subnet associations, route/peer state, rule IDs, client port, authorized principal, request ID, return observation, cost estimate and cleanup plan. Organization-dependent topology remains design-only here.

## Ask both sides for an address

Maya's office needs `booking.aws.test`; the AWS worker needs `parts.office.test`. The first question starts at office DNS and conceptually uses an **inbound** AWS Resolver endpoint. The second starts in the VPC and conceptually uses an **outbound** endpoint and rule. Draw those two paths on the [figure](../../book/figures/hybrid-dns-two-doors.svg) before running the exercise. [AWS's Resolver explanation](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html) describes the real endpoint directions and forwarding rules; the names and addresses here are invented.

Predict four observations: which authority receives each first question, whether an old answer can remain after its authority changes, what the office receives after its rule disappears and the cached answer expires, and whether a correct DNS answer proves booking works. Then run from the repository root:

```sh
python3 examples/hybrid-design/dns_path_lab.py
```

The script starts four **loopback-only UDP DNS** processes: two small authorities and two forwarding resolvers. It sends real local A-record questions in both directions. The office-side cache uses a supplied clock and a 30-second synthetic TTL. At second 5 the private authority changes `booking.aws.test` from `10.80.2.10` to `10.80.9.9`, but the office forwarder still answers with the first value. At second 31 it asks again and gets the new value. At second 62, with its forwarding rule removed and the cache expired, it returns `NXDOMAIN` in this *fixture*. A real missing rule could follow a different configured resolution path; this response is not a Route 53 prediction. A query for the office name through the private-name rule also fails locally. The two directions require separate rules. No system DNS setting, VPN, AWS resource, application server or credit is used.

**Change one fact:** the office receives the intended current address, but the booking worker's subnet uses a table without the required route. Combine this DNS observation with the [subnet path exercise](#use-the-subnets-actual-map) and explain why a DNS edit cannot repair the application request. Next suppose the private record changes during an incident. Record which resolver each client used, answer, TTL, observation time, and whether it was a fresh upstream question before claiming all clients have moved. AWS notes that Resolver query logging does not log answers served from its VPC cache; an absent new log entry alone is not a failed lookup. [Resolver query logging](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-query-logs.html).

Ask Codex to draw the query and application paths separately and find a forwarding loop. Check its service-specific suggestions against [AWS's loop-avoidance guidance](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/best-practices-resolver-endpoints.html). Keep your first answer and correction apart. A later authorized AWS trial would need the selected VPC, endpoints, rules, private-zone association, query-path controls, TTL and logs, application request evidence, endpoint-IP hours, query charges, retention, a complete estimate against its chosen limit, credit terms and cleanup owners. Organization-dependent hybrid work remains design-only here. The local packet proves no AWS DNS, routing, TLS, authorization or customer outcome.
