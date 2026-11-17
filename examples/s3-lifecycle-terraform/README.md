# S3 Lifecycle configuration with Terraform

This is a local teaching example. It creates no bucket during validation. It is designed for a **new, empty, disposable lab bucket** and only manages keys under the `temporary/` prefix. Do not point it at a bucket with existing data until you have inventoried every matching current version, noncurrent version and incomplete multipart upload.

## What the rule means

The example enables versioning, blocks public access and declares one lifecycle-configuration resource for the bucket. After the configured example age, S3 Lifecycle can expire the current version under `temporary/`. Because versioning is enabled, that action generally places a delete marker; it does not immediately erase the older data version. The separate noncurrent-version rule makes older matching versions eligible for permanent deletion after their configured age. The multipart rule aborts incomplete uploads under the same prefix.

Lifecycle actions are asynchronous. A day count is an eligibility rule, not an exact time when a customer loses access or a worker runs. Current-version expiration and permanent deletion of older versions have different recovery effects. Rules can apply to matching objects already in the bucket when configuration changes. These details make the example unsafe as a default retention policy. Read the current [S3 lifecycle action documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-rules.html) and [Terraform lifecycle resource reference](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_lifecycle_configuration) before adapting it.

The example's 30-, 90- and 7-day values are invented lab settings, not business or legal guidance. Set retention only after the data owner approves the requirement. Estimate version storage, requests, retrieval, incomplete-part storage and any other retained costs. The bucket resource uses `force_destroy = false`; this does not stop an S3 lifecycle rule from expiring matching objects.

## Check the files locally

From this directory:

```sh
terraform fmt -check
terraform init -backend=false
terraform validate
```

`init` downloads the HashiCorp AWS provider into the ignored `.terraform/` directory and records a provider lock file for reproducibility. `validate` checks syntax and internal configuration consistency; it does not check AWS permissions, bucket-name availability, S3 acceptance, live cost or the objects a rule would match. No plan or apply is part of this exercise.

Before any future run, estimate the short test's full cost against spending and reserve limits chosen for the account. Confirm the account identity, selected region, unique bucket name, empty bucket, exact lifecycle filters, owner-approved retention, destroy/cleanup procedure and evidence to be captured. A Terraform plan cannot determine whether deletion matches the business's retention intent, and deleting the bucket or removing the rule cannot restore versions already expired.

Use the [lifecycle lesson](../../reader/BOOK-LOCATORS.md#book-7d10901624b228c4) and [paper cases](../backup-lifecycle/README.md#case-2-read-a-lifecycle-rule) first. This example has not been applied to AWS.

## Review a changed rule before validation

Before reading [the assessor](ASSESSOR.md), inspect `main.tf` and its variables without applying them. The owner now requires all versions under `temporary/held/` to remain recoverable for 180 days, while other temporary objects keep the original policy. Does the existing prefix still include the held objects? Does `force_destroy = false` stop lifecycle expiration? Draw current and noncurrent clocks, propose disjoint classification/rule scopes, and explain why syntax validation cannot approve the retention decision. Then change the requirement to immediate customer access removal with continued retention: which enforcing path must change separately?
