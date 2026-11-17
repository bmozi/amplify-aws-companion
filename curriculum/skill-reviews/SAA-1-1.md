# Individual-skill review: SAA-C03 task 1.1

Internal editorial review, October 18, 2026. The [official task page](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain1.html#solutions-architect-associate-03-domain1-task1) currently lists six skills. Our IDs are editorial ordinals, not AWS-issued skill identifiers. Short labels below are original paraphrases; consult the official source for the full wording and examples.

This review connects each skill to a specific section and an original prompt. It does not establish complete task coverage, independent assessment or certification readiness. It reviews one task's six skills, not all 310 inventory entries. The machine-readable companion is [skill-evidence.csv](../skill-evidence.csv).

## Six changed-case prompts

### Skill 01 — Protect human and root access

A publisher cannot deploy, so a teammate proposes a root access key. Explain the difference between the helper's root rejection, MFA, role permissions and successful publication. The recovery mailbox is shared: what risk remains? Compare protection of a standalone account with centralized root access for an Organizations member account. Name the evidence still missing.

Look for: no assumption that a non-root name means least privilege; temporary role access; owner-completed MFA; actual allowed/denied evidence. The recorded candidate policy diagnostics do not finish onboarding. The November 1 lesson adds root-key avoidance, protected recovery channels and the standalone/member-account distinction. Check that the learner does not treat management-account root as removed or the helper as recovery protection. Real non-root reproduction and learner transfer remain pending.

### Skill 02 — Compose an authorization model

Maya hires a publisher, a backend engineer and an investigator. Assign responsibilities and compare direct user grants, IAM user groups and assumable roles. Explain why an IAM user group is not a principal in a resource policy.

Look for: specific action/resource needs, group-versus-role distinction, separate runtime authority and a lifecycle for membership changes. Our actor table and federation section support the explanation. The six [effective-permission cases](../../examples/permission-review/README.md) add worked attachment, boundary, principal and delegation reasoning with separate assessor criteria. No complete group-policy lifecycle or live effective-access review is demonstrated.

### Skill 03 — Design role-based access

The publisher's entry role looks narrow, but it can pass an administrator execution role. Trace the resulting authority. Then propose a partner-account role path without assuming that one policy document alone completes cross-account access.

Look for: trust versus permission, direct versus delegated authority and tested source/target assumptions. The local caller guard and standalone frontend-policy simulation cover only bounded pieces. A complete cross-account implementation is absent.

### Skill 04 — Design account-level controls

A production OU restriction blocks the recovery operator. Use the governance exercise to explain the inherited policy path and a staged correction. Identify why a role named BreakGlass is not automatically exempt.

Look for: ceilings do not grant access, applicable deny behavior, attachment-aware rollback and a tested recovery path. This exercise remains design-only. Control Tower operations, account lifecycle and independent review are not demonstrated.

### Skill 05 — Choose resource-policy access

A partner needs one approved export. Compare a resource-policy grant with access through an assumed role. List the principals, resource scope, encryption-key dependencies and required negative tests before selecting either.

Look for: a concrete access path rather than “allow the partner”; awareness that resource-policy behavior depends on the principal and policy context. Existing units explain the distinction but lack a complete worked resource/key-policy package and live adjacent-object denial evidence. Do not claim this skill complete from Cognito owner checks.

### Skill 06 — Decide when workforce federation fits

The company already has a staff directory. A contractor changes teams and later leaves while holding a temporary session. Compare a separate IAM-user lifecycle with federation, and identify sign-in, assignment, session and recovery dependencies.

Look for: a reasoned choice tied to the existing identity source; a distinction between stopping new sign-ins and handling existing sessions; no accidental Organization creation in the trial. The newly added unit section closes the absence of explanation, but not deployment, revocation testing or learner assessment.

## Knowledge-list check

The official task also includes five knowledge areas. Each now has its own teaching, assessment and remaining-evidence record in the [individual knowledge review](../knowledge-reviews/SAA-1-1-knowledge.md), with a five-case [learner exercise](../../examples/identity-foundations/README.md). This skill review stays focused on the six skills above; neither ledger establishes task completion or certification readiness. Optional service-example depth remains outside this mapping.

## Findings and dispositions

The previous task-to-E01 assignment concealed distinct missing material. A source search found no substantive federation selection lesson in the relevant manuscript units. Added a concrete workforce scenario, group/role distinction, lifecycle questions and AI review prompt to unit 6. The later same-account role-versus-session case adds a bounded resource-policy worked example. Complete resource/key-policy packages and operational federation remain material gaps. All six skill rows stay partial; all independent learner assessments stay pending.

For assessment, provide the prompts without these rationales, record the learner's unaided explanation and then change one constraint. Use the prerequisite guide's explanation/demonstration/transfer/scope criteria. These prompts and rationales are author/model judgments; no participant has yet completed them under independent assessment.
