# Assessor notes: image pipeline design

Assess whether the learner keeps inputs, build, validation, image creation, fresh-result tests, distribution, deployment and cost cleanup as separate evidence boundaries. Reward precise unknowns and a bounded next check. These cases do not calibrate a certification score or prove AWS behavior.

### A. Servers built differently by each shift

Record an approved base AMI and its update cadence, the versioned recipe and components, the build environment and least-privilege instance profile, then validate intended configuration before capture. Test by launching the captured AMI and checking first boot, monitoring-agent health and one application-relevant behavior. Do not require the test to run only against the build instance. Distribute only after configured tests pass. Keep the previous known-good image until the replacement fleet has passed its own deployment and customer-observation checks; Image Builder is not the EC2 fleet rollout controller. Include build compute, logs, snapshots and retained images in cost and cleanup ownership.

### B. A container team reaches for the wrong service

CodeBuild can run source compilation, unit tests and user-defined container build commands. EC2 Image Builder can manage a versioned container-image recipe and image build/test/distribution workflow. ECR stores approved images, their tags/digests and repository access. ECS or another selected runtime controller deploys a service revision. Pin and record the source revision, base image and dependency versions; test the produced container rather than assuming build success means runtime readiness. No one of these services automatically proves the other's work.

### C. The build machine passed, the new instance failed

Stop distribution because the configured post-capture test failed. Preserve the recipe, build/test logs, source image identity and failed image identity; fix the startup/boot behavior and rerun the complete pipeline. The missing evidence was a test that launches from the captured AMI and verifies the monitoring agent after first boot. No Region should receive the image unless its own intended distribution outcome and launch permissions are confirmed. Do not delete diagnostic evidence or assume a partially distributed image was automatically removed; inspect destinations before cleanup.

### D. “Green” does not identify the artifact

Hold launch. Reconcile the destination Region's actual image identifier/digest with the exact recipe and component versions, base image, build execution, test results and distribution record. A digest can identify bytes; it does not prove that the recipe was approved, the contents intended, the vulnerability scan current, or the image booted successfully. A mutable tag is a locator, not a stable cross-Region release identity. Verify each destination copy.

### E. Share an AMI across business accounts

Review the supported Image Builder distribution/share path and the current AMI/snapshot/KMS requirements for the chosen Region and accounts. Check the producer's distribution permissions, consumer launch permissions, key policy and grants, encryption mode, account ownership, revocation behavior, audit visibility and the selected production role. A shared image reference is not enough if the consumer cannot decrypt or launch it. This is intentionally design-only because it depends on an AWS Organization/account boundary and separately authorized credentials.

### F. The failed run still has a bill

First stop a repeating schedule or trigger and any active run using the selected supported control. Preserve the run ID and required diagnostic logs. Inspect actual temporary instances, volumes/snapshots, AMIs, ECR artifacts, logs and validation resources before removing only the known disposable outputs. Before a run, check its estimate against whole-run spending and reserve limits chosen for the account; stop if either fails. Delayed billing means the eventual charge is not yet known. Recheck resources and cost after cleanup and allow the billing data to catch up before recording the final estimate.

## Scoring guide

For each case, score 0–2 in five dimensions: correct tool boundary; controlled inputs and output identity; meaningful build versus post-capture evidence; destination and least-authority reasoning; full cost, stop and cleanup plan. A score of 0 is unsafe or unsupported; 1 is plausible with missing evidence; 2 is reasoned and states assumptions. This is an editorial prompt, not a calibrated AWS certification rubric. The learner's actual attempt is still unobserved.

AWS Image Builder documentation was reviewed for current recipe, component, stage, testing, distribution and cost boundaries. No pipeline was executed, and independent technical and learner review remain pending.
