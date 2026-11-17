# DOP-C02 task 2.3 knowledge review — automate complex work at scale

Internal curriculum review, October 19, 2026. The current [AWS DOP-C02 Domain 2 objective](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain2.html) lists two knowledge items and four skills for task 2.3. Source Markdown was refreshed through `scripts/inventory-knowledge.py --refresh`; the two recorded bullet digests remain unchanged. This review maps both items to current lesson and practice evidence. Both remain partial. No AWS resource or account was queried or changed.

## Knowledge 01 — AWS services and solutions for automating tasks and processes

The reader now has a decision path in [Unit 16](../../reader/BOOK-LOCATORS.md#book-b139eca792554b54): Systems Manager Inventory provides observations for managed nodes; State Manager can maintain a desired configuration; Patch Manager scans or installs against a selected baseline; AWS Config evaluates recorded resource configurations; Automation and maintenance windows can coordinate bounded actions. The lesson also distinguishes inventory, desired state, compliance result and remediation so a reader does not treat them as synonyms. Unit 13 already compares a visual Step Functions state machine with code-first Lambda Durable Functions for multi-step workflows. The new fleet figure ties these ideas into a observe → verify → scan → staged change → verify loop.

The [fleet-maintenance exercise](../../examples/fleet-maintenance/README.md) checks an invented target set, stale inventory, platform eligibility, baseline version, canary health, stop-on-error behavior and duplicate operation identity. The model is deliberately local and sequential. It is not an AWS Systems Manager simulator, a patching implementation or evidence that a selected service can perform a business change safely.

**Remaining evidence:** an independently reviewed service/feature/Region selection for a real fleet, supported OS and patch source; a scoped managed-node identity and delivery path; price and cleanup evidence for an authorized run; and learner transfer across another maintenance case.

## Knowledge 02 — methods and strategies for interacting with AWS software-defined infrastructure

Unit 09 teaches declarative infrastructure ownership, plan review, state, drift and controlled change. Unit 16 now adds the operational side: inspect current managed-node observations, compare them with an approved target and baseline, and use bounded service APIs/workflows for the change. The explanation emphasizes explicit account, Region, target IDs, stable operation identity, idempotent handling, staged rollout, per-target result and reconciliation. It connects to Unit 13's workflow review and existing request/retry material in Unit 27.

The assessment asks readers to reject stale or incomplete target evidence, distinguish a proposed state from observed state, and reconcile a repeated event rather than blindly repeating an effect. The local model proves only its own comparison and transition logic. It does not verify real AWS SDK/CLI/IaC permissions, API throttling, service control-plane outcomes, IAM evaluation, or cross-account deployment behavior.

**Remaining evidence:** a selected, non-root, least-privilege AWS API path; a reviewed change set or automation request and real service response; observed throttling/retry/partial-failure behavior; and an independent reader's explanation without the assessor notes.
