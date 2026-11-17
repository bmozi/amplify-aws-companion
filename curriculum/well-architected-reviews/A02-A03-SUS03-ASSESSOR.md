# Assessor: SUS 03 one-due-hold case

Read the [case](A02-A03-SUS03.md#changed-condition-exercise-the-one-due-hold) after making an independent decision. This is authored reasoning, not a scored learner result or an environmental measurement.

A strong answer preserves two different customer outcomes. A02 can durably accept work for later completion under a stated status contract. A03 must not confirm the last seat twice; eventual expiry discovery and a GSI candidate list do not replace the conditional base-record transaction. One due hold missed by a lagging index still needs a reconciliation route.

The **GSI claim** compares only returned rows. It leaves out index writes, index bytes, query pages, base reads, repeat passes and pre-index holds without `due_partition`. A query might reduce scan work at larger table sizes, but the total cannot be inferred from one returned-row count. Measure the complete path with the same hold distribution and correctness rule. If the table grows, an index becomes a stronger candidate; it still needs eventual-consistency and historical-record coverage.

The **queue claim** confuses event-driven workers with zero idle work. The checked-in Lambda/SQS mapping has a maximum-concurrency setting; the cost packet identifies quiet polling as a meter to estimate. Worker capacity and any retained queue/table/log objects remain separate. A queue may be a good way to smooth repair requests without being free or proving lower emissions.

The **browser claim** changes device and network work. Faster polling can increase requests and downloads without improving the authoritative seat decision. If the customer promise requires a faster status view, compare bounded polling, an authorized subscription or another push path against actual device/network use, server calls, authorization and stale-state behavior. None is selected or measured in this backend-only exercise.

Look for a four-part receipt: (1) correct and timely outcomes, (2) table, index, queue, Lambda, logs, network and client work included or explicitly excluded, (3) a bounded same-workload comparison with access and failure cases, and (4) an explicit statement that resource proxies are not measured electricity or carbon. A claim that one candidate is “greener” from returned-row count or worker-seconds alone does not meet the evidence standard. No independent learner has taken this case.
