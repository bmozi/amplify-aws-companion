# Terraform shapes for three artifact stores

These are **configuration examples for review only**. They are not needed for the local artifact model and no Terraform plan or apply was run. Do not copy them into an AWS account until the identity, repository names, Region, whole-run cost, cleanup and rollback needs have been reviewed. A successful `terraform validate` does not mean an AWS resource was created.

Each subdirectory describes an independent option:

- `codeartifact/` declares a domain and an internal npm repository. It has no public upstream, publisher policy or cross-account policy.
- `ecr/` declares a private ECR repository, AES256 encryption and immutable tags. It has no lifecycle rule because deleting the only rollback image is a business decision, not a safe default.
- `s3/` declares a private artifact bucket, bucket-owner-enforced ownership, all four bucket public-access blocks and versioning. It has no public bucket policy or lifecycle rule; version history needs a deliberate retention and storage review.

The examples pin HashiCorp's AWS provider to 6.69.1 and include a lock file. The lock file keeps the selected provider version and package hashes stable; it does not pin AWS service behavior or make an apply safe. Official provider references: [CodeArtifact domain](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codeartifact_domain), [CodeArtifact repository](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codeartifact_repository), [ECR repository](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecr_repository), [S3 bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket), [bucket public-access block](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block), [ownership controls](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_ownership_controls), and [versioning](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning).

## What was checked

From the repository root, for each subdirectory:

```sh
terraform fmt -check -recursive examples/artifact-repository-config/terraform
terraform -chdir=examples/artifact-repository-config/terraform/codeartifact init -backend=false -input=false -no-color
terraform -chdir=examples/artifact-repository-config/terraform/codeartifact validate -no-color
```

Repeat the last two commands for `ecr` and `s3`. The recorded local check initialized provider 6.69.1 and validated each configuration. Initialization downloaded/reused the provider package; no AWS endpoint was contacted. The default companion runner does not install providers, so this explicit setup step stays outside that runner.

The S3 example requires a globally unique bucket name if someone later deploys it. A name that passes Terraform's local validation may still be unavailable or unsuitable. Versioning retains old object versions and may increase storage. The ECR repository is deliberately not empty after use; Terraform will not delete it while images remain unless someone changes `force_delete`. The default in these examples is conservative, but neither it nor the USD 5 project estimate is an AWS-side spend cap.

No `plan`, `apply`, AWS credential lookup or destruction command belongs to the validation record. Organization-level settings and cross-account policies stay design-only. Before any live exercise, use a scoped identity, check current account and credit terms, refresh regional pricing, estimate the entire workload against chosen spending and reserve limits, and name a cleanup and billing-verification owner.
