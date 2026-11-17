# The backup exists. Can the business use it?

This paper exercise extends [unit 19](../../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153). It uses fictional evidence, creates no resources and spends no credits. Read each packet in order. Write your decision before opening the [assessor notes](ASSESSOR.md); keep your earlier answer when later evidence changes it.

Maya's repair business keeps encrypted invoice exports. Think of a backup as a locked filing cabinet. Having the cabinet is useful only if the recovery team can open it, understand its contents and return the right records to the right people. A green backup job answers only part of that question.

## Draw the recovery dependencies

For this exercise, exports use envelope encryption with an AWS-generated, single-Region symmetric customer-managed KMS key. They are application exports, not claims about every AWS Backup or database snapshot integration. The package includes encrypted data, its encrypted data key and the metadata the supported reader needs. No plaintext key is supplied in this exercise.

```text
Identified export + intact metadata
                 |
Recovery identity can fetch the package
                 |
Correct KMS key is usable by that identity
                 |
Supported reader recovers the records
                 |
Reconcile deletions, holds and expected contents
                 |
Authorized customer receives the correct invoice
```

At each line, name the evidence you need. The arrows are dependencies to investigate, not a deployed recovery architecture.

## Packet 1 — Today's success and yesterday's dependency

The operator supplies this inventory:

| Item | Observed fact |
| --- | --- |
| Current application | Today's synthetic invoice can be read |
| Current export writer | Uses key B |
| Earlier retained export | Manifest identifies key A; file checksum matches its recorded checksum |
| Change record | Writer switched from A to B last week; no older-export migration is recorded |
| Key A | No requests observed in the last seven days |

A teammate proposes retiring key A because B works. Decide whether the evidence supports that proposal. Identify what a checksum proves and what it leaves unanswered. Sketch a bounded restore test and identify its reader, key and business acceptance check. Do not propose testing by making a real recovery key unavailable.

## Packet 2 — The recovery worker has a different badge

A controlled recovery report says the recovery role fetched the earlier export, but the attempted KMS operation failed with access denied. Key A is enabled. A different application role can read that same export using the supported reader. No recovery-role key-policy, IAM or grant review has been supplied.

Does this establish lost ciphertext, missing key material or an authorization-path problem? What should be inspected before changing anything? Explain why granting administrator access is a poor substitute for identifying the intended caller and permissions. Record separately what is observed and what remains a hypothesis.

## Packet 3 — Cancellation is not a recovered service

Change the facts: key A entered pending deletion during an earlier cleanup. A later report says its scheduled deletion was cancelled; its current state is **Disabled**. The team's status message says “recovery complete.” No fresh application read has been recorded.

Explain why that message is premature. Distinguish preserving a key from restoring permitted use of it and from proving the customer receives a correct record. If the key had actually been deleted, would creating a new key with the same friendly alias recover this exercise's old encrypted data key?

AWS documents that pending deletion prevents KMS cryptographic operations, and cancellation leaves the key disabled. Actual deletion of this exercise's symmetric key is irreversible. Quiet recent usage is not an inventory of retained ciphertext. Read the [key deletion guidance](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html) and [cancellation behavior](https://docs.aws.amazon.com/kms/latest/APIReference/API_CancelKeyDeletion.html). These explain the fictional states; they are not instructions to perform cleanup on our account.

## Packet 4 — Readable is not ready to reopen

The permitted recovery worker now reads all 100 expected invoices from the selected export. A separately protected deletion ledger identifies two records removed after that export. The restored application would expose both records if reopened now. No holds apply in this fictional case.

State which recovery boundary has passed and which has failed. Define the reconciliation and authorized/denied read evidence needed before reopening. Do not invent a legal retention rule or a recovery deadline that the packet does not supply.

## Transfer and AI-assisted review

Change one fact: the business rotated material within key A instead of switching to a new key B. Does that alone migrate the old exports or justify deleting A? Consult [AWS rotation behavior](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html).

Then ask Codex: “Challenge my recovery decision using only these fictional packets. Separate bytes, key availability, authorization, record reconciliation and customer behavior. Identify missing evidence; do not invent successful tests or give account mutation commands.” Keep the first answer and assisted revision separately. A fluent response is not a demonstrated restore or an independently assessed learning result.
