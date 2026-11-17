# Search results must still belong to the reader

Two shops store return policies. A shopper at shop A must not receive shop B's policy merely because both contain the word “returns.” Later, shop A replaces returns with exchanges. Its old search entry can remain until the indexing worker catches up.

Run from the repository root:

```sh
python3 examples/search-index/lab.py
```

Requires Python with SQLite FTS5 compiled in. The program creates an in-memory database, downloads nothing, uses no credentials and closes the database afterward. Missing FTS5 fails explicitly; this lab does not install an extension. Do not use Python optimization (`-O`).

## Predict the result

| Situation | What shop A should receive |
| --- | --- |
| Both shops have a current returns policy | Only document 1, its own policy |
| Source changes to exchanges; index still contains returns | Neither the obsolete returns hit nor the not-yet-indexed exchanges hit |
| Index synchronization succeeds | The current exchanges policy |
| Source document is deleted but its index entry remains | No exchanges result |

The deliberate raw-index query returns both shops' IDs. That is the negative control: an index match alone is insufficient. The corrected query joins against the authoritative documents, requires the tenant and current revision, and returns current source text. Sorting by ID makes the test deterministic; this is not relevance ranking.

The phrase helper quotes the search language as well as binding SQL parameters. Asking for `returns OR delivery` means that literal phrase in this interface, not either word. Supporting advanced search operators would require a different explicit input contract. SQL parameter binding alone does not define a search language.

The failure injection interrupts replacement after the index deletion but inside a transaction. The whole index is compared before and after rollback. Repeating synchronization then leaves one current entry. Final checks ensure deletion and replacement did not remove the other shop or the delivery document.

## Try messages out of order

A second local drill changes one policy through four numbered revisions. Before running it, predict the answer for each shop after revision 3's indexing hint arrives, followed by the delayed hints for revisions 2 and 1. Then predict what a search should return after the source records a revision 4 deletion but before the cleanup hint arrives.

```sh
python3 examples/search-index/ordered_lab.py
python3 -m unittest discover -s examples/search-index -p 'test_ordered_lab.py' -q
```

The hints contain only an identity and revision. The worker reads the current source row; it never copies a delayed hint's policy text or tenant. The read path checks the source revision, current tenant and deletion flag before returning a match. Replaying the same current hint leaves one entry. The [separate assessor](ORDERED-HINT-ASSESSOR.md) gives the expected states after you make your own predictions.

The source keeps a deletion marker rather than removing the row immediately. That marker gives the worker a version to compare against late updates. The lab's one SQLite connection makes these operations simple to inspect; a distributed source and search engine need a separate delivery, error, reconciliation, access and retention design. No AWS resources are created.

## Measure useful answers separately

The same command then creates a separate four-document evaluation index. Its fictional reader wants money back for an item. Before the queries run, the authored judgments mark refund instructions (11) and the returns procedure (12) relevant; investment returns (13) and delivery schedules (14) are not relevant to that intent. These are teaching judgments, not collected customer ratings.

| Fixed experiment query | Returned IDs | Precision: useful / returned | Recall: found / all relevant |
| --- | --- | --- | --- |
| `refund` | 11 | 1/1 | 1/2 |
| `refund OR returns` | 11, 12, 13 | 2/3 | 2/2 |
| `reimbursement` | none | Undefined | 0/2 |

The program executes real FTS5 queries and verifies exact identities before calculating these fractions. The experimental OR expression is fixed by the lesson; it does not change the earlier literal-phrase API or allow arbitrary operators through it. Returning all four documents would also achieve recall 1, but precision would fall to 1/2. A policy of “return everything” is not a useful improvement just because it misses nothing.

`None` represents an undefined denominator. With no results there is no returned population whose precision we can measure. With no relevant documents in the judged corpus, recall is undefined too. Do not silently turn either into a perfect score. Unknown document IDs are rejected rather than scored against an incomplete fixture.

These are whole-result-set measures, not precision at the first five results or a ranking score. The corpus is tiny and fully judged for one intent; unjudged real documents cannot automatically be labeled irrelevant. It establishes metric arithmetic and this query tradeoff, not general search quality.

For transfer, change the intent to “How well did my investment perform?” Which judgments change? Why could the same returned IDs now deserve a different score? Then propose a second held-out question before changing the query. Explain how you would avoid tuning against every question you later use to evaluate success.

## What this proves and leaves open

These are real FTS5 queries and SQLite transactions on sequential fixtures. A caller-supplied tenant string is **not authentication**. A deployed service must derive tenant scope from verified identity and protect every path, including counts, snippets, exports and direct index access. The source revision must change whenever searchable content changes; the fixture enforces this convention manually, not through a universal database rule.

The revision check deliberately sacrifices availability of a result during lag. It does not erase old indexed text from storage or backups. Concurrent source changes, worker ordering, rank quality, pagination, language analysis, access revocation races and physical erasure are untested. Local transactions do not establish cross-service atomicity. No OpenSearch configuration, IAM boundary, latency target or cost has been verified.

For a changed case, suppose an old update arrives after a new update, and the document has moved to another tenant. Explain which source version the worker may index, how the read path determines current access, and what happens if that source cannot be reached. Do not solve the outage by returning unverified cached content. Record your chosen freshness/availability policy and its business consequence.

Ask Codex to remove only the revision predicate in a temporary copy and predict which assertion must fail. Run that copy, inspect the failure and restore it; a green original run alone does not show that a test detects the defect you care about.

Engine reference: [SQLite FTS5](https://www.sqlite.org/fts5.html). The lesson uses its basic MATCH and quoted-phrase behavior; the access and freshness contract is our application's responsibility.
