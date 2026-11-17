# From an exam objective to a working decision

Maya can recognize the words *backup* and *replica* on a practice question. Then her repair shop loses a confirmed booking, and she does not know which copy to trust. She needs two kinds of practice: choosing under the facts supplied by an exam question, and finding enough evidence to make a safe decision for a real customer.

Start with the [current AWS exam guide](https://docs.aws.amazon.com/aws-certification/latest/examguides/) for the **exact exam code** you intend to take. It describes the target candidate, content outline and services in scope. It is a map of what may be assessed, not a claim that this book covers every task. Use the [current-chapter task entry points](CURRENT-CERTIFICATION-TASK-ENTRYPOINTS.md) to find a lesson for a selected objective; the older task ledger uses planning-row numbers that do not match today's book chapters. The [book's learning routes](LEARNING-ROUTES.md) help you choose a wider path; the [teaching reference map](TEACHING-REFERENCE-MAP.md) records why this practice sequence uses worked cases, recall and later revisits.

## One target, two receipts

Choose one official task statement. Write its code and source date in your [learning record](LEARNING-RECORD.md), then use the same customer promise in two passes.

| Pass | What you do | What the result can show |
| --- | --- | --- |
| **Exam reasoning** | Read an original scenario without its answer. Underline the requested decision and hard limits. Choose, explain why the other choices fail *under these facts*, and name one fact that would change your answer. | Your reasoning on this case, including an uncertain guess or a mistaken service rule. It cannot predict an exam score. |
| **Application** | Draw the actor, request, data and failure paths. Predict a specific result, try a local or cost-bounded exercise, inspect both success and denial or failure, then reconcile what happened. | The behavior actually observed in that environment. A local model cannot prove an AWS service or customer workload behaved the same way. |

For Maya's lost booking, an exam-style case might **stipulate** that a recovery copy contains all confirmed bookings and that one candidate misses the recovery-time limit. The answer follows from those facts. In a workload review, Maya must establish whether the copy really contains those bookings, whether authorized customers can find them after cutover, and when useful service returns. Read [Chapter 34's worked choice](../reader/BOOK-LOCATORS.md#book-74db35d4dcb1af8a) and [official-task work card](../reader/BOOK-LOCATORS.md#book-a51a3c698f1c515a), then change the time limit before looking back at its rationale. For application practice, use the [local selective-recovery exercise](../examples/integrated-restore/README.md) only for the rows it can verify; keep a real AWS restore and customer check as separate work.

## When an answer goes wrong

Do not write “study recovery.” Write the smallest repairable reason: missed a hard time limit, assumed a copy was current, used the wrong unit, mistook a green endpoint for a recovered booking, or misunderstood the AWS service. Return to the relevant chapter and primary documentation for that reason. Answer a *different* case before opening its rationale. Later, revisit the same idea without looking. There is no universal delay that this book has validated for AWS learners; put a revisit on your own calendar and record whether you could explain it unaided.

Use [AWS's official practice-question and exam-preparation resources](https://aws.amazon.com/certification/certification-prep/) to learn the question style and locate weak domains. AWS distinguishes free question sets and courses from subscription material. A practice score is one diagnostic for that exam format. [Skill Builder and Ramp-Up Guides](https://aws.amazon.com/training/ramp-up-guides/) offer role-based explanations and guided practice when you need another route. Check a lab's current terms before using it. The [AWS Architecture Center](https://aws.amazon.com/architecture/) and [Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) help you challenge a design against more than the one answer choice that won a question.

## One DevOps Engineer – Professional practice branch

These tasks come from [AWS Certified DevOps Engineer – Professional, DOP-C02](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02.html). It is a different exam from CloudOps Engineer – Associate. The following route is partial practice, not comprehensive exam preparation.

For DOP-C02 task 4.1, read Chapter 14's [collection and protection lesson](../reader/BOOK-LOCATORS.md#book-b7d5ab8137297b14), complete the [eight-route design assessment](../examples/telemetry-design/README.md#dop-c02-task-41-collection-and-retention-design-route), and run the [synthetic missing-measurement](../examples/telemetry-design/README.md#run-the-missing-measurement-experiment) and [request-logging](../examples/request-telemetry/README.md) labs. This is partial explanation and local evidence only; it does not test CloudWatch collection, IAM/KMS enforcement, billing or learner transfer.

For DOP-C02 task 4.2, read Chapter 14's [signal analysis section](../reader/BOOK-LOCATORS.md#book-8f3b72d67789ceed), complete the [five-lens triage packet](../examples/operational-evidence-triage/README.md), then run its [small evidence-join lab](../examples/operational-evidence-triage/README.md#run-a-small-evidence-join) before opening the assessor. This is fictional cross-source reasoning and local set/time logic only; it does not test AWS alarms, traces, Kinesis, CloudTrail, Config, Inspector, log queries or billing.

For DOP-C02 task 3.3, read Chapter 17's [automated recovery section](../reader/BOOK-LOCATORS.md#book-abefc2395036f527), run the [local recovery gate model](../examples/recovery-automation/README.md), then attempt the [regional recovery tabletop](../examples/regional-recovery/README.md) before its assessor notes. This is partial design and local-logic evidence only; it does not test AWS Backup, Systems Manager, a load balancer or real failover.

## One CloudOps Engineer – Associate practice branch

For [SOA-C03 Task 1.2, Skill 1.2.3](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain1.html), AWS includes creating or running Systems Manager Automation runbooks. Start with the [alarm diagnostic runbook lesson](../examples/alarm-diagnostic-runbook/README.md). Before viewing its answer, identify the alarm and target, the read permission the runbook would need, and what evidence would distinguish a valid document from an actual successful execution. Compare a custom diagnostic runbook with a suitable predefined one, then name an unauthorized or wrong-target case. The included document and local checks are partial source and design evidence: they do not run Systems Manager, validate live role permissions or show remediation. Check the current guide for the exact exam version and use the [SOA-C03 task entry points](CURRENT-CERTIFICATION-TASK-ENTRYPOINTS.md) to choose other gaps.

For Developer – Associate, use the separate [DVA-C03 starting route](DVA-C03-STARTING-ROUTE.md). It is a four-domain introduction, not a completed developer exam mapping.

## Keep the account boundary visible

A paper case and a local exercise need no AWS spend. Before a live exercise, name the account, Region, scoped identity, selected services, price assumptions, expected run length, stop rule, cleanup owner and later billing check. Choose a limit and credit reserve appropriate to **your** account; the author's personal trial amounts are not a reader default. A budget alert is useful evidence, not a hard spending cap. Organization-dependent examples in this companion remain design exercises unless the reader has an authorized organization environment.

Ask Codex to **withhold the answer** until you have written your first choice and reason. Let it challenge one assumption, then verify service-specific claims in current AWS documentation. Keep the first attempt, AI help, revised reasoning, observed lab result and changed-case answer in separate fields. If the assistant gives the answer early, use a new unseen case to judge your independent reasoning.

You are ready to advance a topic when you can explain the choice in plain language, reverse it when a relevant fact changes, and name what a real implementation would still need to prove. That is a useful learning checkpoint, not a certification or professional-competence guarantee.
