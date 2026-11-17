# Configuration release: decide before changing behavior

Design-only companion to [delivery and recovery](../../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d). No commands, credentials or AWS resources are required. These are authored cases, not observations from a deployed AppConfig integration.

Maya promises a ten percent discount on qualifying quotes. Her application reads a discount setting and returns a price. For each case, record your decision, the next evidence you need, a stop condition and the limits of recovery. Write your answers before reading the [assessor notes](ASSESSOR.md).

1. **Valid but wrong.** The schema permits integers from 0 to 50. Revision B sets the discount to zero. A test reports that the configuration validates and the API returns HTTP 200. Should B proceed? Give an expected customer result for a 1,000-cent qualifying quote and a probe that could reject B.
2. **Mixed readers.** One worker reports revision A, another B. A customer accepts a previously issued 900-cent quote while B would produce 1,000 cents. The business promises to honor unexpired quotes. Specify the transaction record and acceptance behavior. Explain why a new configuration deployment alone cannot prove every worker has adopted it.
3. **Quiet alarm.** An operator attaches an error-rate alarm but disables its actions during maintenance. The candidate has no qualifying quote traffic. The deployment dashboard shows no reported customer errors. Identify the two separate evidence gaps and the decision you would make before expanding exposure.
4. **Incompatible recovery.** Old code reads `discount_percent`; new code reads only `discount_basis_points`. The proposed configuration removes the old field. Both code versions still serve traffic. Explain a compatible transition and what must be true before removing the old representation. Is reverting configuration alone sufficient?
5. **Effects already escaped.** A flag starts promotional emails. One hundred jobs are queued and twenty emails have been sent when the flag is disabled. Specify what must be inspected and controlled for queued work, what cannot be unsent, and how you would verify cessation. Do not assume workers reread the flag.
6. **The hidden button.** A premium feature flag hides a button from ordinary users, but a direct API request still performs the premium operation. Identify the failed boundary and describe both allowed and denied checks. Would a faster flag refresh fix it?

Transfer case: replace the discount with a limit on expensive document processing. Explain how per-worker limits, queued work and delayed usage records affect a claimed spending cap. Identify the enforcing control rather than assuming a configuration value is a global hard limit.

Use the [learning record](../../curriculum/LEARNING-RECORD.md) to distinguish your prediction, reasoning and missing implementation evidence. Codex may challenge your answer by changing one assumption, but should not supply the first answer or invent test results. Completion of this worksheet does not prove AWS permissions, propagation timing, alarm behavior, learner mastery or production readiness.
