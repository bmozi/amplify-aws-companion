# Individual knowledge review for DOP-C02 task 1.1

Internal editorial review, October 19, 2026. Both listed knowledge items now have individual teaching and changed-condition assessment mappings. This is partial evidence for concepts, not evidence that the task's implementation skills or exam readiness are complete. [Official task source](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain1.html).

The current official guide lists knowledge of SDLC concepts, phases and models, and pipeline deployment patterns for single- and multi-account environments. The retained Domain 1 source digest is `04b66f2cbe775bf3d16eb987eb145863dd7d124675ca812597e3a24de457513d`. Inventory bullet digests remain `8fb78b24df18f5eb2b5e277c8af97844d7960104f2882a50fa21d451b8374c34` and `6c7a9b9f61bfe41027d452ddd2e70a3b385dd5fd35469ed761cb241e65267801` respectively.

## SDLC concepts, phases and models

Unit 03 now begins with Maya's appointment-reminder request and traces need, planning, design, implementation, checking, release, operation and learning. It explains that this is a loop, not a required one-way waterfall. Iterative/Agile work revisits assumptions; a staged model can agree on more detail earlier; either still needs feedback, tests and operational learning. The section distinguishes continuous integration, continuous delivery and continuous deployment at the production-approval boundary, using AWS Prescriptive Guidance.

The five [pipeline design cases](../../examples/pipeline-design/README.md) include a mistaken data-use assumption and a stop-publication scenario. The [assessor](../../examples/pipeline-design/ASSESSOR.md) checks whether learners return to discovery/design after a requirement changes, preserve first reasoning and distinguish successful build from customer acceptance. No independent learner has attempted or calibrated these cases.

## Single- and multi-account pipeline patterns

Unit 03 uses the workshop/rooms analogy to compare ease, access boundaries, blast radius and operating burden. It explains why separate accounts can help isolate development/test/production and why a cross-account handoff still needs explicit trust and artifact-access design. It does not prescribe an organization or universal account count. For CodePipeline it cautions that destination roles, artifact-bucket access and key policies may be relevant, depending on the design.

The design exercise changes the context from a personal static site to a booking service and a small operations team. The assessor checks the complete access/artifact/key/log/cost/recovery path and rejects the assumption that additional accounts alone establish safety. No AWS account, organization, role or pipeline was inspected or changed.

## Remaining evidence

Coverage remains partial. The exercise is design-only; it has no measured AWS implementation, selected service configuration, policy simulation, cost estimate or independent technical/learner review. The five task skills (repository setup, version control integration, build configuration, secret management and deployment strategy selection) are not claimed as covered by this review. Recheck the AWS objective wording before future reuse, then test a selected low-cost sandbox plan only when the documented cost, access and cleanup gates are met.
