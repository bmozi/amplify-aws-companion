# Five checks before a customer request reaches its data

A customer clicks “View my invoice.” Before the application can safely do that, several separate questions must have good answers: who is the customer, which record belongs to them, where should the request travel, what secrets can the worker use, and which outside threats need controls? A green check at one step does not automatically answer the next.

This design exercise covers five task 1.2 knowledge points with individual partial evidence mappings. The [security-service selection point](../security-finding-review/README.md) already has its own mapping and seven cases. These are original practice cases, not official exam questions. Do not configure AWS or send real traffic to test them.

## Follow Maya's invoice request

For each case, write: **what the business needs; which component enforces it; what could still go wrong; a safe next test; and what would change your design.** Try the question before opening the linked existing exercise, then record your revision. The companion labs use local or fictional inputs and do not prove live AWS behavior.

1. **Configuration and credentials.** A booking worker needs a supplier password; a browser needs only the supplier's public URL. A teammate proposes putting both values in the website build settings. Decide which value is a secret and where each belongs. Then the supplier accepts a new password while one warm worker still uses the old one. How should the team restore access without logging the password or retrying forever? Use the [credential-lifecycle exercise](../credential-rotation/README.md); then change the case so the secret store is temporarily unreachable.
2. **Service endpoints.** A private worker sends same-Region photos to S3 and also calls a different AWS API. A diagram shows one “private endpoint” for both. Explain why endpoint type and service scope matter, and compare the supported endpoint path with general internet egress and its full cost. Then change the S3 destination to another Region. Use the [route comparison](../network-cost-routing/README.md); its sample rates are fictional teaching values, not AWS prices.
3. **Ports, protocols and network traffic.** The browser needs HTTPS to the public application; the application needs one database port; nobody should connect to the database directly from the public internet. A security group allows the request, but the response times out after a subnet ACL edit. Trace the required direction, protocol, port and return path. Separate TLS server verification from customer authorization. Use the [network lesson](../../reader/BOOK-LOCATORS.md#book-6948135871204c55) and [TLS boundaries lab](../tls-boundaries/README.md), then change the case so the request succeeds but asks for another customer's invoice.
4. **Secure application access.** Alice and Bob belong to different repair shops. Both have a record called `shared-id`. Decide what sign-in establishes and what the application must check before returning a record. Then let a background job run after Alice's membership is revoked: what identity and authority should that job use? Use the [tenant-isolation exercise](../tenant-isolation/README.md) and [application identity lesson](../../reader/BOOK-LOCATORS.md#book-422c5f26d4302648). The local fixture does not configure Cognito or an AWS policy.
5. **Threats from outside AWS.** A public form accepts text that later becomes part of a database query, and a bot sends a burst of requests that threatens service capacity. Explain why SQL injection and denial-of-service are different threats and why one control cannot promise to stop both. Identify what request filtering, application query handling, rate/capacity limits and customer authorization each contribute. Use the [threat review](../threat-review/README.md), [layered request lab](../layered-request-boundary/README.md), and the lesson on [protection at the boundary it understands](../../reader/BOOK-LOCATORS.md#book-23c89700c50c9c00). Then change the case: ordinary customers share a carrier address, so a simple per-IP rule blocks legitimate users.

## Use Codex after your first answer

Ask Codex to challenge one case at a time. Provide only fictional values and sanitized diagrams. Ask it to label documented service behavior, your assumptions and missing evidence separately. Do not ask it to generate deployable rules from this worksheet. Save your first answer, AI critique, revised answer and the source you checked; a fluent answer does not prove an AWS control works.

| Case | Initial answer | Changed condition and revision | Next evidence needed |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

Continue with [the network path lesson](../../reader/BOOK-LOCATORS.md#book-6948135871204c55), [identity and authority](../../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [tenant isolation](../../reader/BOOK-LOCATORS.md#book-422c5f26d4302648) and [security findings](../../reader/BOOK-LOCATORS.md#book-367ab937e61db26d). Each goes deeper on one boundary; this exercise connects them around one customer request.
