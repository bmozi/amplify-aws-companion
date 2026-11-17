# Local artifact identity model

Maya publishes a website ZIP twice. Her consumer must retrieve the exact release the team approved, not whichever bytes a reused label happens to name. This small Python exercise makes explicit versions, overwrite rejection and digest mismatch observable on your own machine.

Run from the repository root:

```sh
python3 examples/artifact-repository-model/publish.py
```

Before running, predict what happens if Maya publishes `repair-site@1.0.0` a second time, changes the saved bytes without updating the receipt, or asks for a retention preview that keeps only one version. The fixture creates a temporary directory, tests both releases, tries each defect and removes the directory at the end. The preview reports a candidate but deletes nothing.

The receipt is an ordinary local JSON file stored beside the bytes. Anyone who can edit both can forge a matching pair. The fixture has no concurrent publishers, signed provenance, authorization, replication, encryption, lifecycle engine or customer. A digest detects a mismatch only if the expected digest is protected and actually checked.

This is **not** a CodeArtifact, ECR or S3 emulator. AWS services have different identities and behaviors: package formats and upstreams, container manifests/tags/digests, and S3 object keys/version IDs. Use the separate [AWS repository configuration cases](../artifact-repository-config/README.md) to reason about those differences. None of these exercises creates a cloud resource or checks a current price.

## Change the requirement

1. Keep three versions and identify which ones a rollback plan still needs. What other evidence must you check before deleting older versions?
2. A tag named `production` now points to another image digest. Explain why the tag label alone does not prove the runtime uses the tested image.
3. Two publishers race to publish the same package version. Name the atomic control the local script lacks and how you would verify the real service's behavior.

Keep your initial answer separate from AI suggestions. Verify AWS-specific claims in current primary documentation; local success does not establish cloud configuration, permissions or pricing.
