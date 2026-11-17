# Review protective-control coverage across a fictional organization

This local exercise checks whether a supplied control matrix accounts for its declared accounts, Regions and controls. It uses fictional records and Python's standard library. It does not read AWS credentials, contact AWS or change an account.

## Try it

From the repository root, predict which rows need investigation, then run:

```sh
python3 examples/protective-control-review/lab.py
```

The sample declares three accounts, two Regions and five controls. The checker should report a missing web-request control and old sensitive-data evidence in production's west Region, plus an exception that needs an owner and follow-up. It should preserve the development patch exception and its compensating measure instead of silently calling that row compliant. Not-applicable rows need a stated reason.

The script exits with status 1 when review items remain. That is an intentional exercise result. To see how omissions are detected, copy `controls.json` to a temporary file, remove a row, duplicate another row or increase an active observation's age, then pass that file's path to `lab.py`.

## What it teaches and what it cannot prove

The matrix forces a reviewer to name account, Region, control, status and evidence freshness together. It catches missing declarations, duplicate rows, unsupported statuses, stale evidence, unexplained exceptions and unreasoned `not_applicable` entries. These are bookkeeping checks over input supplied by the learner.

The checker cannot retrieve or authenticate an AWS observation, establish that an organization or delegated administrator exists, interpret a Security Hub policy, prove a Config recorder is complete, check the path of a packet, evaluate a WAF rule, verify a Macie sample, or show that a key can decrypt a recovery copy. The fixture treats inputs as fictional and trusted. Its 72-hour freshness limit is an invented teaching threshold, not an AWS guarantee or recommendation. An actual review must use service-specific evidence, precise scope and current documentation.

Do not replace the fixture with account IDs, customer data, credentials, finding exports or production logs. Do not run a paid service to complete this local exercise. Organization-dependent deployment remains design-only; a future live lab would first need a separately authorized sandbox and current scoped cost estimate.
