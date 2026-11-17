# When a correct-looking total hides wrong rows

Use Python 3 with its standard SQLite module. From the repository root:

```sh
python3 examples/dashboard-grain/lab.py
```

The drill creates and closes an in-memory database. It makes no network calls, writes no persistent business data and requires no AWS credentials or additional packages. It is part of the default companion check suite.

## Predict before running

Shop A has three eligible orders, each worth 1,000 cents. Order 1 has two tags, order 2 has one, and order 3 has none. A fourth order is canceled and excluded by the fixture's stated policy. Shop B also has an order numbered 1, so both joins and business keys need shop scope.

One row per order becomes one row per matching tag after a raw join. Predict the row count and sum for a left join, which retains the untagged order. Then predict an inner join, which loses that order. Finally predict `SUM(DISTINCT amount)` when all three orders cost the same amount.

| Query | Result in this fixture | Why it is wrong |
| --- | --- | --- |
| Raw left join | Four rows, 4,000 cents | Order 1 appears twice |
| Raw inner join | Three rows, 3,000 cents | Order 1 appears twice and order 3 disappears; correct-looking total conceals both errors |
| Distinct amounts | 1,000 cents | Equal prices are not duplicate orders |

The corrected query groups tags by shop and order before joining, keeps the untagged order, and compares the report with hand-authored expected identities and amounts. Shop B is checked separately. This is parameter scoping, not an authenticated tenant boundary.

## Interpret missing evidence

All three eligible orders have a promised time of 100 in fictional time units. The first arrived at 90, the second at 110, and the third has no delivery timestamp. Read three different measures in `before`: on-time among known outcomes is 1/2; confirmed on-time among all eligible orders is 1/3; known-outcome coverage is 2/3. Missing evidence is shown explicitly rather than invented as a delivery result. A shop with no qualifying orders has undefined rates, represented by JSON null.

The exercise then records late evidence that the third order arrived at 95. `after` has three known outcomes and two on-time deliveries; sales remain 3,000 cents. That update models evidence arriving later, not a change to the fictional time at which the delivery occurred.

## Transfer the reasoning

Maya asks for revenue by tag. If one order has both “gift” and “priority,” should its full amount appear in each category, should it be split, or should categories be mutually exclusive? State the business rule before writing SQL, and identify whether summing chart bars should equal company revenue. There is no single correct allocation policy without that requirement.

Ask Codex to propose a new fixture that defeats a totals-only check. Verify the expected identities by hand, then decide which assertions distinguish the error. Do not let generated query output become its own answer key.

The assertions cover actual sequential SQLite query results, not Athena or Quick Sight execution, data ingestion, source authentication, concurrent updates, time-zone semantics or reader comprehension. No live access or cost claim follows from this local drill.

## One chart, four receipts

Maya opens a green delivery chart at 09:00 and considers cutting staff. First, write down the exact eligible Shop A order IDs, the fraction she needs, the newest source-change time, and the reader who should be allowed to see the rows. A chart title supplies none of those receipts.

From the repository root, run:

```sh
python3 examples/dashboard-grain/decision_lab.py
python3 -m unittest discover -s examples/dashboard-grain -p test_decision_lab.py -v
```

The first case holds the decision: the chart displays **1/2** from known outcomes, while only **1/3** of the three eligible orders is confirmed on time; a delivery result is missing and the 08:00 import predates an 08:10 source change. The 09:00 page opening does not repair either gap. The second case adds the missing delivery outcome, refreshes the fictional import at 08:20, and displays **2/3**. Its result is `ready_for_human_review`, never a staffing instruction.

Before opening the [assessor](DECISION-ASSESSOR.md), predict the result of these changes and name the receipt each tests:

1. The displayed fraction is **1/2** but all three deliveries now have outcomes and two were on time.
2. The chart shows **2/3**, but its source changes at 08:30 and the last import succeeded at 08:20.
3. The $30 total is still correct, but order 3 is missing and order 1 appears twice.
4. A Shop B order enters the Shop A fixture, while the displayed total still looks plausible.
5. No orders qualify this morning. Should the chart display 0%, 100%, or no defined rate?
6. The local allowlist says only Shop A, and the code passes. Has Maya's real Quick Sight reader identity been denied Shop B's dataset, underlying source and exported copies?

Ask Codex to invent one more totals-preserving change and say which assertion would catch it. Check its expected IDs and arithmetic by hand. The drill trusts supplied expected IDs, source/import times and allowed shops; it checks sequential SQLite rows only. It does not authenticate a reader, execute Quick Sight or Athena, prove refresh lineage, measure AWS costs, or make a staffing decision. A live experiment needs a separately reviewed whole-run estimate and spending and reserve limits chosen for the account.
