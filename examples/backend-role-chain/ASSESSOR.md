# Assessor notes: follow the role that actually builds

Open only after the learner records a first answer. These are provisional reasoning criteria for fictional cases, not verified AWS permissions or a calibrated exam key.

**A — hold backend mutation.** A non-root caller reduces one risk, but the CloudFormation execution role remains broadly powerful under the stated attached policy. Inspect its effective ceiling, trust and the deployment-role path before claiming scoped deployment. AWS documents `AdministratorAccess` as the CDK bootstrap default; this case stipulates an actual attachment rather than inferring current account state from that default.

**B — hold backend mutation.** The branch-shaped caller policy does not describe the downstream CDK roles, CloudFormation execution authority or who may later operate the stack. Record those identities and policy documents before deciding. A narrow-looking first policy cannot establish the whole chain.

**C — hold pending stack-access review.** CloudFormation can reuse a stack's associated service role for later operations. AWS warns that users with permission for stack operations may use that role even without a fresh `iam:PassRole` grant. Check the second operator's exact stack actions, stack identity and service-role association, and test intended and forbidden operations with a reviewed safe target. The narrow execution policy is useful but does not settle who may invoke it through the stack.

**D — hold.** The denial is evidence the current path cannot deploy as configured. Replacing it with account-wide `iam:PassRole` would permit passing unrelated powerful roles. Review the named execution-role ARN, intended CloudFormation service, deployment workflow and policy evaluation; generate or validate a candidate scoped grant and test one intended pass plus representative forbidden roles. Do not write a wildcard repair from the error message alone.

**E — hold.** A denied or incomplete read is **unknown**, not proof the role lacks an administrator policy. Obtain the missing inventory under appropriate read-only authority. The preflight is designed to retain this as a review item rather than producing a clean verdict.

**F — limited static publication path only after its own live review.** The proposed frontend role is intentionally shaped for one Amplify Hosting branch. It has not been installed or verified live in this project. It does not grant the CDK backend deployment and execution path, and stretching it for that purpose would erase its narrow job. Keep backend repair separate.

For the changed **A** case, the file-publishing role and asset bucket become a separate path to inspect: trust, assumption permission, bucket scope, object write/read, and the effect of a malicious or mistaken asset. A narrowed execution role does not automatically narrow asset publishing. A strong response also keeps cost and cleanup separate from IAM; a correct allow/deny result does not prove a Free-plan run is affordable or fully removed.

Score reasoning by traceability, not service-name recall: identify the principal at each step, the action requested, the resource/role affected, the applicable boundary, and the observation still needed. Do not award “least privilege achieved” from the synthetic tests, a missing finding, the diagram or an AI answer. Independent learners have not attempted this packet.
