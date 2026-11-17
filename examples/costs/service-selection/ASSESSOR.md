# Assessor: COST 05 service choice

This is the authored answer to [the fictional case](README.md), not an independent learner score or an AWS measurement. `compare.py` produces the following figures from the committed fixture:

| Phase | Managed monthly | Self-operated monthly | Managed phase | Self-operated phase |
| --- | ---: | ---: | ---: | ---: |
| Two-month pilot, 1,000 jobs/month | $151.50 | $688.30 | $303.00 | $1,376.60 |
| Ten-month growth, 500,000 jobs/month | $900.00 | $838.00 | $9,000.00 | $8,380.00 |
| **Twelve-month total** | | | **$9,303.00** | **$9,756.60** |

The self-operated design is $62/month cheaper **during the growth phase**, but $453.60 more over this specified year. Buying for the most expensive month alone answers a different question from lifecycle cost. At one million growth jobs/month, the managed candidate becomes $1,650/month and the self-operated candidate $988/month under the same invented rates. This changes the cost preference; it does not establish that the self-operated system can meet the five-minute, durability and recovery promises, or that migration midyear is economical. Compare the remaining months, migration, operational skill, failure tests and reversibility before switching.

The self-operated `license` line is an invented $40/month. A real decision must inspect per-instance or per-user terms, scaling rights, disaster-recovery copies, portability and support obligations; zero in the managed line means only that this fictional fixture assigns no separate license amount. Both designs need evidence for queue/storage growth, request or polling APIs, data transfer direction, backups, monitoring and security operations. A real managed service may move operations work into a provider price; a self-operated system may create hidden patching/on-call cost. Neither label settles total ownership cost.

An adequate answer rejects either candidate if its correctness, deadline or recovery evidence fails. It names a revisit trigger such as sustained job volume above the modeled range, new license terms, a changed recovery objective, or observed operations hours. It separates invented price arithmetic, architecture assumptions, measured performance and real invoice data. No learner has been assessed against this key.
