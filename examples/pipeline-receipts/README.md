# Keep the test receipt attached to the parcel it tested

Maya's booking team checks a pull request, merges it, builds a parcel, tests it, and prepares to release. A green dashboard says the pipeline finished. But one test command exited zero while its report contained a failed customer case, and another test examined a freshly rebuilt parcel rather than the one queued for release. The word “passed” has lost its object: **which bytes, which test, which environment and which customer promise?**

Read [the illustrated lesson](../../reader/BOOK-LOCATORS.md#book-e9ba63b117c5c2ae) and the existing [real local consent pipeline](../pipeline-testing/README.md). This new receipt screen is a separate, fictional decision model. Run it from the repository root:

```sh
python3 examples/pipeline-receipts/lab.py
python3 -m unittest discover -s examples/pipeline-receipts -p 'test_*.py' -v
```

The screen expects pull-request unit and static checks, a post-merge build, and isolated integration, acceptance and security checks against the **same reviewed source and artifact**. It rejects a missing or duplicate stage, nonzero exit, a report with failures despite exit zero, a stage that ran zero checks, stale source, different artifact or a production test environment. A performance-sensitive change additionally needs a supplied isolated load receipt, an estimated run at or below **USD 5**, a reserve of at least **USD 100**, and a stop condition. These are editorial safety rules for the fictional packet. The script does not run those tests, calculate an AWS bill, invoke AWS, inspect GitHub Actions or prove that a real CodeBuild project is configured.

Answer the changed cases before opening [assessor reasoning](ASSESSOR.md):

1. **Repository and artifact:** The web source is in Git; the tested ZIP is placed in an artifact repository; a container variant uses an image repository. Which record names the reviewed commit, which stores the release bytes, and which exact identity must the deploy stage consume? What changes if a second build uses floating dependencies?
2. **Source events:** A pull request runs fast unit and static checks. A merge to `main` builds a new artifact. Which tests must be rerun against the merged source and artifact? Why is a passing PR check from an older commit insufficient? Distinguish a test-only workflow from the separate, currently manual/disabled Amplify publishing route in this repo.
3. **Build and secret:** A CodeBuild project compiles the app. A buildspec uses a plaintext environment variable for a supplier credential, and the build log prints a transformed version. Identify the secret source and effective role/access boundary that must be corrected. Do not paste credentials into an assistant, buildspec or test receipt.
4. **A zero that misleads:** A shell command exits zero, but the test report says one acceptance case failed. Another run has zero tests. Which receipts block promotion? What must a CI job report and preserve so a green command cannot hide those outcomes?
5. **Coverage and health:** Unit coverage rises from 81% to 91%, but no test checks that a denied customer leaves zero reminders. A process exits zero after startup, but its booking endpoint returns wrong data. What does each signal establish? Which positive and negative behavior checks are still needed?
6. **Performance change:** A query change is expected to double request volume. A team proposes a stress test against production during peak hours. Design an isolated, representative load or benchmark stage with target throughput, latency, error and dependency measures, duration, stop threshold, estimate, reserve and cleanup. Explain why local toy timings cannot establish production capacity.
7. **AWS-backed integration:** A test must verify an actual S3 object permission or Lambda invocation in an isolated account/Region. Name its identity, test data, resource lifetime, concurrency collision rule, result, cleanup and billing evidence. Which of those cannot be proved by the local SQLite/HTTP lab?
8. **Deploy and stop:** Choose a bounded canary or another eligible strategy for Maya's booking API, with a stable artifact and customer-specific stop signal. The canary returns HTTP 200 but loses a confirmed booking. What must happen before expanding traffic? What if an earlier schema change prevents rollback?

Ask Codex to find a receipt that could be green while the customer promise fails, then verify its suggestion against the concrete test oracle and current service documentation. Keep the first answer, AI critique and corrected answer separate. Cross-account and organization-dependent variations in this exercise stay design-only. Any future live AWS stage needs scoped non-root access, selected Region/resource support, complete cost and cleanup review before it runs.

Sources: [official DOP-C02 Domain 1 tasks](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain1.html), [CodeBuild buildspec commands, secrets and reports](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html), [CodeBuild test reports](https://docs.aws.amazon.com/codebuild/latest/userguide/test-reporting.html).
