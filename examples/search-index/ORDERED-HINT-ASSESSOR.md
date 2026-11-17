# Ordered search hints: assessor notes

Use after the reader predicts the [four-revision exercise](README.md#try-messages-out-of-order).

1. The source reaches revision 3 before the worker processes its hint. Shop B owns the seven-day exchanges policy. Applying hint 3 writes that current source revision to the index. Shop A receives no result; shop B receives the current exchanges text.
2. Hints 2 and 1 arrive afterward. Their revision numbers are below the current source revision, so both are ignored. Arrival time does not make an older policy authoritative.
3. Revision 4 records deletion in the source. The read path now withholds the policy even while revision 3 remains in the search index. Hint 3 is obsolete; hint 4 removes the index entry. A hidden search result does not prove physical erasure from backups or logs.
4. A hint for revision 5 while the source still says 4 is rejected. The worker cannot invent a source state from an event claim.

A strong changed-case answer says what must happen if the source revision is unavailable: the worker cannot confirm the hint, and the read path must follow the chosen freshness and access policy rather than silently trusting old index text. The lab cannot prove a distributed transaction, actual OpenSearch version conflict, signed producer identity, independent tenant authorization, or deletion from retained copies.
