# Fast answers can be newly wrong

Maya's repair assistant answers warranty questions. Its response time looks normal and its token use is stable. A new policy bulletin has entered the source library, however, and a reviewer finds two answers that omit an important condition. An operations chart can be green while the assistant is becoming less useful. The first step is to keep **service health** and **answer quality** as separate signals.

This offline exercise supports [SAP-C03 skill 5.3.5](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain5.html). It extends the [authorized-retrieval lesson](../../reader/BOOK-LOCATORS.md#book-c7716c08655f741e) and [A20 answer-evaluation lab](../agent-evaluation/README.md). The five current and four baseline observations are invented; no model or AWS account is called. The small sample is for learning a measurement boundary, not statistical proof of drift.

```text
customer question -> model/API metrics: latency, errors, tokens
                 -> agent trace: tool step, decision, timeout
                 -> reviewed answer + source version + business rule
                 -> investigation signal -> owner verifies cause and safe response
```

AWS provides [Bedrock runtime metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html) for invocation volume, latency, tokens and errors. [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) offers agent sessions, steps, latency, tokens and error signals when configured for the selected application. Neither metric stream alone says that an answer preserves the source's qualifiers. A separate, authorized evaluation must compare responses with current permitted evidence and the business rule. Model invocation content logging can expose sensitive prompts/outputs and add retention cost; choose its scope, access, redaction and deletion deliberately.

AWS's [SageMaker Model Monitor data-quality page](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-data-quality.html) currently says Model Monitor is closed to new customers. Do not write a new-customer deployment plan that assumes enrollment is available; verify the current service path and choose supported measurements for the actual model. This exercise uses a generic evidence join, not Model Monitor.

## Run the bounded join

Predict whether latency alone raises a concern. Then, from the repository root:

```sh
python3 examples/ai-operation-signals/lab.py
python3 -m unittest discover -s examples/ai-operation-signals -p 'test_*.py'
```

The script counts reviewed responses and unsupported answers, shows mean latency, token totals and source versions, and emits a **quality investigation signal** when a small fixture rule is met. It does not infer the cause. In `observations.json`, change one `unsupported` current review to `unreviewed` and rerun; then restore it. Missing review is **unknown**, not a passing answer. Next change one `source_version` back to `policy-v1`. What does that suggest, and what record would distinguish a retrieval/index error from a model regression?

## Decide before the assessor

Write a one-page response with: the affected customer promise; numerator, denominator and review coverage; service-level latency/error/token signal; the source-version and evaluation evidence; at least two competing causes; one safe read-only check for each; a bounded action owner; and what would prove recovery. Include one case where an agent tool call is authorized but produces the wrong business effect, and one where the tool gate denies an unauthorized proposal. Do not use an average response time as a substitute for a tail-latency SLO or a tiny reviewed sample as population quality.

Ask Codex to challenge the denominator, identify a green chart that could hide wrong answers, and propose a test that separates changed source data, retrieval mismatch, prompt/model behavior and policy regression. Verify its AWS claims against the primary documentation above. Compare with the [assessor notes](ASSESSOR.md). A real program needs representative consented/approved data, privacy controls, labeling protocol, thresholds based on business impact, drift detection appropriate to the model, cost limits and independent human review.
