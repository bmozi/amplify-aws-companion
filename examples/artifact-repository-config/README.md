# Choose and configure an artifact repository

These are original design cases for DOP-C02 task 1.3 skill 01. They ask you to choose and configure the service boundary for a particular artifact. They are **design-only**: no Terraform apply, AWS credential, package repository, ECR repository, S3 bucket or spending is involved. Read the separate [assessor notes](ASSESSOR.md) after recording your first decisions.

The [Terraform examples](terraform/README.md) make the configuration shape concrete. They remain un-applied examples and intentionally contain no organization policy, cross-account access, external package source, ECR cleanup rule or public website setup.

For each case, name the artifact, producer, consumer, repository service, lookup identity, publisher/reader boundary, trust/source rule, retention and recovery rule, Region/account assumptions, cost drivers and a test that would disprove your choice. A statement such as “use S3 because it stores files” is incomplete if the consumer expects a package-manager API or container manifest.

## Case 1 — The dependency works on one laptop

A small team maintains an internal JavaScript library used by three applications. Each build currently downloads a mixture of public packages and an unversioned copy of the library from a shared drive. A new hire needs reproducible installs. Choose a package workflow, decide whether a domain should be shared, explain where upstream packages come from, and prevent an unreviewed public package from silently replacing an internal name.

## Case 2 — The image tag moved

A container was scanned and tested as `repair-api:release`. A later build pushed another image under the same tag. The deploy job still says it is using `release`, but the team cannot show which image digest reached the runtime. Design the repository and handoff configuration. Include the behavior expected on a second push and the evidence to pin the tested image.

## Case 3 — The ZIP has a public URL

A static website ZIP is uploaded to S3 and someone proposes making the whole bucket public so a deployment job can download it. Separate the build-artifact store from the public website origin. State bucket ownership, public-access and versioning choices, the key/version identity, and what would authorize the intended publisher and reader.

## Case 4 — Keep one month of images

An ECR repository grows continuously. The proposal is “delete everything older than 30 days.” The previous known-good release is 46 days old and the current deployment is failing. Replace the rule with a retention decision that protects required rollback images. Explain how to preview a lifecycle policy and what its timing means for storage estimates.

## Case 5 — A private build cannot reach packages

A CodeBuild worker runs in private subnets. It can write logs but dependency installation times out. The team suggests granting broad repository permissions. Separate network reachability from authorization. Name the endpoints, routes or egress path to investigate, then describe how a narrow package-reader identity differs from a package publisher.

## Case 6 — Artifacts cross an account boundary

A fictional company has separate production and development accounts. Production needs an approved container image produced in development, but the development account must not deploy to production or read production data. Draw the identity and repository boundaries, identify which account owns the repository and encryption key, and list both an allowed pull and denied push/deploy test. Keep this organization-dependent design fictional.

## Self-check before comparing

- Can the consumer's native tool retrieve this artifact type?
- Is the name/tag/key mutable, and if so, how is the exact content pinned?
- Can an upstream source introduce a same-name dependency?
- Do retention and recovery match rollback needs, including noncurrent S3 versions?
- Did you count storage, requests, transfer, key, scan, logging and network charges where they apply?
- Is the next step a paper design or an actual cloud deployment? This packet only supports the former.
