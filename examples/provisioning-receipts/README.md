# A successful operation can leave a destination behind

Maya's booking team prepares a reviewed machine image, then plans a release to test and two production locations. The release dashboard says **SUCCEEDED**. One production destination is `OUTDATED`, still has the old image, and has no usable booking capacity. A top-level green status cannot tell Maya that customers in every intended location received the release. This is a fictional packet; no AWS operation or resource is created.

Run the local receipt screen from the repository root:

```sh
python3 examples/provisioning-receipts/lab.py
python3 -m unittest discover -s examples/provisioning-receipts -p 'test_*.py' -v
```

The model checks the reviewed source and infrastructure-plan identities, exact target set, failed-instance count, destination status, image digest, capacity and customer behavior. Its passing case means only that the **supplied fictional receipts** are internally complete. It does not discover actual stack instances, inspect permissions, synthesize CDK, run a Terraform plan, deploy an AMI or measure customers. AWS documents that a StackSet operation can report `SUCCEEDED` while some stack instances failed within the configured failure tolerance; inspect operation results and each target's status and reason before treating the rollout as complete. [AWS StackSets troubleshooting](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-troubleshooting.html).

Attempt these changes before opening [assessor reasoning](ASSESSOR.md):

1. **Image shelf:** The image recipe's test passed, but the production receipt still names yesterday's image digest. What is the difference between building, distributing and launching the reviewed AMI or container image? Which exact identity must travel with the release?
2. **Two infrastructure owners:** A CDK app synthesizes a CloudFormation template for the backend. A Terraform configuration also plans to create the same table. Which definition owns it? Compare a CDK/CloudFormation change set with a Terraform plan as previews, and explain why neither proves business behavior.
3. **First failed boundary:** One deployment fails. Its stack event names a subnet with insufficient available addresses; another says access denied. For each, identify the observed error, the next service-specific evidence, the responsible owner and a bounded correction. Do not widen permissions or resize a network from a vague dashboard headline.
4. **Three destinations:** A StackSet operation says `SUCCEEDED`, with one failed instance. Name the account/Region and instance result you must inspect before retrying. Explain why a permitted failure count cannot be reworded as “all locations updated.”
5. **Share or create:** Another team needs a supported subnet owned by a network account. Compare sharing that existing resource through AWS RAM with deploying a new stack into each account using StackSets. Who owns the shared resource? What additional account/Region and permission checks are required? What changes if the resource type cannot be shared?
6. **Traffic and customer:** A release controller moves traffic to the new application. The homepage works, but a known confirmed booking is missing in `prod-west`. What should happen to the release gate and incident clock? Which compatible previous state or roll-forward repair is possible if the database has already changed?
7. **Toolchain transfer:** The personal lab uses Git for reviewed source, Terraform for Amplify Hosting and Amplify Gen 2/CloudFormation for its backend. Trace one change from commit to selected destination, name each tool's state/owner, and show how to stop automatic publishing for an unrelated GitHub repository without disabling Git itself.

Ask Codex to challenge your destination inventory and the first failed boundary. Give it only fictional receipts, not live credentials or customer records. Verify service-specific claims against current AWS documentation. Cross-account and Organizations work stays **design-only** unless separately authorized in a suitable environment. Any separately authorized live lab first needs a scoped non-root identity, an exact Region/resource whole-run estimate, account-appropriate spending and credit-reserve limits, a stop condition, cleanup and later billing reconciliation.

References: [EC2 Image Builder](https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html), [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html), [CloudFormation change sets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html), [StackSets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html), [AWS RAM](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html), [StackSets troubleshooting](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-troubleshooting.html).
