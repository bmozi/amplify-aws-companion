# Decide whether a CDN solves a measured need

Read the [network path lesson](../../reader/BOOK-LOCATORS.md#book-6948135871204c55). These fictional cases are a strategy screen, not a distribution-creation guide or AWS certification question. No cloud resources or traffic are created.

For each case, state the customer or operator promise, candidate path, content class, audience pattern, cacheability, authorization boundary, likely cost drivers, success measure and one condition that would make you reject or remove the CDN.

| Case | Supplied facts | Decision to make |
| --- | --- | --- |
| A — Public field guide | A public repair guide has the same images for everyone. Readers are spread across three continents; distant readers report slow image loads. Origin requests and latency by location have not yet been measured. | Is CloudFront a candidate? Name a baseline and a small first measurement that could reject the idea. |
| B — Private invoice | The invoice URL is `/invoice/current`. The response depends on the signed-in customer. A proposed cache rule uses only the URL path. | Should the response be shared at the edge? What positive and negative tests must pass before any future cache exception? |
| C — Nearby staff dashboard | One office team reads a small dashboard from a regional application. The response already meets its published latency target and origin capacity is not constrained. | What value could an edge path add, and what extra cost or troubleshooting boundary would it introduce? Is keeping the current path a valid decision? |
| D — Seat booking | A customer posts a booking request. The system must not confirm two reservations for one remaining seat. The front end could be globally accessed, but the write authority and retry behavior are regional. | Which read-path benefits might an edge service offer? Which correctness and recovery problems remain outside caching? |
| E — Frequently changed safety notice | A public safety notice must be withdrawn quickly when an authorized editor discovers an error. The team edits the same URL in place and has not agreed on the acceptable stale interval. | Compare explicit TTL, versioned path and invalidation approaches. State what old URLs, copies and offline downloads remain outside the control. |

## Compare before and after

Do not use “fast” as the whole objective. For a safe synthetic test or existing observation, compare:

- viewer p50/p95 latency across the audience locations that matter;
- cache hits, misses and origin request/byte volume;
- correct language/variant and fresh content;
- authorization denials for another customer's private response;
- origin failure and uncached-read behavior;
- current request, delivery, origin, security, logging and operating cost components.

The answers can differ by path. A public static image may benefit from caching while a nearby dynamic dashboard does not. A public request may still use an edge network while its dynamic result is not cached. A cached guide can load while a booking API is broken. A cache hit proves only that a matching stored response was served; it does not prove that current origin data, a private record or a write is healthy.

Ask Codex: “Challenge my CDN decision using only these fictional facts. Separate measured results from assumptions, list cost items I omitted, propose one changed constraint that would reverse my answer, and do not produce deployment commands.” After reviewing its critique, record which assumptions you corrected and which measurements remain necessary. Codex can help find a missing question; its response is not a performance measurement or a security test.
