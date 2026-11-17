# Price the units, then price the whole path

Maya counts a million reads and asks what they cost. Before multiplying by a price, she needs to know what each read asks the database to do. Think of a parcel carrier: the number of parcels is useful, but their sizes and delivery requirements also affect the charge.

For this paper calculation, use DynamoDB Standard on-demand request prices in **US East (Ohio), us-east-2**, retrieved on **October 30, 2026**. The [official regional price catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-2/index.json) returned version `20260911124422`, published September 11, 2026. Its selected request dimensions were $0.000000125 per read request unit and $0.000000625 per write request unit. Retrieval date and catalog publication date are different facts. Refresh the catalog before making a real decision.

The [AWS unit rules](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/read-write-operations.html) round individual item reads in 4-KB blocks and ordinary item writes in 1-KB blocks. Read consistency changes the multiplier. Here, KB means 1,024 bytes, and the stipulated sizes are DynamoDB item sizes, not merely the length of an application's JSON file.

## A small difference at a boundary

Each row below represents **one million successful operations** on a single Region's table. Read rows refer to individual existing items; write rows insert new items. No index, retry or replication work is included.

| Operation and stipulated item size | Units per operation | Request subtotal |
| --- | ---: | ---: |
| Eventually consistent item read, 4,096 bytes | 0.5 read units | $0.0625 |
| Eventually consistent item read, 4,097 bytes | 1 read unit | $0.1250 |
| Strongly consistent item read, 4,096 bytes | 1 read unit | $0.1250 |
| Transactional item read, 4,096 bytes | 2 read units | $0.2500 |
| Ordinary new-item write, 1,024 bytes | 1 write unit | $0.6250 |
| Ordinary new-item write, 1,025 bytes | 2 write units | $1.2500 |

For the first row: 1,000,000 operations × 0.5 units per operation × $0.000000125 per unit = $0.0625. Units cancel, leaving dollars. One extra byte in the second row crosses a rounding boundary. That doubles this request component, not every charge in the application.

Do not weaken a correctness requirement merely to select the cheaper row. If the operation needs a stronger guarantee, price that requirement. Do not apply this per-item calculation unchanged to Query or Scan: read aggregation and evaluated data need their own treatment.

## What the subtotal leaves out

This table is deliberately not a complete run estimate. Storage, indexes, backups, restore tests, streams, replicated writes, transfer, application compute, authentication and monitoring must be included when selected. Retries can change the number of attempted operations. A monthly total also does not establish capacity for a concentrated burst.

The catalog contains separate zero-price and charged tiers for some other meters. Do not subtract an allowance or trial credit just because a catalog mentions one. Account eligibility, shared consumption and credit terms need separate evidence. No account was inspected for this example, and no resource needs to be created to read it.

## Change one fact

Without looking back at the table, predict the read subtotal for two million eventually consistent reads of 4,097-byte items. Then explain why projecting only one attribute would not automatically justify pricing a smaller stored item. Name two missing cost categories before calling your answer an application estimate.

Ask Codex to check the arithmetic and the stated scope. Require it to identify the operation, byte boundary, consistency, price source and date. Keep its suggested assumptions marked as assumptions until verified. This example is a dated price calculation, not an AWS bill, workload benchmark or permission to deploy.
