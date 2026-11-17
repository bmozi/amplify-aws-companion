# API contract review: what did the service promise?

Original contract assessment for the [request lesson](../../reader/BOOK-LOCATORS.md#book-16b52b3769a877e6). The six cases below review a proposed customer API. The local exercise implements a bounded HTTP demonstration; it is not an AWS endpoint or production service. Answer before reading the [assessor reasoning](ASSESSOR.md).

For each case, state what the client knows, what it does not know, the required server behavior and the evidence needed to verify the contract.

1. **The optimistic receipt.** The API validates a request and returns 202 before saving anything. Storage then fails. The interface says “Your request is safely stored.” Compare this with the lesson's durable-acceptance promise. Does the HTTP status alone establish the missing storage evidence?
2. **The disappearing reply.** R17 and its dispatch obligation were committed, but the client receives no response. It generates a new retry key. Explain the duplicate risk and specify a recovery interaction using the original caller-scoped key. What should happen if the client reuses that key with changed appointment details?
3. **The public progress link.** A status URL contains a hard-to-guess request ID. The handler returns the record without checking the caller. Someone argues that the ID is the password. Define the missing authorization and an adjacent-customer denial test. What changes if a previously authorized user's access is revoked?
4. **Two different successes.** A status read returns HTTP 200 with a business state of rejected. The interface announces “Repair completed” because the HTTP request succeeded. Explain the error. Then the customer closes the tab: does that cancel outstanding work in the contract as written?
5. **The forgotten retry window.** Retry mappings are retained for one day, but an offline client retries a three-day-old operation. The operator promises that duplicate work is impossible because the request still carries a key. Identify the unsupported claim and a documented recovery path that avoids blindly creating a new effect.
6. **The changed entry requirement.** The initial proposal selected API Gateway HTTP API. The business now requires a private API endpoint. Using the official product comparison, identify which selection must be revisited and what remains to verify after choosing a product. Do not confuse a private backend integration with a private client-facing API endpoint.

Submit a one-page contract covering operations, trusted caller, accepted input, durable acceptance boundary, status ownership, retry identity/lifetime, error meaning, polling limits and cancellation. Compare a synchronous response with acceptance plus progress lookup for the stated repair work. Explain when the simpler synchronous option would fit. Keep existing IAM-invoked lab handlers distinct from the proposed customer API.

Ask Codex to find one contradiction between the interface wording and the server promise. Review its source claims and record assistance separately. No independent learner trial, API Gateway configuration or live denial result is established here.

## Run the receipt experiment on your laptop

Imagine handing the clerk your repair form and leaving before hearing the receipt number. Did the clerk lose the form, or only the reply? Run this exercise from the repository root with Python 3.10 or later:

```sh
python3 examples/api-contract/lab.py
```

It needs only Python's standard library. It starts a temporary HTTP server on `127.0.0.1` at an automatically selected port, sends actual local HTTP requests, stores records in a temporary SQLite file, then closes the listener and removes the file. It makes no AWS calls and installs nothing. Do not expose this teaching server to a network: its public fixture strings stand in for authenticated identities, and its fault-injection headers are deliberately test-only controls.

### Predict, run, explain

Before running, predict how many accepted request rows and work obligations should remain after each step. An obligation means “work remains to be handled”; the lab has no worker that books repairs.

| Observation | Request / obligation count | What the evidence means |
| --- | --- | --- |
| Bad identity, empty repair or injected failure between the two inserts | 0 / 0 | Rejection and rollback leave no half-accepted request |
| Both inserts commit, but the server closes without replying | 1 / 1 | A missing HTTP reply does not prove the operation failed |
| Original caller retries with the original key and input | 1 / 1 | HTTP 200 returns the existing receipt; no new work was accepted |
| Original key with changed input | 1 / 1 | HTTP 409 reports a conflict instead of silently changing the work |
| Another customer submits the same key | 2 / 2 | Keys belong to a trusted caller scope, not a global shared namespace |
| Six concurrent submissions with one new key | 3 / 3 | One HTTP 202 acceptance and five HTTP 200 replays identify the same request |
| A local operator records rejection | 3 / 3 | HTTP 200 on the status read reports `rejected`; HTTP success is not repair success |
| Original customer submits the same repair with a fresh key | 4 / 4 | The negative control creates another operation; text equality does not define retry identity |

The other customer also tries to read the first customer's existing status URL and receives 404 without the record. An unknown fixture identity receives 401. These are real responses from this local handler, not Cognito or IAM results.

### Why the two inserts stay together

Open `lab.py` at `BEGIN IMMEDIATE`. Each request has its own SQLite connection. The transaction obtains the write reservation before checking the caller/key association; the unique `(owner, retry_key)` constraint also defines the database invariant. The new request and its obligation commit together. A deliberately injected failure after the request insert rolls back that insert. The server only sends its acceptance after the commit. The concurrent test sends six HTTP requests through a thread pool and checks that all resolve to one identifier, with only one additional obligation.

That demonstrates this SQLite implementation under the tested local interleaving. It does not prove every possible schedule, distributed database behavior, machine-crash durability or delivery to a real supplier. Readers should trace the transaction and the negative controls as well as inspect the passing result.

### What remains outside this lab

There is no TLS, real sign-in/token verification, revoked-access integration, API Gateway, external worker, cancellation, retry-record expiry, overload policy or production request parser. SQLite retains associations only for this temporary run. The fixed caller fixtures test ownership logic after identity selection; they cannot prove secure authentication. Status changes are a local operator action, not a completed business process. The HTTP server is teaching code, not a deployment template.

Explain why the safe retry uses the original key, why returning a receipt before commit would break the promise, and why another caller cannot use that key to read your record. Ask Codex to locate the exact assertions supporting each explanation and identify one claim those assertions cannot establish. Keep the six design cases above: several intentionally ask about requirements this executable does not implement.

## Release compatibility

After the receipt experiment, complete [Yesterday's client meets today's server](COMPATIBILITY-REVIEW.md). It adds a separate serialized-response matrix and six lifecycle questions; the HTTP lab above remains unchanged.
