# Individual skill review for DOP-C02 task 2.1

Internal editorial review, October 19, 2026. The [official objective](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain2.html) names four separate skills. Each mapping below is partial. Case numbers refer to the [governance review exercise](../../examples/governance-review/README.md), with criteria in its separate [assessor notes](../../examples/governance-review/ASSESSOR.md). These exercises are design-only for the personal trial account; they do not establish a live AWS implementation, independent review or exam readiness.

## Compose and deploy IaC templates — skill 01

[Unit 09](../../reader/BOOK-LOCATORS.md#book-485621100165252b) teaches the Terraform change lifecycle, state ownership and remote backend collaboration. [Unit 16](../../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e) introduces CloudFormation modules, CDK constructs and Service Catalog products in plain language. Cases 15, 19 and 20 ask learners to select a rollout, define reusable inputs and reject a syntactically valid but unsafe template. Earlier validated Terraform examples provide some actual IaC schema/format experience.

Coverage remains partial because this chapter does not compose and deploy a representative SAM/CloudFormation/CDK workload or compare their full change/recovery workflow. No AWS plan, change set, synth/deploy or rollback occurred. A complete practical follow-up needs a selected template, scoped identity, reviewable diff, positive/negative checks, a bounded cost estimate and cleanup evidence.

## Apply CloudFormation StackSets across accounts and Regions — skill 02

Unit 16 explains StackSet purpose, permission models, OU targeting, automatic deployment and account-leave behavior, rollout waves, operation preferences, drift and business-level acceptance. Cases 15–17 require the learner to choose a small wave, inspect partial failures, account for deletion/retention and define a stop owner.

This is design-only. No Organization or StackSet exists in the personal trial. There is no operation, per-account/Region result, drift report, auto-deployment or retained-resource observation. A real assessment needs a separately authorized multi-account environment and an approved target list, tested recovery, cost and cleanup plan.

## Select configuration-management services — skill 03

Unit 16 compares AppConfig, Systems Manager State Manager and AWS Config according to what changes. Case 18 changes the requirement across gradual feature delivery, managed-node desired state and configuration compliance. It explicitly treats OpsWorks as a historical exam term because AWS lists OpsWorks services as shut down on May 1, 2024.

Coverage is selection and design, not configuration. No application rollout, node association, Config recorder/rule, rollback or measured result exists. Refresh lifecycle and feature details before a real implementation; evaluate least-privilege roles, enrolled targets, cost and recovery in an authorized environment.

## Implement reusable IaC patterns and controls — skill 04

Unit 16 distinguishes CloudFormation modules, CDK constructs and Service Catalog products/constraints. Cases 19–20 ask about ownership, versions, consumer inputs, permissions, safe defaults, retention, validation, cost, rollout and retirement. The accessible figure [governance-automation-path](../../book/figures/governance-automation-path.svg) locates review, rollout and evidence in a simple sequence. [Unit 09's governed-plan lesson](../../reader/BOOK-LOCATORS.md#book-897eb92eeddf89d2) and the [local Terraform proposal lab](../../examples/governed-delivery/README.md) add actual saved-plan JSON inspection, two rejected proposals and an emergency-intent reconciliation in disposable state. The [two-consumer module lab](../../examples/reusable-module/README.md) now builds and consumes local v1/v2 Terraform modules through separate state histories, checks rejected inputs and upgrades only one consumer.

The mapping is partial. The local string-and-shape guard is a small proposal check, not effective IAM or a reusable governance product. The providerless Terraform module is built and consumed locally by two configurations, but its version folders are mutable paths, not a published immutable release, and its retention value creates no lifecycle control. No CloudFormation module, CDK construct, Service Catalog product, launch constraint or multi-account governance rollout exists. A future implementation needs selected consumers and standards, an immutable source, scoped test environment, security checks, change review, failure behavior, cost and cleanup evidence, plus independent learner and technical review.
