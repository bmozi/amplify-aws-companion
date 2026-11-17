# Design an image pipeline that proves its output before sharing it

Read the [image-build lesson](../../reader/BOOK-LOCATORS.md#book-11ab415a3475c8e5), then attempt these cases before opening [ASSESSOR.md](ASSESSOR.md). This is a no-cloud design lab. It creates no AMIs, images, roles, pipelines, cross-account shares or charges.

## Follow the loaf from recipe to shelf

A recipe names the ingredients and their order. An image pipeline uses a versioned recipe to choose a base image and components, builds and validates the customization, creates an image, tests a fresh result, and distributes it to named destinations. A distribution setting cannot turn a failed image into a safe one. A successful build step cannot prove what a new instance will do after launch.

For each case, draw the recipe, the build environment and the intended destination. Then record:

1. Which artifact is being built: AMI, container image or application package? What exact base image and component versions are inputs?
2. Which tool owns each step? Consider CodeBuild for user-defined build commands, EC2 Image Builder for repeatable AMI/container-image recipes and image tests, ECR for container-image storage, and the runtime deployment controller.
3. What runs during build, validation and post-capture test? What observation would fail the pipeline?
4. What exact image identity, recipe version, component versions and test record must travel to the consumer?
5. Which Region/account receives the image? What permissions, encryption key, network, license or runtime conditions must be checked?
6. Which resources could cost money or remain after failure? Who stops and cleans them up, and how will residual usage be checked?

Do not put customer records, private keys or long-lived credentials in a base image. Do not treat a tag, “latest” label or green pipeline as enough to identify approved bytes. Keep the image build separate from deployment of application code and separate again from database migration.

## Design cases

### A. Servers built differently by each shift

Two operators create EC2 instances for the same appointment API. One applies the current runtime patch; the other follows an older checklist. The fleet autoscaling group can replace instances at any time. Design a versioned AMI recipe with a base-image update policy, build components, validation, a fresh-instance test and a named distribution target. Decide which checks belong before capture and which require the captured image. State how an old known-good image remains available until the new fleet has been observed.

### B. A container team reaches for the wrong service

A worker needs a container image with a system package, a small runtime and application code. A developer proposes Image Builder, CodeBuild and ECR as interchangeable “the image service.” Assign each job to the appropriate tool. Include how source and dependency inputs are fixed, how the container is tested, how the approved digest is stored, and which service later replaces the running tasks.

### C. The build machine passed, the new instance failed

The recipe's build and customization validation succeeded. A test on the captured AMI then fails because the monitoring agent does not start after boot. The distribution configuration includes three Regions. Decide what must happen to the distribution, what evidence to preserve, and which check was missing. Explain why a successful package installation during the build phase did not test first boot.

### D. “Green” does not identify the artifact

The pipeline says Succeeded, and an operator plans to launch `appointment-current`. Two image versions carry that label in different Regions. The records do not show which recipe revision, base image and test result produced the label in the destination Region. State what must be reconciled before launch. Explain what a digest proves and what it does not prove about the contents or security of an image.

### E. Share an AMI across business accounts

The image team wants a hardened AMI in a production account owned by another group. The AMI uses an encrypted snapshot and the groups have separate operators. Propose a design review that checks the distribution mechanism, Region, account permissions, encryption-key use, launch requirements, ownership and revocation path. Keep organization policy and cross-account execution design-only; no learner should create an Organization for this case.

### F. The failed run still has a bill

A scheduled pipeline fails during testing after launching build and test instances. The cost dashboard is delayed. Snapshots, logs and a test image may remain. Establish a stop-and-cleanup sequence that preserves diagnostic evidence without retaining unowned resources forever. Include a pre-run estimate, account-appropriate spending and credit-reserve limits, resource ownership and a later bill check. State what you cannot conclude while billing has not caught up.

## Transfer check

Change one fact: the base image receives an urgent security update; a Region is unavailable; the component downloads an unpinned package; or the test suite passes but never boots a fresh instance. Revise the recipe, evidence gate, distribution choice and recovery plan. Preserve the first answer and say which evidence changed your decision.

Ask Codex to identify one hidden build input and one unnecessary permission. Verify its suggestions against current AWS documentation and the exact target platform. A model's proposed recipe is not a built image, and a local file check is not Image Builder behavior.

## Evidence boundary

These cases assess service selection and pipeline design only. They do not validate component syntax, create or test an AMI, build a container, verify account sharing, inspect the user's credits or prove cleanup. Before any live exercise, check the selected Region's support, current prices, quotas, identity, launch network, stop condition and cleanup plan. Set limits for the account in use. Organization-dependent account-sharing and enforcement labs remain design-only unless separately authorized in a suitable environment.
