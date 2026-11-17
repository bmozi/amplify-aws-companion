# Region choice starts with a shortlist, not a slogan

Maya's repair service currently uses the personal lab's Ohio Region. A colleague finds a Region with a lower-looking sustainability number and asks to move the database there. What happens if the customer contract forbids that location, the exact service feature is unavailable, or the new design adds cross-Region copies and a slower seat decision? The attractive number does not answer those questions.

This [fictional decision model](lab.py) checks data-location permission, required service availability, a customer latency limit, a **complete** estimated run and a **projected** credit reserve. Its default toy case uses a fictional USD 5 run limit and USD 100 reserve for arithmetic practice; these are not targets for a reader's account. Missing evidence stays `pending`; a violated hard requirement is `reject`; passing these toy inputs yields only `paper_shortlist`. A paper shortlist is not permission to provision. The model compares two invented carbon numbers only when their declared method, workload, boundary and period match, and even that comparison orders *supplied toy values*, not real Region impacts.

Run from the repository root:

```sh
python3 examples/region-selection/lab.py
python3 -m unittest discover -s examples/region-selection -p 'test_*.py' -v
```

The three labels are fictional. `region-alpha` is a complete paper candidate, `region-beta` fails residency despite a lower toy number, and `region-gamma` lacks transfer/replication accounting. None represents an actual AWS Region. Seven changed-condition tests reject the forbidden or unsupported option, keep missing costs pending, enforce the case's run/reserve gates and refuse incompatible carbon comparisons. They do not validate live account credits, official rates, service availability, legal residency, network latency or an emissions method.

**Change the case:** copy `region-alpha` and set `estimated_run_cents=600` and `projected_credit_reserve_cents=8000`. First predict what a USD 5 run limit and USD 75 reserve will say. Then raise only the run limit to USD 7. In Python, pass `max_run_cents=500` and then `700`, with `min_reserve_cents=7500`, to `shortlist`. The first case rejects the USD 6 estimate; the second reaches a paper shortlist. The *price* did not fall when the team changed its rule. If you compare two toy carbon values, pass the same chosen limits to `compare_synthetic_carbon` so both candidates are screened against the same rules. For a real account, set limits from its plan, applicable credit terms, existing commitments and your own willingness to spend; confirm current prices and complete meters separately.

Before a **real** Region choice, the owner must define customer/data constraints; check each required service and feature in candidate Regions; estimate the whole path with dated regional prices, transfers, copies, logs and cleanup; test latency and recovery with representative users; and select a consistent sustainability accounting method and boundary. The current lab's Ohio deployment is a historical design choice, not a claim that Ohio is the best environmental location. A moved frontend with an unchanged data Region is a different architecture than moving both; draw every new network and authority boundary.

Use the [SUS 01 review](../../curriculum/well-architected-reviews/A02-A03-SUS01.md) and its [assessor](../../curriculum/well-architected-reviews/A02-A03-SUS01-ASSESSOR.md) for the changed case. Ask Codex to challenge your proposed shortlist by finding an omitted transfer or unsupported service feature, then verify its claims with current primary AWS sources and real workload evidence. No AWS call or credit is used by this lab.
