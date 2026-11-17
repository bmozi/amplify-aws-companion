# Review, maintenance and learner trials

## Research baseline

The task ledger links to official certification domain pages and records the date examined. The [Well-Architected ledger](well-architected.csv) maps 57 questions across the six pillars to original exercise extensions. It is a question inventory, not a completed best-practice audit of a deployed workload. Some questions concern organizational behavior that a personal lab cannot establish.

Use the [official question appendix](https://docs.aws.amazon.com/wellarchitected/latest/framework/appendix.html) for detailed practices. Select applicable workload lenses when implementing serverless, SaaS or AI examples; record why a lens applies. A selected lens is an additional review, not evidence that the workload meets it.

Before freezing a chapter, check its service capabilities, quotas, supported regions, prices, security guidance and lifecycle status. Keep the claim, source URL, checked date and implementation evidence together. Recheck at each companion release and when a service notice or exam change affects a lesson. No background research schedule is currently configured.

The DOP-C02 guide still contains OpsWorks examples; AWS's [shutdown reference](https://docs.aws.amazon.com/general/latest/gr/full_shutdown_services.html) lists OpsWorks/Stacks. Preserve that historical exam-source distinction and teach supported configuration-management alternatives for new labs. Do not treat every service named in an exam guide as a deployable recommendation.

## Bounded comparison with existing learning resources

Publisher descriptions and contents were inspected October 18, 2026; this is not a full-book review or a market-wide survey.

| Resource | What the inspected source establishes | Consequence for this book |
| --- | --- | --- |
| [AWS for Solutions Architects, third edition](https://www.packtpub.com/en-us/product/aws-for-solutions-architects-9781836641933) | Publisher presents architectural patterns, migration, certification alignment and generative-AI coverage | These subjects are not unique to AMPLIFY AWS; breadth or AI mentions alone cannot justify a novelty claim |
| [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) | Official guidance provides a structured architecture review approach | Teach the framework in concrete business exercises and cite its authority rather than implying we invented it |
| [AWS professional certification preparation](https://aws.amazon.com/certification/certified-solutions-architect-professional/) | AWS provides an exam guide and preparation/practice resources | Our original scenarios complement official preparation and cannot certify exam readiness |

### Expanded comparison and editorial consequences

A second bounded pass on October 18, 2026 examined the following publisher listings and official training overview. The scope is the material visible on those pages: descriptions, contents, audience labels and resource links. Full books, paid lessons, linked code execution, errata resolution and learner outcomes were not reviewed. A missing item on a sales page means **not established by this inspection**, not absent from the resource. The resources are comparison examples, not a complete market sample or a purchase recommendation.

| Resource and inspected edition | Audience and teaching structure visible in the source | Maintenance evidence visible in the source | Consequence for our own acceptance criteria |
| --- | --- | --- | --- |
| [Amazon Web Services in Action, third edition](https://www.manning.com/books/amazon-web-services-in-action-third-edition), March 2023, Andreas Wittig and Michael Wittig | Practical deployment and operations introduction for developers and infrastructure practitioners; examples span core infrastructure and containers | Publisher links source code, a GitHub repository, errata and an AWS-update article; this inspection did not test their current contents | A companion repository and broad service coverage are established publishing practices. Our examples must work at a recorded revision; having a repository is not a differentiator by itself |
| [AWS Cookbook](https://www.oreilly.com/library/view/aws-cookbook/9781492092599/), English edition, December 2021, John Culkin and Mike Zazon | Publisher labels it intermediate to advanced; contents organize practical recipes across security, networking, storage, databases, compute and other areas | Listing links an errata page; correction turnaround and current recipe compatibility were not inspected | Recipe-level tasks already exist elsewhere. Our connected lessons must explain when a recipe fits, when it fails and what changes with business context |
| [AWS Solutions Architect training overview](https://aws.amazon.com/training/learn-about/architect/) | AWS describes a guided course sequence and a ramp-up guide with additional learning formats | Official landing page provides routes to learning resources; individual course revisions and lab availability were not checked | A learning path alone is not novel. We must demonstrate understandable prerequisites and transfer to an unfamiliar case |

The English Cookbook edition is identified deliberately. A search also returned a Korean listing dated May 2025; that is not evidence of a revised English edition. Edition, language and publication date must remain separate fields in any later comparison. Do not use a newer translation date as proof of updated technical guidance.

These observations support a bounded conclusion: broad AWS topics, hands-on examples, guided progression and companion resources are already represented in the inspected sources. They do not establish that our combination is unique, that other authors omit cost or failure analysis, or that our material produces better learning. The following decisions are our editorial response, not findings about competitors' quality.

### Test the proposed contribution using our own material

| Proposed reader benefit | Concrete trial using this repository | Evidence needed before claiming the benefit |
| --- | --- | --- |
| Explain decisions in ordinary language | Give the reader unit 02, then a changed workload where database saving limits photo completion | Reader distinguishes capacity from throughput, includes continuing arrivals in backlog recovery and explains why adding workers may not help |
| Transfer a foundation to another business | Move from last-seat reservation to the equipment-rental transfer challenge | Reader identifies both scheduling conflicts and physical readiness without assuming that a free calendar slot means usable equipment |
| Make cloud cost and retirement understandable | Use the cost reconciliation exercise after a fictional resource removal | Reader separates usage time from reporting time, replaces snapshots rather than adding them and identifies retained-resource evidence |
| Use AI while retaining engineering judgment | Have Codex propose a release plan, then ask the reader to review it against the publishing guide | Reader detects an unsupported deployment-identity assumption and distinguishes pausing builds from removing resources; retain the actual proposal and review, not a fabricated successful exchange |
| Reproduce and maintain the material | Give a reviewer a named source archive and the companion instructions | Record environment, exact archive hash, requested checks, failures, assistance and correction; distinguish local execution from AWS behavior |

Use the [chapter evidence ledger](chapter-evidence.csv), [compute cases](../examples/compute-selection/README.md), [business transfer challenge](../examples/business-transfer/README.md), [cost reconciliation exercise](../examples/costs/RECONCILIATION-REVIEW.md) and [publishing guide](../reader/GITHUB-TO-AMPLIFY-FIELD-LESSON.md) as the starting artifacts. Existing internal checks support some implementation claims; they do not supply the reader evidence in this table.

Record baseline experience, initial prediction, first-attempt result and assistance separately. A reader who succeeds after a detailed hint has a different result from one who independently transfers the concept. A small trial can reveal an instruction defect or misconception; it cannot establish market-wide superiority or reliable certification pass rates. Review the affected passage and repeat a changed case after a correction rather than merely rerunning the same memorized answer.

For later comparative evaluation, obtain lawful access to the exact editions, choose a shared task and comparable prerequisites, and record what each source actually teaches. Do not score an unread chapter as zero. Keep publisher claims, reviewer observations and learner behavior in separate columns. No such comparative learner trial has been conducted.

Our proposed contribution is a connected ELI5 progression with explicit cost/cleanup evidence, AI-assisted work checked by the reader, and repeated business-context variations. Its value must be demonstrated by completed material and reader trials. No claim of being the first or surpassing every other book is supported.

## Independent learner trial

Recruit a consenting beginner and an experienced operator/architect who did not author the material. Recruitment and messaging have not been performed. Use synthetic data and local exercises first. Do not ask participants to buy resources to validate a draft.

Give each participant the same frozen instructions and record their environment. Ask them to predict outcomes, complete an exercise, explain a failure and solve one changed requirement. Record where they needed help and distinguish a setup failure from a conceptual misunderstanding. Avoid coaching during the independent portion; document any intervention.

Capture: participant pseudonym and relevant experience; consent to recorded notes; source revision; task; start/end; outcome; help requested; incorrect prediction; explanation in their own words; severity; proposed remedy; retest outcome. Do not infer comprehension from satisfaction alone or generalize from two people to all learners.

A technical reviewer separately checks IAM boundaries, correctness under concurrency, cost assumptions, recovery semantics and current documentation. Author/model review remains internal review even when performed in a fresh context.

### First bounded pilot packet

Use the [six separate reader tasks](../examples/learner-pilot/README.md) for a bounded trial. The beginner traces source, package contents and an old served URL. The experienced operator resolves a supplier's accepted request with a missing local reply and unverified lookup. The architecture reader transfers a repair-shop decision method to a food bank, then handles a two-depot partner and selective recovery. The Amplify-privacy reader judges a later list page, cross-user file overwrite and failed cleanup. The operations reader classifies exact customers whose work remains unfinished or whose deadline was missed, then handles a later completion and an exact due-time boundary. The certification-to-application reader chooses a recovery design from stated evidence, then changes the decision when a second rehearsal supplies different evidence. Each has a changed case and a separate assistance phase. Keep the [assessor criteria](../examples/learner-pilot/ASSESSOR.md) hidden until the independent response is retained. These tasks test different outcomes; do not average them into a book-wide score.

Freeze the actual source revision/archive before providing it, record consent and prerequisites, and leave result fields blank. Optional local execution is assessed separately from written reasoning. Recruitment, delivery and participant observations remain unperformed; this packet supplies procedure and criteria only. Do not fill blank observations with predicted answers or AI-generated participant responses.

For a written first attempt, a facilitator prepares and checks a separate assessor-free packet from the private book source. This lab packet does not include that packaging tool or the chapter text it needs. Give each participant only their assigned reading and task, record the packet hash, and keep assessor notes with the facilitator. Optional execution uses a separately checked source archive. No participant observations have been made.

## Figure and accessibility review

Inventory each figure's purpose, source, caption, text alternative, chapter and status. For every arrow, explain its meaning in nearby prose. Distinguish data flow, control flow and trust boundaries; do not rely on color alone. Check labels at print size and enlarged ebook text. Current SVGs have editable Python source; desktop review does not establish print-size or ebook readability.

The visual program and [inventory reconciliation](../reader/OWNER-RECORD-BOUNDARY.md) track the larger current collection; the earlier seven-figure opening-unit inventory is historical and is not a count of the current book. Reconcile the inventory against the exact source and output selected for review. A figure's descriptive text or inventory entry does not establish readable print, Kindle behavior, accessibility or a deployed architecture. Review the actual final renderings and distinguish illustrative designs from observed implementations.

## Publication and continuity

Maintain the private repository until code/content licensing, account portability and history review are complete. Do not replace private account identifiers with false claims of clean-account verification. Keep execution evidence and credentials outside tracked source. Before a public release, inspect the complete intended Git history as well as the current tree and verify the actual remote visibility.

Synchronize book text, examples, figures and assessments at a named revision. Use an errata entry containing affected revision, symptom, impact, correction and verification. Follow the workspace exact-final-file visual review standard before promoting print/ebook artifacts. Working manuscript additions do not update the earlier reviewed DOCX automatically.

## Capstone trial materials

Use `examples/capstones/OPERATIONS.md` with its fixed fictional incident JSON and `ARCHITECTURE.md` for integrated practice. Keep `ASSESSOR.md` and checker output out of the first attempt. The provisional scoring thresholds are editorial choices; they have not been validated with learners. Record first attempts, assistance, scoring evidence and changed-scenario transfer separately. The fixture checker verifies arithmetic and referential consistency, not the quality of a learner response.
