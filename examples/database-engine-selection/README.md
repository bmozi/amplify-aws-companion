# Database engine selection worksheet

This paper exercise practices SAA-C03 task 4.3 skill 02. It creates no AWS resources. Read [unit 25](../../reader/BOOK-LOCATORS.md#book-a0f96d3c7762ff92), then prepare your engine inventory and recommendation before reviewing the [assessor notes](ASSESSOR.md).

## Scenario

Maya's repair application currently uses PostgreSQL with PostGIS, stored procedures and a fixed driver version. A hosting move is being planned. A colleague proposes MySQL because the team has MySQL experience and both engines use SQL. The business goal is to change hosting while preserving confirmed booking, repair and invoice behavior. No approved requirement asks for an engine conversion.

## Workcard

1. List the application behavior that depends on an engine: queries, types, indexes, transactions/isolation, constraints, stored procedures, extensions, collations/sorting, timezones, drivers, ORM behavior, pool settings and admin scripts.
2. Classify each item as required, optional or unverified. For each required item, check support for the exact RDS/Aurora engine and version, Region, permissions and service configuration. Record the official source and date.
3. Compare keeping PostgreSQL with converting to MySQL. State the business benefit needed to justify conversion, migration work, dual-running or write pause, rollback, recovery and skill/maintenance consequences.
4. Design a parity fixture containing Unicode/case sorting, timezone boundaries, decimal rounding, nulls, duplicate keys, a conflicting update, rollback, stored procedure outputs and application-generated queries. Define expected outcomes independently of the candidate engines.
5. Specify correctness, latency, concurrency, recovery and lifecycle-cost measures. Use current regional pricing only after the resource shape and query mix are known. Do not claim a winning engine from general product features.
6. Ask Codex to find undocumented dependencies and propose test inputs. Independently confirm each feature and expected result in application source, engine documentation and business rules.

## Change one condition at a time

Repeat the decision if PostGIS is removed; the required extension is absent in the chosen version or Region; the application adds heavy JSON indexing; the team changes ORM; an old driver cannot support the target; a migration unexpectedly changes sorting or numeric values; a tested feature needs privileges the managed service does not grant; or the cost comparison has no representative workload. State whether the engine decision, managed-service decision or migration plan changes.
