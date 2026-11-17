# Prepare for SAA-C03 with AMPLIFY AWS

SAA-C03 is this book's primary certification target, selected by John Briggs on October 31, 2026. CloudOps and professional material remain useful extensions. You do not need a prior certification to use this route. You do need time to learn the prerequisites, explain unfamiliar decisions and practice the relevant AWS tools. Reading every page is an activity; being able to solve a new problem is the outcome.

The [official guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html), its four domain pages, service lists and revision page were downloaded directly on October 31. The [source baseline](source-baseline-2026-10-31.json) records hashes and links for 14 tasks, 82 skills and 107 knowledge items. The revision page reports version 1.1, October 29, 2026. AWS says guide updates normally precede exam changes by approximately one month; check the guide again before booking. A publication date alone does not establish the exact content of an individual's appointment.

## Start without a deadline

Start with Chapter 1 and continue in order if that suits you. No diagnostic, AWS account or exam booking is required before reading. The prerequisites in [the learning routes](../LEARNING-ROUTES.md) apply when you reach the corresponding hands-on exercise; you can first work through its paper example.

1. Read the chapter goal and follow its concrete example. Pause at a section boundary when you cannot explain the decision in your own words. Note the unfamiliar term or missing step and return to the glossary or earlier lesson.
2. Attempt the chapter's practice before its worked explanation. Keep your first reasoning and any help you used. A reading session can end after one useful section; there is no chapter-per-day target.
3. Use [the 28 diagnostic questions](DIAGNOSTIC.md) when useful. Taking them before study gives an optional baseline; taking them after reading gives a first post-study assessment. Record which chapters you have read so we do not confuse those two observations. In either case, save answers before opening the key and work without the book or AI during the attempt.
4. Use the task routes below to revisit weak areas. After time away, attempt [the changed cases](TRANSFER.md) before their assessor. Explain why a credible alternative fails the supplied requirements.
5. Use fresh AWS official exam-preparation questions and a current official practice exam when you can explain all four domains. Record the material, date, version, prior exposure and feedback. Do not copy protected questions into this repository. Review weak objectives and seek a new unseen assessment; repeating a familiar test measures a different skill.
6. Choose an exam date when the evidence supports attempting it. There is no imposed calendar or book-defined score equivalent to AWS's passing score.

The actual exam uses multiple-choice and multiple-response questions. Read the requested number of selections. Answer against the stated requirements, distinguish a necessary condition from a sufficient solution, and reserve time to revisit uncertainty. AWS reports a scaled score; a percentage correct on these original questions cannot be converted to that score. Review current duration, delivery, identification and accommodation requirements in [AWS certification preparation](https://aws.amazon.com/certification/certification-prep/) and the booking process before purchasing an appointment.

## Read by the decision you must make

The weights are AWS's domain weights, not proportions of this book and not task-level weights. Each row is a starting route; [the task work cards](TASK-CARDS.md) supplies every skill and knowledge item's specific lesson, assessment and remaining work. All inherited objective statuses remain partial.

| Task | Learn and practice | Explain before moving on |
| --- | --- | --- |
| 1.1 — Access | Chapters 3 and 28; identity and account-governance exercises | Trace a caller, role, resource and applicable limits; distinguish workforce federation from application login. |
| 1.2 — Workload protection | Chapters 4, 6 and 10; network diagnosis and security cases | Separate a route, network filter, sign-in, record authorization and attack control. |
| 1.3 — Data controls | Chapters 9, 17 and 21; protection and restore exercises | Explain encryption, key access, TLS, retention, replication and recoverable history separately. |
| 2.1 — Decoupling | Chapters 5, 19, 20, 23 and 26; durable requests and reservation labs | Choose queues, fanout or orchestration; show retries, state ownership and independent scaling. |
| 2.2 — Availability | Chapters 14–18 and 30; recovery and fault drills | Compare AZ and Region failure, RTO/RPO, standby dependencies and a customer-level recovery observation. |
| 3.1 — Storage performance | Chapter 11; storage access exercises | Choose object, shared file or block interfaces and the exact workload and failure boundary. |
| 3.2 — Compute performance | Chapters 5 and 26; scaling exercises | Match runtime, resource pressure, queue depth and startup time; identify the downstream limit. |
| 3.3 — Database performance | Chapters 12–13; database-selection and read-path exercises | Distinguish replica, standby, cache and proxy; preserve engine compatibility and correctness. |
| 3.4 — Network performance | Chapters 4, 29 and 30; network-path exercises | Choose routing, load balancing and hybrid connections from protocol, capacity and availability. |
| 3.5 — Ingestion | Chapters 24–25; ingestion and reporting exercises | Separate acquisition, buffering, transformation, catalog, authorization and presentation. |
| 4.1 — Storage cost | Chapters 2, 11 and 17; lifecycle and retention exercises | Compare storage, requests, retrieval, minimum duration, transfers and restore needs. |
| 4.2 — Compute cost | Chapters 2 and 5; whole-path cost and purchasing exercises | Fit a commitment to a stable baseline and an interruptible option to recoverable work. |
| 4.3 — Database cost | Chapters 2, 12–13 and 27; capacity and migration exercises | Include connections, replicas, backups, licensing, migration and operating effort. |
| 4.4 — Network cost | Chapters 2, 4 and 29; route-cost exercises | Price the actual bytes and hops while retaining required failure isolation and access. |

Security is 30%, resilience 26%, performance 24% and cost 20% of scored content. Use these proportions to allocate mixed revision time, while giving a weak foundational task extra practice regardless of its domain. Do not infer that the diagnostic's equally represented tasks reproduce those weights.

## What a useful personal readiness review contains

For each task, retain an unaided explanation, a new selection question and a changed-requirement answer. Name the failed requirement in each rejected alternative. For practical exercises, distinguish a paper design, local fixture and AWS observation. An AWS deployment is not necessary to prove that a written distinction is taught, but a local fixture cannot establish a claimed service behavior.

An internal readiness discussion can proceed when every task has been studied, no unexplained critical security or recovery misconception remains, multiple fresh mixed assessments show consistent reasoning, and current official practice feedback supports attempting the exam. These are study criteria, not a statistically validated pass rule. Keep assistance and prior exposure visible.

The book's recommendation gates are maintained in [the acceptance record](ACCEPTANCE.md). Its source mapping and locally passing tools establish less than independent technical review, learner effectiveness or an exam result. Until those gates have evidence, recommend this material as a practical study companion with declared limitations, not as a sole-source promise of passing.

## John's author-learner case study

John has reported zero AWS certification experience and no target exam date. He has existing AWS project experience and has participated in developing this book; neither should be erased from the baseline. Use [the private study record](../../reader/OWNER-RECORD-BOUNDARY.md) to preserve dates, source versions, unaided answers, other resources, assistance and eventual exam outcome. Do not read the assessor files before submitting first attempts.

An eventual pass would support the statement that John used the book as part of his preparation and passed the named exam on the recorded date. It would not isolate the book's causal effect or validate a general pass rate. Separate independent learners and an AWS-qualified technical reviewer would strengthen the broader publication claim. Do not collect or publish recalled real exam questions.

## Practice without the internal review criteria

The task cards use the current evidence mappings. Their [skill practice prompts](practice/README.md) are separate from the internal reviewer criteria. Save your first answer before opening assessor material. The 28-question diagnostic samples tasks; it does not assess all 189 objectives.
