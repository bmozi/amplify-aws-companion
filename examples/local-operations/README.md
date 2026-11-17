# Local engineering drills

A student learns more from watching a failed operation than from memorizing a service name. These four drills use only Python's standard library, SQLite and temporary local files. They make no AWS calls and require no credentials or cloud spending.

Run from the repository root:

```sh
python3 examples/local-operations/lab.py
```

Optionally save a report to an existing private evidence folder with `--output evidence/local-drills.json`. Temporary databases and release files are removed even if a drill raises an exception. The optional report persists at the path you choose.

## Predict before running

1. Two callers compete for one seat. Predict the number of successful reservations and what a winner's retry should do. Read `reserve`: transaction locking and a conditional decrement protect the invariant. SQLite locking is not DynamoDB transaction behavior.
2. A database loses a business record after a backup. Predict whether an integrity check alone detects the missing record. The drill checks both database integrity and expected business content after restoring to another database.
3. Four synthetic request windows contain healthy traffic, failures, no traffic and a tiny sample. Predict each monitoring state. No data is distinct from zero errors; insufficient samples need their own treatment.
4. A candidate release returns an incorrect fixture result. Predict which artifact stays selected. The drill blocks that candidate, promotes a correct candidate and reselects the previous artifact. This is a local selection gate, not a cloud deployment.

Inspect the report. Expected behavior is one `reserved` and one `full`, an unchanged replay, matching restored data, four different signal states, a blocked bad release and removed temporary resources. Caller order and measured local restore time may vary. Do not compare machine speed from a single run.

## Adapt without copying

### Follow the checked bytes through publication

The release drill now separates checking from promotion. Its trusted local receipt records the artifact digest, configuration and destination. Predict four outcomes before running: a bad result; a rebuilt JSON file with the same version and values but different whitespace; the checked file with a changed multiplier; and the checked file aimed at another destination. Each must leave the old selection intact. The unchanged checked combination must publish. The rebuilt file can publish after its own successful check, showing that rejection is about missing matching evidence rather than a permanent ban on rebuilding.

A digest identifies bytes; it does not say that their behavior is useful. In this fixture, the independent expected result is 42. Configuration changes the result, so matching artifact bytes alone cannot preserve the promise. The destination is part of the receipt because a check for the practice environment is not approval for production.

The receipt is an ordinary dictionary created inside a trusted Python process. It is not signed, cannot authenticate an outside builder and is not resistant to an operator forging it. There is also no concurrent publisher or time gap between verification and storage in this fixture. Real deployment needs protected evidence, access controls, compatible environment checks and observation of the served version. Ask Codex to identify which of those boundaries this code actually enforces before describing it as a secure pipeline.

### Check whether the checks notice a broken guard

A passing exercise is more convincing when a deliberately broken version fails for the right reason. This technique is called mutation testing: change one small rule in a disposable copy, predict which assertion should fail, and run that copy. Never apply this experiment to a real deployment script or disable a live permission check.

For this local fixture, try the following changes individually in a temporary copy of `lab.py`, leaving the assertions intact. Restore the original before each next change. Run the copy with ordinary Python, without `-O`, and inspect the assertion that fails rather than treating any error as success.

| Deliberate defect | Expected failed assertion |
| --- | --- |
| Replace only the artifact mismatch expression with `False` | Unchecked rebuilt bytes must not promote |
| Replace only the configuration mismatch expression with `False` | The changed multiplier must not promote |
| Replace only the destination mismatch expression with `False` | The practice receipt must not promote to production |
| Replace the expected-result rejection condition with `False` | The wrong-result candidate must receive no check receipt |
| Change the missing-receipt guard to always return `False` | The valid candidate must promote |

The last case matters: a controller that refuses everything can satisfy rejection tests while being useless. The successful path supplies a separate requirement. A syntax error, missing dependency or unrelated reservation failure does not show that the release assertion detected your mutation. Record the actual failing expression, then remove your disposable copy. These five changes exercise five known defects; they do not establish that every possible implementation error is covered.

Change the reservation exercise to two seats and three callers. Preserve the invariant and explain duplicate requests. Add a post-backup confirmed reservation to a separate fixture and calculate what the backup cannot recover. Change the alarm threshold and state how equality should behave. Introduce a release that passes one check but fails another and require both checks before promotion.

Ask AI to suggest a failing interleaving or omitted restore dependency. Before accepting its fix, explain the failure and show a test that would have caught it. These exercises support E08, E12, E14 and E15; they do not satisfy AWS-specific implementation or independent learner-review requirements.

## Inspect what the build actually packages

Maya removes an expired offer from her website source. The new homepage appears correctly, but the release ZIP still contains the old offer at its original path. A builder that copies current files into yesterday's output folder can preserve files that are no longer in source. A homepage check alone misses that defect.

Run this separate local exercise with Python 3, without optimization:

```sh
python3 examples/local-operations/build_inputs.py
```

Before running, predict the ZIP member names after removing `expired-offer.html` from source and adding `hours.txt`. The first path reuses the old output folder and demonstrates the stale-file defect. The second path creates a new temporary staging directory for each build. It checks exact expected file names and contents, so a build that merely drops everything cannot pass.

```text
Current source -> reused output -> current + stale files
Current source -> fresh staging -> expected files only
                                    |
                                 release ZIP
```

The two fresh builds produce identical ZIP bytes in this fixture. File ordering, archive timestamps, permissions and compression choice are explicitly controlled. Changing the hours input creates a different artifact while the earlier artifact remains unchanged. A recorded digest identifies the resulting bytes; it does not prove the business approved the new hours.

This is real local flat-file copying and ZIP creation, not a frontend compiler, dependency resolver or CodeBuild pipeline. There are no generated external assets, downloads, environment substitutions or secrets. Two matching builds in one process on one host do not establish reproducibility across operating systems or toolchain versions. Fresh staging removes this specific stale-output path; it does not establish that all source inputs are correct, complete or authorized.

For a real application, record the source revision, lockfile, tool/runtime versions, configuration and any generated inputs needed to explain the output. Inspect the packaged paths as well as a representative behavior. Decide which build caches are reusable and how they are keyed; a dependency cache and the directory published to customers are different things. Do not delete arbitrary working folders as a cleanup shortcut. This drill owns and removes only its temporary fixture tree.

Ask Codex to inspect the release package and name evidence that the expired offer is absent. Then change the case: the stale file is gone from the new ZIP, but an older deployment or edge cache can still serve it. Explain why clean packaging does not establish withdrawal from every serving location. Use the [media publication review](../media-publication/README.md) for that separate delivery boundary. Record your prediction, actual result and AI-assisted correction separately.

Before reading the [artifact-generation review criteria](../../curriculum/knowledge-reviews/DOP-1-3.md#artifact-generation-decisions--ordinal-02), answer these changed cases:

1. The homepage check passes and the ZIP checksum is recorded, but no one lists the ZIP's paths. Which expired-offer failure could remain, and what additional evidence would distinguish it?
2. A clean build downloads “the latest” content during execution. Two runs from the same Git revision differ. Which input was not fixed, and what does each artifact's checksum still establish?
3. A repair produces an empty ZIP, so the forbidden old page is absent. Explain why the removal assertion passes while release acceptance should fail.

Keep your first answers and any assisted revisions. These practice cases do not provide a certification score.
