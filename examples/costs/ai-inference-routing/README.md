# The cheaper AI route can break the data promise

Maya's repair shop wants an AI assistant to summarize service notes. The notes may be processed in two approved US Regions. A teammate finds a lower token rate for a global inference profile and calls it the obvious saving. First ask **where a request may be processed**. A cheaper route is not useful if it breaks the data-location rule.

This offline lab supports [SAP-C03 skills 3.1.4 and 3.2.5](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain3.html) and extends the [inference-path lesson](../../../reader/BOOK-LOCATORS.md#book-48cc78d9103148e5). The JSON uses **invented rates, token counts and destination lists**. It is not a current Bedrock quote, account estimate, model benchmark or live request. In particular, a real global profile can include more destinations than the three in this teaching fixture.

## Four meters and one boundary

```text
approved processing Regions
       |                  standard input tokens ─┐
       v                  cache-read tokens ────┼─> fictional token subtotal
candidate profile          cache-write tokens ──┤
       |                  output tokens ─────────┘
       v
possible destination Regions -> reject if any destination is unapproved
```

The *source Region* is where the application calls Bedrock. An inference profile can route processing to a *destination Region*. A geographic profile confines routing to its defined geography; a global profile may reach supported commercial Regions beyond that geography. AWS says cross-Region inference has no extra routing charge and prices the request from the source Region. Global profiles can have lower model token rates, but the actual model, Region and date matter. [AWS cross-Region guidance](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html), [global profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/global-cross-region-inference.html), [model/Region options](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html).

Prompt caching can reduce repeated input processing for supported models, but it is not an automatic bill reduction. AWS reports cache-read and cache-write tokens separately; cache writes may carry a higher rate, and an eligible request need not hit the cache. Cross-Region routing can increase cache writes during demand shifts. [AWS prompt-caching guidance](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html).

## Predict, run, change one fact

Before running the program, predict whether the lowest token subtotal is location-eligible. Then, from the repository root:

```sh
python3 examples/costs/ai-inference-routing/lab.py
python3 -m unittest discover -s examples/costs/ai-inference-routing -p 'test_*.py'
```

Open `scenario.json`. Change `allowed_processing_regions` to include `eu-west-1`, and run again. Then restore it and change `cache_read_input` to `0`, moving those tokens to `standard_input`. Explain why each answer changes. Compare with the [assessor](ASSESSOR.md) only after recording your own decision.

The calculator **only** multiplies four fictional token meters by four fictional rates and checks a simplified set of possible destinations. A real proposal needs current model/profile support and prices, a complete destination list, applicable organization policies, a legal data-location interpretation, input/output quality and latency measurements, retries, quotas, guardrails, storage, logging, and any other billable components. Batch processing and SageMaker serving may be better for a different time promise. A source-Region CloudTrail event does not by itself mean inference was processed there; inspect the destination evidence. No AWS account or credits are used here.

Ask Codex to argue for the cheap global route and for the narrow geographic route. Require it to identify the fact that would change the decision and cite current AWS documentation. Check the links yourself; an AI-generated cost claim is not a price receipt or compliance approval.
