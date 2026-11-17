# Read the query plan before buying more database

Run from the repository root:

```sh
python3 examples/query-plans/lab.py
```

The lab uses Python's standard SQLite module, creates 20,000 synthetic appointment records in a temporary database and removes the database afterward. It needs no credentials, network or installed packages. Run without Python optimization.

The business request is: return the earliest 20 open appointments for tenant 07, with the record ID breaking equal-time ties. The program calculates the expected ordered result from the fixture in Python, independently of the SQL query. It runs the same SQL before and after creating an index on tenant, status, creation time and ID. Both results must exactly match that oracle, and the indexed query must execute fewer SQLite virtual-machine instructions for this fixture.

The instruction count comes from SQLite's progress callback with an interval of one. It measures executed SQLite VM work in this run, not rows examined, physical disk I/O, CPU cycles, wall-clock duration or billable AWS units. Instrumentation itself adds overhead. The program prints the SQLite version and plan details; exact counts and plan wording may change by engine version. A failed work comparison needs investigation, not a weakened correctness check.

On the initial local run with SQLite 3.53.4, the baseline executed 61,405 VM instructions and the indexed query executed 136. Both returned the same 20 ordered records. The baseline plan showed a table scan and temporary sort; the indexed plan showed a covering-index search. This is evidence for one synthetic dataset and query, not a general speedup ratio or a PostgreSQL/RDS benchmark.

Two changed cases prevent overgeneralizing:

- Removing the tenant predicate returns other tenants' records even though the index still exists. The script detects this deliberately unsafe query. An index is not authorization.
- Asking for the earliest closed appointments across all tenants has a different access pattern. Its result is checked independently and its plan is reported. This lab does not assert that the first index must help it.

Before looking at the output, sketch how records ordered by tenant, then status, then time could help the first query. Explain why an across-tenant time ordering is different. Then propose a second index and name its storage/write-maintenance cost before creating it in a separate experiment.

For a negative control, replace the index columns with only `status` in a disposable copy. That may still improve some work, so it is not a reliable failure oracle. A stronger control is to omit index creation entirely: the required work reduction should fail. Separately change the safe query's tenant predicate to `tenant!=?`; exact membership must fail even if the query executes quickly.

See [the manuscript explanation](../../reader/BOOK-LOCATORS.md#book-8d7fd952f0661828). SQLite documents its [query plans](https://www.sqlite.org/eqp.html) as debugging output whose format can change, so this exercise prints them for review rather than parsing them into production behavior. Its [query-planning guide](https://www.sqlite.org/queryplanner.html) explains the relationship between search, ordering and indexes.
