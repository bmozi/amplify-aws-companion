# Review an infrastructure change before applying it

Read unit 9 and run the local Terraform lifecycle drill first. These fictional cases extend E16. They require no AWS access or infrastructure changes. The snippets are teaching summaries, not executable plans or observed account state. Write your decision before opening [the assessor notes](ASSESSOR.md).

For each stage, record: what you know, what remains unknown, the next observation, who owns the change, and the condition that would let work resume. “Apply” and “stop forever” are not the only choices. A pause should protect the system while a specific question is resolved.

## Stage 1: a tidy rename

A colleague changes a resource label from `orders` to `customer_orders`. The stated intention is to preserve the existing database. Their review summary says:

```text
old address: delete
new address: create
business requirement: keep existing records and endpoint
backup: not checked
```

They say the diff contains only a name change. Decide whether the proposed lifecycle satisfies the requirement. Explain what an address mapping might solve and what it would not establish about data or provider-specific replacement behavior.

## Stage 2: the mapping is present

The revised plan records the previous address. It also proposes replacement because a separate provider attribute changed. The reviewer notices the mapping and concludes that replacement has been prevented.

Identify the two independent changes. Specify the evidence needed to continue with either a pure refactor or an intentional replacement. Do not invent which AWS attribute is involved: ask for the actual action, attribute and provider behavior before deciding.

## Stage 3: the environment disagrees

Test has applied the address migration. Production still uses the earlier source revision. A cleanup commit removes the migration record because test no longer needs it. The deployment team wants to promote that commit directly to production.

Explain why one environment's success cannot establish the upgrade path for another. List the source, inputs, state location and current addresses that must be identified for each environment. State how you would preserve a reviewable migration path without giving both tools ownership of the same resource.

## Stage 4: a lock and an uncertain writer

An apply lost its terminal connection. A second operator sees a state lock and wants to force-unlock it. The original runner's status has not been inspected. The dashboard remains available.

Does availability establish that the writer stopped? Name the authoritative process or job observation needed. If the writer is active, what should the second operator avoid? If it is terminal, what else must be reconciled before a new apply? Treat lock removal as a scoped recovery action with an owner, not a routine response to waiting.

## Stage 5: an old state copy

The current state record cannot be located. Yesterday's protected copy records a database that was intentionally deleted this morning and omits a replacement resource created afterward. The business application currently uses the replacement. Someone proposes restoring yesterday's state and immediately applying yesterday's code.

Trace what the old record knows and what it cannot reverse. First distinguish missing state from a wrong backend or workspace. Then describe the inventory, ownership reconciliation and plan review needed before any changes. Explain why the state copy is not a backup of the application's business records.

## Stage 6: recovery and access

After repairing the change process, the infrastructure plan reports no changes. The homepage returns HTTP 200. A second test customer can read the first customer's private note.

Decide whether recovery can be declared complete. Identify the successful observations and the failed requirement separately. Name the immediate containment question, a bounded correction and the positive and negative customer checks needed afterward. Do not respond by granting wider access to make all requests succeed.

## Stage 7: the reassuring empty destination

An operator opens a new empty working folder, pushes a saved state snapshot and plans against the configuration packaged beside it. Both commands succeed; the plan reports no changes. The snapshot and configuration came from test, but the incident concerns production. No production backend or resource inventory has been identified.

Explain why the earlier lineage rejection does not protect this empty destination. Name the missing evidence that would connect the recovered record to the intended environment. Does changing the folder name to `production` supply that evidence? Compare your prediction with the wrong-history negative control in the local state-record drill. Do not interpret its synthetic resource as an actual cloud database.

## Explain the whole decision

Present a five-minute handoff that follows one environment from proposed change to verified business behavior. Include the last safe stopping point, rollback or roll-forward limits, cost of overlap, retained resources and the evidence still missing. Ask Codex to challenge one assumption at each stage, then revise only where the supplied evidence supports it. Do not paste raw state, credentials or sensitive plan values into the assistant.

Use the E16 rubric for requirements, correctness, security, cost, recovery and explanation. These are design answers; only separately attached local or live observations count as execution evidence. No independent learner has been assessed here.
