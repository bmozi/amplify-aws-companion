# Where does a cloud rule actually stop the change?

Maya's team writes a template for a reports bucket. Her rule says, “the bucket must declare encryption and all four public-access-block settings.” A check in the repository passes. A second operator then creates a bucket directly in the AWS console, and a third changes a deployed bucket later. Did the repository check control those changes? Trace the path before answering.

This offline exercise supports [SAP-C03 skill 5.1.2](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain5.html) and follows the [governance lesson](../../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e). It does not activate a CloudFormation Hook, create a Config rule or attach an SCP. It is not a complete S3 security policy.

```text
template in Git -> local/CI rule -> reviewed deployment -> CloudFormation Hook -> resource
                                                     direct API path ─────────────> resource
resource state -> AWS Config / drift review -> owner decision -> bounded repair
organization permission boundary -> evaluates applicable actions, not template prose
```

One door check does not guard every door. [CloudFormation Guard](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-guard.html) can validate templates before deployment. [CloudFormation Hooks](https://docs.aws.amazon.com/cloudformation-cli/latest/hooks-userguide/hooks-concepts.html) can warn or fail selected CloudFormation operations according to their configured target and failure mode. [CDK aspects](https://docs.aws.amazon.com/cdk/v2/guide/aspects.html) act during synthesis of a CDK app. [CloudFormation drift detection](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html) and AWS Config observe selected deployed properties under their respective scopes. An SCP limits applicable member-account principals' available permissions; it does not turn a failing template rule into an allow or a repair. Each must be scoped and tested for the chosen account, Region, resource and call path.

## Run the small specimen

From the repository root:

```sh
python3 examples/policy-as-code-gates/gate.py
python3 -m unittest discover -s examples/policy-as-code-gates -p 'test_*.py'
```

Open `template.json`. Change `RestrictPublicBuckets` to `false`, then run the gate and restore it. Remove `BucketEncryption`, run again and restore it. The Python specimen inspects only two declared template-property conditions. It is **not** CloudFormation Guard, a Hook, a policy evaluation engine, a proof of effective encryption or a deployed-resource check. For an actual policy-as-code implementation, translate the reviewed requirements into supported Guard/Hook/CDK rules, test passing and failing templates with those tools, and prove the enforcement and bypass scope in an authorized environment.

## Six changed-condition decisions

For each case, name **the actor, path, check that can see it, check that cannot, expected observation, owner and rollback consequence**.

1. **Pull request:** A trainee removes one public-access-block flag. Which local or CI validation should stop the change before it reaches the main branch? What does a green check prove about that one template?
2. **CloudFormation change:** A team edits the stack through a different repository. Could a configured Hook catch the targeted resource operation even though the first repository's check did not run? What must be true of Hook scope and `WARN` versus `FAIL`?
3. **Direct API:** An administrator creates a bucket outside CloudFormation. Would the same Hook or CDK aspect necessarily see it? What identity, resource and organization controls would you inspect? Do not assert that an SCP alone enforces the desired object-level property.
4. **Later drift:** An operator changes a property after deployment. Distinguish a proactive check from Config evaluation and CloudFormation drift detection. What owner should review an automatic remediation proposal before it can overwrite a deliberate emergency change?
5. **False pass:** The specimen passes because the property exists, but the encryption configuration is malformed or the bucket's actual effective controls differ. What deeper schema, change-set and live negative tests would you require? How would you detect a resource type the rule never visits?
6. **Organization rollout:** A policy is to apply across several accounts and Regions. Name the canary scope, unaffected management-account path, service support, evidence of intended denial, recovery operator and cost of a mistaken broad rule. Keep organization changes design-only in this exercise.

Ask Codex to find a path your rule does not observe and a false positive or false negative in the specimen. Verify each proposed AWS behavior against current primary documentation. Compare your answer with the [assessor notes](ASSESSOR.md). The exercise uses no AWS account, cloud resource or credit.
