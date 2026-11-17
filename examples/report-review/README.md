# Review one report from sale to reader

This is a design-only transfer exercise for unit 14. It requires no AWS account, installation or spending. Write predictions before reading [the assessor notes](ASSESSOR.md). No independent learner trial has been performed.

## The situation

Two shops use independent sale numbers. Shop A's sale 42 is 1,000 cents at second 10; shop B's sale 42 is 2,000 cents at second 20. All amounts use the same currency. The report window is seconds 0 through 59 inclusive. A arrives at second 11, repeats unchanged at 12, and B arrives at 130. An unauthorized sender also submits an otherwise valid 90,000-cent sale claiming to be shop A. The trusted intake rejects it before the business ledger.

The owner wants a provisional report at second 60 and an updated report when more evidence arrives. For this fixture, the expected source manifest contains exactly the two authorized producer/ID pairs. This is an exercise assumption, not a method for proving that real registers recorded every sale.

## Submit one evidence sheet

1. Predict the total at seconds 60 and 131. List the keys counted and the missing keys at each time. Name the field or trusted context that separates the two sale 42 records, and explain why the unauthorized submission must not be repaired merely by changing its schema.
2. A receipt sender and an analytical report each need every accepted sale. Draw their processing boundaries. One shared queue lets either worker take each message. Explain the resulting risk and propose a delivery arrangement that meets the stated need. Include duplicate handling and how replay avoids sending a second receipt.
3. A report query becomes faster after conversion to another file format. Propose checks for totals, identities, currency, timestamps and missing or conflicting rows. State what additional measurement would support a cost or speed claim. Do not use a successful conversion as the answer key.
4. A partner may receive only a permitted aggregate. An engineer grants that partner direct read access to all underlying objects to fix a query error. Explain what boundary has changed, what access should be investigated, and why removing access tomorrow cannot recall a copy downloaded today.
5. A search index contains yesterday's return policy. The source now has a different policy; a delayed job attempts to publish the older version after the newer one. Describe version and authorization checks at indexing and reading time. Distinguish freshness from relevance: a current document can still answer the wrong question.
6. The next day, shop A refunds 400 cents. The business has not decided whether to restate yesterday's sales or report refunds separately today. Write the question the owner must answer before implementation. Explain why neither arrival time nor an overwrite of sale 42 can silently choose that policy.

Finish by marking every claim **fixture calculation**, **design decision**, **local execution evidence**, or **live observation**. This exercise supplies only the first two unless you attach separate, relevant evidence. Ask Codex to challenge your sheet with one failure at each boundary; verify its arithmetic and reject any claim of a live result it did not observe.
