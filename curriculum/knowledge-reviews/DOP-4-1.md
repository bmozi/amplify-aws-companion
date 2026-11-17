# Individual knowledge review for DOP-C02 task 4.1

Internal editorial review, October 18, 2026. The [current official Domain 4 task page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain4.html) lists five knowledge areas for collecting, aggregating and storing logs and metrics. The mappings below are partial. AWS documentation was checked for the service behaviors linked in Unit 08; no AWS configuration or learner outcome was tested.

## 01 — Monitoring applications and infrastructure

Unit 08 starts with the customer promise, then asks how to trust the observation and investigate it. It distinguishes business completion from process health and relates metrics, logs and traces to different questions. The new [collection routes section](../../reader/BOOK-LOCATORS.md#book-b7d5ab8137297b14) teaches the application/host agent, log-group, metric-filter, subscription, metric-stream and Logs Insights paths. Existing customer-signal, request-telemetry and observability-handoff labs provide synthetic or loopback evidence.

**Still required:** choose an actual workload, instrument it, and independently verify complete collection, access, missing-data behavior, cost and learner transfer.

## 02 — CloudWatch metrics: namespaces, metrics, dimensions and resolution

Unit 08's metric-label and time-window sections explain identity, cardinality, supported resolution, period/statistic and why a graph cannot reconstruct missing measurements. The telemetry-design lab calculates fictional dimensions and exercises fixed-cadence missing and late readings. Its arithmetic is not CloudWatch metric storage, billing or alarm behavior.

**Still required:** verify selected metric type, namespace, dimension sets, resolution, query/retention behavior and current pricing in an authorized AWS environment.

## 03 — Real-time log ingestion

The new lesson maps structured application events and CloudWatch-agent log files into CloudWatch Logs, then distinguishes queries, metric filters and subscription delivery. The request-telemetry lab exercises allowlisted synthetic events and a loopback failure/alert path.

**Still required:** test delivery, latency, retry, duplication, backpressure and completeness with the selected log producer and AWS destination. Loopback listeners do not test CloudWatch ingestion.

## 04 — At-rest and in-transit encryption

Unit 08 explains CloudWatch Logs default encryption, optional customer-managed KMS control, transport encryption, reader/key policy and how a disabled key blocks retrieval of data encrypted with it. It separately asks learners to consider the encryption and lifecycle of any S3 export.

**Still required:** inspect actual log group, transport, KMS key, policy, grants, rotation/disablement behavior and exported-object encryption in the selected Region. No key or data was created.

## 05 — IAM roles and permissions for log collection

The lesson distinguishes the collector's write authority from the investigator's read authority and the deletion owner's authority. It uses an EC2 instance role for CloudWatch-agent publication and requires review of service/delivery roles and destination permissions. The eight design cases change those boundaries independently.

**Still required:** implement and test allowed/denied actions for the chosen agent, log group, KMS key and destination. No IAM permission was changed.

## Limits

All five individual knowledge mappings are partial. The local exercises validate only their stated synthetic or loopback logic. They do not establish CloudWatch installation, metric-filter/stream/subscription behavior, KMS, IAM enforcement, current bill or certification readiness. Organization-wide log centralization remains design-only.
