# Who may talk to whom?

Read the [Chapter 4 segmentation lesson](../../reader/BOOK-LOCATORS.md#book-b61caf132a09a950). Maya's fictional repair shop has a public ALB, private application, private database and separate private worker. The worker uploads to one restricted S3 bucket and calls a public supplier API. The case's ports are 443, 8080 and 5432; they are **scenario inputs**, not recommendations for every application.

Before running anything, draw five required conversations and three forbidden ones. For each, mark the route, source egress rule, destination ingress rule, subnet forward and reply behavior, and any service permission. Distinguish the *network path* from the authority to read or change a repair record. Write your first answer before opening [assessor notes](ASSESSOR.md).

## Run the cloud-free contract check

From the repository root, with Python 3.9 or newer:

```sh
python3 examples/segmentation-contract/lab.py
```

The program reads [topology.json](topology.json), evaluates a deliberately small symbolic model, and makes six mutations. It opens no socket and calls no AWS API. `--json` prints the per-flow gates. You can copy `topology.json` to a temporary file and pass `--fixture PATH` to test a revision without changing the source fixture.

Predict each result first:

| Mutation | Which required path or forbidden path changes? | Which gate should explain it? |
| --- | --- | --- |
| Remove the worker's supplier route |  |  |
| Remove the database-to-application reply allowance |  |  |
| Remove the worker's S3 endpoint-policy allowance |  |  |
| Remove the worker's S3 identity allowance |  |  |
| Remove the fictional bucket's S3 allowance |  |  |
| Add worker egress to DB **and** DB ingress from worker |  |  |

Now change one fact at a time:

1. The supplier API is replaced by the *same-region S3 operation* already in the design. Would the worker still need public supplier egress or a NAT path? What evidence would show the actual route? Re-estimate the whole path without assuming that every AWS service has a gateway endpoint.
2. The worker now needs to record a processing result in the database. Decide whether a direct DB connection is justified or a bounded application API is preferable. If direct access is selected, state the exact DB operation, network rules, application credential, concurrency budget and failure recovery. “Both are private” is not a reason.
3. An operator broadens DB ingress but leaves worker egress narrow. What would the small model report for worker → DB? Why is the broadened rule still a review finding even if that single path remains blocked today? Then add worker egress and observe the new opening.
4. The S3 gateway endpoint reports available, but the worker gets an S3 access denial. Separate route, endpoint policy, identity policy, restrictive bucket policy and object/key access from one another. Which exact request and policy evaluation would distinguish them? The fixture models only three chosen allow flags, not IAM's full policy evaluation.
5. A return packet is stopped by a subnet ACL after the application opened a DB connection. Why does the stateful security group not make the stateless ACL remember that connection? Which rule order, port range and actual flow record would need inspection in AWS?

Ask Codex to critique your first drawing without naming a service for you. Let it challenge the least justified permission, then solve one changed case unaided. Record where the code is only symbolic: its routes are named pairs rather than CIDRs and prefix-list priorities; its security rules are exact tuple matches rather than AWS rule aggregation; its ACL reply flag omits ephemeral ports and rule numbers; its three S3 policy flags do not implement IAM. The exercise proves only that this local contract distinguishes its tested changes. It does not prove a deployed VPC, ALB, NAT, endpoint, policy, TLS handshake, supplier response, cost or customer result.

Before any account lab, use a scoped non-root identity, name the account and Region, inspect the actual resources and dependencies, estimate the whole run against spending and reserve limits chosen for the account, and define a stop and cleanup check. This packet creates no billable resource. The book's [whole-request diagnostic](../network-diagnostics/README.md) provides a separate local HTTP and longest-prefix example; neither lab replaces a live path observation.
