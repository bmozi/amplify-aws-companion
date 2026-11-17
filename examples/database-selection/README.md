# Database selection review

Six original design cases; no database is deployed. Read [unit 25](../../reader/BOOK-LOCATORS.md#book-0fb36d2b3a5c21aa). For each case give one candidate, one credible alternative where the facts support it, a rejected assumption, and a test that could change your decision. Then compare with [assessor reasoning](ASSESSOR.md).

1. An existing PostgreSQL repair application uses PostGIS, stored procedures and a fixed driver version. The owner wants to move hosting while preserving behavior. A colleague proposes MySQL because both use SQL.
2. A high-volume device-status application only reads and updates by device identifier and lists records through specified indexed patterns. The proposal asks for DynamoDB. Later, the owner adds frequent unplanned relationship queries across devices, contracts and service visits.
3. A reservation must never allocate its last seat twice. The team rejects every non-relational option because it believes only SQL databases have transactions.
4. A fictional workload averages 1,000 requests per second, but one customer generates 850 of them. A benchmark distributes all requests evenly across customers and is used to claim adequate production capacity.
5. The shop adds an authoritative database, a cache and a separate reporting store “for scalability,” although it has no measured bottleneck. The design does not identify which result is authoritative or how copies recover after an outage.
6. A candidate returns results faster but sorts product codes differently and changes invoice rounding. The author labels the migration successful because row counts match.

A complete response states what is known, what is assumed, and what remains to be tested. These practice cases are not calibrated AWS certification questions.

## In-memory authority and recovery cases

Read the [in-memory lesson](../../reader/BOOK-LOCATORS.md#book-1a9c241595d0995a). For each case, name the authoritative record, what an acknowledged write promises, what a reader may see after failure, and the observation that could overturn your first choice. Give one feasible candidate and one credible alternative for the stated job. Do not infer a feature from the word *cache* or *memory*.

7. **A disposable display.** Confirmed appointments live in a relational ledger. The public page repeatedly shows the next available slot, but the ledger alone decides bookings. A proposed ElastiCache layer disappears during a busy hour. What can be rebuilt, what must remain correct, and how might rebuilding overload the ledger? Compare adding a cache with improving the source query first.
8. **A misplaced confirmation.** A team moves the only confirmed-appointment record into an ordinary in-memory cache because reads are fast. Its newest snapshot precedes appointment R17. The app has already told the customer R17 is confirmed. All nodes then fail. Is restoring that snapshot enough? Compare the current design with an eligible synchronous durable-write configuration, and name the customer-path restore test and full cost review still required.
9. **A changed write promise.** A separate high-throughput key/value workload needs a durable in-memory primary in one Region. A proposal uses node-based ElastiCache for Valkey with asynchronous durability but promises no lost acknowledged writes. Another proposal uses synchronous durability; MemoryDB is also considered. Which statement fails before any benchmark? What would make a replica read unsuitable for a just-written value? Then change the requirement to accepting writes in two Regions and identify which capabilities and conflict rules must be checked afresh. Keep this exercise design-only; it creates no multi-Region resources.

Write the first answer before opening the [separate assessor](ASSESSOR.md#in-memory-authority-and-recovery). A correct service name without the acknowledgment, authority and recovery reasoning is incomplete.

For cases 8–9, predict and run the [local acknowledgment and restart lab](../in-memory-authority/README.md). Compare its two receipt orders and older snapshot with your design answer; the lab tests only those local boundaries.
