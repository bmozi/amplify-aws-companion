"""Three synthetic publisher receipts for the learner; no account access."""
from copy import deepcopy
import json

from review import INLINE, ROLE, review


ACCOUNT = "123456789012"
SUBJECT = "repo:harbor@10/learning@20:ref:refs/heads/main"
BRANCH = f"arn:aws:amplify:us-east-2:{ACCOUNT}:apps/dexample123/branches/lab"
PROVIDER = f"arn:aws:iam::{ACCOUNT}:oidc-provider/token.actions.githubusercontent.com"
POLICY = {"Version": "2012-10-17", "Statement": [
    {"Sid": "CreateAndStartDeploymentForOneBranch", "Effect": "Allow",
     "Action": ["amplify:CreateDeployment", "amplify:StartDeployment"], "Resource": BRANCH},
    {"Sid": "ReadJobsForOneBranch", "Effect": "Allow", "Action": "amplify:GetJob",
     "Resource": BRANCH + "/jobs/*"},
    {"Sid": "ReadCurrentFreePlanForPublicationGate", "Effect": "Allow",
     "Action": "freetier:GetAccountPlanState", "Resource": "*"}]}
TRUST = {"Version": "2012-10-17", "Statement": [{
    "Effect": "Allow", "Action": "sts:AssumeRoleWithWebIdentity",
    "Principal": {"Federated": PROVIDER},
    "Condition": {"StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": SUBJECT}}}]}


def cases():
    base = {"expected_account_id": ACCOUNT, "checks": {
        "identity": {"account_id": ACCOUNT},
        "github_provider": {"exists": True, "arn": PROVIDER},
        "github_provider_detail": {"url": "token.actions.githubusercontent.com",
                                   "client_ids": ["sts.amazonaws.com"]},
        "publisher_role": {"arn": f"arn:aws:iam::{ACCOUNT}:role/{ROLE}",
                           "max_session_duration": 3600,
                           "permissions_boundary": None, "trust_document": TRUST},
        "publisher_inline_names": [INLINE], "publisher_inline_" + INLINE: POLICY,
        "publisher_attached_names": []}}
    extra = deepcopy(base)
    extra["checks"]["publisher_attached_names"] = [{"PolicyName": "ExtraAccess",
        "PolicyArn": f"arn:aws:iam::{ACCOUNT}:policy/ExtraAccess"}]
    unreadable = deepcopy(base)
    unreadable["checks"]["publisher_attached_names"] = {"error": "access_denied"}
    return {"declared_documents": base, "extra_attached_policy": extra,
            "unreadable_attachment_list": unreadable}


if __name__ == "__main__":
    for name, receipt in cases().items():
        print(name, json.dumps(review(receipt, POLICY, account_id=ACCOUNT, subject=SUBJECT), sort_keys=True))
