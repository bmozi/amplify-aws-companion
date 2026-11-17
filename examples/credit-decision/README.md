# One green balance, eight different decisions

Maya's fictional Free-plan account shows USD 81 in remaining credits. She chooses a USD 75 reserve for later work and a USD 10 maximum estimate for one practice run. A proposed USD 3 Amplify run leaves USD 3 **above** her chosen reserve. These values are invented; a reader must choose limits for their own account and credit terms. Subtract with the [local calculator](lab.py). The arithmetic is necessary but insufficient: plan state, individual credit terms, service access, the full set of charges, concurrent work, identity and teardown are separate questions. See [Unit 34's worked lesson](../../reader/BOOK-LOCATORS.md#book-537eaee737885382) and [the four-gate figure](../../book/figures/credit-publication-gates.svg).

Before running the program, write an answer for each change below. Say **hold** or **candidate for separate live review**, name the first missing or failed condition, and state what observation would settle it. Do not call the latter decision permission to deploy.

| Case | Changed fact | What to investigate |
| --- | --- | --- |
| A | The plan is active; its selected services and credit terms were reviewed, the full estimate is USD 3, no other lab is active, and Maya has a scoped non-root identity and cleanup owner. | Which live facts still need independent verification? |
| B | The USD 81 badge is unchanged, but no one reviewed individual credit terms for Hosting and backend meters. | Does a balance imply applicability? |
| C | The proposed service has not been confirmed available on the Free plan. | Would a large credit balance make it available? |
| D | The Free plan ends before the planned experiment ends. | Which date governs the decision? |
| E | Another experiment is already active. | Can both runs claim the same headroom? |
| F | The only current execution identity is root. | Does a correct price authorize this identity? |
| G | The reported balance is USD 77; the same USD 3 estimate would cross Maya's chosen USD 75 reserve. | What is the exact headroom? |
| H | The run has no cleanup owner. | What could remain after the app work stops? |

Run from the repository root:

```sh
python3 examples/credit-decision/lab.py
python3 -m unittest discover -s examples/credit-decision -p 'test_*.py'
```

The script uses fixed invented observations and `Decimal` arithmetic. Change `spending_limit_usd` or `reserve_usd` in a copy of the case to test your own proposed rule. Its strongest output says only `candidate_for_separate_live_review`. It **does not** read AWS, authenticate a credit listing, decide actual product eligibility, estimate a real application, reserve credits across machines, restrict requests, cap spending, or remove resources. The focused tests check the favorable case, independent denial conditions, simultaneous reasons, changed limits, invalid input and expiration exactly at the run end. Read [assessor reasoning](ASSESSOR.md) after your attempt.

For a real proposed run, use the [cost-and-credit field lesson](../../reader/COST-AND-CREDIT-FIELD-LESSON.md) to plan the whole run. The [read-only account preflight](../../scripts/publisher-account-preflight.py) is this project's owner-side example, not a portable approval command. Review current plan state and individual credits against the exact service and Region, identify every applicable cost meter and retained resource, and choose a whole-run limit and reserve for that account. The current account has not been refreshed by this fictional exercise. The owner-side per-credit receipt remains private; do not paste account identifiers or credit IDs into public learner work. AWS documents [Free-plan access](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html) separately from [the per-credit fields returned by GetCredits](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_billing_GetCredits.html).

Ask Codex to review your answer in two passes. First, have it name any condition you inferred from the balance that the packet did not supply. Second, have it propose one changed fact that reverses your answer. Check its arithmetic with the script and its AWS-specific claims against the cited AWS pages. Record your first answer and AI-assisted revision separately; this pack has not been tested with independent learners.
