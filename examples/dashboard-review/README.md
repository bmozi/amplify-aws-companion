# Choose and challenge a dashboard

Read unit 30. These original cases are design-only and require no AWS resources. Answer before opening [the assessor notes](ASSESSOR.md). For each answer name a candidate, a rejected alternative, the relevant business requirement and the evidence that could change your decision.

1. An analyst investigates one anomalous week of S3 records. Three managers later request the same filtered report every morning. Explain why the first task may use Athena directly and the second may justify a maintained analytics dashboard. Locate the catalog, query and presentation responsibilities.
2. A customer needs the present shipping status of one order. A proposed dashboard imports data nightly. Identify the mismatch and a suitable application access path; include authorization for that order.
3. The source dataset completes at 08:10, the last successful import was 08:00, and the dashboard opens at 09:00. Can its opening time prove freshness? Compare imported and direct-query modes, including a failed upstream ingestion.
4. A has 9 on-time deliveries out of 10; B has 1 out of 100. Compute the mean shop percentage and the fraction of all orders. Choose the answer for an order-level target, then handle a period with no qualifying orders. State one business rule needed for canceled orders.
5. A reader sees only shop A after selecting a filter. The author tested access as a dataset owner. Explain why neither observation proves reader isolation. Design positive and negative cases, including an unrestricted rule and access to underlying files.
6. The team wants to publish an interactive report for two annual review meetings. Compare a static reviewed report with managed analytics. Name costs, refresh responsibilities and access consequences without inventing prices. Changing the audience to daily self-service users should trigger another comparison.

Transfer: Maya now operates shops in two time zones and late events can revise yesterday's results. Write the reporting-window and revision questions before choosing a visualization. Ask Codex to critique your assumptions, then mark every unsupported service or measurement claim as a question to verify.

For a runnable follow-up, complete [the dashboard grain drill](../dashboard-grain/README.md). It checks SQL joins and missing-outcome denominators locally; it does not turn these service-selection cases into cloud verification.
