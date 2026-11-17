# SAP-C03: the published architecture assessment

Checked October 27, 2026 against the [AWS SAP-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03.html) and its five linked domain pages. The source hashes and extraction checks are in [the dated receipt](source-rechecks/2026-10-27-sap-c03.json). This is a **source inventory**, not a claim that this book covers every skill or prepares a reader to pass the exam. The existing SAP-C02 evidence ledger retains its original exam identity.

Think of the guide as a building inspector's checklist. A chapter that explains a firewall is useful, but a checklist item asking the architect to choose and justify several controls has not been met merely because the word *firewall* appears. For each skill we must connect an explanation, a decision under changed conditions, and evidence of what the reader can actually do.

| Domain | Share of scored content | Tasks | Numbered skills |
| --- | ---: | ---: | ---: |
| 1. Architecture Design and Implementation Built for the Cloud | 25% | 5 | 34 |
| 2. Security, Compliance, and Governance | 25% | 5 | 24 |
| 3. Cost-Optimized Architecture Design | 15% | 4 | 19 |
| 4. Resilience, Migration, and Business Continuity | 15% | 3 | 17 |
| 5. Operational Excellence and Automation | 20% | 4 | 21 |
| **Total** | **100%** | **21** | **115** |

The new guide uses numbered **Skill** statements under its tasks. It does not have the separate numbered knowledge and skill lists used by the earlier SAP-C02 ledger. The counts above come from all five domain pages, with unique task and skill IDs checked against their domain and task prefixes. They are source counts, not book coverage percentages.

## Task inventory and initial teaching route

These route names identify promising book areas for *manual review*. They are not verified one-to-one skill assignments. The official domain pages are [1](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain1.html), [2](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain2.html), [3](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain3.html), [4](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain4.html), and [5](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain5.html).

| Task | Official topic, shortened | Skills | First book route to examine |
| --- | --- | ---: | --- |
| 1.1 | Cloud-native architecture | 13 | Delivery, containers, events, tenant boundaries, service communication |
| 1.2 | AI and ML integration | 4 | Authorized retrieval, agents and human approval |
| 1.3 | Hybrid integration | 5 | Hybrid network paths and migration decisions |
| 1.4 | Network architecture | 5 | Network paths, private access and global routing |
| 1.5 | Data, storage and databases | 7 | Data choice, events, reports and governed sharing |
| 2.1 | Identity security | 5 | Identity, authority and temporary access |
| 2.2 | Encryption and key management | 4 | Data protection and cryptographic migration |
| 2.3 | Multi-account governance | 6 | Accounts and governance; organization work stays design-only |
| 2.4 | Compliance architecture | 6 | Security evidence, residency and audit paths |
| 2.5 | Responsible AI security | 3 | Agent tool boundaries and approval cases |
| 3.1 | Pricing models | 4 | Cost and context; price selection |
| 3.2 | Network and transfer cost | 5 | Network paths and traffic assumptions |
| 3.3 | Allocation and visibility | 5 | Tags, bills, shared charges and budgets |
| 3.4 | Storage and database cost | 5 | Storage and data lifecycle decisions |
| 4.1 | Migration strategy | 6 | Migration and hybrid lessons |
| 4.2 | Disaster recovery | 6 | Recovery as a business promise |
| 4.3 | Continuity and resilience | 5 | Failure drills and customer recovery |
| 5.1 | Infrastructure as code | 4 | Terraform, review and rollback |
| 5.2 | CI/CD and DevSecOps | 5 | Delivery, security gates and publisher labs |
| 5.3 | Observability | 7 | Request telemetry and incident decisions |
| 5.4 | Operational automation | 5 | Recovery controllers and operations |

## What the new source changes

The guide now explicitly names AI integration and responsible AI controls, post-quantum cryptography, modern service communication, cost allocation, and operations among its skills. A previous bridge based on announced themes was a sensible preparation exercise, but it no longer serves as the authoritative task list. In particular, the new [task 2.2](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain2.html) names ML-DSA and ML-KEM. The book's new [three-job explanation](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153) and [decision exercise](../examples/crypto-migration/README.md) are **partial teaching evidence** for that topic; they do not show configured KMS policies, compatibility, protocol safety, or learner performance.

All 115 skills now have internal passage or exercise links and a bounded partial judgment. The next substantive check is with independent learners on selected changed-condition cases. Preserve the source's verbs: *design* and *implement* may demand different observations. A local exercise, a cloud configuration, and a correct learner decision are distinct evidence. No AWS resource or credit was used to assemble this inventory.

The [Domain 1 skill review](SAP-C03-DOMAIN-1-EVIDENCE.md) maps all 34 IDs and finds 34 partial and no gap skills after existing compute-placement teaching was found and new real-time status and dual-stack labs were added. The [Domain 2 skill review](SAP-C03-DOMAIN-2-EVIDENCE.md) maps all 24 IDs and finds 24 partial and no gap skills after provider-evidence and AgentCore Identity path lessons were added. The [Domain 3 skill review](SAP-C03-DOMAIN-3-EVIDENCE.md) maps all 19 IDs and finds 19 partial and no gap skills after the existing EBS selection exercise and new tag-governance and shared-cost lessons were found or added. The [Domain 4 skill review](SAP-C03-DOMAIN-4-EVIDENCE.md) maps all 17 IDs and finds 17 partial and no gap skills after the illustrated mainframe and organization backup exercises. The [Domain 5 skill review](SAP-C03-DOMAIN-5-EVIDENCE.md) maps all 21 IDs and finds 21 partial and no gap skills after the AI operating-signal, container-monitoring and cross-account archive exercises. All 115 IDs have now received a bounded internal mapping judgment; **none is verified complete**, and this is not a certification-readiness result. The [teaching-gap register](SAP-C03-GAP-QUEUE.md) now has no clear missing lesson in this bounded map; it records remaining proof gates.
