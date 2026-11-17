# Review a network workload from evidence

## Why this exercise exists

A monthly bill went up and users report that the application feels slower. You have a route table, a small sample of VPC Flow Log-like records, NAT gateway metric totals, and billing line items. Decide what the evidence supports before proposing a network change.

All data below is fictional. The CSV is a **teaching normalization**, not an AWS-exported file: `source_group` is an analyst-added label, and the rows are synthetic flow observations. The exercise creates no AWS resources, reads no credentials, and uses no AWS price.

## Try it

From the repository root, run:

```sh
python3 examples/network-workload-review/lab.py
```

Inspect [`evidence.csv`](evidence.csv). The lab aggregates bytes only from `OK` rows by the analyst-added source group and action, counts non-`OK` statuses, and prints the separate NAT and billing observations. The `SKIPDATA` row has no byte measurement; its missing interval is an unknown, not zero traffic. The script intentionally does not join the datasets or declare a root cause.

Before opening the [assessor guide](ASSESSOR.md), write down:

1. One fact directly supported by each evidence source.
2. Two plausible explanations for the slower requests.
3. One observation that could disprove each explanation.
4. The route, service and business promise you would verify before changing anything.
5. A safe test, success measures and rollback condition.

Now change two facts **before** reading the assessor. First, an independent destination inventory identifies `external-updates` as a public software vendor rather than S3. Revisit any S3 gateway-endpoint proposal. Second, imagine the vendor label was wrong and a verified same-Region S3 destination is responsible for some traffic, with the workload's current attached route pointing to NAT. State what additional eligibility, permission, timing and byte evidence would justify a **bounded** endpoint canary, and why the entire 900 GiB billing row still cannot be called savings. Keep both first answers in your learning record.

## Synthetic evidence packet

- The workload uses two Availability Zones. One app group has higher observed flow bytes to an analyst-labeled `external-updates` destination.
- NAT metrics show 920 GiB processed from source during the sample month. This metric does not identify the application responsible for each byte.
- Billing has 900 GiB of NAT processed data and a separate regional-transfer line. These are fictional monthly aggregates, not packet-level joins.
- p95 latency rose from 180 ms to 410 ms for one operation; retries also rose. The source of delay is not yet known.
- The Flow Logs sample includes a `SKIPDATA` status. Treat the sample as incomplete evidence.

AWS defines `SKIPDATA` as records skipped during an aggregation interval. A real export has its own fields and missing-value conventions; this CSV is a simplified lesson fixture. The [AWS record-field guide](https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html) explains the status, while the [NAT metric guide](https://docs.aws.amazon.com/vpc/latest/userguide/metrics-dimensions-nat-gateway.html) defines `BytesInFromSource` as bytes the gateway received from VPC clients. Neither source maps the fictional monthly bill to this sample's `app-a` or `app-b` label.

The intended result is a review plan, not a winning answer such as “add an endpoint.” A valid design keeps the multi-AZ requirement, determines whether the external destination is an AWS service or public update host, checks the actual route and application timing, and measures a bounded change against the same user-visible promise.

