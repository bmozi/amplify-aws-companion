# A small pool repeated many times becomes a large request

These are original design exercises, not a database benchmark. Read [the connection lesson](../../reader/BOOK-LOCATORS.md#book-8d7fd952f0661828), record your prediction and reasoning, then consult [assessor notes](ASSESSOR.md). No cloud resources are needed.

1. A fictional 240-connection planning ceiling leaves 40 reserved and 20 for other clients. Twelve application processes each permit ten connections. Calculate the possible application demand and remaining allocation. Distinguish configured demand from observed open connections.
2. A rolling deployment temporarily runs 24 processes. Compare a seven-connection pool with limiting rollout overlap. Explain why fitting the connection budget alone cannot prove a response-time target.
3. A background importer adds eight processes, each allowing five connections, during that 24-process/seven-connection rollout. Recalculate the allocation. Name the operating coordination that the earlier budget omitted.
4. A customer's request times out while a transaction waits for another service. A colleague assumes the database connection is now free. What driver, cancellation, transaction and pool observations would test that assumption?
5. A proxy has a fictional backend allowance of 180 connections; 120 remain occupied by pinned sessions. A colleague promises that another 1,000 clients will be served immediately because “the proxy pools connections.” Explain the missing evidence and the finite capacity still required.
6. A query completes in 20 milliseconds after waiting 900 milliseconds for a pool connection. Should the investigation begin by adding an index? Explain the timing evidence and distinguish waiting from query execution.

Transfer: the application adds a second region and both deployments can reach the same database. Explain how to count those clients, their failure/retry behavior and administrative needs without claiming that a regional label creates another database connection budget. Then describe the changed ownership and consistency questions if each region instead gets a separate writable database.

Ask Codex to challenge your calculation and propose one failure that the arithmetic cannot detect. Keep the original prediction, corrected reasoning, assumptions and assistance in your learning record.

After the design cases, run the [local connection reuse and cleanup exercise](../connection-pool/README.md). It supplies bounded SQLite observations for the cleanup question; it does not benchmark the fictional connection allocations above.
