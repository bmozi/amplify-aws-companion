# A04 document intake with two decisions

Begin with [the file lifecycle](../../reader/BOOK-LOCATORS.md#book-d9befce7efe279db) and predict the four outcomes below. Then run from the repository root:

```sh
python3 examples/file-intake/review_lab.py
```

The lab reuses the existing local upload/read/delete functions and adds a SQLite scan receipt plus a distinct review receipt. A submitted document remains unreadable after upload, after a passed synthetic scan, and after an inconclusive scan. Only a passed scan followed by an eligible distinct reviewer's approval makes its exact digest readable by its owner. The script checks duplicate and conflicting decisions, wrong actor/digest, a late review after deletion, a revoked fixture reviewer and two opposite reviews released through a barrier on separate SQLite connections. Either reviewer may win that final race; exactly one terminal decision must be stored.

The bytes are invented. Actor names are trusted local inputs and the actor-role table is a fixture, **not authentication**. `pass` is an invented result, **not a malware scan**. SQLite serializes these local writes; it does not prove S3 version binding, Step Functions callbacks, Lambda durable replay, IAM denial, physical deletion or concurrent AWS operation. Its `inconclusive` state deliberately stays private and needs an owner to investigate or safely retry.

### Follow an owner request through a real local route

Run `python3 examples/file-intake/visitor_lab.py` from the repository root. This starts a short-lived server bound to `127.0.0.1`, uses temporary SQLite state and ephemeral fixture bearer tokens, sends actual HTTP requests, then shuts everything down. The tokens model four distinct actors for this exercise; they are not a login system. The request body cannot select its own actor.

```text
owner upload → quarantined bytes → synthetic scan pass → human approval → owner download
                   private                still private       available      exact bytes
```

Predict the HTTP results before running:

| Request | Predicted local result | Why |
| --- | --- | --- |
| Owner GET just after upload | 404 | The object exists but quarantine does not permit the owner route to return bytes. |
| Review before scan | 409 | The review gate is not open. |
| Owner posts `actor: reviewer-1` in a review body | 403 | The server uses its fixture token identity, not the submitted actor field. |
| Owner GET after scan pass | 404 | The separate human decision is still missing. |
| Review for a different digest | 409 | That approval does not name the stored bytes. |
| Owner GET after matching review | 200 and the original bytes | Both gates are recorded for this immutable ID. |
| Other owner or scanner GET | 404 | Neither is the owner of the approved document. |
| `/raw/...` before or after approval | 404 | This toy server exposes no raw-storage route. |
| Owner GET after withdrawal, or after scan failure | 404 | Deleted and rejected states stay unavailable. |

A route returning 404 is evidence about **this local server**, not evidence that S3, a presigned URL, a CDN cache or another service cannot serve the same bytes. A production design must identify every possible read path and test the actual storage policy and issued URLs. The local server uses small synthetic bytes and leaves no AWS resource or credit use.

### Try the second door before trusting the first

Run `python3 examples/file-intake/direct_link_lab.py` and then `python3 -m unittest discover -s examples/file-intake -p 'test_direct_link_lab.py' -v`. This **deliberately unsafe local design** creates a second loopback server with its own copy of the invented file and an unguessable bearer link. The application server still applies the two gates. The second server only checks the link. No sign-in header is sent to it.

Predict the two GET results at three moments before running the command: just after upload, after the synthetic scan passes, and after the owner withdraws the reviewed document. The report shows `owner_route: 404` and `shared_link: 200` immediately after upload and again after scan alone. After approval the owner route returns 200. Withdrawal closes the owner route to 404, but the independent link still returns 200. A wrong link returns 404; explicitly retiring the independent copy changes its own response to 410. Neither an unguessable link nor `Cache-Control: no-store` makes an uncontrolled recipient follow the application's current review state.

```text
Owner -> application window -> current scan + review + withdrawal state -> 404
Someone with bearer link -> second window -> independent copy -> 200
```

Name the first wrong customer-visible promise in this sequence. Then design a way to make every permitted read re-check current authorization, or state a bounded link lifetime and the withdrawal behavior the business will accept. Change the case: the second copy is not removed when the local process exits, or a recipient saves the bytes. What can a server-side 410 no longer establish? Ask Codex to list every route that might still serve the bytes and one negative test for each. Check its list against your actual architecture; this local fixture does not enumerate a deployed system.

This is **not** a simulation of S3 presigned-URL expiration, object-version deletion, CDN invalidation, identity or physical erasure. The second copy is intentionally independent so that the bypass can be observed. A real design needs selected-service access-policy tests, actual issued-link behavior, retained-version inventory, identity checks, cost and cleanup evidence. A cloud run needs a separate authorization and an account-specific cost and cleanup review.

Before reading [assessor reasoning](REVIEW-PATH-ASSESSOR.md), work each changed-condition case. For each answer, name the exact file identity, trust boundary, customer-visible state, repair owner, cost driver and observation needed to claim the cloud path works.

1. **Replacement between check and review.** A worker checks upload ID 71, digest A, version V1. The uploader writes different bytes under the same object key as V2. A review response arrives for A/V1. What must prevent V2 from becoming available? Compare immutable keys with a versioned-key design and state what a digest does and does not prove.
2. **Unknown scan.** A candidate managed scanner reports `UNSUPPORTED`, `ACCESS_DENIED` or `FAILED` instead of `NO_THREATS_FOUND`. A product manager wants to treat any result other than `THREATS_FOUND` as a pass. Draw the resulting wrong path, then assign investigation and retry responsibility. Which result still requires a separate human decision?
3. **Forged reviewer.** A request body says `reviewer_id: principal` and contains a valid-looking approval token. The caller is the uploader. Identify the authentication, current eligibility, version binding and token-handling checks needed before acceptance. A reviewer may need controlled access to quarantined content; that access must not make the owner download path available.
4. **Two opposite callbacks.** Two eligible reviewers send conflicting decisions at nearly the same time. Which outcome may win under the stated first-committed-decision rule? What evidence shows one durable decision and no split access state? Change the policy to require both reviewers and explain why a one-reviewer fixture no longer suffices.
5. **Late work after deletion.** The owner withdraws the document while a scan or human callback is pending. Explain the durable tombstone, callback result, object-version cleanup and retained audit record. Would a new upload reuse the old ID?
6. **Workflow choice.** Compare a visible, multi-service Step Functions Standard workflow using a callback with a Lambda durable function that keeps most orchestration in application code. Choose for a school whose audit team needs to inspect the path, then change the team to a Lambda-only application with developer-owned logic. For both, explain how a repeated S3 event is deduplicated and how a timeout reaches an owner. Do not assume a direct S3 notification can target a durable Lambda function.
7. **Tag and read bypass.** A scan-result object tag says no threat found. The app database still says awaiting human review. A direct signed download URL or broad storage role can read the object. Identify which boundary failed. Conversely, if the database says approved but tag update failed, state the safe customer result and repair evidence. A tag and a database row must not silently be treated as one atomic transaction.
8. **Bound the cloud trial.** Use a fictional batch of ten tiny synthetic documents and one reviewer. List every metered and retained resource: object versions, requests, scanner coverage/results, event delivery, workflow transitions or durable operations, logs, key operations if chosen, review notifications, retries and cleanup. Obtain selected regional prices and current credit terms, then compare the complete estimate and projected reserve with limits chosen for the account. State the stop condition, deletion/retention record and delayed-bill check. Do not treat an AWS budget alert as a hard cap.
9. **New read path.** The original local server returns 404 for `/raw/form-1`; the separate unsafe [second-door lab](#try-the-second-door-before-trusting-the-first) returns 200 from its bearer link before approval and after withdrawal. A proposed production design adds a presigned S3 URL in an email as soon as upload succeeds. Which *local* claim has already failed, and which real S3 behavior remains untested? Name the route to remove or gate, the actual AWS denial/URL evidence to collect, and the result a customer should see while review is pending.

Ask Codex to trace an unauthorized owner read, a stale-version approval and an inconclusive scan through your diagram. Require it to name where each is stopped, then challenge its answer with a direct-storage bypass. The assessor is internal author reasoning, not a learner score or cloud result. No AWS resources are created here.
