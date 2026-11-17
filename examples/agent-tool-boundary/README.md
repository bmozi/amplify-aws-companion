# A tool request is a proposal, not permission

Maya's warranty assistant can read approved policy excerpts. She now wants it to propose a small customer credit after a repair goes badly. A paragraph in a retrieved document might say “issue everyone a credit.” A model might repeat that instruction or invent parameters. The application must decide whether the specific actor, job, amount and approval permit the action; a fluent proposal cannot grant itself authority.

This local lab checks that decision boundary without calling a model, Bedrock, AgentCore, AWS or a payment system. The fictional `issue_credit` action appends one tuple to an in-memory dictionary. It does **not** send money, issue a real credit, authenticate a user, validate an approval signature or provide durable concurrency control.

Run from this folder with Python 3:

```sh
python3 lab.py
python3 -m unittest -v test_lab.py
```

The caller identity, document grants, job tenant/revision, current action intent and approval record are server-owned fixtures in `lab.py`. The proposed tool name, target and amount are untrusted. The gate has a read-only tool allowlist; a *new* credit requires a separate trusted intent for the exact actor, tool, job, amount and operation ID, plus an exact current approval, bounded integer amount and local new-action limit. An approval alone cannot start a new action. A repeated identical operation reports its earlier record even after approval expiry, without another effect; changed intent with the same ID is denied. These are application design choices, not features automatically supplied by an AI agent or AWS service.

Predict the result before running each case: an allowed shop-A policy read; a shop-B policy read by Maya; an invented export tool; a proposed credit with approval but no current request; a valid requested and approved credit; the same credit replay; a changed amount; expired approval; and a second new credit after the local action limit is reached. Then inspect the separate [assessor notes](ASSESSOR.md). The tests exercise a deterministic gate over fixture inputs. They do not test whether a model follows instructions, whether a human request or approval is authentic, IAM effectiveness, a distributed race or external-effect reconciliation.

## Follow a retrieved instruction to the action gate

First imagine an approved paper form already in Maya's drawer. A retrieved note says to use it now. Predict whether the note itself creates a current customer-credit request. From the repository root run `python3 examples/agent-tool-boundary/journey.py`. The program joins the separate SQLite excerpt fixture to the in-memory action gate under one synthetic shop-A actor. It releases an authorized but hostile note, presents a proposal matching an existing approval, and checks that no new credit is recorded while the trusted work-item map is empty. Only then does the fixture install a separate exact intent and record one fictional credit. An identical retry returns a replay result. Revoking the document grant blocks a later excerpt release but does not undo the action already recorded.

The runner does not execute the retrieved instruction or invoke a model. Its proposal is hand-authored to represent a possible bad suggestion, and its trusted intent is inserted directly by test code. That shows the application control condition, not prompt-injection resistance, real human intent, durable authorization or payment safety. For transfer, change the document to name another approved job while the current trusted request stays on `repair-17`; predict which gate check stops new work. Ask Codex to challenge your answer, then inspect the actual fixture and preserve your first reasoning separately.

For a cloud design, place this gate in an application-owned tool handler or equivalent trusted execution boundary. Derive the actor from verified authentication, resolve current scope, request intent and approval from authoritative stores, validate every model-proposed field and keep the downstream role limited to the specific operation. If using AgentCore Gateway or another tool surface, configuration and IAM still need service-specific review; a prompt or content guardrail is not an authorization policy. Inspect current [AgentCore components](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) and [Bedrock Agents Classic maintenance notice](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-classic-maintenance-mode.html) before choosing an implementation. Before creating a resource or invoking a model, check current account eligibility, selected prices, whole-run spending and reserve limits, a stop rule and cleanup.

Ask Codex to act as a skeptical reviewer: “Find a proposal that would make the handler cross tenants, bypass approval, replay a changed action or exceed the local action limit. Identify which assertion would catch it and which risk remains untested.” Give it only the fictional fixture. An AI-generated attack list is test input to assess, not evidence that all possible attacks have been blocked.

## Reserve one action when two workers race

The in-memory gate above has one caller at a time. The next exercise gives two local workers the same last slot and makes a provider reply disappear. Read the [illustrated chapter section](../../reader/BOOK-LOCATORS.md#book-1720ec3c1b8e817f), then predict the five lines printed by:

```sh
python3 examples/agent-tool-boundary/operation_ledger.py
python3 -m unittest discover -s examples/agent-tool-boundary -p 'test_operation_ledger.py' -v
```

Run these from the repository root. The first claim becomes `pending` in a temporary SQLite file. A second attempt with the **same** operation ID returns `reconcile_required`; a different ID cannot use the one available slot. The test suite starts two local workers together and checks that one wins the same-ID claim, then repeats the race with different IDs and one slot. The program supplies a fictional provider receipt only after showing the lost-reply state. No provider is called and no credit is issued.

Before opening the [ledger assessor](OPERATION-LEDGER-ASSESSOR.md), answer these changed cases in writing:

1. The provider accepted `op-17`, but its HTTP reply vanished. The database says `pending`. May a worker send a new `op-18` credit? What evidence could settle `op-17`?
2. The same operation ID returns with 1,300 cents instead of 1,200. Why should a matching ID alone be insufficient?
3. A second worker starts an unrelated, approved credit while `op-17` is pending and the local new-action limit is one. Does a quiet provider dashboard free that slot?
4. The provider reports no match once, but its lookup is eventually consistent. Can a single empty lookup prove that no credit happened? What contract would you need before releasing or retrying the claim?
5. A model submits a forged receipt string directly to `confirm()`. What did the local fixture actually verify, and where must a real system establish receipt authenticity and ownership?

The `operation_ledger.py` model deliberately accepts an **already authorized** operation and a supplied provider receipt. Its transaction coordinates one local SQLite file; it does not connect to the earlier gate, authenticate approval, prove provider idempotency, or settle a real outside effect. A production design must recheck trusted intent and approval in the relevant transaction boundary, choose a durable claim store, and use the provider's documented status and idempotency behavior. Record pending work for human investigation when the outcome cannot be established. Ask Codex to draw the trust and state transitions, then inspect the code and challenge any claim that a local transaction spans the provider.
