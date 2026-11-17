# Price the road you actually choose

Maya's static repair guide has a new proposal: use Amplify's **preview self-managed hosting** so the team owns the S3 bucket and CloudFront distribution. A colleague copies the managed Amplify Hosting worksheet's USD 0.75023 subtotal and calls the experiment cheap. That number describes another road. It says nothing about the new distribution's requests, bucket operations, default alarms or what remains after the demonstration.

This is a **fictional, offline planning exercise**, not a rate quote or permission to deploy. AWS's [self-managed configuration guide](https://docs.amplify.aws/react/deploy-and-host/self-hosting/define-hosting/) documents the S3/CloudFront resources, selectable WAF/domain/logging/compute/storage behavior, alarms enabled by default, and an SNS topic when no topic ARN is supplied. The [getting-started guide](https://docs.amplify.aws/react/deploy-and-host/self-hosting/getting-started/) describes a no-scope `ampx deploy` that can deploy both backend and frontend. Exact generated resources depend on the package version and chosen configuration; inspect a synthesized plan before a real estimate. The feature remains preview and AWS does not recommend it for production yet.

First predict whether the included static scenario passes *fictional* USD 5 and USD 100 guardrails. Then run from the repository root:

```sh
python3 examples/costs/self-managed-hosting/assess.py examples/costs/self-managed-hosting/plan.json
python3 -m unittest discover -s examples/costs/self-managed-hosting -p 'test_*.py' -v
```

The plan uses invented prices and quantities. Each selected meter must have a quantity, rate and explanation; each unselected meter needs a reason. The monitoring flag is **true** because that is the documented default, so alarms and SNS must be estimated. The build runs on a local laptop with zero AWS build charge; external CI needs a separate billing review. The hypothetical 30-day AWS run has a USD 1.74 base, USD 0.50 contingency and USD 2.24 total. An invented USD 105 credit balance would leave USD 102.76. Passing this arithmetic **never changes the result to live-approved**: the balance is invented, rates are invented, and account identity, actual generated resources, service eligibility, active runs, bounded cleanup and scoped identity remain unverified.

Now change one condition at a time, write your prediction, run the checker and compare with the [assessor](ASSESSOR.md):

1. Remove `cloudwatch_alarms` while monitoring remains enabled. Why does a small idle meter matter even before traffic?
2. Turn on `waf` but leave its row `not_applicable`. What new configuration and request counts must be inspected?
3. Add a row called `amplify_hosting_subtotal` with USD 0.75023. Why is this a category error?
4. Increase the fictional contingency to USD 4. What does the whole-run ceiling do? Then lower the fictional balance to USD 101 and restore the contingency. What does the reserve do?
5. Select SSR or a managed pipeline. Which new meters and permission/trigger surfaces enter the inventory? Would setting this repository's manual publisher flag to `false` stop a separate pipeline?
6. Suppose `retainOnDelete` is selected for the build bucket or CloudFront access logging is enabled. How will you discover the exact retained bytes, requests, ownership and deletion deadline? A green stack delete or stopped pipeline is not a final billing receipt.

Ask Codex to challenge the **first omitted meter**, the **first AWS write**, and the **first retained resource** in your proposal. Compare its answer with the official selected-version construct and service pricing pages before any account decision. Use the [credit commitment lesson](../credit-commitments/README.md) to see why two individually passing fictional plans can still spend the same headroom twice. GitHub Actions, if used, has a separate billing owner. Before a live lab, choose your own whole-run limit and reserve, coordinate concurrent work, and plan cleanup; organization-dependent cases here remain design-only.
