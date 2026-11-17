# Authorized retrieval without a model

A search result can be relevant and still belong to someone else. This lab demonstrates that distinction with real SQLite FTS5 retrieval, current permission checks and source-bound quotations. Read [the lesson](../../reader/BOOK-LOCATORS.md#book-c7716c08655f741e) first and predict which documents each actor may receive.

Run from the repository root:

```sh
python3 examples/authorized-retrieval/lab.py
```

Requires Python 3 with SQLite FTS5. No packages, credentials, network listener, model or AWS resources are used. All fictional documents live in memory and disappear when the connection closes. Run without Python `-O`, because assertions check expected outcomes.

The script verifies Alice/Bob separation, Eve's empty grant set, unknown/inactive actors, an erroneous cross-tenant grant, fabricated quotes, cross-user citation reuse, revocation between retrieval and release, changed source versions and a refreshed index. An unrestricted-search negative control retrieves the private fixture, showing that the dataset would expose a missing permission filter. Query length and returned document count are bounded.

A malicious instruction remains quoted text. This is **not** a prompt-injection evaluation: no model interprets it and no tool executor exists. The result packet contains exact excerpts rather than generated answers. Full-body digests and substring checks do not validate truth or whether a generated claim follows from a quote.

The actor strings are trusted fixtures, not authentication. Tests are sequential; no concurrent permission-change guarantee is established. The fixture's source and index have explicit manual synchronization, no durable cache and no distributed ingestion. FTS relevance is lexical; it is not vector search or a claim about Bedrock retrieval quality. The shared index can also affect ranking through global statistics; no side-channel isolation claim is made.

Record the printed engine version and each observed outcome. Explain why a cached candidate needs a fresh access check. Then implement the lesson's manager-only variation without weakening tenant isolation. Do not treat the printed pass as evidence of AWS IAM, real identity validation, model grounding, cloud costs or learner mastery.

Next, attempt the [A20 answer-review cases](ANSWER-REVIEW.md) before reading the [assessor](ANSWER-ASSESSOR.md). They test whether an authored answer preserves source meaning and keeps a customer-credit action behind a separate gate. This is a human reasoning exercise layered on the executable excerpt checks, not a hidden model call or an automated natural-language scorer.
