# Two clicks are not necessarily two reviewers

Original design challenge for [the approval lesson](../../reader/BOOK-LOCATORS.md#book-842e431cbcce6c95). The original SQLite lab implements a single designated reviewer. A separate optional drill now demonstrates the local admission subset of the policy below. Preserve your first design before reading the [assessor guidance](TWO-REVIEWER-ASSESSOR.md). No deployment or spending is part of this exercise.

## Business brief

Maya's repair shop proposes a price-list publication. The fictional policy requires approval from two distinct eligible people other than the requester. Each person must review the same exact artifact and destination. Both approvals must remain unexpired and both people must still be eligible when execution is admitted. The requester can cancel before admission but cannot approve. Cancellation after admission must be reported honestly as an in-progress or completed-effect question, not promised as reversal.

For this exercise, the action contains its ID, revision, artifact digest, website destination and effective date. Reviewer eligibility is an authoritative business record, not a role name supplied by the browser. Times are fictional UTC instants. An approval expires at its deadline, not one instant afterward. An action change creates a new revision that requires new approvals. The example makes no legal or regulatory compliance claim.

These are chosen business rules. Another organization might allow delegation or define different review groups, but would need to specify and test that different policy.

## Design before selecting a service

Describe the records for the action, each review, current eligibility, cancellation and execution admission. Specify the invariants, including how repeated submissions from the same person behave. Compare two bounded designs:

- One transactional store holds action revision, eligibility and decisions, so an admission transaction can check a consistent local state.
- Reviewer eligibility comes from an external authority. Define the freshness, revocation and in-progress-operation policy; do not claim an atomic read across that authority and an unrelated database without a supporting mechanism.

Neither choice proves that the external website publication and the workflow receipt can commit together. Keep admission, dispatch, publication outcome and reconciliation separate.

## Cases to defend

| Case | Evidence supplied | Decision to explain |
| --- | --- | --- |
| Duplicate click | Reviewer A submits the same approval twice after losing the first reply | Count approvals by distinct authorized person, not request count |
| Requester as reviewer | Requester A approves; eligible reviewer B also approves | Apply the requester exclusion even if A normally holds a reviewer role |
| Changed destination | A approves revision 1 for the training website; B approves revision 2 for the public website | Decide whether either revision has the required matching approvals |
| Revoked reviewer | A and B approved; B's eligibility is revoked before admission | Preserve the review history while preventing an invalid present authorization |
| Exact expiry | B's approval expires at 12:00; admission is attempted at 12:00 | Apply the boundary consistently without a grace period invented by code |
| Concurrent cancel/admit | The requester cancels while the executor tries to admit the action | Define a serialization boundary and honest outcomes for both possible orders |
| Lost provider reply | Admission succeeds; publication may occur; the reply disappears | Preserve operation identity and reconcile the effect rather than treating two approvals as proof of success |
| Replacement reviewer | B is unavailable; an operator changes the stored reviewer label to C | Explain why relabeling a past decision is not C's review |

Submit a decision table, a record sketch and acceptance tests. Include a positive case with two distinct eligible non-requesters approving the same revision before expiry, and a negative control that would incorrectly count A's repeated click twice. For a live system, tests also need the real sign-in and eligibility paths; trusted test strings cannot establish identity.

Ask Codex to identify a case where every individual read looks valid but their combination is stale. Require it to name the exact operation ordering, affected record and violated policy. Review the proposed remedy against the two storage alternatives, and state what remains unresolved at the external publication boundary.

## Run the local admission drill after your design

Run `python3 examples/approval-workflow/two_reviewer_lab.py` from the repository root without `-O`. It uses only the standard library and a temporary SQLite database. Trusted actor strings and synthetic integer times stand in for identity and a clock; they are not authentication or timestamp evidence.

The script excludes the requester even though that fixture identity is eligible, rejects an unknown actor, deduplicates one reviewer's repeat, rejects an attempted expiry change through replay, and prevents approvals for different revisions from combining. It keeps the revoked review as history while excluding it from current admission. A real replacement fixture review restores the required pair. Two barrier-released admission callers on separate connections produce one admission row and one duplicate result. Exact expiry and cancellation before admission block work; cancellation after admission reports `already_admitted`.

Read the count query as well as its output. It joins current local eligibility, matches revision and digest, excludes the requester and requires expiry strictly later than now. The review primary key enforces one stored decision per person per revision. SQLite serializes these write transactions, including the controlled eligibility/revision changes. The demonstration does not implement real eligibility administration, a general revision-edit API, distributed revocation, review-group policy, historical identity proof or every concurrent ordering. Cancellation/admission orders are controlled sequential examples; only duplicate admission is exercised concurrently here.

An admission row is permission to start the next stage, not evidence of a published website. No dispatch or external effect exists in this drill. The provider-reply and external-authority design cases remain outside its execution coverage. Connections close and the temporary database is removed.

## Choose a waiting mechanism — design only

After solving the policy cases, use the lesson's official service references to answer three orchestration questions:

1. A task submits an asynchronous job and receives an HTTP acceptance response. May the next business step assume that job finished? Compare Request Response with a supported `.sync` integration.
2. The proposal uses an Express workflow and expects `.waitForTaskToken` to pause for a manager. Check whether that integration pattern is supported. Does selecting a supported pattern establish reviewer authorization?
3. An operator stops a workflow while an integrated job is running. What evidence is needed before claiming the job stopped and its resource use ended?

These questions select mechanisms for specified behavior; they do not authorize provisioning. Include the exact integration, workflow type, timeout, permissions and outcome evidence in any future implementation plan.
