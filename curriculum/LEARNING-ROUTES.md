# Learning routes and prerequisite checks

Begin with the smallest task you can explain and verify. The routes below help you choose an entry point, then connect each skill to a customer or operator problem.

## Start with one visible result

Before the long foundation chapters, try [the local note-boundary exercise](../reader/FIRST-SUCCESS.md). Predict whether an empty list protects a private note, run one Python command, then inspect the direct request. It needs no AWS account. If terminal commands are new, begin with the cost exercise below. Keep your first explanation: later chapters will supply real sign-in, durable storage and AWS authorization for the boundaries this small fixture leaves open.

Use [cumulative retrieval practice](RETRIEVAL-PRACTICE.md) alongside the stage checkpoints. At your next session, explain the previous idea without notes. At a stage boundary, solve a mixed case before opening its separate feedback. Return after a longer gap with a changed requirement; there is no chapter-per-day target.

For SAA-C03 preparation, follow the [self-paced certification route](saa-c03/README.md) alongside these foundations. You may start at Chapter 1 and read in order. The diagnostic is optional before reading; whenever you attempt it, save your answers before consulting its key and record what you have already studied. Other certification routes remain optional extensions.

## Before using AWS

Use [the first cost exercise](../docs/FIRST-LOCAL-EXERCISE.md) to predict a result, run Python and inspect its exit status. Learn to locate/edit files and distinguish absolute from relative paths. Check Python, Git and Node versions as the exercises require them. Practice commits, diffs and restoring an uncommitted change in a disposable repository.

Next, use [the guided data-contract exercise](../examples/data-contract/README.md#start-with-one-update) to explain zero, omission, null and empty values. Attempt its two-editor extension after the first distinction is clear. Local validation is not a stored cloud record.

Before deployment, identify the account, Region, scoped identity, permitted actions, whole-run estimate, spending limit and cleanup owner. Read the cost and identity lessons. App, AWS and GitHub sign-ins have different jobs. Keep credentials out of learning records.

## Find your route through the book

Begin with the [seven-question map](../reader/BOOK-LOCATORS.md#book-d491e5c73a6f8cc6), then cost, identity, network and compute foundations. Transfer the map to the clinic in [E30](EXERCISES.md#e30). Chapter 6 connects those boundaries to the first Amplify app. Read ownership and environment separation before deployment changes and data protection before extending private-data use.

Continue in contents order through data, operations, durable workflows and shared platforms. If you jump ahead, return to the identity, cost or recovery foundation that your decision needs. The stages mark changes in the job, not isolated courses.

Use the longer chapters' core routes before their extensions. Delivery has a [four-pass sequence](../reader/BOOK-LOCATORS.md#book-fac09bc05d613a74) and [integrated release review](../examples/release-review/README.md). Events has a [four-stage sequence](../reader/BOOK-LOCATORS.md#book-012fc3bf0676058e) and [integrated report review](../examples/report-review/README.md). Choose the relevant platform branch; studying a deployment does not authorize running it.

The [certification-to-application routes](CERTIFICATION-TO-APPLICATION.md) connect optional CloudOps and professional extensions to practice. The SAA route remains the primary certification path.

## Routes

| Route | Entry | Suggested chapters in this book | Exit evidence |
| --- | --- | --- | --- |
| Beginner | Local file, Git and JSON checks | 1–9 | Trace one request, deny another user's access, explain the estimate, reproduce and clean up a small authorized lab |
| Operator | Beginner outcomes, basic scripting | 14–20, 25, 33 | Diagnose an unfamiliar failure, restore validated data and deliver an incident report |
| Architect | Beginner outcomes and basic operations | 11–13, 21–24, 26–32, 34 | Compare two feasible designs against measured requirements, then defend a changed design |
| Certification review | Corresponding practical route | 34, then revisit the chapters where your evidence is weakest | Explain original scenario answers and demonstrate the practical objectives separately |

These are learning routes, not mandatory AWS certification prerequisites. Security, cost, sustainability and AI verification recur in every route. Specialty-depth AI, networking and data engineering can branch from the core; this book does not promise complete preparation for every specialty exam.

## Check your understanding between stages

Keep Maya's repair request in view as the book grows. Each checkpoint below changes her problem. Before looking up a worked response, write what you think will happen, why, and what observation could show you are wrong. Use the [chapter outcome map](../reader/BOOK-LOCATORS.md#book-b15b8fcb83e64495) for the smaller task in each chapter and the [learning record](LEARNING-RECORD.md) to keep your first answer separate from hints and later evidence.

### After Chapters 1–5: trace the promise

A customer tries to upload a repair photo. The site loads, but a separate status lookup returns 403. What do you know about each action, and can you identify the layer that issued the 403 from those facts alone? Name one observation that could narrow the source and the permission decision still to investigate. Sketch a short lab estimate, including duration, possible idle costs, a stop rule and cleanup; mark missing prices and quantities as unknown. If these questions blur together, revisit identity, network and cost. Save your answer before consulting the [reasoning guide and changed case](STAGE-ONE-REASONING.md). This paper answer is design evidence.

### After Chapters 6–10: make the first app private and changeable

Maya adds private notes to the public website. Identify what Hosting delivers, what Auth establishes, where the note is stored, and which backend authorization rule refuses another customer's read. Name the resource owner and the cleanup action for each part you propose. Run the [loopback note-boundary exercise](../examples/amplify-walkthrough/README.md#run-the-local-note-boundary): an empty list and a denied direct read are different results. The fixture's actor header is forgeable, so it does not prove that Field Lab's deployed owner rule works. If you cannot explain who owns a resource or how a preview avoids production data, revisit infrastructure ownership and environment separation. A live claim needs two test-user sign-ins and a direct API denial at the intended backend.

### After Chapters 11–13: find the authoritative record

Two application workers can accept requests, while a fast read cache still shows an older appointment. State which store owns the confirmed booking, which read may be stale and what happens when the cache disappears. Change the case: both workers try to take the last appointment slot. Show where the one-slot decision must be made. If the answer relies on each worker's private memory or treats a cache hit as proof of a committed booking, return to compute, storage and database read paths.

### After Chapters 14–18: recover the customer path

The website is green, but accepted jobs stop completing after a release. Name a customer-visible signal, one observation that could distinguish two causes, the condition for stopping the release and the evidence needed after a restore. Include the last confirmed job and the elapsed time until an authorized customer can read its result. If you can show only a healthy process, a configured alarm or an existing backup, revisit observation, incident investigation and recovery. None alone proves the customer's work survived.

### After Chapters 19–25: keep long work truthful

Maya's service sends an acceptance receipt, loses the reply, receives a retry and later sees the same work message twice. Trace the stable request identity, saved acceptance, worker effect and customer status lookup. Add an approval and an event-derived report: which version was approved, and how will a late or repeated event change the report without double-counting the repair? If you cannot distinguish accepted, dispatched and completed, return to durable requests and the relevant workflow chapter. Use the local drills for the boundary they actually exercise.

### After Chapters 26–31: cross a new boundary deliberately

Maya acquires another shop. Its data and staff must move, its office needs a path to the application, and the chosen Region may lack service availability or quota for the proposed cutover. Draw the account, network, data and authority boundaries; name a reconciliation and a reversal condition. Choose what to check before promising the move. Organization and hybrid examples in this companion are design exercises; an account diagram is not a deployed control.

### After Chapters 32–34: defend and revise the design

Now a customer requires confirmed bookings to survive a regional failure within a stated time and data-loss limit. Compare two feasible designs against that promise, whole-run cost and operating work. State the evidence that supports your choice and one changed requirement that would reverse it. Keep your unaided first answer, Codex's critique and your source-checked revision as separate records. A strong explanation is progress; a real recovery claim still requires a tested recovery and an observed customer result.


## Check readiness chapter by chapter

Use the checkpoints and [chapter outcomes](../reader/BOOK-LOCATORS.md#book-b15b8fcb83e64495) to choose the next task. In the [learning record](LEARNING-RECORD.md), preserve your prediction, source, observations, assistance and changed-case explanation. Separate a design answer, local result and live AWS observation. Reading or a green check alone does not establish mastery.

## Three passes through a lesson

First predict a worked example. Next solve a guided change. Then attempt an unfamiliar case independently and return after a delay without notes. Use [cumulative practice](RETRIEVAL-PRACTICE.md) to connect earlier lessons. An optional tutor can ask one question at a time after your first attempt; keep assisted revision separate.

For certification, check the exact [current exam guide](https://docs.aws.amazon.com/aws-certification/latest/examguides/), map weak objectives to mechanisms and use fresh [official preparation](https://aws.amazon.com/certification/certification-prep/). The [practice route](CERTIFICATION-TO-APPLICATION.md) connects question reasoning to a separate engineering check; neither substitutes for the other. The [teaching reference map](TEACHING-REFERENCE-MAP.md) explains the learning sources.

## Glossary

| Term | Plain explanation and important limit |
| --- | --- |
| Account | An AWS resource and billing boundary; resources may still be shared or accessed across accounts |
| Region / Availability Zone | A geographic service area / an isolated location within a Region; they are different failure boundaries |
| Authentication / authorization | Establish who is acting / decide what that actor may do |
| Role / policy | An assumable identity / rules governing access; a role name alone proves no permissions |
| VPC / subnet / route | Your virtual network / an address segment / a rule for where traffic goes next |
| DNS / TLS | Resolve a name / protect and authenticate a connection; neither proves application authorization |
| Compute | Resources executing your instructions, whether functions, containers or machines |
| Transaction | A group of database operations that succeeds or fails together within the system's supported scope |
| Idempotency | Repeating an operation preserves its intended effect; retries still need stable identifiers and correct handling |
| Queue | Work held for later processing; delivery and processing completion are different events |
| IaC / state / drift | Infrastructure definitions / the tool's resource record / disagreement between expected and observed configuration |
| Metric / log / trace | A measurement over time / event details / a linked request path |
| SLI / SLO | A service measurement / a target for that measurement over a stated period |
| RTO / RPO | Recovery time target / acceptable data-loss window; objectives are not measured outcomes |
| Replica / backup | Another maintained copy / a recoverable historical copy; either needs tested recovery procedures |
| Quota / budget | A service limit / a spending plan or alert mechanism; neither is automatically an account-wide dollar cap |
| Sustainability | Meeting needs with less avoidable resource use; lower cost alone does not quantify emissions |

For an unfamiliar term, write the concrete problem it solves, its technical definition and where the analogy breaks. Add that explanation to your own glossary before moving on.

For a longer explanation, follow the [network, contract, state and cost vocabulary stories](../reader/VOCABULARY-STORIES.md). Read the story you need when a term interrupts a chapter; you need not study them all before starting.
