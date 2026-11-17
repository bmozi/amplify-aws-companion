# Individual knowledge review for DOP-C02 task 1.3

Internal editorial review, updated October 19, 2026. This records partial evidence for all three knowledge ordinals: artifact use, generation and lifecycle management. It does not establish repository configuration or automated AWS build skills. [Official domain source](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain1.html).

Fetched the official Markdown directly after the browser retrieval reported unsupported Markdown content type. Parsed task 1.3 as three knowledge and three skill entries. Ordinal 01 matches the accepted inventory SHA-256 `c32784b8a4e0f9ad5fec337941a1da51ec73b87e7521adc0226f7aa8cffd41c9`; domain SHA-256 is `04b66f2cbe775bf3d16eb987eb145863dd7d124675ca812597e3a24de457513d`. Retained source: `artifacts/curriculum-research/dop-artifact-review-source.md`. Ordinals are editorial identifiers, not AWS-issued scores.

## Evidence that supports the mapping

Unit 03's “Keep the tested package attached to its evidence” explains an artifact as the actual built bytes, distinguishes a version label from a digest, and connects the checked artifact to configuration, destination and behavior. The compact diagram shows the handoff decision. It explicitly separates matching bytes from trustworthy evidence and observed service behavior.

The [local operations drill](../../examples/local-operations/README.md#follow-the-checked-bytes-through-publication) asks readers to predict rejection and promotion outcomes. Its [implementation](../../examples/local-operations/lab.py) tests the customer result before creating a trusted local receipt. Changing artifact bytes, configuration or destination rejects promotion and leaves the prior selection unchanged. Matching inputs succeed; a rebuilt file with equal parsed values succeeds after its own check. These positive cases prevent an always-reject controller from satisfying the exercise. The author recorded source-bound local execution in a separate owner log; this mapping did not rerun the drill. Follow the linked lab to collect your own result.

The [publication-boundary assessment](../../examples/publication-boundaries/README.md) and [assessor notes](../../examples/publication-boundaries/ASSESSOR.md) extend reasoning to competing release paths, effective publishing authority and a shared-repository transfer. These fictional cases test design reasoning; they do not authenticate a real publisher. E15 and the learning record preserve first predictions, observed results and AI-assisted revisions separately.

## What remains before a stronger claim

The receipt is an ordinary in-process dictionary. It does not prove builder identity, signature validation, tamper-resistant evidence storage, concurrent handoff integrity or protected repository access. The teaching does not implement CodeArtifact, S3 artifact delivery or ECR permissions. Selecting a locally retained predecessor does not establish a compatible cloud rollback or a retention/deletion policy.

Add the selected service's access and lifecycle design, verify permitted and unrelated-target operations through the actual scoped role, test artifact availability and handoff integrity under realistic failure conditions, and connect the observed serving version to its release evidence. Use current service documentation and bounded costs for any live run. Assess an independent reader's changed-case response. Artifact generation is reviewed separately below. This knowledge review does not establish the three implementation skills; see the separate [task 1.3 skill review](../skill-reviews/DOP-1-3.md), where all three skills now have partial individual evidence maps. These maps do not prove live repository, build-service or image-pipeline configuration. A source ZIP or successful local build alone cannot close them.


## Artifact lifecycle decisions — ordinal 03

Re-fetched the official domain Markdown on October 18, 2026. Task 1.3 still contains three knowledge and three skill entries. Knowledge ordinal 03 matches accepted SHA-256 `c609e7764a2f4197dc06daa82300f68444af921c908054743fba39d8f3e020c9`; domain digest remains `04b66f2cbe775bf3d16eb987eb145863dd7d124675ca812597e3a24de457513d`. Retained source: `artifacts/curriculum-research/dop-retention-review-source.md`.

Unit 15's “Keep a recovery image for a reason, then retire it deliberately” supplies explicit lifecycle teaching: use-based retention, exact image/reference inventory, replacement versus current-process health, policy preview versus recovery requirements, restricted investigation retention, bounded cost comparison and post-cleanup verification. Its dependency diagram makes the join between registry and operating records visible. It cites official ECR behavior while keeping the broader business decision separate from rule evaluation.

The [five retention cases](../../examples/artifact-retention/README.md) and [separate assessor criteria](../../examples/artifact-retention/ASSESSOR.md) require decisions under missing vulnerability, pull-permission, retrieval-time and pricing evidence. A ZIP transfer tests which principles survive a change of artifact service and which ECR mechanics cannot be assumed. E15 and chapter evidence link these actual files. The scoped HTML review records visual coverage, not learner comprehension.

Coverage remains partial. No real lifecycle policy preview, artifact deletion, archive retrieval, cross-reference inventory reconciliation, replacement startup or billing measurement was performed. These require a selected service, current documentation/prices, effective identity review, bounded execution and observed recovery/cleanup. No account-wide deletion is authorized by the fictional cases. Artifact-generation knowledge is reviewed below; implementation-skill evidence is maintained separately.


## Artifact generation decisions — ordinal 02

Re-fetched official domain Markdown on October 18, 2026. Task 1.3 contains three knowledge and three skill entries. Knowledge ordinal 02 matches accepted SHA-256 `772ee89930d3976506279a3b9f34cb7ba0ac809d5789b567ba54c2ab3c94e6e5`; domain SHA-256 remains `04b66f2cbe775bf3d16eb987eb145863dd7d124675ca812597e3a24de457513d`. Retained source: `artifacts/curriculum-research/dop-generation-review-source.md`.

Unit 03's “Build the parcel from the intended contents” explains source, tools, dependencies, configuration and generated inputs before artifact handoff. Its diagram distinguishes stale output from fresh staging. The [build walkthrough](../../examples/local-operations/README.md#inspect-what-the-build-actually-packages) and [executable](../../examples/local-operations/build_inputs.py) show real static-file copying and ZIP creation. An updated homepage can coexist with an unwanted old file. Fresh staging must produce both the required names and their expected bytes. Controlled archive metadata and ordering yield identical fixture bytes twice; changing one input changes the result.

An owner-only execution record reports a passing suite and a negative control that reintroduced the stale file and failed at the exact-content assertion. This review did not rerun the [build-input drill](../../examples/local-operations/README.md#inspect-what-the-build-actually-packages). Run it to collect your own result. The manuscript visual review covers presentation only. Neither result establishes an authenticated builder, reproducibility across hosts or a complete CodeBuild pipeline.

For the walkthrough's three changed cases, assess the following reasoning after the learner attempts them:

1. A homepage check and digest can accurately identify a package that still contains the expired offer. Inspect the complete path/content contract and relevant behavior. The digest cannot decide whether the chosen contents were intended.
2. A mutable downloaded input means the Git revision alone is not the whole build recipe. Record and control the actual downloaded version/content and other relevant inputs. Each digest still identifies its own output bytes; differing outputs do not automatically mean either is malicious or that a previous check covers both.
3. Absence of a forbidden file is only one condition. Require the intended pages and data with expected content/behavior. The positive exact-content assertion prevents an empty package from satisfying release acceptance.

These criteria assess artifact-generation reasoning, not AWS tool configuration. Coverage remains partial: the executable has no compiler, external dependency resolution, secret injection, container-image build or machine-image creation. Further work needs a selected real toolchain, complete input provenance, cache-invalidation and dependency evidence, build-role access, actual generated-output behavior and an independent changed-case learner response. This knowledge review does not establish repository or build-tool configuration; see the separate task 1.3 skill review for partial CodeBuild and image-build coverage. Skill 01 (artifact-repository configuration), skill 02 (build-tool configuration) and skill 03 (image-build automation) now each have partial individual maps in the separate skill review. Their service configurations and real permissions remain unverified. No cloud execution or credits are required for this review.
