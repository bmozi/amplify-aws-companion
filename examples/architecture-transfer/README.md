# Reuse the foundation, then change the promise

Three teams ask for an upload form. Maya's repair shop needs a receipt for a service request and may assign the work later. A school needs to accept a document but must not show it as approved until scanning and a separate human decision finish. A software provider needs a ticket from one customer organization to remain invisible to every other organization. The screens can look similar. The promises cannot be copied from one to another.

Use the [one-path, three-promises diagram](foundation-and-context.svg) while completing the design questions. Then run the local contract walk below. The diagram is an original teaching model, not a deployed AWS architecture. The [architecture defense lesson](../../reader/BOOK-LOCATORS.md#book-aadca742bfb00b8e) explains how to keep a decision provisional and name evidence that would reverse it. The [architecture design studies](../../curriculum/ARCHITECTURE-STUDIES.md) develop A02, A04 and A10 as deeper, design-only cases.

## Start with a common path

Draw the path **actor → accepted request → authoritative record and private file → later work → authorized result → observation**. At each arrow ask who may act, what fact becomes durable, what can be retried and who can see the result. This is a checklist for reasoning, not a mandate to use one AWS service or one database in all three businesses.

The foundation stays useful because every case needs an identity decision, a record of what was accepted, a way to avoid accidental duplicate effects, a read rule, a recovery plan and whole-path cost. The context changes what *accepted* means and which later transition is allowed:

| Business | Exact promise to test | Distinct authority and state | First result that would reject a careless copy |
| --- | --- | --- | --- |
| Repair service, A02 | A repeated submission keeps one intended request; scheduling can fail without erasing acceptance | Customer submits; worker assigns after a durable receipt | Two assignments from one retry key, or a receipt with no recoverable record |
| School document review, A04 | Arrival and a clean scan do not publish an approved version | Uploader, scanner and human reviewer have separate transitions; owner read opens only after the required gates | A reviewer or owner sees an unapproved file through any read path |
| Multi-tenant ticket service, A10 | Organization B cannot read, change, export or restore organization A's ticket | Tenant membership and resource scope apply to API, object, cache, worker and recovery paths | A guessed ID, shared cache or restore exposes another tenant's record |

**Worked decision:** A repair request arrives twice because the first reply was lost. The application returns the same accepted-request receipt for the same caller and retry identity, and one durable record feeds later assignment. That can satisfy the repair acceptance promise in the stated local design. Copying the same `accepted` label to the school would be wrong: the school has only acknowledged private intake, not approval. Copying the same shared query to the SaaS service would be wrong unless tenant authority is enforced on every relevant read and mutation path. The label is reusable; its meaning and proof are not.

## Compare two bounded designs

For the school, compare **synchronous validation before any intake receipt** with **private durable intake followed by asynchronous scan and review**. The second can let a caller track progress despite slow work, but it requires explicit private states, duplicate-event handling and cleanup. The first has a smaller state machine but can leave a long or failed upload without a useful accepted-work receipt. Neither may call a scan result human approval. The owner must set the deadline and rejection behavior before choosing.

For the SaaS provider, compare **shared application and selected shared data with tenant-scoped access** with **shared application and selected dedicated data per tenant**. The first reduces repeated resource sets but places more weight on correct tenant enforcement and selective restore. The second can make some data boundaries clearer while adding provisioning, deployment, backup and cost work. Neither removes the need to check shared identity, workers, caches and exports. See [Unit 11](../../reader/BOOK-LOCATORS.md#book-422c5f26d4302648) for those paths.

Record why an alternative loses under the stated facts, then name one changed fact that could make it win. Do not score unknown behavior as passing. A good decision record says which observation would reject the preferred choice.

## Watch three different promises in one local run

A receipt is like a numbered ticket at a counter. It can prove that someone took your request, but it does not prove that a technician was assigned, a school approved a file, or another organization may see a ticket. Predict the following observations before running the lab:

| Local path | What has happened? | What must still be refused or treated as unknown? |
| --- | --- | --- |
| Repair-like booking | A reply disappears after a SQLite commit; the worker is replaced | Retry must recover one record. A separate external technician scheduler's outcome is still unknown. |
| School file | The bytes are stored, then a synthetic scan passes | Owner download must still be denied until a distinct human review approves the exact bytes. |
| Two-organization service | Both organizations use `shared-id` for different notes | A guessed neighbor ID and a forged tenant choice must fail; warm and cold cache reads must stay separate. |

From the repository root, run `python3 examples/architecture-transfer/lab.py`. It uses the existing [two-process lost-reply experiment](../resilience-exercise/PROCESS-LAB.md), [school two-gate functions](../file-intake/REVIEW-PATH.md) and [tenant query/cache fixture](../tenant-isolation/README.md). It starts only loopback HTTP, synthetic SQLite files and in-process caches, then removes its temporary files. The JSON names each observed local fact, the tempting copied rule it would miss, and its evidence boundary. A failed assertion stops the run; do not turn a failed or unrun command into a passing result.

Read the three `copying_rule_would_miss` fields. For each, write one customer-visible failure if a team blindly reuses the repair shop's `accepted` label. Then name the real system component and observation needed to test your correction. An external scheduler needs a provider-specific stable operation and reconciliation contract; the local booking record cannot establish its effect. The school fixture cannot see a presigned object URL or real scanner. The tenant fixture cannot prove authenticated membership, every export/restore path, or fair completion time. The point is to keep a reusable *question* while changing the *proof*.

The combined run is narrower than an integrated production application. It composes three preexisting local fixtures; it does not couple their databases or establish a common AWS implementation. Read their individual source and tests before changing one. For a change challenge, let a school district reviewer inspect two assigned schools and a franchise employee inspect only one shop. Specify the distinct authorization relations and the forbidden-neighbor requests; a shared group string is insufficient. Record the estimated meters and cleanup for any later cloud experiment. Choose whole-run spending and reserve limits for the account you will use.

## Make the transfer yourself

Before opening the [assessor notes](ASSESSOR.md), answer each case using six fields: **customer promise, first missing fact, two feasible responses, rejecting observation, whole-path cost/cleanup drivers, and evidence level**. Draw the actor and data boundaries. Keep your first answer, AI critique and revision as separate records.

1. **Repair retry:** The booking API acknowledges a request, the scheduler times out after it may have assigned a technician, and the customer retries. What must the receipt and worker preserve? Which external-effect fact is still unknown?
2. **School scan:** A file passes the scanner but its human reviewer has not acted. An operator suggests reusing the repair `accepted` page as the school download page. Identify the two different facts hidden by that one word and the read-path denial to test.
3. **School direct link:** The normal owner route denies an unapproved document, but an older emailed object URL still opens it. Does the application gate prove the promise? What must be inventoried and changed?
4. **Tenant recovery:** A shared database backup restores organization A's missing ticket by replacing the entire current table. Organization B's recent updates vanish. Compare isolated reconstruction with a selected dedicated boundary; what else must be reconciled?
5. **Noisy customer:** Organization A sends 100 times its usual work. Organization B's tickets remain private but exceed its completion deadline. Which promise failed, and which two shared resources would you inspect before claiming a queue feature fixes it?
6. **Changed business:** A repair franchise asks to see only its own shops, while a school district asks for a district reviewer to inspect multiple schools. Can the same group-name check implement both? Define the authorization scope and one forbidden-neighbor test for each.

**Transfer to a fourth context:** A museum publishes approved image variants to the public. Reuse the foundation's identity, record, later-work, authorized-result and observation questions. Replace the school owner's private read promise with a public *complete approved set* promise. What changes in cache, version selection and withdrawal? The [A05 publication packet](../media-publication/README.md) provides a deeper case after you write your answer.

Ask Codex to produce a claim–evidence–unknown table for your first answer and one counterexample for each copied assumption. Have it name the source for any AWS-specific claim. Keep the business owner's acceptance criteria yours; check the assistant's proposed service behavior against current primary documentation before using it. A polished AI diagram cannot prove an authorized read, a timed recovery or a bill.

This packet provisions nothing. It uses fictional businesses and design reasoning, not a compliance finding, measured workload, AWS integration or learner result. For any later account experiment, use a scoped non-root identity, verify current plan and applicable credit terms, choose a whole-run ceiling and credit reserve for that account, estimate every selected meter, and define stop conditions and verified cleanup. Multi-account organization controls remain design-only here.
