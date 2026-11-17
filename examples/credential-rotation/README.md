# Replace a credential without losing track of its consumers

Maya's worker asks a supplier whether appointments are available. The supplier accepts one credential; a separate store tells the worker which credential to use. The worker keeps a short-lived copy. All three must agree for a request to succeed.

```text
                     retrieve synthetic credential
          Worker ──────────────────────────────────→ Local store
             │                                            │
             │ cached copy                  change stored value ≠ change supplier
             │                                            │
             └──── read-only availability request ───→ Local supplier
                                                       accepts one value
```

Run from the repository root, using Python's standard library:

```sh
python3 examples/credential-rotation/lab.py
```

The program starts two temporary loopback HTTP servers on operating-system-assigned ports. No AWS credentials, SDK, internet request or paid service is used. It disables environment proxy use for these requests. The store is intentionally unauthenticated and the connection is unencrypted: use only the public fixtures already in the source. Other local processes could reach these listeners while they run. This is not secure secret storage.

The program stops and closes both servers, including on assertion failure. All state is in memory and disappears afterward. Run without Python optimization; `-O` is rejected because assertions provide the exercise's checks.

## Predict before running

| Change | Expected observation | Why it matters |
| --- | --- | --- |
| Start with matching values | One retrieval and one successful supplier request | Establish a working baseline |
| Change only the store, then expire the cache | Two supplier denials; bounded refresh does not repair disagreement | A stored value is not proof of target acceptance |
| Make the supplier match the store | Access recovers | The target and stored value now agree |
| Replace both while a worker holds the old value | First request denied; one refresh and second request succeed | A running consumer can lag behind replacement |
| Make the supplier return 503 | One failed request; no credential refresh | Service availability differs from authentication |
| Make the store unavailable before cache expiry | Cached credential still succeeds | Caching can preserve availability temporarily |
| Advance the clock to cache expiry | Retrieval fails; no supplier request is sent | The policy does not silently extend cache lifetime |
| Reject the cache while the store is unavailable | One denial, then retrieval failure; cached value discarded | Rejected credentials are not used as fallback |
| Restore the store with the wrong value | At most two denied supplier calls | A persistent fault cannot cause an endless retry loop |
| Reconcile the value and probe the old credential | New access succeeds; old credential gets 401 | Recovery and old-credential rejection are separate checks |

The same run now includes a **two-worker overlap round**. First it publishes B before the supplier accepts B: the new worker is denied while the old worker remains usable, so the plan must stop before retiring A. Next the supplier temporarily accepts A and B, the store publishes B, both workers succeed, and the old worker refreshes to B when its cache expires. Only then does the fixture retire A and directly verify A receives 401 while both workers still succeed. Predict each result before running. The synthetic supplier's two accepted strings model an overlap contract; this is **not** an implementation of Secrets Manager's alternating-database-user rotation, Lambda rotation stages, or a guarantee that every provider can accept two credentials. AWS's [rotation-function stages](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_lambda-functions.html) and [alternating-user tutorial](https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_rotation-alternating.html) describe their distinct supported behavior.

The printed result includes counts and outcomes, never the credential strings. An assertion checks that these three fixture values are absent from the summary. This is a specific output check, not proof against every possible leak: the store response and request header intentionally carry the values in plaintext on loopback.

## Read the code as a small policy

`Fixture` represents the store and target independently. The scenario changes their state directly; it does not implement a rotation transaction. `Worker.refresh` clears its old cache before attempting retrieval. `Worker.availability` retrieves on expiry, retries this read-only request once after a 401, and stops on continued rejection or a 503. `observe` checks the result and actual server request counters.

The injected `now` values let us test expiry without waiting. They are authored clock inputs, not measured production rotation times. The ten-unit cache lifetime is an example, not a recommended AWS cache setting. A production clock, concurrent refreshes, rate limits, latency and retry scheduling need separate design. Unexpected transport errors terminate the exercise; this code is not a complete production error handler.

Do not copy the retry rule blindly into a payment or other modifying operation. This supplier endpoint only reads availability. A real operation may commit before its response is lost; safe retries then need an appropriate idempotency contract and reconciliation. A 401 also does not universally mean rotation: investigate the actual provider's authentication contract.

## Change the business constraint

1. The supplier allows two credentials during a transition. Draw the sequence that proves the new credential works before the old one is retired. What happens to consumers that never refresh?
2. The supplier permits only one credential. Explain why a zero-interruption promise needs more evidence than this sequential lab can provide.
3. A worker has a valid cache when a security incident requires immediate revocation. Explain why shortening the cache lifetime alone is not proof that the supplier rejects that credential now.
4. The store is reachable but returns a value for the wrong supplier. State the expected bounded failure, diagnostic fields and recovery owner without printing the value.

Ask Codex to trace the observed request counts, then propose a negative test that would fail if the worker retried forever or retained a rejected credential. Give it only this synthetic source. Review its reasoning and run the test; do not accept a confident description as execution evidence.

## What this does not establish

There is no Secrets Manager deployment, IAM enforcement, KMS encryption, managed rotation, version staging, Lambda rotation function, real provider integration, or concurrent workload. The two workers are called sequentially against loopback HTTP; the round does not measure concurrent refresh or prove zero interruption. The example explains the consumer/target consistency problem using actual local HTTP. The AWS implementation and its service-specific guarantees remain separate work.

Return to [the identity and secret lifecycle lesson](../../reader/BOOK-LOCATORS.md#book-47726780fac09ca7). Compare your predictions with the output and explain one discrepancy before changing the code.
