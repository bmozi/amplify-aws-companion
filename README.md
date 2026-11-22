# Thinking in AWS companion

This source companion supports Thinking in AWS by John Briggs (earlier working title: AMPLIFY AWS). It contains learning routes, cloud-free exercises, diagrams and source specimens. The commercial manuscript, cover artwork and private owner records are not included.

Start with [the reader route](reader/README.md), [the first local exercise](docs/FIRST-LOCAL-EXERCISE.md), and [command scope](reader/COMMAND-SCOPE.md). Use the book locators when a lesson points to a chapter. Local checks run without an AWS account.

## Browser practice for paperback and Kindle readers

Open [Thinking in AWS book resources](https://bmozi.net/books/thinking-in-aws) for request-flow, retry, and recovery activities. The same resources support both editions. You can also download this repository and open `reader/interactive/index.html` locally; the browser activities need no AWS account or installation.

Existing exercise names, book locators, and command paths remain supported. If your book links to the [original companion revision](https://github.com/bmozi/amplify-aws-companion/tree/b2c7eab899b9fbf0621ae1cd912a6d981b4cda72), that snapshot is preserved. Continue using it for the matching source, or use these optional browser activities alongside it.

## Inspection-only cloud source

Live AWS entry points are disabled in this snapshot, including credential export and deployment wrappers. Infrastructure and policy files remain source specimens. Do not copy them into an active account or workflow without a separately reviewed identity, ownership, budget, lifecycle and cleanup design. Fictional account IDs, example Regions and illustrative prices are not verified reader settings. The historical USD 100 reserve and USD 5 run example are not universal requirements.

Author attribution does not identify the current operator. Original material remains Copyright © 2026 John Briggs, all rights reserved. Public availability does not select an open-source or general redistribution license. Third-party dependency terms and provenance limitations are described in [the notices](THIRD-PARTY-NOTICES.md).

## Browser build scope

The app install is frontend-only. Its Vite build bundles browser files; it does not perform full TypeScript/backend typechecking or cloud deployment. See [the browser build instructions](app/README.md) and [the separately unresolved backend toolchain](app/BACKEND-TOOLCHAIN-STATUS.md).

## Local verification

From this directory, run `python3 scripts/check-companion.py --lab-only` for the short manifest-bound check, or `--lab-only-expanded` for the declared cloud-free groups. Local services may create temporary files/processes; read the selected lab's cleanup instructions. No passing local check establishes deployed AWS behavior or learner mastery.

# Start here: learn AWS by making and checking decisions

For SAA-C03 preparation, start with the [self-paced study route](curriculum/saa-c03/README.md). Save the diagnostic first attempt before opening any answer key; the route supplies a task-by-task reading and practice sequence.

Suppose a customer presses **Save note**. A page may say “saved,” but which service accepted the request, where is the note, who may read it, and what happens when a reply is lost? *AMPLIFY AWS* starts with questions like these. The companion gives you small ways to test the reasoning before you spend money in an AWS account.

The book follows 34 chapters from a customer request through identity, cost, networking, data, operations, recovery and architecture decisions. Source filenames retain older unit numbers; use the **chapter number in the book's contents** for reading order. The [learning routes](curriculum/LEARNING-ROUTES.md) offer beginner, operator, architect and certification-study paths without treating one route as a universal prerequisite list.

If certification is part of your goal, use the [exam-to-application practice route](curriculum/CERTIFICATION-TO-APPLICATION.md). It shows how to turn one current AWS objective into both a reasoned scenario answer and a separate, bounded engineering check.

## One way to use each chapter

1. Read the customer situation and the diagram. Say what must happen in ordinary words before naming AWS products.
2. Answer the chapter's first question **before** opening its reasoning check. Keep that answer, including uncertainty.
3. Change the stated condition and decide again. Explain which constraint changed your choice.
4. Open the linked local exercise and run only what its README says is cloud-free. Record the source version, prediction, command and observed result.
5. If a live AWS exercise would answer a remaining question, first identify the account, Region, scoped non-root role, whole-run estimate, credit terms, spending and reserve limits, stop rule and cleanup owner. Choose limits from your own account and workload.
6. Return after a delay and try a fresh case. A familiar page or a correct answer letter is not the same evidence as explaining and operating a system.

Use the [learning record](curriculum/LEARNING-RECORD.md) to separate your first answer, AI help, local observation, cloud observation and changed-case decision. The [Field Lab reader playbook](docs/FIELD-LAB-READER-PLAYBOOK.md) explains those evidence levels through the Amplify notebook application.

Before copying any command, use the [command-scope field card](reader/COMMAND-SCOPE.md). It shows which examples inspect files, which change your computer, and which contact or change an AWS account. Predict the effect first; a command labeled “lab” is not automatically cloud-free.

## Your first three stops

For unfamiliar terms, use the [vocabulary stories](reader/VOCABULARY-STORIES.md).

For a product name, use the [service-to-decision finder](reader/SERVICE-FINDER.md) to locate the relevant chapter and comparison.

For an early hands-on result, [test a private note's second entrance](reader/FIRST-SUCCESS.md) before the full Amplify chapter. Then use [cumulative retrieval practice](curriculum/RETRIEVAL-PRACTICE.md) to revisit ideas across the book.

| If you want to… | Start here | What you can establish |
| --- | --- | --- |
| Understand cost without an account | [First local exercise](docs/FIRST-LOCAL-EXERCISE.md) | Your estimate's inputs and arithmetic, not a future bill |
| Follow the first app | [Amplify application chapter](reader/BOOK-LOCATORS.md#book-e8d9fb108293da29) | Which parts serve a page, sign-in, notes and files, and what still needs testing |
| Practice a release decision | [Publisher-role field lab](reader/PUBLISHER-ROLE-FIELD-LAB.md) | Local source and policy boundaries, not a GitHub publication or a visitor result |

After the cost exercise, try the [data-contract walkthrough](examples/data-contract/README.md#start-with-one-update). It asks you to predict what zero, an omitted field and an empty note mean, then connects that local result to authority, stale edits and lost responses. For a different business context, take the [food-bank pickup challenge](examples/food-bank-pickup/README.md#predict-the-customer-view): decide what a customer may truthfully be told before stock is confirmed. The two examples share a habit—define the promise, the boundary and the evidence—but solve different business problems. Neither requires an AWS account.

The [release-switch and job-badge evidence case](reader/GITHUB-PUBLISHER-EVIDENCE-CASE.md) lets you distinguish a dated read-only GitHub identity probe from an actual application release.

The [GitHub-to-Amplify field lesson](reader/GITHUB-TO-AMPLIFY-FIELD-LESSON.md) compares three independent publishing roads, their stop controls and the resources that remain after releases stop.

Most examples use invented data and run locally. Read a lab's cost and prerequisite notes before installing dependencies or starting a service. A local fake is useful when it tests whether a checker catches a mistake; it does not prove AWS enforced the same rule. AWS Budgets can notify, but an alert is not a universal spending cap. The [cost-and-credit field lesson](reader/COST-AND-CREDIT-FIELD-LESSON.md) shows how to estimate, stop, remove resources and reconcile delayed billing.

Codex can ask you to defend a choice, trace a request, inspect a diagram or challenge a missing assumption. Keep its suggestion beside your original answer and verify technical claims in current AWS documentation and observed behavior. Do not paste credentials, private account receipts or customer data into a public exercise.

Copyright © 2026 John Briggs. All rights reserved.
