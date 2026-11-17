# Assessor reasoning for the two-door export

Use this after preserving the learner's first answers. These are **predicted outcomes under the stated fictional policies and assumptions**, not observed AWS results.

1. The intended version and key-use path are present in the specimen. A real read must still confirm actual role identity, S3 object encryption metadata, key state/Region, effective policies and a correct plaintext result. Policy text alone does not prove success.
2. The explicit S3 deny on a different `s3:VersionId` stops that object-version request under the specimen. KMS access cannot grant S3 object access.
3. An unversioned read uses `s3:GetObject`; the named object's explicit deny rejects it under the specimen. The approval is tied to one version's bytes, not whatever later becomes current.
4. The key policy has no general decrypt delegation to the account principal. A broad reader IAM allow alone cannot add the missing key-policy authority. Investigate the exact intended role, key and conditions; do not widen all keys to recover one export.
5. Direct KMS use lacks the `kms:ViaService` value required by the reader statement. S3 Bucket Keys change the encryption context from object ARN to bucket ARN, so the specimen's context condition may no longer match. Inspect the actual request and object/key configuration. A 403 by itself does not locate the gate.
6. The reader needs the correct protecting key and authorization in the operation's context. Object bytes, a version label and permission to an unrelated key are not decryption evidence. The application must also keep restored or exported plaintext within its approved audience.

Reject answers that treat the static checker as an IAM simulator, claim a KMS permission supplies S3 access, assume a version ID is a business approval, or suggest deploying these fictional JSON files unchanged. For changed-case assessment, remove the version-specific deny or enable Bucket Keys and ask the learner to revise the diagnosis and test plan without asserting a live result.
