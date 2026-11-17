# Assessor: organization backup governance

The learner should distinguish a policy attachment from a complete effective policy, a successful job from a copied recovery point, and a restored resource from correct bookings.

1. Inspect the effective policy for that member, not merely the root policy; verify required selection, schedule, vault/role, service opt-in and recent job/recovery point after the OU change. The older green job cannot show current coverage.
2. The missing tag can remove the database from selection. A 25-hour-old point misses the stated one-hour data-loss promise even if the copy survives. Repair selection and test it, but report the already-exposed recovery gap honestly.
3. Check the selected resource's encryption/copy support and key policy in both accounts, the copy-job failure, and destination point age. The key owner and authorized backup team must restore permissions through controlled change. Do not assume a standard destination vault grants direct cross-account restore. Choose a documented copy-back path or a separately designed clean recovery account path, then run and validate it before claiming recoverability.
4. The exercise fails its business acceptance gate. Job completion is insufficient. Compare booking `B-204` against an independent confirmation ledger or other trusted record, establish whether it fell after the recovery point, and repair the customer promise through an approved process.

A strong answer also names management-account-only actions, delegated backup administrator limits, destination vault copy permission, KMS dependencies, support/Region checks, a clean restore target, retention and cost. It does not claim this local lesson proved an AWS configuration, a full compromise recovery or a learner's competence.
