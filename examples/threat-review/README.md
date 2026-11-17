# Threat review: a repair photo crosses several boundaries

Original design exercise, October 18, 2026. This is a proposed repair-photo workflow assembled from teaching patterns, not a claim that every component below is deployed in A01. It performs no network requests, penetration testing or cloud changes.

The customer uploads a photo for a repair. A worker inspects it, an assigned technician can view approved content, and an operator can investigate failures. Assets include photo contents, ownership records, approval state, deployment authority and a finite operating budget.

```text
Untrusted customer device
       │ request plus claimed object/repair identifiers
       ▼
API: authenticate actor; authorize repair and operation
       │ controlled upload scope
       ▼
Private intake storage ── event ──→ inspection worker
       │                              │ approved/rejected decision
       └──────────────────────────────▼
                         authoritative metadata
                                      │ check current access + status
                                      ▼
                         authorized technician download

Separate path: reviewed source → deployment identity → infrastructure
Separate copies: diagnostic logs, exports, backups, generated previews
```

A box is a responsibility in this design. It is not necessarily a separate server. An arrow identifies a data/authority crossing to investigate; it does not prove encryption, permission or successful delivery.

## Worked threat register

These are threats to evaluate, not asserted vulnerabilities in the deployed lab. Owners are fictional roles to assign to real people before implementation. Controls are proposals unless linked evidence explicitly establishes a narrower behavior.

| ID | Actor, action and unwanted result | Proposed control and owner | Evidence to require | Current boundary |
| --- | --- | --- | --- | --- |
| T1 | Customer substitutes another repair's object ID and reads its photo | API checks current actor, repair ownership and object association; application owner | Same object requested by owner and non-owner through API and file path | Local tenant fixtures teach scope; not this end-to-end cloud flow |
| T2 | Uploader changes bytes after inspection; approved name now resolves to uninspected content | Bind approval to immutable content/version identity; file-workflow owner | Change content between inspection and publication; verify rejection or reinspection | Local file lifecycle demonstrates its fixture; cloud version enforcement pending |
| T3 | Repeated uploads and retries exhaust inspection capacity or budget | Bound input/work, rate/concurrency and retries; operations owner | Controlled bounded overload with useful rejection and no unbounded replay | No public stress test authorized; cost/queue exercises are narrower |
| T4 | Old queued job runs after access is revoked | Recheck the authority needed at execution/release; application owner | Enqueue, revoke, execute and confirm intended denial | Sequential retrieval/tenant examples do not prove distributed revocation |
| T5 | A build change uses deployment authority to alter unrelated resources | Review source and effective role/trust/pass-role scope; deployment owner | Permitted release plus unrelated-target denial under actual role | Frontend policy candidate checked; live scoped release remains open |
| T6 | Diagnostic logs copy private images or credentials to a wider audience | Minimize/redact content; restrict readers and retention; operations owner | Inspect success/error logs using synthetic markers and verify denied access | No complete deployed log-content/access audit claimed |

## Prioritize without inventing probabilities

Treat unauthorized photo disclosure and substitution of approved content as release-blocking concerns for this fictional workflow because they violate its central privacy and inspection promises. Investigate their reachable paths before polishing dashboards. Resource abuse also needs a bound before public exposure. This is an editorial priority decision based on stated impact, not a measured attack frequency or formal compliance rating.

For each threat, record assumption, reachable path, affected asset, proposed prevention, detection, recovery, named owner and residual risk. A control may reduce one path while leaving another. Do not mark the threat closed merely because a relevant AWS service has been selected.

## Changed-case challenge

Add a contractor who may see only assigned repairs, a preview generator that copies images, and a customer revocation while a download link remains valid. Update the diagram and register. Explain whether access is checked when the link is created, when it is used, or both, and what evidence would establish the intended revocation behavior for the selected mechanism.

Then suppose the inspection worker has permission to read every customer's uploads. Explain why application ownership checks and workload IAM scope are separate reviews. Propose a credible narrower design and its complexity, without claiming it already exists.

Ask Codex to find an omitted actor, copy or bypass path after writing your first answer. Do not provide real photos, credentials or customer identifiers. Keep AI suggestions separate from verified controls and perform only scoped synthetic tests.

Assessment: a strong answer traces each new copy and authority decision, predicts a failed-control case, identifies an owner and states remaining evidence. The exercise does not provide security certification or validate a live exploit.
