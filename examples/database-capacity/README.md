# Size changes the capacity calculation

Run `python3 examples/database-capacity/lab.py` from the repository root without Python optimization. It uses standard-library arithmetic and synthetic inputs; it does not install packages, call AWS or estimate dollars.

Predict these results before running:

| Fictional work | Expected arithmetic |
| --- | --- |
| 100 successful strong single-item reads/second, each item 4,097 bytes | 200 read units/second |
| Same reads, eventual consistency | 100 read units/second |
| Same items, transactional reads | 400 read units/second |
| 40 successful new-item writes/second, each item 1,025 bytes | 80 write units/second |
| Same items, transactional writes | 160 write units/second |
| Fivefold peak of original strong reads and ordinary writes | 1,000 read and 400 write units/second |
| One successful update shrinking 3,000 bytes to 500 bytes | 3 write units |

The [AWS operation rules](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/read-write-operations.html) are the source for the rounding and operation factors. The workload numbers are original fictional inputs. These are consumption calculations, not recommended provisioned settings or performance guarantees.

Two separate strong reads of 1 and 8,191 bytes consume three units together. Averaging their sizes first gives 4,096 bytes and incorrectly predicts two units for the pair. Explain why rounding each individual operation matters. The calculator is not a Query/Scan calculator; those operations require their own rules.

Input sizes mean the operation-relevant item size, not the length of a JSON request or just one text field. Attribute names and values contribute to DynamoDB item size. Storage-billing overhead is a separate consideration. Consult [item sizing](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/CapacityUnitCalculations.html) when deriving real inputs.

Changed cases: successful attempts rise by 50 percent; one customer concentrates most requests on a small key set; an index is added; retries include rejected requests; the target requires immediate visibility of a confirmed write. Expected reasoning: recompute the stated successful-attempt volume (300 read units/second for the first case), investigate key-level behavior, account for index work, use operation-specific failure accounting, and preserve required freshness. Do not switch consistency merely to obtain a smaller number.

The first exercise deliberately excludes index maintenance and failed conditions; the bounded worksheet below adds those two cases. Both still exclude transaction conflicts, multi-Region replication, partition limits, latency, autoscaling, dollar rates and headroom. Neither validates a live configuration or all database capacity planning. Compare a selected cloud design against representative measurements only after identity, pricing and credit prerequisites are satisfied.

Ask Codex to identify every hidden unit in an estimate—bytes, operations, seconds and item boundaries—and to show one boundary case. Verify its calculation against the fixture and the exact operation documentation.

## Count attempts and index work separately

Maya's ledger has a separate directory for open requests. A successful new request writes both records. A rejected duplicate still makes DynamoDB evaluate a condition against the table item. A successful change from open to confirmed removes one directory entry and writes another. A note that is not projected into the directory changes only the table. These different outcomes must not be priced as four identical writes.

Predict each row before running `python3 examples/database-capacity/attempts_lab.py` from the repository root. The script makes no AWS calls and prints the assumed operations and arithmetic.

| Fictional attempts in one second | Table write units | GSI write units | Why |
| --- | ---: | ---: | --- |
| 40 new 1,025-byte requests; 900-byte index entries | 80 | 40 | Each table item rounds to two 1-KiB blocks; each new index entry uses one. |
| 20 rejected duplicates with existing 1,500-byte items | 40 | 0 | The failed condition is charged against the existing table item; no index write completes. |
| 10 updates moving an indexed key, 1,500-byte table items | 20 | 20 | Two table blocks and an old-index delete plus new-index put per attempt. |
| Five 1,500-byte note edits outside the index | 10 | 0 | The stated index key and projection do not change. |
| **Total calculated work** | **150** | **60** | These are separate work pools, not capacity settings or dollar estimates. |

The small model accepts only ordinary, single-item writes with one GSI whose projected entries are at most 1 KiB. Set `index_key_changed` when the indexed key moves; if it is false and old/new index byte sizes match, you are asserting that the projected index entry is unchanged. Equal sizes alone cannot prove equal values. The script rejects projection-size changes because it cannot infer their full write path from byte counts. It also omits transaction conflicts, expression evaluation beyond the stated failed condition, hot partitions, bursts and retries outside the input counts. The [AWS item-operation rules](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html) and [GSI rules](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html) govern the real service.

Try these changes without looking at the output first: a failed condition finds no existing item; 10 open requests become closed by *removing* the sparse index entry; a nonprojected note edit also changes an attribute that **is** projected; and the same per-second totals concentrate on one hot partition. Explain which rows the script can model, which need a more detailed operation description, and which require live measurement. Then run `python3 -m unittest discover -s examples/database-capacity -p 'test_*.py'` to check the local boundary cases. For an authorized cloud study, request consumed-capacity details for table and indexes and inspect actual throttling, latency and distribution after checking current prices and a spending limit. The local totals alone cannot size that study.
