# Remote Terraform state design cases

These cases use no AWS credentials, create no state bucket, and run no remote backend. The first case has a separate **local-backend observation** below; the remaining remote-backend decisions are design only. Start with the [infrastructure ownership lesson](../../reader/BOOK-LOCATORS.md#book-485621100165252b), attempt each decision, then compare it with the [assessor notes](ASSESSOR.md).

## 1. Two operators, one production key

An engineer and a CI job both plan changes to `prod/hosting/terraform.tfstate`. The engineer's run is still applying when CI starts. Explain what the S3 backend lock is meant to do, which key it protects, and why `-lock=false` is not a normal fix.

## 2. A workspace is called `production`

The bucket policy grants the deploy role access to every state object. The operator says the `production` workspace is isolated because its name is different from `development`. Identify the actual access boundary and the changes needed if dev and production must have different authorized writers.

## 3. A lock remains after a laptop crash

The `.tflock` file still exists, but CloudTrail observations are incomplete and a CI job might be running. Define the evidence needed before any force-unlock or lock removal. State the risk of removing a live writer's lock.

## 4. The state object was overwritten

S3 version history contains an older Terraform state. A later apply may have created a resource after that version. Explain why restoring the old state does not delete the later AWS resource, what lineage and serial can tell you, and why a new plan and resource inventory are required before mutation.

## 5. State migration starts from an empty key

The team configures a new backend key, runs init and sees an empty destination. Decide whether to create resources, migrate the local state or stop. Define a private backup, expected source/destination identity, reviewed command and read-only verification that would make the migration acceptable.

## 6. A console change ignores the lock

While Terraform holds the state lock, an administrator changes the Amplify branch setting in the console. Explain why the lock did not prevent this, which tool owns the correction, and how to preserve or reverse the emergency intent without blindly applying a stale plan.

## Record the decision

For each case, name the state key, active writer, actor permission, service observation, recovery record and next stop condition. Keep account-specific state and plans private. These cases do not demonstrate S3 backend locking, actual IAM enforcement, successful state recovery or AWS drift behavior.

## Watch two local Terraform commands meet at one lock

Imagine two mechanics editing the same equipment list. The first is still recording a change when the second opens the list. A lock can tell the second to wait; it cannot tell a third mechanic what changed on the actual machine.

Before running the script, predict the second command's answer. Then predict what a **plan only** with locking deliberately disabled might propose while the first apply has not committed state. From the repository root, with Terraform 1.6 or later installed:

```sh
python3 examples/remote-state-design/local_lock_lab.py
```

The script creates a temporary configuration with only Terraform's built-in `terraform_data` resource and the default **local** backend. A controlled `local-exec` command holds the first apply for eight seconds and marks when it reaches that point. A second plan with locking enabled is refused. A deliberately unsafe, read-only `-lock=false` plan sees no committed object and proposes `create`; the script **never applies that plan**. After the first apply exits, a normal plan proposes `no-op`. It asserts all three outcomes and removes the disposable configuration, state and plan files. AWS and inherited Terraform environment variables are excluded from the child processes.

The observation shows why bypassing a lock can lead a reader to reason from an old record. It does not establish S3 `.tflock` behavior, IAM permissions, a remote runner's failure mode or protection against console and other-controller edits. Do not copy `-lock=false` into an operational fix. A remote design still needs an exact backend key, role and lock-object policy, known active writer, state history and service inventory.

**Changed case:** two teams use different state keys but manage the same AWS object. Would a successful lock on each key prevent conflict? Explain what would have to change in resource ownership before either team applies. Ask Codex for a counterexample where the lock succeeds yet the customer's service is wrong; verify it against this script's narrow observation before reading the [assessor](ASSESSOR.md).
