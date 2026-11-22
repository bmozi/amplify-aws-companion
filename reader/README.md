# Start here: learn AWS by making and checking decisions

For SAA-C03 preparation, start with the [self-paced study route](../curriculum/saa-c03/README.md). Save the diagnostic first attempt before opening any answer key; the route supplies a task-by-task reading and practice sequence.

Suppose a customer presses **Save note**. A page may say “saved,” but which service accepted the request, where is the note, who may read it, and what happens when a reply is lost? *AMPLIFY AWS* starts with questions like these. The companion gives you small ways to test the reasoning before you spend money in an AWS account.

The book follows 34 chapters from a customer request through identity, cost, networking, data, operations, recovery and architecture decisions. Source filenames retain older unit numbers; use the **chapter number in the book's contents** for reading order. The [learning routes](../curriculum/LEARNING-ROUTES.md) offer beginner, operator, architect and certification-study paths without treating one route as a universal prerequisite list.

If certification is part of your goal, use the [exam-to-application practice route](../curriculum/CERTIFICATION-TO-APPLICATION.md). It shows how to turn one current AWS objective into both a reasoned scenario answer and a separate, bounded engineering check.

## One way to use each chapter

1. Read the customer situation and the diagram. Say what must happen in ordinary words before naming AWS products.
2. Answer the chapter's first question **before** opening its reasoning check. Keep that answer, including uncertainty.
3. Change the stated condition and decide again. Explain which constraint changed your choice.
4. Open the linked local exercise and run only what its README says is cloud-free. Record the source version, prediction, command and observed result.
5. If a live AWS exercise would answer a remaining question, first identify the account, Region, scoped non-root role, whole-run estimate, credit terms, spending and reserve limits, stop rule and cleanup owner. Choose limits from your own account and workload.
6. Return after a delay and try a fresh case. A familiar page or a correct answer letter is not the same evidence as explaining and operating a system.

Use the [learning record](../curriculum/LEARNING-RECORD.md) to separate your first answer, AI help, local observation, cloud observation and changed-case decision. The [Field Lab reader playbook](../docs/FIELD-LAB-READER-PLAYBOOK.md) explains those evidence levels through the Amplify notebook application.

Before copying any command, use the [command-scope field card](COMMAND-SCOPE.md). It shows which examples inspect files, which change your computer, and which contact or change an AWS account. Predict the effect first; a command labeled “lab” is not automatically cloud-free.

## Browser practice

Use the [shared paperback and Kindle resources](https://bmozi.net/books/thinking-in-aws), or open the [offline activity instructions](interactive/README.md). Follow a request, inspect duplicate acceptance, and compare recovery promises before returning to the named chapters.

## Your first three stops

For unfamiliar terms, use the [vocabulary stories](VOCABULARY-STORIES.md).

For a product name, use the [service-to-decision finder](SERVICE-FINDER.md) to locate the relevant chapter and comparison.

For an early hands-on result, [test a private note's second entrance](FIRST-SUCCESS.md) before the full Amplify chapter. Then use [cumulative retrieval practice](../curriculum/RETRIEVAL-PRACTICE.md) to revisit ideas across the book.

| If you want to… | Start here | What you can establish |
| --- | --- | --- |
| Understand cost without an account | [First local exercise](../docs/FIRST-LOCAL-EXERCISE.md) | Your estimate's inputs and arithmetic, not a future bill |
| Follow the first app | [Amplify application chapter](BOOK-LOCATORS.md#book-e8d9fb108293da29) | Which parts serve a page, sign-in, notes and files, and what still needs testing |
| Practice a release decision | [Publisher-role field lab](PUBLISHER-ROLE-FIELD-LAB.md) | Local source and policy boundaries, not a GitHub publication or a visitor result |

After the cost exercise, try the [data-contract walkthrough](../examples/data-contract/README.md#start-with-one-update). It asks you to predict what zero, an omitted field and an empty note mean, then connects that local result to authority, stale edits and lost responses. For a different business context, take the [food-bank pickup challenge](../examples/food-bank-pickup/README.md#predict-the-customer-view): decide what a customer may truthfully be told before stock is confirmed. The two examples share a habit—define the promise, the boundary and the evidence—but solve different business problems. Neither requires an AWS account.

The [release-switch and job-badge evidence case](GITHUB-PUBLISHER-EVIDENCE-CASE.md) lets you distinguish a dated read-only GitHub identity probe from an actual application release.

The [GitHub-to-Amplify field lesson](GITHUB-TO-AMPLIFY-FIELD-LESSON.md) compares three independent publishing roads, their stop controls and the resources that remain after releases stop.

Most examples use invented data and run locally. Read a lab's cost and prerequisite notes before installing dependencies or starting a service. A local fake is useful when it tests whether a checker catches a mistake; it does not prove AWS enforced the same rule. AWS Budgets can notify, but an alert is not a universal spending cap. The [cost-and-credit field lesson](COST-AND-CREDIT-FIELD-LESSON.md) shows how to estimate, stop, remove resources and reconcile delayed billing.

Codex can ask you to defend a choice, trace a request, inspect a diagram or challenge a missing assumption. Keep its suggestion beside your original answer and verify technical claims in current AWS documentation and observed behavior. Do not paste credentials, private account receipts or customer data into a public exercise.

Copyright © 2026 John Briggs. All rights reserved.
