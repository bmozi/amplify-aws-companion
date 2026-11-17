# Follow a finding into the running release

Design-only, fictional evidence exercise for [unit 15](../../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5). Labels A, B and C stand for distinct image digests; they are not actual digest strings. `F-101` and `F-202` are invented findings, not CVE identifiers or reports about real packages. No scanner, AWS account or vulnerable software is required.

## Stage 1: the proposed release

The invoice service currently runs image A. An authored scan report for A completed yesterday and lists F-101 as high severity against a fictional runtime parser, version 1.0. The fictional advisory says version 1.1 contains a fix. Whether the application exposes the affected parser behavior has not been investigated.

The team updated the dependency lock file and built image B. Its unit tests passed. The dashboard still displays A's scan result under the mutable `candidate` tag. A developer proposes approving B because “the dependency was fixed and the build is green.”

Write a decision before proceeding. Identify facts, unknowns, the exact artifact needing evidence, one useful test and what would prevent release. Do not invent a successful scan of B, a reachable exploit or a production rollout. Explain why rejecting unsupported approval does not require claiming B is vulnerable.

## Stage 2: new evidence

After recording your first answer, consider these additional fictional observations:

- A completed report now explicitly names B. F-101 is absent, and final-image package inventory shows parser 1.1.
- That report lists F-202 as moderate severity in a different runtime package, with no fix specified in the report. Exposure analysis is still incomplete.
- The invoice totals test passes. The customer-isolation test has not been rerun against B.
- The service's desired configuration names B, but current inventory shows two serving tasks on B and one still on A.
- The rollback configuration still selects A. Its compatibility with the current data schema is unknown.

Update the decision. Separate resolving F-101 in B from the release decision, remaining old-task exposure, F-202 investigation and rollback readiness. State who must decide any temporary exception and what evidence that decision needs. No universal severity threshold has been supplied; do not invent company policy.

## Stage 3: a misleading green result

Another build produces C using an older unsupported base. A report contains zero findings, but the supplied evidence does not establish scanner support for that base. The team prefers C because its count is lower.

Explain why the lower count cannot settle the comparison. Propose evidence for coverage, maintained dependencies, business behavior and denied access. Then change one requirement: the application must handle a new file format. Explain which earlier compatibility and exposure conclusions must be revisited.

Read [the assessor notes](ASSESSOR.md) only after writing your answers. Keep a one-page decision record with artifact identity, scan scope/time/status, observed tests, open questions, decision owner and next check. Ask Codex for counterexamples afterward and preserve your unaided reasoning. This exercise supplies no actual vulnerability, remediation, AWS or learner evidence.
