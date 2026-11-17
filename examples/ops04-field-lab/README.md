# A green website can still lose a note

Maya opens the Field Lab and sees the lesson page. She signs in and presses **Save entry**, but the note is not there after a refresh. The page is available; the promised private note is not. An HTTP 200 for the page is useful evidence about one delivery step, but it cannot stand in for the whole experience. The [four-receipt diagram](observation-layers.svg) shows where the customer outcome needs its own check.

This is a **design and assessment packet**, not installed monitoring or a live outage. Work from the checked-in [browser calls](../../app/src/main.tsx), [owner-scoped model](../../app/amplify/data/resource.ts) and [Field Lab lesson](../../reader/BOOK-LOCATORS.md#book-e8d9fb108293da29). The browser calls `Entry.create` or `Entry.update`, checks returned GraphQL errors, then displays “Saved to your private data model.” It also uses `observeQuery` to refresh its list. The source defines the intended path and visible message; it does not prove a deployed request completed, that a second user was denied, or that the message was actually observed. This packet does not find explicit RUM, synthetic transaction or end-to-end trace configuration in those inspected paths. Absence from the inspected files is not an account-wide inventory result.

AWS's current [OPS 04 question](https://docs.aws.amazon.com/wellarchitected/latest/framework/ops-04.html) separates five practices. Apply each to this *one* customer promise before choosing a product:

| Practice | Plain-language question | Field Lab candidate and evidence still needed |
| --- | --- | --- |
| [BP01 Identify KPIs](https://docs.aws.amazon.com/wellarchitected/latest/framework/ops_observability_identify_kpis.html) | Did people finish the task they came for? | Define attempted authenticated saves and notes confirmed after refresh in the same observation window. Agree on a target and exclusions with the owner; page views are a different denominator. |
| [BP02 Application telemetry](https://docs.aws.amazon.com/wellarchitected/latest/framework/ops_observability_application_telemetry.html) | What did our code attempt and return? | Record safe attempt, result class, time and release identity at the relevant client/API boundaries; check coverage and retention. The current UI error message is not a durable operating metric. |
| [BP03 User experience](https://docs.aws.amazon.com/wellarchitected/latest/framework/ops_observability_customer_telemetry.html) | What did a real or scripted user actually experience? | A bounded real-user or synthetic signed-in save-and-refresh path could test the visible result. An anonymous page canary cannot prove private save. A synthetic account needs permission, cleanup, privacy and its own cost estimate. |
| [BP04 Dependency telemetry](https://docs.aws.amazon.com/wellarchitected/latest/framework/ops_observability_dependency_telemetry.html) | Which needed service was slow, denied or unreachable? | Separate Hosting delivery, Cognito sign-in, AppSync request, resolver/DynamoDB work and optional file storage. Observe the actual dependency boundary before assigning cause. AWS Health status is context, not proof that this user's save worked. |
| [BP05 Distributed tracing](https://docs.aws.amazon.com/wellarchitected/latest/framework/ops_observability_dist_trace.html) | Can we follow one request across those steps? | Plan safe correlation across the client/API/resolver/data path and check which spans actually appear. A browser event ID, a log line and a sampled trace do not automatically form a complete trace. |

The rows are proposed evidence paths, not a claim that CloudWatch, X-Ray, RUM, Synthetics or an observability product is configured. Choose a route only after a scoped identity, privacy review and current price check; monitoring itself can incur RUM, canary, metric, log, trace, storage and query charges. Set a whole-run spending limit and protected reserve for the account you will use. An organization-wide monitoring exercise requires an appropriately governed environment and remains design-only in this packet.

## Run the offline observation check

From the repository root, predict which of three fictional windows supports a note-save fraction, then run:

```sh
python3 examples/ops04-field-lab/ledger_lab.py
python3 -m unittest discover -s examples/ops04-field-lab -p 'test_*.py' -v
```

The [case file](cases.json) gives the local checker a separate list of expected attempt IDs, the events the telemetry feed saw, and notes confirmed after refresh. Only the first window has both closed observation windows and matching independent attempt IDs; it reports 16/20 at the stated review point. In the second window the attempt feed stops and there is no independent ledger: 12 confirmations among 15 *seen* attempts are not a full-window result. In the third, an independent ledger knows about five more attempts even though the telemetry heartbeat is green. The checker names those missing IDs and refuses a rate. All three show 100 successful static-page loads but no total page-attempt count, so none supports a page-load success rate.

Change one fact in `cases.json`: reopen the confirmation window, duplicate an event ID, or remove a known attempt from the observed feed. Predict the result before rerunning the checker. Ask Codex to propose a metric that would mistakenly call the third case healthy, then explain why its denominator or feed-coverage claim fails. The IDs and results are invented. This local program proves only its reconciliation rules; it does not test the browser, GraphQL persistence, AWS telemetry delivery, heartbeat reliability or a real customer's experience.

## Decide from a complete fictional attempt ledger

In one ten-minute teaching window, the fixture has 100 successful static page loads, 20 distinct authenticated note-save **attempts**, and 16 of those notes confirmed after refresh. Four attempts have no confirmed note at the review point. These counts are stipulated as complete for this case; they are not Field Lab observations. Calculate the page-load success fraction and the save-confirmation fraction using their own denominators. Say what the four unconfirmed attempts mean and what they **do not** prove. A browser-level success message or API 200 would still need a durable refreshed-note observation for this promise.

Now change the evidence, not the application: the note-attempt telemetry feed stopped after its fifteenth event, while the static-page feed continued. The four previously unconfirmed attempts are no longer a complete observed count for the full window. Which rate becomes unknown, and which page-load observation stays valid? What independent heartbeat or reconciliation would reveal the missing feed without turning missing events into zero failures? Compare your answer with the second and third local cases; a green heartbeat alone is weaker than an independent count of expected attempts.

Finally, a teammate says all four missing notes were caused by an expired Cognito session. That is a hypothesis. Name one observation that could support or weaken it and one observation that would distinguish an AppSync authorization error from a write or synchronization problem. Keep private note content, email addresses, tokens and unbounded request IDs out of metric dimensions. A safe correlation token may be retained in access-controlled diagnostic events only after a data-handling decision.

Use the [assessor notes](ASSESSOR.md) only after answering. Ask Codex to list every sentence in your answer that treats a page response, UI message, API result, trace sample or AWS service-health signal as proof of a confirmed note. Then verify the critique against the fixture and source; an AI proposal is not a deployed monitor or a learner result.

**Figure review:** `observation-layers.svg` (SHA-256 `b6ba0c851b89bc03eeb653c85b7069c8bf4cf638213d7054f9bd804366d5c5e1`) was rendered to a 1200 × 560 PNG (SHA-256 `5d21b0ffafd5abdf2ba88e8c837c9b701bbf4d415eacc45b7de2da4f67b37f7d`) and inspected at original resolution on October 20, 2026. Text, arrowheads, box boundaries and evidence labels were readable without overlap. This is a standalone companion-figure review, not final print or ebook page review.
