# A15 durable approval and copy changed cases

Attempt these before reading the criteria. The local program accepts only synthetic part numbers and quantities; it has no AWS credentials or policy evaluator.

1. Maya approves version `v1` for Supplier P. Her screen times out after the owner ledger commits. She retries with the same digest and supplier. What can the retry safely say? What if she retries with Supplier Q?
2. Supplier P stores the exact bytes, but the delivery reply is lost. Maya then withdraws future source access. Should the operator resend, assume the copy is absent, or ask the supplier to look up the exact version and digest?
3. A withdrawal happens after an owner read has supplied bytes to a delivery worker but before the worker stores them on Supplier P's shelf. Can the owner claim that the supplier received nothing?
4. Two requests to approve the same version for different suppliers arrive together. What must be atomic? Does a passing single-process test establish an AWS cross-account fence?

## Assessor reasoning

1. The retry reads the durable exact decision and returns `already_approved` for Supplier P. A changed recipient is a different intent and is refused. The reply loss does not turn a committed approval into a new grant.
2. The local supplier shelf can be reopened and queried for the exact key, version, recipient and digest. Its matching record resolves this fixture's lost reply without resending. A real recipient would need an authenticated lookup and trustworthy receipt; neither a timeout nor an empty owner-side queue proves absence.
3. No. Withdrawal blocks later owner reads, but cannot erase bytes already returned to a worker. The test deliberately stores an in-flight copy after withdrawal. The business procedure needs an acknowledgment, recipient cleanup and evidence whose limits are stated.
4. The comparison and assignment of an exact version to one supplier must share one authoritative transaction. The SQLite fixture serializes those local writers and allows one supplier. It does not prove distributed cross-account ordering, IAM, S3 or KMS behavior.

Ask Codex to draw the four clocks: approval commit, reply arrival, owner read and supplier copy. Challenge any answer that makes two SQLite files into one atomic AWS transaction, treats an S3 version ID as content approval, or calls withdrawal proof of recipient deletion. Preserve the first human answer beside the assisted revision; compare the two versions and explain what changed.
