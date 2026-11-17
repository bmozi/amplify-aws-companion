# Assessor: ongoing AI quality is a separate signal

The fixture's current window has two unsupported answers among four reviewed answers; one fifth answer is unreviewed. The baseline has no unsupported answers among its four reviewed answers. The script reports an investigation signal because its deliberately simple sample rule is met. It does **not** prove statistical drift, root cause or production incident severity. Current mean latency is lower than baseline in this fixture, which shows why performance metrics alone miss answer correctness. The token totals are usage observations, not a bill without current rates and other meters.

Changing a reviewed unsupported answer to `unreviewed` lowers review coverage below the fixture's stated minimum, so the script refuses to establish the comparison. This is not evidence the answer became correct. A wrong `source_version` suggests a retrieval, index, cache or citation lifecycle issue; it does not rule out a simultaneous model/prompt or business-rule change. Compare exact source versions, retrieved passages, prompt/model versions, authorization and human review before assigning cause.

For a real service, keep at least four layers separate:

1. **Runtime:** Bedrock/agent latency, tokens, errors, throttles and step traces show operational behavior under their defined metric scopes. [AWS runtime metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html), [AgentCore observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html).
2. **Evidence access:** Was the retrieved source current and permitted for the actual caller at answer time?
3. **Answer quality:** Does an independently reviewed sample preserve each condition and abstain where evidence is missing? Review coverage, sampling and delayed labels matter.
4. **Business effect:** Was a proposed tool action separately authorized, executed once, receipted and correct for the customer? A fluent answer and a successful API call are different results.

An acceptable response names a safe first action such as holding automated warranty decisions while investigating, not deleting logs or silently changing model versions. Recovery evidence includes a frozen changed-condition case set, reviewed real-world sample, current source and permission checks, stable customer signal and a monitored rollback/release. None of these outcomes was observed in AWS or with independent learners here. AWS currently states that [SageMaker Model Monitor is unavailable to new customers](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-data-quality.html); a plan must verify current eligibility rather than copying an old tutorial.
