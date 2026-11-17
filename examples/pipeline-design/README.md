# Pipeline design: the delivery route is a business decision

This no-cloud exercise practices the two knowledge topics listed under DOP-C02 task 1.1: software development lifecycle (SDLC) concepts, phases and models; and single- versus multi-account pipeline patterns. It does not configure a repository, pipeline, AWS account, organization, role, key or deployment. The official objectives are in the [AWS DevOps Engineer Professional guide](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain1.html).

## Before you look at the assessor

For each case, write down your first design and label assumptions. Draw the route from code change to customer. For every stage, name its purpose, evidence, who or what can approve it, the account it touches, and what happens on failure. Then use Codex as a reviewer with the prompt in unit 03. Save its response separately, check product claims against current AWS documentation and record what you changed.

Do not put credentials, private customer data or account identifiers into a prompt. Do not run commands or create resources for these cases. If you later want to implement one, first estimate all AWS costs and establish the scoped identity, stop condition and cleanup proof. Choose spending and reserve limits for your own account.

## Cases

1. **Small personal portfolio.** One developer publishes a static portfolio from GitHub. There is no customer data. A pull request should receive quick feedback, and the owner wants to decide before the public branch publishes. Describe the lifecycle and the smallest sensible pipeline. Explain what a one-account choice simplifies and what it does not prove.
2. **A mistaken assumption.** The portfolio now has a contact form. The team discovers that its original plan sent a visitor's email address to an analytics tool. Show where the lifecycle should return to discovery/design, what checks should block promotion, and why a green build alone is not acceptance.
3. **A production service.** A team operates a booking service with development, test and production environments. A faulty change could lose bookings. Compare one account with distinct accounts. Include human approval, artifact promotion, account-to-account trust, encryption/access, observability and recovery.
4. **Tiny team, little operating capacity.** Two maintainers cannot staff a complicated platform. The organization still wants a strong production boundary. Propose a phased route that begins with a minimum viable pipeline and describes when additional environments/accounts are justified. Include maintenance burden and cost.
5. **Stop publishing.** A repository's connected branch should stop deploying while learners continue to use GitHub for unrelated code. Explain how to identify and pause every active publishing route, inspect in-flight work and decide what to do with later commits. Do not equate disconnecting one trigger with shutting down an entire hosting service.

## Record your reasoning

| Case | Lifecycle model and feedback loop | Account boundary and access path | Gate/evidence | Failure, stop and recovery | Cost/cleanup | Assumption to verify |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |

After the first attempt, compare with [ASSESSOR.md](ASSESSOR.md). That file is a discussion aid, not a calibrated exam score. Record what changed in the [learning record](../../curriculum/LEARNING-RECORD.md).
