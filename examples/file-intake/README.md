# Uploaded does not mean available

Run `python3 examples/file-intake/lab.py` from the repository root. Python's standard library is sufficient. The exercise stores invented byte strings and metadata in a temporary SQLite database, then removes it. It does not contact AWS or scan files for malware.

Predict the results before running:

- An owner cannot read a quarantined upload.
- An approval for different bytes is rejected, and the immutable object ID cannot be overwritten.
- A matching synthetic approval makes the owner's object readable; repeating it changes nothing.
- Another owner cannot read or delete that object.
- A rejected object remains unreadable; conflicting terminal verdicts are rejected.
- Deletion removes the payload from the record and keeps a tombstone. A late approval cannot resurrect it, and that ID cannot be reused.
- A 1,025-byte fixture exceeds this exercise's 1,024-byte application limit and is rejected.

Actors and verdicts are trusted function arguments supplied by the test harness, not authenticated users or scanner results. The digest identifies bytes; it does not establish safety. Setting a SQLite field to NULL and removing a temporary file is not secure physical erasure. The script does not test S3 versioning, IAM, URLs, encryption, event ordering or concurrent cloud behavior.

Adapt the exercise by adding a new immutable ID for a revised upload. Prove that approval for the old ID cannot approve the new one. Then design a review timeout: should it reject, remain quarantined or escalate? Explain who may retry and what prevents unlimited work.

Ask Codex to find an illegal state transition and propose evidence that would expose it. Verify its answer against the code rather than accepting a claim that a familiar-looking file extension is safe. Next run the [two-gate review and loopback HTTP visitor exercise](REVIEW-PATH.md) to see how an application read route changes the customer-visible result. Read [the file-intake lesson](../../reader/BOOK-LOCATORS.md#book-98f19229e5a86e66), then apply its rules to A04 and E06.
