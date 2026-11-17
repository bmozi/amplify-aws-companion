# A search result is not the policy decision

Maya asks whether a household repair accepted on October 2 is covered. Search ranks the general 45-day policy first. A later bulletin says repairs accepted from October 1 have 60 days. If the assistant copies the first search result into its answer, it gives the wrong duration. If it copies the bulletin without the acceptance date or receipt, it also gives an unsupported answer.

This local exercise places a **manually approved rule catalog** between retrieved candidates and the answer. The catalog binds each rule to exact source version and digest, repair type, start date and priority. These entries are invented teaching facts; the program does not read the policy prose and understand it. In a real business, an accountable owner would have to approve that interpretation and its changes. A score says how well a search result matches the query, not which policy governs the customer.

Predict these four outcomes, then run from the repository root:

```sh
python3 examples/policy-precedence/lab.py
python3 -m unittest discover -s examples/policy-precedence -p 'test_*.py' -v
```

| Changed case | First question |
| --- | --- |
| Household repair accepted September 30, with receipt | Is the later bulletin in force yet? |
| Household repair accepted October 2, with receipt | Why does the lower-ranked bulletin win? |
| October 2 repair without a receipt | Can the program promise coverage from these facts? |
| Commercial repair on October 2 | Does a household duration apply? |

After predicting, remove the bulletin from the candidate packet; revoke Alice's grant; revise its source; then insert an equal-priority contradictory approved rule. The seven local tests show where the result becomes `abstain` instead of quietly falling back to the general policy. Read the [assessor](ASSESSOR.md) after writing your own explanations.

The fixture uses SQLite as a local store and fixed pretend retrieval scores. It does **not** run Bedrock, an FTS/vector index, a model, a real authorization provider or a warranty system. The earlier [authorized retrieval lab](../authorized-retrieval/README.md) exercises actual local FTS5 and permission/version checks; this continuation focuses on the **business interpretation after discovery**. AWS's [Knowledge Bases retrieval guide](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve.html) describes relevant chunks, metadata and a relevance score; it does not make that score a warranty precedence decision. The current AWS guide also says Knowledge Bases guardrails do not apply to retrieved references at runtime. Neither a score nor a guardrail replaces an application-owned access and policy rule.

Ask Codex: “Use the dated repair facts and the approved source rules. Tell me which rule applies, which evidence is missing, and what would make you abstain. Then challenge your answer if the bulletin disappears or changes.” Give it fictional data only. Compare its reasoning with the local output and the source texts; an AI explanation is not approval of the catalog or proof of customer coverage. For a future Bedrock trial, choose account-appropriate spending and reserve limits, check current service and Region eligibility, use scoped non-root access, price the whole run through cleanup and record a stop rule. No AWS use is needed here.
