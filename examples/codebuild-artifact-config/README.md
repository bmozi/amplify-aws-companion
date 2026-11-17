# Configure a build tool to create the intended artifact

**Purpose:** practice translating a software change into a bounded CodeBuild project and a verifiable artifact handoff. This is a design exercise. It creates no AWS resources, starts no CodeBuild job and makes no claim about the learner's account.

Read the [ELI5 lesson](../../reader/BOOK-LOCATORS.md#book-1f5858d645449c9d) first. Keep the project settings, buildspec, service role, artifact destination, cache and later deployment stage distinct. Record the selected source revision and the exact files the next stage should receive.

The [sample buildspec.yml](buildspec.yml) is an editable starting point for a Node application that produces `dist/`. It is not a complete CodeBuild project or a deployable application. Read the book's recipe table, then inspect each path and command against the application you actually build.

## Case 1: The green build with an empty handoff

The `build` command exits with status zero. Its output is in `dist/`, but the buildspec lists `README.md` under `artifacts.files`. The downstream website action reports that `index.html` is missing.

Write a repair that selects only the intended website output. State which project-level output settings must agree with the buildspec, and identify the observation that would prove the downstream stage received those bytes. Explain why “build succeeded” is insufficient.

## Case 2: The broad packing list

The repository contains source, tests, `dist/`, `.env.example`, a developer's local `.env`, and a scratch directory. The proposed artifact selector is `'**/*'` from the repository root. The build command writes new files over an existing output directory.

Choose a fresh output strategy, a narrow `base-directory` and file selector, and explicit exclusions if required. State how you would prove both that the obsolete file is absent and that the expected page is present. Never use actual secrets in this exercise.

## Case 3: Permission creep

The build only runs lint, tests and compilation, but its service role has administrator access because an earlier team used the same role for deployment. The build does not publish an image or deploy an application.

Draw the starter identity boundaries: who starts the build, what the CodeBuild service role can read/write, where logs go, and which later deploy identity would be separate. Name one positive permission test and one denied unrelated-resource test. Do not write a wildcard policy as the answer.

## Case 4: A secret in the recipe

A developer has placed a package-registry token in a plaintext project environment variable and echoes it during troubleshooting. The private package fetch works.

Replace the secret path with a managed secret reference and the smallest read permission. Explain why masking in logs is not permission to print the secret, and what to check after changing the role. Include a safe redacted test; do not supply a real token.

## Case 5: The private-subnet hang

The build is attached to private subnets to reach an internal test endpoint. It also needs to fetch source, dependencies, upload its artifact and send logs. The subnets have no NAT route or VPC endpoints. A proposed fix adds a NAT gateway but includes no estimate.

List each required network path and compare a narrowly designed endpoint approach with NAT egress. State which paths are AWS service endpoints and which may be external package hosts. Keep the decision conditional on endpoint support, availability, throughput and current price. No network changes are made in this lab.

## Case 6: Build or Lambda action?

One team asks for a TypeScript application to be compiled and packaged. Another asks for a short post-deployment check that requests a URL, verifies a health response and reports pass/fail to CodePipeline.

Assign the build and custom check to appropriate tools. Trace what each result proves, its permissions and its output. Explain why using Lambda as a custom CodePipeline action does not make it the general build worker. State the additional application-level observation needed after deployment.

## Cost and safety card

Any future AWS execution must first have a current Region-specific whole-run estimate within spending and reserve limits chosen for the account, use a scoped non-root identity, set a timeout and stop condition, avoid production data, and document cleanup and billing verification. Include CodeBuild compute duration/type and possible source, artifact, cache, log, VPC/NAT/endpoint and transfer costs. This case set does not authorize or perform that execution.

Before reading the separate [assessor notes](ASSESSOR.md), save your answers and ask Codex for one new changed case, one least-privilege review and one failure observation. Verify all service-specific claims against current AWS primary documentation; keep Codex's suggestions separate from your corrected answers.

## Evidence boundary

These cases assess design reasoning. Pair them with the [local build-input drill](../local-operations/README.md#inspect-what-the-build-actually-packages), which does execute copying and ZIP creation locally. Neither this case set nor that local drill establishes a working CodeBuild project, effective AWS role permissions, source connection, artifact-store behavior, VPC route, live cost or independent learner outcome.
