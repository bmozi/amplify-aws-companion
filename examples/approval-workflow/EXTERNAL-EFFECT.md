# After approval, did the publisher actually do it?

Maya's two reviewers approve the same fictional price-list revision for the training site. A workflow admits that action, but approval does not place bytes on a website. This standard-library exercise crosses a second local transaction boundary so a lost reply can be observed rather than explained away.

Before running, predict four states: no reviews; two matching reviews and an admitted action; provider commit with a lost reply; successful matching provider lookup. Then run without Python optimization from the repository root:

```sh
python3 examples/approval-workflow/external_effect_lab.py
python3 -m unittest discover -s examples/approval-workflow -p 'test_external_effect_lab.py'
```

The drill imports the existing [two-reviewer policy](TWO-REVIEWER-REVIEW.md). Its first SQLite database holds the reviewed action, current fixture eligibility, distinct matching reviews, admission and a stable `publish:<action>:<revision>:<digest>` dispatch identity. The second SQLite database represents a publisher. `publish()` commits a synthetic effect there, then deliberately loses its reply. Local state becomes `unknown`; the provider already has one effect. `reconcile()` reads by that same operation identity and confirms only a matching digest, destination, artifact and receipt. Repeating the same provider call yields the same receipt and one effect row. Reusing the operation ID with changed content is rejected.

Five focused tests check lost reply and replay, admission and exact-action binding, a changed payload under an old key, missing or mismatched provider evidence, and a matching digest with the wrong target. The last is a negative control: a digest in one row cannot excuse a wrong published destination in another. Each test uses temporary files and removes them. The scripted demonstration also refuses dispatch before admission.

For transfer, draw a line between the workflow and the provider. Move the failure to each side of the line: before provider commit, after commit but before reply, and after reply but before local receipt. Specify which observation permits `confirmed`, which remains `unknown`, and whether retrying the **same** operation ID is supported by the chosen provider. If there is no reliable provider lookup or idempotency guarantee, do not translate absence from one read into proof of failure or promise exactly-once effects. Define an investigation and corrective-action owner.

Ask Codex: “Invent a retry path that would publish twice despite two valid reviews. Show the operation IDs and provider observations. Then propose an invariant and a negative test.” Check its answer against the actual local rows, not just the names of workflow states.

This is a two-database **local simulation**, not an HTTP integration, AWS service, authenticated reviewer, real website, provider guarantee or customer-visible acceptance test. The receipt hash is a deterministic fixture value, not a signed or externally authenticated statement. The two databases are not atomically committed together. The simulated provider retains idempotency keys forever; real retention and consistency must be verified for a selected API. No cloud resource or trial credit is used. A future live experiment needs scoped identity, a reviewed whole-run estimate and cleanup. Choose whole-run spending and reserve limits for the account you will use.
