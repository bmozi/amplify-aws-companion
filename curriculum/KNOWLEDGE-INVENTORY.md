# Knowledge is a separate coverage question

The [SAP-C02 task 4.1 review](knowledge-reviews/SAP-4-1.md) adds four partial knowledge mappings and three separate partial skill mappings for portfolio assessment, tracking, asset planning, wave planning, 7Rs and TCO. These are local teaching and fictional assessment links; current source-ledger totals appear below.

The [task 4.2 review](knowledge-reviews/SAP-4-2.md) adds six knowledge and five skill partial mappings for choosing file, server, database, network, identity and governance migration mechanisms. A local arithmetic drill disproves the fictional five-day transfer path; it does not test an AWS transfer.

The [SAP-C02 task 3.5 review](knowledge-reviews/SAP-3-5.md) adds four knowledge and five skill partial mappings for cost-conscious architecture, purchasing models, transfer charges, reporting, resource utilization, granular investigation, tags and alert design. Its CSVs and figures are fictional and the alert remains design-only.

A skill asks what a learner can do. A knowledge list identifies concepts they need to understand while doing it. A task assignment does not show that either has been taught thoroughly. The new inventory exposes the separate knowledge lists instead of allowing them to disappear behind the task totals.

The checked baseline contains **259 separately listed knowledge entries** across 19 official domain pages and 66 existing tasks:

| Exam baseline | Separate knowledge entries | Interpretation |
| --- | ---: | --- |
| SAA-C03 | 107 | Editorial positions within each task's knowledge list |
| DOP-C02 | 59 | Editorial positions within each task's knowledge list |
| SAP-C02 | 93 | Transitional baseline; not SAP-C03 coverage |
| SOA-C03 | Not separately enumerated | These checked task pages use numbered skills; zero inventory rows does not mean no knowledge is required |

[knowledge-inventory.csv](knowledge-inventory.csv) records the source task link, ordinal, inherited chapter/exercise assignment and a digest of the source bullet. It does not reproduce the full guide or invent a paraphrase for an unreviewed concept. Open the linked task's **Knowledge of** list and count to the stated position. An ordinal is our editorial identifier, not an official AWS objective ID. A changed list can shift ordinals, so compare content as well as counts before reusing an old mapping.

[knowledge-sources.json](knowledge-sources.json) records the fetched-source hashes, fetch time, per-task counts and source structure. The [individual knowledge evidence ledger](knowledge-evidence.csv) now contains 259 partial reviews. All 107 SAA-C03 knowledge entries have individual partial mappings; all DOP-C02 task knowledge lists have individual review files ([task 2.1](knowledge-reviews/DOP-2-1.md); [task 2.2](knowledge-reviews/DOP-2-2.md); [task 2.3](knowledge-reviews/DOP-2-3.md); [task 3.3](knowledge-reviews/DOP-3-3.md), [task 4.1](knowledge-reviews/DOP-4-1.md), [task 4.2](knowledge-reviews/DOP-4-2.md), and [task 4.3](knowledge-reviews/DOP-4-3.md), [task 5.1](knowledge-reviews/DOP-5-1.md), [task 5.2](knowledge-reviews/DOP-5-2.md), and [task 5.3](knowledge-reviews/DOP-5-3.md), [task 6.1](knowledge-reviews/DOP-6-1.md), [task 6.2](knowledge-reviews/DOP-6-2.md)). The [SAP-C02 task 1.1 review](knowledge-reviews/SAP-1-1.md) maps all five task 1.1 knowledge bullets as partial, and does not establish SAP-C03 coverage. The [SAP-C02 task 1.2 review](knowledge-reviews/SAP-1-2.md) maps all four security-control knowledge bullets as partial through the integrated design packet. The [SAP-C02 task 1.3 review](knowledge-reviews/SAP-1-3.md) maps three recovery knowledge points as partial through the regional packet. The [SAP-C02 task 1.5 review](knowledge-reviews/SAP-1-5.md) maps three cost and purchasing knowledge points through an illustrated lesson and design packet. The [SAP-C02 task 1.4 review](knowledge-reviews/SAP-1-4.md) maps three multi-account knowledge points through an illustrated design packet. The [task 2.1 review](knowledge-reviews/SAP-2-1.md) maps four deployment knowledge points through a platform-choice lesson and design packet. The [task 2.2 review](knowledge-reviews/SAP-2-2.md) maps five continuity knowledge points through a whole-path lesson and design packet. The [task 2.3 review](knowledge-reviews/SAP-2-3.md) maps six security-control knowledge points through a layered-request lesson and design packet. The [task 2.4 review](knowledge-reviews/SAP-2-4.md) maps six reliability knowledge points through a DNS/capacity lesson and design packet. The [task 2.5 review](knowledge-reviews/SAP-2-5.md) maps four performance knowledge points through a changed-bottleneck packet and local cold-cache lab. The [task 2.6 review](knowledge-reviews/SAP-2-6.md) maps five cost knowledge points through the whole-path cost lesson and fictional photo archive case. The [task 3.1 review](knowledge-reviews/SAP-3-1.md) maps five operational-improvement knowledge points through the whole-loop lesson and fictional packet. The [task 3.2 review](knowledge-reviews/SAP-3-2.md) maps seven security-improvement concepts through an illustrated lesson, a fictional packet and a local credential handoff. Other linked SAA reviews and topic-specific partial mappings cover identity, workload security, distributed compute, databases, compute design, network architecture, storage, costs, recovery, containers, APIs, events, artifact evidence and deployment. No entries remain inventory-only. Every individual review is still partial; live service behavior, independent learner response and final certification coverage are not established. The [SAP-C02 task 4.3 review](knowledge-reviews/SAP-4-3.md) and [task 4.4 review](knowledge-reviews/SAP-4-4.md) cover the last nine knowledge entries with a two-phase lesson and local/design assessment. The [SAA-C03 task 2.2 review](knowledge-reviews/SAA-2-2.md) maps all twelve resilience knowledge bullets individually; the [task 2.1 review](knowledge-reviews/SAA-2-1.md) maps all sixteen compute/network bullets. The 246 individually reviewed skills remain partial and are a different population; do not add these counts into a completeness percentage.

## Refresh without silently changing the baseline

From the repository root:

```sh
python3 scripts/inventory-knowledge.py --refresh
```

The script fetches public official Markdown pages into ignored `artifacts/curriculum-research/` and produces candidate inventory/report files there. It does not write the accepted curriculum files, run AWS account APIs, install packages or deploy resources. Without `--refresh`, it uses the cached source and checks its bytes against the fetch record. A missing or altered cache requires investigation or a fresh fetch; it is not silently accepted.

The parser rejects missing tasks, duplicate tasks, unclassified/nested bullets, changed skill counts and changed separate-list structure. These checks catch some source-format drift, not every possible semantic change. Inspect changed bullets and assignments before deliberately copying reviewed candidates into the curriculum. Candidates begin with pending statuses; reconcile existing evidence and source-bullet hashes before accepting a refresh. A changed source hash requires renewed semantic review, not automatic preservation of a prior mapping. Keep official source text in the ignored research cache rather than publishing a replacement copy of the exam guide.

The baseline review checked all task and skill counts, the 53 separate knowledge-list headings, representative counts for SAA 3.3, DOP 1.1 and SAP 1.1, and SOA's absent separate-list structure. Four malformed-input cases were rejected. This is inventory validation, not an individual semantic review of 259 concepts.

## Turn an entry into teaching evidence

Take one entry at a time. Read the official concept in context, write a concise original explanation using the business example, identify an exact manuscript section, and create a changed-case question that requires understanding. Link relevant implementation or observation when the concept calls for it. State what remains untested and retain learner review as pending until a learner actually attempts it.

Ask Codex to find the concept in the manuscript and distinguish a passing mention from an explanation or tested example. Check its citations and challenge a missing case. A fluent summary of a source is not proof that a reader can use the concept.

The [task 2.1 individual review](knowledge-reviews/SAA-2-1.md) binds the API and container-orchestration mappings to exact source bullets and distinguishes local HTTP behavior from proposed gateway/cluster operation.

The [task 3.2 scaling review](knowledge-reviews/SAA-3-2.md) binds the scaling-capability mapping to its exact source bullet and separates planning arithmetic from an installed controller.

The [DOP-C02 task 2.1 change-management review](knowledge-reviews/DOP-2-1.md) maps one knowledge entry to local Terraform behavior and seven design cases; it does not claim the neighboring AWS tool-deployment skills.

The [DOP-C02 task 1.4 methodology review](knowledge-reviews/DOP-1-4.md) connects the release teaching and evidence to two knowledge entries and lists the remaining platform-specific gaps. E15 now provides a linked progression through the release companions.

The [SAP-C02 task 3.4 review](knowledge-reviews/SAP-3-4.md) individually maps six reliability knowledge points as partial, with Unit 07/22 teaching, nine fictional design cases and a local synthetic growth screen. It preserves selected AWS failure, account quota, independent technical and learner review as open work; these mappings do not establish SAP-C03 coverage.
