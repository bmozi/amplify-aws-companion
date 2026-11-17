# Signed release assessor

Read after recording your decisions in the [exercise](README.md). This fictional policy is a teaching example, not a validated security policy.

The exact signed and current fixture passes **the local gate**. All changed conditions hold. The missing or wrong signature fails at the trust boundary. Changed artifact or report bytes fail the signed fingerprint. A signed old report is authentic but stale under the exercise's chosen seven-day rule. An open high finding crosses the exercise's chosen threshold. An unknown finding status or severity also holds because the fictional policy cannot classify it, even when the report is signed. Operating-system-only coverage is incomplete for this exercise even if it reports zero findings. A signed pending report is not a completed scan. A properly signed report for A cannot approve B.

Look for a reader who explains why **authentic** and **acceptable** are different questions. The signature authenticates a statement under the pinned public key; it does not inspect dependencies. The report has to name the exact artifact, include sufficient scope and be current. A clean report still needs trustworthy scanner coverage, business tests, denied-access tests and observed deployment identity. A digest mismatch shows changed bytes; it does not say whether the change was malicious.

For the exception transfer, require the exact artifact digest, finding ID and affected operation, accountable owner identity, reason, mitigation evidence, expiry, protected signature or approval record, and a verifier that checks those fields against the current release. An exception for an old digest, an untrusted signer or an expired time must fail. If scanner support for the base image is unknown, an exception to one finding cannot create missing coverage. The scenario supplies no real exception authority or accepted risk decision, so do not score an invented approval as evidence.

The local test reports are evidence of code paths only. They cannot establish an actual ECR scan, AWS Signer identity, OCI signature, EKS/ECS admission, cost, rollout, customer safety or independent learner transfer.
