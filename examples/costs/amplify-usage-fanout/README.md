# Trace one Amplify visit into usage quantities

A person opens the Field Lab, reads notes, saves one, uploads a file or runs the text inspector. The browser makes several requests even though the person experiences one visit. The [diagram](../../../book/figures/amplify-visit-cost-fanout.svg) shows why the static Hosting transfer number is only one part of a run estimate.

Run this local exercise without AWS credentials:

```sh
python3 examples/costs/amplify-usage-fanout/lab.py
python3 examples/costs/amplify-usage-fanout/lab.py --visits 80000
python3 examples/costs/amplify-usage-fanout/test_lab.py
```

The [fictional plan](plan.json) assumes 100 visits, 25 distinct signed-in people, 500,000 hosted bytes per visit, two note lists, one save per four visits, one file upload and one file download per twenty visits, and one text inspection per ten visits, five live-connection minutes per visit and one delivered update per note save. It assumes one DynamoDB read unit per list and one write unit per save. Those last two are **proxies**, not measurements of the generated resolver or proof of DynamoDB billable units. The inspected [browser code](../../../app/src/main.tsx) uses `observeQuery()` for live notes, calls Storage for files (including an initial list and a list after each upload), and makes an authenticated query for the Lambda inspector; the exact service work, retries, object size, transfer direction and free allowances need live evidence.

At 100 visits, the model yields 0.05 GB of Hosting transfer, 235 assumed AppSync operations, 500 connection minutes, 25 delivered updates, 200 assumed DynamoDB read units, 25 write units, five S3 uploads, five S3 reads, 105 S3 lists, 0.005 GB added S3 storage, ten Lambda invocations and 0.00002048 GB of new inspector logs. For the added duration exercise, it assumes 0.25 GB of Lambda memory for 0.25 seconds per inspection, yielding 0.625 GB-seconds; it charges the new inspector log bytes for a full GB-month of retention. These numbers come **only** from the plan's assumptions. The 25 Cognito users are a distinct-user proxy; do not multiply sign-ins into monthly active users. At 80,000 visits, the unchanged half-megabyte assumption yields 40 GB of Hosting transfer. That exceeds both the older 5 GB teaching worksheet and the separately revised smoke record's 0.15 GB forecast. Neither describes that audience. The 25-user input also becomes implausible at that scale; update the whole plan, not just one number.

AWS describes [`observeQuery` as a live feed](https://docs.amplify.aws/react/frontend/data/subscribe-data/); the exact connection and message billing quantities still require observation. The original quantity model deliberately contains no prices. To form a real estimate, inspect the exact backend and retained resources, establish a bounded audience and action mix, check current regional price units, include omitted paths and multiply the quantities. AppSync may meter GraphQL operations, real-time messages and connection minutes; DynamoDB has read/write and storage dimensions; S3 has storage and request dimensions; Lambda has requests and duration; CloudWatch Logs has ingestion and storage dimensions. The account's actual configured options decide which apply. See the official [Amplify](https://aws.amazon.com/amplify/pricing/), [AppSync](https://aws.amazon.com/appsync/pricing/), [DynamoDB](https://aws.amazon.com/dynamodb/pricing/), [S3](https://aws.amazon.com/s3/pricing/), [Lambda](https://aws.amazon.com/lambda/pricing/), [Cognito](https://aws.amazon.com/cognito/pricing/) and [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/) pages for current meters and rates.

Try three changes before reading the [assessor notes](ASSESSOR.md): (1) change visits to 80,000; identify every assumption that now needs reconsideration, not only Hosting transfer; (2) double `lists_per_visit`; predict which model quantities change and which do not; (3) remove `log_bytes_per_inspection`; explain why the lab refuses a missing assumption. Then explain what the model omits: existing resources, retries, exact real-time subscription behavior, storage retention, unlisted network paths, GitHub Actions, current credits and delayed billing. The [smoke publisher record](../publisher-smoke-run-estimate.json) remains `review_needed`; do not paste fictional quantities into it as if they were reviewed account evidence.

Ask Codex to trace one UI action to the source call, list uncertain downstream meters and challenge the audience forecast. Have it label source evidence, model assumption and live observation separately. A fluent estimate is not a price check or billing result.

### Keep the proposed smoke audience on one worksheet

The earlier 100-visit teaching case uses half a megabyte of hosted files per visit. The pending publisher smoke record uses **1.5 MB per visit**, so copying the earlier Hosting line into its backend discussion mixes two different crowds. The [smoke-plan fixture](smoke-plan.json) changes that one Hosting input while keeping the fictional action mix visible. Run the [bridge](smoke_bridge.py) and its [changed-case checks](test_smoke_bridge.py) locally:

```sh
python3 examples/costs/amplify-usage-fanout/smoke_bridge.py
python3 -m unittest discover -s examples/costs/amplify-usage-fanout -p 'test_*.py' -q
```

Imagine pricing the food for 100 guests after measuring the room rental. The room bill is real arithmetic for the stated assumption, but the food count still depends on who arrives and what they order. Here the script groups selected **pre-allowance** public-rate lines for Hosting, Cognito, AppSync, DynamoDB, S3, Lambda and CloudWatch under the same 100-visit assumption. It outputs **USD 0.3994908960875** across those selected lines; USD 0.375 of that is a deliberately conservative Cognito Essentials proxy for 25 distinct users before any allowance. The network group remains **unknown**, not a false zero. Retained resources, actual resolver work, response transfer, authentication tier, retries, logs, optional paid features, credit terms, GitHub billing and cleanup still need review. The output has no `reviewed` status and cannot be copied into the [pending publisher record](../publisher-smoke-run-estimate.json).

### Compare the worksheet with the app's source

The cost plan says **0.25 GB of Lambda memory** and an average **1,000,000-byte file**. Those are invented workload inputs. The checked-in [function definition](../../../app/amplify/functions/inspect/resource.ts) says `memoryMB: 128`, or 0.125 GB using 1,024 MB per GB; the [browser](../../../app/src/main.tsx) refuses a file larger than 5 MiB. A maximum file size is not an average. The source setting is also not proof that the deployed Lambda has that setting. Run the narrow [source-assumption audit](source_assumption_audit.py):

```sh
python3 examples/costs/amplify-usage-fanout/source_assumption_audit.py
python3 -m unittest discover -s examples/costs/amplify-usage-fanout -p 'test_*.py' -q
```

For the fixture's ten inspections at an assumed 0.25 second each, substituting the checked-in 128 MB setting gives **0.3125 GB-seconds**, compared with the plan's **0.625 GB-seconds**. This is a changed calculation, not a measured duration. Five uploads of 1,000,000 bytes add **0.005 decimal GB** in the plan; if each instead reached the browser's 5 MiB cap, they would add **0.0262144 decimal GB**. The cap case is a stress question, not a prediction. The audit intentionally refuses to identify a changed setting it cannot recognize and never approves the publisher estimate. It reads two source files as text and cannot inspect a generated stack, deployed configuration, actual network calls or account bill.

**Changed case:** raise the function to 512 MB and the browser cap to 10 MiB in a copied source tree, without changing the visitor actions. Which two quantities rise? Which planned 0.25-second and one-megabyte assumptions could still be wrong? Now change only the worksheet memory to 0.125 GB; why does agreement with source still leave the publisher record pending? Ask Codex to identify the exact source line for each claim, then to name the deployed-resource and measured-use receipts it lacks. Check its answer against the [assessor](ASSESSOR.md) and the source, not against its confidence.

Before opening the [assessor](ASSESSOR.md), change the copied plan back to 500,000 Hosting bytes per visit. Predict the bridge's response and explain why the new subtotal cannot be accepted for the 1.5 MB smoke record. Then change the public Hosting rate in a copied price snapshot; explain why a rate that no longer matches the pending worksheet must stop the bridge. Ask Codex to identify one service action the fixture did not count, then check that claim against `app/src/main.tsx` and the generated backend before a live estimate. A passing script only reconciles selected assumed rows; it does not verify an account or authorize publication.


## Put dated public rates beside the fictional quantities

Think of this as pricing fifteen items on a grocery list while knowing that the cart still contains uncounted items. The [October 24, 2026 Ohio snapshot](public-prices-us-east-2.json) records 18 selected on-demand meters, their units and SKU/tier identities, and SHA-256 digests of seven [public AWS offer files](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api-fetching-price-list-files-manually.html). The Lambda offer file changed since October 21; the selected rates did not. The [local price exercise](public_price_lab.py) uses fifteen of those rates. It needs no AWS credentials:

```sh
python3 examples/costs/amplify-usage-fanout/public_price_lab.py
python3 examples/costs/amplify-usage-fanout/public_price_lab.py --visits 80000
python3 examples/costs/amplify-usage-fanout/public_price_lab.py --plan examples/costs/amplify-usage-fanout/publisher-audience-plan.json
python3 -m unittest discover -s examples/costs/amplify-usage-fanout -p 'test_*.py' -q
```

At 100 fictional visits, the **selected, pre-allowance subtotal is USD 0.384490896087500000**. This is arithmetic over assumed quantities, not the price of running Field Lab. In particular, the calculation applies a public Cognito Essentials rate to 25 proxy users **before** the service's free tier; it does not know whether the account's actual pool is Essentials or whether an allowance applies. The 0.01 GB-month Hosting storage input is also an invented [scenario](public-price-scenario.json). The three added lines price five assumed S3 reads, 0.625 Lambda GB-seconds and a full month of the new inspector logs. They do not measure real file access, function duration or log retention. The output still enumerates eleven missing whole-run categories, including actual resolver work, outbound traffic, retained backend data, optional WAF/cache, other resources, current account credits and GitHub billing. At 80,000 visits the Hosting proxy rises to 40 GB, exceeding the old 5 GB assumption, but the new subtotal remains incomplete and the 25-user assumption needs revision. Never use either result to change the [smoke publisher record](../publisher-smoke-run-estimate.json) from `review_needed`.

The snapshot is deliberately dated because public prices and tiers can change. To compare it with today's public Ohio offer files, run `python3 examples/costs/amplify-usage-fanout/refresh_public_prices.py --check` with network access; this reads public files only and fails if their bytes or selected rates differ. `--write` deliberately replaces the snapshot for **review** after a change; inspect the SKU, tier, unit, rate and omitted meters before using it in a lesson. AWS [explains the bulk file schema](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/reading-service-price-list-file-for-services.html). A matching snapshot proves the selected public file bytes, not the account's credit eligibility or deployed configuration. Before any live run, verify the exact generated resources, expected traffic and retention, current account terms and a reviewed full-run estimate with contingency and teardown.

### Keep the Hosting and backend crowds together

Use the separate [10,000-visit plan](publisher-audience-plan.json) to practice a *single* audience: 10,000 visits at 500,000 hosted bytes each give 5 GB Hosting transfer. Suppose 2,500 of those visitors sign in during the month, four visits per person on average, and keep the small plan's action rates. The fifteen selected public-rate lines total **USD 38.4263196087500000 before allowances**. Cognito Essentials alone contributes `2,500 × $0.015 = $37.50` under that deliberately conservative calculation. Choose a hypothetical whole-run limit of USD 30: this selected subtotal already exceeds it, so the plan must stop. Now choose USD 50: the selected subtotal fits, but missing meters and contingency still prevent a go decision. The limit belongs to the reader's scenario; neither amount is an AWS spending cap. Use the [three-price decision exercise](../reader-budget-decision/README.md) to test a reader-chosen run limit, credit reserve and gross-budget margin separately. The [older 5 GB worksheet](../publisher-run-estimate.json) remains `review_needed` and is not selectable by the live workflow; this fictional plan cannot authorize it. The separate [100-visit smoke record](../publisher-smoke-run-estimate.json) also needs its own whole-run review.

That $37.50 is **not a predicted Cognito bill**. [AWS Cognito pricing](https://aws.amazon.com/cognito/pricing/) currently describes a 10,000-MAU free tier for eligible direct/social sign-ins on Lite and Essentials, but the actual pool tier, account or organization allowance, sign-in path and other charges have not been checked here. The model assumes all 500 uploaded 1 MB files occupy a full month of storage; gradual uploads would change that average. The code prices assumed S3 GETs, Lambda duration and new-log retention; it does not price actual download transfer, measured runtime, all retained logs or generated GraphQL work. A learner should change the signed-in share, action mix and duration, then compare the result with a *verified* account-aware estimate; they should never copy this selected subtotal into the reviewed publisher gate. Ask Codex to point to each browser call, separate user assumptions from measured service meters, and identify which omitted item could reverse the decision.

### Check the page files before accepting a bytes-per-visit guess

The pending smoke worksheet now assumes **1,500,000 hosted bytes per visit**. Imagine pricing the delivery of a book by guessing its weight before putting it on a scale. The guess helps with planning, but the actual package gives a better starting point. Build the current frontend, then measure the HTML and the script/style files it directly names:

```sh
npm --prefix app run build
python3 examples/costs/amplify-usage-fanout/bundle_size.py --dist app/dist
python3 -m unittest discover -s examples/costs/amplify-usage-fanout -p 'test_*.py' -q
```

The [script](bundle_size.py) records each entry file's SHA-256, raw byte count and size after **local gzip** compression. It also counts all static files, including later routes that the entry page does not name. It refuses an external, missing or escaping entry reference instead of silently leaving a file out; the [focused tests](test_bundle_size.py) show that adding an unlinked later page changes the all-file total but not the entry total. On the October 25 build, the three entry files totaled **1,230,970 raw bytes** or **283,366 locally gzipped bytes**; all **20 static files** totaled **1,344,387 raw bytes**. The earlier 500,000-byte guess was below the complete raw set. The pending smoke worksheet now rounds up to 1,500,000 bytes per visit; the publisher preflight rejects a reviewed figure below the exact built ZIP's raw byte count. Neither local measurement proves how many bytes Amplify actually serves: compression negotiation, cache hits, later pages and API responses all change the path. A public visitor count is also a forecast, not an enforced cap. Keep the smoke estimate in `review_needed` until the exact deployed bundle, service transfer, audience, backend work, retained resources and current account room are reviewed together.

**Changed case:** add a file to a copied `dist` and link it from the copied `index.html`; rerun the measurement. Which digest and total change? Then point the reference to an external CDN. Explain why the local tool refuses to turn that unknown transfer into zero. Ask Codex to identify every additional request the signed-in screen can make, then check its answer against `app/src/main.tsx` and a future browser network trace. A local file size is evidence about local bytes, not a cloud bill.

### Observe a local browser visit

The ZIP rule is intentionally cautious. A visitor does not necessarily fetch every file in the ZIP. A browser may request only the entry files, receive gzip-compressed responses and reuse files it already has. Run a real **local Chrome** entry visit and same-tab reload against the built static publisher:

```sh
node examples/costs/amplify-usage-fanout/browser_transfer_probe.mjs --dist app/frontend-publisher/dist
```

The probe starts a localhost server and a temporary Chrome profile. It enables the page's JavaScript so its entry assets load, but blocks nonlocal page requests in DevTools and routes other outbound HTTP traffic to a dead local proxy. It deletes the temporary profile afterward. The output lists local paths, response status, response **body** bytes and browser cache events; it does not save request bodies or client configuration. It does not require AWS credentials. Check that the reported `dist` and file set match the build you intend to study.

In the October 25 local build, the **first** entry visit received 284,455 response-body bytes for HTML, CSS and JavaScript under this server's gzip policy. A same-tab reload made one local request: `index.html` returned `304`, while two assets were served from cache, so the recorded response-body total was zero. A `304` still transfers headers. The raw **all-file** set is 1,344,387 bytes. These are three different measurements with different boundaries; none is the Amplify Hosting bill or a safe ceiling for a public audience. The browser did not complete a signed-in customer journey or measure API transfer. A different route, cache state, server configuration or visitor can change every number.

Before reading the [assessor](ASSESSOR.md), predict what happens if you link a new stylesheet from a copied `dist/index.html`, then rerun the probe. Explain why the first response-body total should rise while the same-tab reload can remain small. Decide whether that observation justifies reducing the pending 1,500,000-byte planning input. Name the evidence you would need from the **actual** hosted branch and backend before changing it. Ask Codex to separate the exact artifact policy, this local browser observation, the audience forecast and later billed AWS usage.
