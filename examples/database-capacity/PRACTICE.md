# Compare database work before reading the worked totals

Read [the capacity lesson](../../reader/BOOK-LOCATORS.md#book-0d3958fd8dbbeb15). Save an unaided answer before opening the [separate reasoning](PRACTICE-ASSESSOR.md) or running the worked calculators. These are new fictional inputs, not AWS rates, performance measurements or recommended settings.

1. In one second, an application successfully performs 60 individual strongly consistent reads of 4,100-byte items and 25 ordinary new-item writes of 2,050-byte items. Each new item also adds one 700-byte entry to one GSI. Calculate table read work, table write work and index write work separately. Change only the reads to eventual consistency; then explain whether that change is acceptable for a just-confirmed booking. Exclude retries, transactions and other operations from this first calculation.
2. Ten additional conditional writes fail against existing 2,050-byte table items. No item or index entry changes. Which work pool grows? Then concentrate every attempt on one key: what does the aggregate calculation fail to establish?
3. A different relational database completes 800 storage reads/second at 64 KiB each and 200 writes/second at 16 KiB each. The fictional planning ceilings are 1,500 IOPS and 60 MiB/s. Compare both meters. Then double only the read size. Why can a below-ceiling result still coexist with a slow query?
4. A request spends 700 ms waiting for an application connection and 30 ms executing SQL. Compare reducing deployment overlap, adding an index, and changing database capacity. Identify the first observation needed before choosing. Explain why the number of SQL queries alone is not a storage-IOPS count.

For every recommendation, give a rejected alternative, a correctness check, a changed fact and missing evidence. No AWS resources or spending are needed.
