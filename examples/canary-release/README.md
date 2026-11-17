# A ready server can still return the wrong price

Run from the repository root with Python 3, without `-O`:

```sh
python3 examples/canary-release/lab.py
```

The exercise starts three real local HTTP version endpoints and a local forwarding endpoint on operating-system-assigned loopback ports. It creates no AWS resources, credentials, files or business records. Each server is shut down when the exercise exits, including after an assertion failure. Allow local loopback connections.

The independent fixture contract is a 10 percent discount on 1,000 cents: the quote must be **900 cents**. The bad version reports ready and returns HTTP 200, but quotes 1,000 cents. The forwarding endpoint initially selects the stable version. It then sends two of each ten sequential requests to the bad candidate. Eight stable responses succeed; the two candidate responses violate the business contract.

The controller examines candidate responses and selects rollback as soon as it sees a wrong quote, even if that is the only candidate observation. Promotion requires at least two passing candidate observations. The next ten requests must all return stable-version quotes. It then trials the repaired version and sends all ten final requests to that version after its candidate checks pass. No candidate observations or a single passing observation hold the release; one failing observation rolls it back.

These thresholds and traffic slots are fictional teaching choices. Two passing observations are not a production confidence standard. The routing is deterministic, sequential and synthetic, not AWS weighted routing or a load test. No database writes, sessions, retries, caches, concurrent requests, authentication or external effects are included.

## Check that the recovery test can fail

```sh
python3 examples/canary-release/lab.py --disable-rollback
```

This negative control must exit nonzero with `rollback did not restore stable responses`. It leaves the candidate selected after the alarm so that the next response window exposes the missing recovery action. This is an intentional failure, not a passing test. The standard companion runner executes the normal drill; the negative control was checked separately during development.

## Explain the evidence

1. Why did readiness and HTTP status fail to detect the defect?
2. How many candidate requests were observed, and how many were wrong?
3. What observation proves that the controller changed the actual response path?
4. Why would no traffic require a hold rather than promotion?
5. If the candidate charged a customer before rollback, what additional recovery would be needed?

Expected reasoning: distinguish process availability from business correctness; count the candidate cohort separately; verify returned version and quote after switching; do not interpret missing evidence as success; switching code does not reverse a payment. Ask Codex to propose a missing-case test, then trace whether it actually exercises that condition.
