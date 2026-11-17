# SEC 03 lab: the badge recipe and the badge in the drawer

Maya writes a recipe for a GitHub publisher badge. The recipe trusts one repository branch and permits three narrow actions for one Amplify branch, plus a read-only Free-plan check. A recipe on disk is not the badge AWS actually issued. Before publishing, she needs a **read-only receipt** from the account: which role exists, who may assume it, every policy attached to it, and what could limit it.

Run `python3 examples/publisher-role-evidence/lab.py` from the repository root. It uses three entirely **synthetic** receipts and makes no AWS call. Predict each result first:

1. The role documents match the declared recipe. What does that prove, and what still needs a live test?
2. An additional managed policy is attached. The original inline policy did not change. May Maya still claim the role has only the original three grants?
3. The account reader is denied permission to list attached policies. Does that mean there are none?

Then change the trust `sub` to another repository or change the publication resource to `*`; run `python3 -m unittest discover -s examples/publisher-role-evidence -p 'test_*.py' -v`. The tests check that those changes demand review. This is deliberately a **document alignment screen**, not an IAM evaluator: it does not calculate resource-policy grants, session/organization controls, effective service authorization or whether a GitHub job can publish. A matching receipt still needs review of its observation time, current repository settings, appropriate allowed and harmless forbidden operations, and the served website. Read the [assessor](ASSESSOR.md) only after writing your decisions.

```text
Declared badge recipe         Read-only account receipt
  trust + one policy     →     trust + inline + attached + boundary
             \                       /
              compare exact documents
                       │
           match, difference, or unknown
                       │
       review live authority and customer result
```

For a **future authorized** account review, the [publisher preflight](../../scripts/publisher-account-preflight.py) writes a private, owner-only receipt. `review.py` accepts that receipt, the declared policy file, account ID and independently verified GitHub subject. It prints only a compact alignment result, not policy contents. Treat any difference, missing read, older receipt, unexpected boundary or attachment as review-required. Even a `matched` result is **not** permission to turn on publishing. Check the account's plan, credits, current regional prices, whole-run estimate, chosen spending limit and reserve, role session, target and stop plan separately. This exercise installs no organization-dependent IAM feature.

Ask Codex to act as a reviewer: “Which document did I inspect, which actual role/session remains unproven, and what harmless test would distinguish a missing grant from a missing resource?” Keep a record of its critique and verify policy claims against [AWS's SEC 03 guidance](https://docs.aws.amazon.com/wellarchitected/latest/framework/sec-03.html) and [IAM evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html). Do not paste tokens, credentials, or the private receipt into a public AI service.
