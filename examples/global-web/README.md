# A21 Separate a cached page from a safe booking

Read [the A21 networking lesson](../../reader/BOOK-LOCATORS.md#book-3a0e495a74946954) and [entry-point packets](../network-selection/README.md#a21-extension-the-guide-loads-but-the-booking-is-uncertain) first. This local Python fixture uses a loopback HTTP server and invented invoice strings. It does not configure CloudFront, Route 53, a second Region, authentication or an AWS bill.

Maya's public guide can be cached. Her private invoice cannot be shared between customers, and a booking requires its own authoritative write path. Predict the four observations below, then run from the repository root:

```sh
python3 examples/global-web/cache_boundary.py
python3 -m unittest discover -s examples/global-web -p 'test_*.py'
```

| Local condition | Question to answer before running |
| --- | --- |
| Deliberately unsafe URL-only invoice cache, warmed by Alice | What bytes does Bob get from the same `/invoice/current` URL? |
| Private responses excluded from shared cache | Do Alice and Bob receive distinct fixture bytes? What does a stranger header get? |
| Public guide warmed, then origin marked unavailable | Which guide still loads, and what happens to an uncached guide request? |
| Same outage, private invoice and booking request | Does a cached guide's 200 prove either business path works? |

The negative control **intentionally leaks Alice's invoice to Bob**: it looks up the shared URL before checking the actor. The safer fixture never stores a private response in that shared cache. It returns each selected actor's own bytes, and an unrecognized actor string gets 403. These responses do **not** prove authentication: `X-Fixture-Actor` is a caller-supplied test header, so someone could claim `alice`. A real application must derive identity from a verified session/token and enforce record ownership at its origin. Adding an untrusted actor header to a cache key would not repair that authority problem by itself.

After the public guide is warmed, the fixture marks its origin unavailable. A warm guide request still returns 200 from the local cache; the uncached guide, private invoice and synthetic booking request return 503. This is a contrast between observations, not a model of CDN propagation, origin failover, DNS behavior, or a write whose response was lost. Use the separate [lost-response drill](../network-selection/README.md#observe-a-committed-booking-with-no-response) for that uncertainty.

Change the case: suppose the guide contains a customer's name. Should it still follow the public cache rule? State the classification, exact cache key and access decision, source of trusted identity, retention/withdrawal behavior, and the positive and cross-customer denial tests needed before reuse. Ask Codex to challenge your first answer with a warm-cache bypass and a cached-success/failed-booking observation. Compare with the [assessor notes](ASSESSOR.md) after writing your own decision.

## Bring bookings back with their receipts

The cache case asks whether a page can load. This next case asks whether a confirmed booking survives **returning** from a recovery location. Read [the illustrated return-trip lesson](../../reader/BOOK-LOCATORS.md#book-82b02ac5cd03762a), then predict what the first store knows after the second store accepts Bob. Run:

```sh
python3 examples/global-web/failback_lab.py
python3 -m unittest discover -s examples/global-web -p 'test_*.py'
```

The program creates two temporary SQLite files and removes them afterward. It accepts Alice at the first store, closes that toy writer, copies and checks Alice at the second, then accepts Bob at the second. A premature route back to the first shows Alice and **misses Bob**. Copying back while the second writer remains open returns `NO_GO_WRITER_OPEN`. Once it closes, the copy and exact receipt comparison return `READY`; the first writer opens with both bookings visible. The tests also reject a missing source receipt and conflicting bookings for the same slot. A no-go result means stop and investigate, not discard a confirmed customer record.

Before opening [the assessor](ASSESSOR.md), answer three changed cases: (1) the first store is unreachable and nobody can inspect its most recent accepted receipts; (2) a stale client can still write there after a route change; (3) two locations have each confirmed a different customer for 09:00. Which business promise can you honestly make in each case, and which observation would let you move forward? Keep a first answer, ask Codex to challenge one assumption, then inspect the output and the linked AWS sources. The fixture uses cooperative Python flags and sequential copy. It does not prove a distributed writer fence, cross-Region replication, zero data loss, DNS convergence or customer-visible recovery.

## When two locations promise the same slot

The [illustrated writer-choice lesson](../../reader/BOOK-LOCATORS.md#book-16dbdc0753249a38) changes one fact: both locations can write before their copies meet. Predict whether two local `UNIQUE(slot)` rules can protect **one shared** 09:00 appointment, then run from the repository root:

```sh
python3 examples/global-web/conflict_lab.py
python3 -m unittest discover -s examples/global-web -p 'test_*.py'
```

The first run uses two separate temporary SQLite files. Alice and Bob each receive a local `ACCEPTED` result for the same 09:00 slot. A deliberately invented final-value selection leaves one visible row and reports the other acknowledged receipt as `missing_confirmed`. Reversing the selected winner changes **which** customer loses visibility, not whether the business promise failed. This is a negative control for the claim that converged data alone proves valid reservations. It is **not** a simulation of DynamoDB's timestamps, replication, MREC or MRSC.

The second run permits one toy writer at a time. The second rejects a request while closed; after the first closes and Alice's receipt is copied and checked, it opens. Bob's 09:00 request then conflicts, while 10:00 is free. The check uses cooperative flags in one process. A stale client, another deployment, a lost reply or an uninspected source could bypass the toy handoff, so this result does not prove a distributed fence or zero-loss regional failover.

Write your own answers before reading the [assessor](ASSESSOR.md):

1. Which customer promise failed in the two-writer case, even if the databases eventually show the same row?
2. If the invented winner changes from Bob to Alice, which fact changes and which one does not?
3. What evidence would a real single-writer move need before the second location may confirm a booking if the first cannot be queried?
4. Compare one writable Region, DynamoDB MREC global tables and MRSC for a **single authoritative slot item**. Which behavior is documented, and which application decision remains yours? Include the supported-Region, transaction and cost constraints you would verify.
5. Bob received a timeout after the second location wrote 10:00. Would a new request ID, a retry with the same ID, or a declaration of failure be justified? Name the receipt lookup and customer status you need.
6. Two different item keys both claim 09:00 in a proposed schema. Does a strongly consistent conditional write on each key enforce one shared slot? Change the data model or write boundary before answering.

Ask Codex to challenge the first choice by adding a delayed old-region client and a duplicate confirmation. Check its service-specific statements against [AWS global-table design guidance](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-global-table-design.html). Keep the local output, source revision and what was *not* observed in your learning record. No AWS call or credit is used.

For any later AWS trial, verify the account and plan eligibility, use a scoped non-root role, price requests/transfer/storage/logs and any repeated capacity with current regional rates, set a whole-run limit and credit reserve appropriate to that account, and record teardown. This exercise makes no AWS call and does not authorize global deployment.

## Test the late old writer

Read [the check-at-write lesson](../../reader/BOOK-LOCATORS.md#book-2d2fd946b7e4aa3f) and its diagram. A local handoff script can close a flag, but a separate old deployment may still believe it is open. Predict all three results, then run:

```sh
python3 examples/global-web/fence_lab.py
python3 -m unittest discover -s examples/global-web -p 'test_*.py'
```

The first negative control leaves both local flags open. Two independent SQLite files accept `09:00`; neither file knows the other's unique-slot rule. The second negative control checks the old owner's epoch while it is still valid, transfers ownership, and then lets the old process write to its separate file. The early check was true; the later effect was still unsafe. No network race is needed to see the ordering problem.

The third case uses **one** local SQLite authority for both owner generation and booking rows. In a single transaction it checks `epoch=2, owner=second` and inserts the slot; epoch 1 requests return `STALE_WRITER`, including one for a different free slot. An attempted stale ownership transfer is also refused. This demonstrates the local atomic boundary the earlier cases lacked. It does not demonstrate two-region fencing: the program is sequential, all guarded workers use one reachable SQLite file, and the supplied owner string is not authenticated.

Before reading [the assessor](ASSESSOR.md), answer these changed cases:

1. The old worker checked epoch 1, paused, and writes after epoch 2 is active. Which of the three approaches refuses it, and why?
2. The shared authority is unreachable during the transfer. What customer-facing status is honest if the business requires no duplicate confirmed slot?
3. A queue worker writes straight to an older regional database and never calls the authority. Does a perfect epoch check on the web API protect that effect?
4. Alice has an accepted receipt at the old store but its last update cannot be inspected. Can the new authority safely claim zero lost confirmed bookings merely by incrementing an epoch?
5. Who is allowed to transfer ownership? The fixture accepts caller-supplied owner strings; identify the real authentication, authorization and audit evidence a production design would require.

Ask Codex to draw one operation that combines the current-generation and slot conditions at the actual write boundary, then challenge it with an unreachable authority and a bypassing writer. Verify any proposed AWS mechanism against its current primary documentation before using it. This is a cloud-free teaching run; any later AWS experiment needs its own account-specific cost and credit checks.
