# What does the publication ZIP digest prove?

Start with [Unit 26's publishing lesson](../../reader/BOOK-LOCATORS.md#book-116eb4010fad5dcc) and the checked-in [workflow](../github-workflows/amplify-publish.yml). Its build job makes a ZIP, computes a SHA-256 digest and writes a commit/run marker. The publisher's [actual verifier](../../scripts/deploy-frontend-from-github.py) checks those values before any AWS call. Predict three outcomes, then run `python3 examples/frontend-publisher/build-trust-lab.py` from the repository root. Run the three focused tests with `python3 -m unittest discover -s examples/frontend-publisher -p 'test_build_trust.py'`.

The drill creates only temporary local ZIPs with invented HTML and a fictional commit/run ID. It imports the publisher's `expected_marker()` function but does not call its deployment function, install npm packages, use AWS credentials or publish anything.

| Case | Predict the publisher's digest/marker check | Predict comparison with independently approved HTML |
| --- | --- | --- |
| Approved page is packed and hashed | ? | ? |
| Page changes after the approved ZIP digest is recorded | ? | ? |
| A hypothetical build step changes the page, then packs and hashes it with the right commit/run marker | ? | ? |

After observing the results, explain why the third ZIP passes the publisher's transfer-integrity check. Name the controls that would need a different trust root: reviewed source and workflow writers, dependency/caller review, a constrained credential-free build job, independent content or behavior checks, and a scoped publisher job. The hosted `deployment.json` marker can identify served commit/run metadata; it cannot certify all page bytes or customer sign-in. Compare your answer with the [assessor notes](BUILD-TRUST-ASSESSOR.md). This is a synthetic trust-boundary demonstration, not exploitability evidence for any npm advisory or proof of live GitHub/AWS behavior.

**Codex practice:** Ask Codex to classify each check as transfer integrity, source/build trust, hosted revision observation or customer acceptance. Require a counterexample for any claim that the digest alone proves the site's content is safe. Verify its answer against the actual verifier and three local results.
