# Assessor notes: CodeBuild artifact configuration

Keep this file separate from the learner's first response. These are evaluation criteria, not a single required architecture. Review the learner's changed-case explanation as well as the initial answer.

## Case 1

A strong response identifies the mismatch between the produced `dist/` directory and the declared output paths. It selects only the built site and checks that CodeBuild's project artifact configuration and any CodePipeline output artifact are compatible. Evidence includes the build ID/source revision, artifact object or pipeline artifact identity, complete expected file list and a downstream check of those bytes. A successful command alone does not show the artifact was uploaded or passed to the next action.

## Case 2

A strong response writes into a fresh staging/output directory, selects a narrow `dist/` base and expected files, and prevents local environment files and scratch files from entering the artifact. It states both a negative assertion (the obsolete or sensitive path is absent) and a positive assertion (required content exists and behaves correctly). Do not accept an empty ZIP as proof of correctness. The local drill already supplies a real stale-file counterexample; do not claim it exercises CodeBuild.

## Case 3

The CodeBuild service role is an execution identity assumed by the service; it is not the human caller and does not need administrative authority merely because a later stage deploys. Scope source/artifact/log read-write permissions to selected resources and add no deployment permissions unless the build's defined job requires them. Separate the caller, build role and downstream deployment role. Test the intended path and an unrelated resource denial. Exact actions and resource types vary by chosen source and artifact integration and require current policy review.

## Case 4

Move the token into Secrets Manager or Parameter Store, reference it through supported build configuration, grant only the required secret-read action to the build role and avoid printing it. Confirm secret rotation/version behavior and that the new build can retrieve the intended key without exposing the value. Log masking is not a safe-output contract; transformations or explicit application output may reveal it. Never request or record an actual secret.

## Case 5

The answer inventories source, external package, internal test endpoint, artifact upload and log paths, then checks endpoint support, DNS, routing, security-group egress, route tables and relevant role permissions. It compares the fixed and data-processing charges of NAT with endpoint-specific charges and operational complexity, using current Region pricing and availability. The cheapest valid plan may be no VPC attachment if the internal endpoint is not needed; it may not assume every external hostname can be reached through an AWS endpoint. A design claim is not a route test.

## Case 6

CodeBuild is the normal fit for installing a toolchain, running a compiler/tests and packaging an artifact. A CodePipeline Lambda action can fit a short, bounded custom task such as an HTTP check; it must report its result using the action contract and have scoped permissions/timeouts. The Lambda action's success does not establish the whole application works, and a CodeBuild success does not prove deployment. A post-deployment probe must inspect the intended endpoint and business-relevant response, and independent customer observations may still be needed.

## Score each case on these dimensions

- Correct boundary: source, project, buildspec, role, cache, artifact store and deployment are not conflated.
- Positive and negative evidence: required output is present and forbidden/stale output is absent.
- Changed-case transfer: the recommendation changes when the workload, trust boundary, network need or output changes.
- Cost and cleanup: estimated support resources and stop conditions are named before live work.
- Evidence language: design, local execution, cloud execution and learner outcome remain distinct.
