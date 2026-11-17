# Assessor notes: source portability is a bounded claim

These are authored criteria, not calibrated learner results. Keep the reader's first answer separate from AI-assisted revision.

1. The AMD64 failure is not repaired by repeating ARM. Inspect the AMD64 image's Node binary path and the Dockerfile's target-architecture selection. The official Node archive uses an `x64` label while Terraform uses `amd64`; the runner must choose the matching pair. A new checksum/command result is needed for that lane.
2. Two passing reports over different ZIP hashes test two different source snapshots. They cannot support a one-snapshot cross-platform claim. Repackage from the intended clean commit and rerun both lanes against that exact archive; retain both reports and hashes.
3. The source archive check establishes manifest-preserved local code/tests under two container CPU families on one host. It does not build, inspect or run the stated application image in ECS. Verify image platform/digest, task definition runtime platform, startup/readiness, effective permissions, a correct invoice and the full customer path before making an ECS result claim. A green process or successful pull is narrower than the invoice promise.

A strong answer labels native ARM and emulated AMD64 separately, counts requested and not-requested checks, and leaves independent-machine portability and live AWS behavior open. The exercise has no observed learner response.
