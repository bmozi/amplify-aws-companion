# When a template changes, which thing changes?

Maya keeps repair records in a private bucket. A teammate wants a clearer tag; another wants a new bucket name. Both edits fit in one line of a template. They do not have the same consequence. Read the [decision picture](change-decision.svg), predict each result, then run the local model.

```sh
python3 examples/cloudformation-change-review/review.py
python3 examples/cloudformation-change-review/security_gate.py
python3 examples/cloudformation-change-review/retention_cost.py
python3 -m unittest discover -s examples/cloudformation-change-review -p 'test_*.py'
```

To inspect the **same six actual templates** with a separate local validator, export them into a new scratch directory:

```sh
python3 examples/cloudformation-change-review/export_cases.py --out /tmp/cloudformation-change-cases
```

This writes `baseline.json` and the five named proposals. The directory must not already exist, so a previous study is not silently overwritten. First predict which proposals a syntax and resource-property validator might reject. Then run a current validator against each exported file and write down its exact rule IDs and messages. Ask a different question of a security rule: could a syntactically valid edit still weaken public-access or transport protection? Finally ask what neither local check can observe about a deployed stack, retained objects or a customer's read. Exporting and inspecting files creates no AWS resources.

For a reproducible run with the **actual** local tools, install [cfn-lint](https://github.com/aws-cloudformation/cfn-lint#install) and [CloudFormation Guard](https://docs.aws.amazon.com/cfn-guard/latest/ug/setting-up.html) separately from their official sources. Then run this from the repository root after making your prediction:

```sh
python3 examples/cloudformation-change-review/validate_cases.py
```

The runner exports the six templates to a temporary directory, checks their resource schemas with cfn-lint for `us-east-2`, and evaluates the included [project-specific Guard rules](archive-study.guard). It reports each tool's result separately; `--out PATH.json` saves the full local report, and `--cfn-lint PATH` / `--cfn-guard PATH` select isolated executables. It never installs tools, calls AWS, creates a stack or estimates a bill. The rule file deliberately assumes this lesson's named resources and canonical policy structure. It is not a general S3 compliance standard or an effective-permission test.

The JSON [baseline template](baseline.json) is a **fictional study**, not a deployment recipe. It defines a private, encrypted, versioned bucket, a separate policy denying insecure transport, retention on deletion and replacement for **both** resources, and an owner note. The script loads it and makes five **in-memory** proposals. It neither calls AWS nor writes a proposed template. The baseline is not a snapshot of an existing stack or account.

| First predict | Then inspect |
| --- | --- |
| Add a `Review` tag | AWS's bucket property reference says `Tags` updates without interruption. Does that prove a customer can still read a record? |
| Add a `BucketName` using the stack name | AWS's bucket property reference marks `BucketName` as replacement. What happens to existing objects and the old retained bucket? |
| Turn off `BlockPublicPolicy` | This property can update without interruption. Should a security review allow it just because the update is not a replacement? |
| Remove the HTTPS-only deny from the separate bucket policy | The bucket properties do not change at all. What would a bucket-only comparison miss? |
| Add an unfamiliar property | Can a small local rule table safely guess CloudFormation behavior? |

The local output intentionally says `REVIEW_WITH_CHANGE_SET` for the tag proposal and `HOLD` for the others. These are **teaching decisions**, not CloudFormation's own change-set status. The transport case would fool a check that looked only at `ArchiveBucket`: all of its properties are unchanged, while `TransportPolicy` loses the statement that denies HTTP requests. The reviewer now reports that separate resource change and holds because its tiny rule table does not classify bucket-policy semantics. AWS documents the `aws:SecureTransport` deny and the separate public-access block settings; neither guard silently replaces the other. [S3 HTTPS policy example](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies.html), [S3 public-access block](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).

Run the second local checker before reading the assessor. It asks a different question: does **this fictional archive design** still declare four public-access blocks, default encryption, versioning, retention for bucket and policy, and a non-TLS deny for both bucket and objects? It holds the `public` and `transport` proposals for distinct reasons. It passes `name` even though the change reviewer holds replacement, and passes `unknown` even though a resource-property validator should reject an unfamiliar property. A security-invariant pass therefore cannot answer whether the template schema is valid, whether an update replaces data, or whether the deployed policy actually denies a request. Change one protection in a scratch template and predict which checker would notice it.

A real change set previews proposed changes and requires a separate decision to execute. It does not guarantee that an update will finish successfully or that the application still works. A drift-aware change set has additional drift capabilities, but those too depend on an actual stack and selected resources. [AWS change-set guidance](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html), [drift-aware change sets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/drift-aware-change-sets.html).

The bucket reference marks `BucketName` as **Replacement**, `Tags` and `PublicAccessBlockConfiguration` as **No interruption**. It also says a specified name must change when replacement is needed. The model uses only those three documented facts; anything else is unknown. A change in the referenced bucket may also affect the bucket policy and consumers. Check the actual change set rather than extrapolating from the one property. [AWS bucket resource reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-s3-bucket.html).

## Name the data and authority that do not travel automatically

The old bucket has fictional customer objects. `UpdateReplacePolicy: Retain` is meant to keep the old physical bucket when CloudFormation replaces it. It does **not** copy those objects into the new bucket, redirect customers, preserve every permission, or pay for retained storage. An apparently successful infrastructure update can therefore leave a new empty destination and a bill for two buckets. Record the old bucket owner, inventory, retention duty, migration/cutover steps, rollback point and eventual cleanup authority before approving a replacement. [AWS update-replace policy](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-attribute-updatereplacepolicy.html).

The policy is a **separate resource with a separate lifecycle**. AWS says CloudFormation removes a bucket policy on stack deletion unless that policy has `DeletionPolicy: Retain`. Its `Bucket` reference requires replacement when the target changes. The study template now gives the policy both `DeletionPolicy: Retain` and `UpdateReplacePolicy: Retain` so the old bucket's HTTPS-only deny is intended to survive a stack deletion or bucket replacement. This is a design intention, not a live permission result. A real reviewer must confirm the effective policy on **both** physical buckets, account-level public-access settings, owner, migration and eventual cleanup; retention may leave unmanaged resources and continuing charges. [AWS bucket-policy resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-s3-bucketpolicy.html), [deletion retention](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-attribute-deletionpolicy.html).

The public-access negative control teaches a different point: **change impact and security impact are separate questions**. A change without replacement can still weaken a protection. Do not treat a green syntax result, a tag-only difference or a policy-file review as evidence that the installed stack, actual object access and customer path are safe.

## Count the cabinet left behind

Think of replacing the archive bucket as moving to a new filing cabinet while keeping the old cabinet in a locked room. Keeping it may protect a rollback. It also leaves data to own, protect and eventually remove. The [fictional retention worksheet](retention-cost.json) gives the old bucket 18 GiB of current objects and 12 GiB of older versions, and the new bucket 18 GiB of copied objects. It assumes 14 overlapping days, a **made-up** USD 0.03 per GiB-month, and a simplified 30-day month. Predict the old-bucket and combined storage subtotals, then run `retention_cost.py`. This is arithmetic practice, not an AWS price quote.

The script reports USD 0.42 for old retained storage and USD 0.672 combined storage during the overlap. Neither is a complete run estimate: the fixture explicitly leaves copy requests or transfer, reads and writes, logging, and later version growth unpriced. It also records no old-object inventory, copy reconciliation, customer read, cleanup owner or verified deletion. The decision therefore stays `HOLD_FULL_COST_AND_CLEANUP` even if you shorten the overlap to one day and make the subtotal tiny. Make a separate list of what a real owner must measure, who may delete the old bucket, and which evidence must exist before declaring cleanup complete. A `Retain` flag is not that evidence.

Use [the assessor](ASSESSOR.md) only after answering these changed facts:

1. The new bucket name is approved, but nobody has counted old objects. What evidence is missing before a customer cutover?
   Now suppose someone says the old bucket is safe because its `DeletionPolicy` retains it. Which separate resource and retained cost still need review?
2. The tag proposal is accepted locally, but an emergency console edit changed the live bucket. Which observation is missing from this exercise?
3. The public-access block is weakened while a bucket policy still denies insecure transport. Does the TLS deny replace the public-access guard?
4. A real change set reports no resource replacement, but a customer read fails. Which layer must be investigated next?
5. The `ArchiveBucket` properties are unchanged, but the separate `TransportPolicy` statement is removed. What did a bucket-only comparison miss, and which observations would you need before calling transport safe?
6. The replacement finishes and the new bucket has 18 GiB of copied objects, while the old bucket still holds 30 GiB including prior versions. What did the fictional storage subtotal count, what did it omit, and who can declare the old bucket ready for cleanup?

Ask Codex to challenge your decision with the exact changed property, the official property behavior, a possible failed customer read and an omitted cost. Check its response against the cited reference and the local output. Do not paste live templates containing sensitive metadata, credentials, account IDs or customer data into a prompt.

**Validation boundary.** The change and security scripts parse a deliberately small part of JSON; the cost script uses made-up inputs and does not retrieve AWS prices. The optional runner invokes real cfn-lint and cfn-guard against exported templates, but cannot prove service-side validity, a change set, effective IAM evaluation, drift or customer behavior. Before any real deployment, inspect an account-aware change set and actual stack/permission facts, price the whole run against limits chosen for that account, and test the customer operation. This project does not authorize deploying this bucket. Organization-dependent rollout remains design-only.
