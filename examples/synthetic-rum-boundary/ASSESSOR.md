# Assessor: three evidence windows

Keep this separate from the learner's first attempt. The fixture is fictional and tests reasoning, not CloudWatch behavior or exam readiness.

## Expected interpretation

| Window | Supported statement | Unsupported shortcut |
| --- | --- | --- |
| A | All five **reported** scripted runs succeeded. Twelve of forty **received** sampled client sessions reported an error (`30%` of that observed sample). Five of seventy stipulated accepted bookings lack completion (`70 − 65`). | “Five green canaries mean customers are fine”; “30% of all visitors failed”; “twelve of two hundred is the true customer error rate”; “the release caused it.” |
| B | Five scripted runs succeeded and all sixty stipulated accepted bookings completed. The independently counted 180 visits produced **no received RUM session**, so client experience in that window is unknown from RUM. | “Zero reports means zero browser errors” or “the complete accepted-work count proves every visiting customer could submit.” |
| C | Two of three reported canary runs succeeded, one reported run failed, and two expected run results are absent. The twenty received RUM sessions reported no error. The accepted-work count cannot establish backlog because completeness is unverified. | “The canary success rate is two of five” without separating absent reports; “zero RUM errors and equal accepted/completed counts prove recovery.” |

None of the windows proves every visitor succeeded. A canary is an intentional test from a selected context. RUM describes received sampled sessions and may miss clients or paths. An accepted-work ledger starts after intake, so it does not count a browser that could not submit. Even a complete ledger must be joined to outcomes and deadlines before declaring the business promise met.

For A, a useful next read-only check compares the erroring sampled sessions by route, version and device with the scripted steps, then inspects the five unfinished accepted requests against their due times and durable completion records. For B, inspect RUM client installation, page selection, permissions and delivery while using another independent customer-path signal; avoid assigning a zero error rate. For C, inspect the missing canary run/step/artifact evidence, and establish whether the accepted-work source captured every eligible request before computing a backlog. These are examples, not the only valid checks. An urgent containment decision can precede full root-cause proof if its target, owner, risk, observation window and reversal are recorded.

In the changed A case, the observed twelve client errors disappear from the supplied evidence; **client experience becomes unknown**, not healthy. The complete accepted-work ledger still shows five unfinished bookings. Five green scripted runs remain limited to their configured route and identity. A strong learner revises only the conclusions affected by changed evidence.

When A instead has zero expected, reported and successful canary runs, there is no scripted journey evidence. The twelve observed client errors and five unfinished accepted bookings are unchanged. Check the intended schedule and its owner before deciding whether the absence is expected or a monitoring failure.

## Design and Codex review criteria

Credit a design that states the specific canary identity and journey, separates scheduled from reported runs, names artifact/permission failure as an alternative to application failure, and chooses RUM collection/sampling with a privacy and cost boundary. The learner should identify URL or free-form fields that could carry customer data, decide notices/consent with the relevant owner, and estimate the full service path using current regional pricing before a live run. No deployment is authorized by this packet. A Codex critique adds value only when its arithmetic and AWS claims are checked against the fixture and current primary documentation.

This fictional exercise does not run AWS Synthetics or CloudWatch RUM, observe actual customer outcomes, or establish current account eligibility or billed costs.
