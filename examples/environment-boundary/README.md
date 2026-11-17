# Different website names can lead to the same backend

Maya's practice site has a bright TEST banner. A synthetic booking still appears in the live schedule. The banner and hosting URL describe the storefront; the browser's connection configuration decides which identity, API and file destinations it reaches. [Amplify's generated client outputs](https://docs.amplify.aws/react/reference/amplify_outputs/) include backend connection details. [Amplify also documents deliberately sharing backend resources across branches](https://docs.amplify.aws/react/deploy-and-host/amplify-hosting/share-resources/).

This cloud-free exercise uses **fictional, schema-shaped** `amplify_outputs.json` values, not a deployed output file. The separate notification destination is an invented integration inventory; it is not a standard Amplify outputs field. First draw the destinations for three frontend names: `practice`, `preview` and `live`. The approved fictional plan deliberately points `preview` at the `practice` backend. Explain what a preview tester can change in practice data before treating that preview as isolated.

Before running, predict three findings:

1. All three frontend URLs differ; preview and practice use the same Auth user pool, data endpoint, file bucket and notification substitute. Is that an accidental leak or a declared shared dependency? Is preview isolated?
2. Practice keeps its URL and TEST banner but its entire client outputs and notification target are copied from live. Which paths lead to live resources?
3. Practice has its own identity and files, but one data endpoint is copied from live. Why would checking only sign-in and file storage miss the error?

Write your answers, then run from the repository root without Python optimization:

```sh
python3 examples/environment-boundary/lab.py
python3 -m unittest discover -s examples/environment-boundary -p 'test_*.py'
```

The program compares each supplied bundle with a separately supplied approved destination map. It checks an Auth user-pool ID and client ID, Data endpoint URL and default authorization mode, Storage bucket name and invented notification target; it also reports cross-frontend sharing. Five tests cover declared preview sharing, copied live configuration, a single live data endpoint inside a mixed bundle, changed client/auth-mode settings, and a missing destination plus an undeclared frontend. Read the [assessor reasoning](ASSESSOR.md) after your attempt.

## Inspect a real local address book without publishing its identifiers

The fictional bundle teaches the two-arrow idea. The [read-only inspector](inspect_outputs.py) takes the next step: it parses an actual Gen 2 `amplify_outputs.json` for **this Field Lab's** Auth, Data and Storage categories. It reports the file's SHA-256, schema version, Regions, selected authorization settings and whether required fields are present. It does not print user-pool IDs, API URLs, bucket names or their values. With `--compare`, it reports which destinations match another outputs file. A preview and practice file with the same Data destination are sharing that back room, even if their website URLs differ.

From the repository root, after obtaining the intended file through the documented backend lifecycle, run:

```sh
python3 examples/environment-boundary/inspect_outputs.py app/amplify_outputs.json
python3 examples/environment-boundary/inspect_outputs.py /PATH/TO/preview_outputs.json --compare /PATH/TO/practice_outputs.json
```

The second command is optional; do not invent or download another environment merely to run it. If a separately reviewed release record already names the exact expected file digest, pass `--expected-sha256` with that **recorded** digest. A mismatch exits 1. A missing required Field Lab field, malformed JSON or unsupported major version exits 2. Do not generate the expected digest from the same unreviewed file and call that approval.

Predict first: if only Data differs, can the two pages still share a Cognito user pool? If all selected fields match, have you proved the pages are served from the same branch? If the Regions differ, is it necessarily a mistake? The assessor explains the limits. AWS [defines outputs as generated client configuration](https://docs.amplify.aws/react/reference/amplify_outputs/) and [documents intentional branch resource sharing](https://docs.amplify.aws/react/deploy-and-host/amplify-hosting/share-resources/). The inspector understands selected major-version-1 fields; it is not full schema validation. Review custom outputs and other runtime configuration separately. Even a matching digest cannot identify a live stack, prove current permissions or data isolation, establish served browser bytes, or price the resources. The local command makes no AWS call.

For transfer, add a fourth frontend whose approved plan shares identity with practice but has separate data and files. Explain the user experience, what can still be shared through sign-in, and which actual allowed and denied requests a future cloud test must make. Ask Codex to produce a destination map from a fictional release packet, then hide one connection in a separate runtime setting and see whether its proposed review notices the omission.

When the locked frontend publisher dependencies are installed, continue with the [built-browser drill](../frontend-publisher/config-build-lab.py). Predict whether a practice URL with copied live configuration passes its approved plan. Compare the copied build with the valid live build: identical site bytes can be wrong for one target and right for another. The drill searches only invented host markers in generated JavaScript; ask Codex what destination channels that check could miss, then inspect the build input paths before accepting its answer.

## Follow this local file into this local browser build

The source file is like the address book on Maya's desk. The website build makes a travel copy for the browser. A correct desk copy does not prove that the travel copy has the same addresses. The [built-output audit](audit_built_outputs.py) compares selected literal Auth, Data and Storage values from a locally reviewed outputs file with local built JavaScript. It prints field names, booleans and hashes, not the destination values. First predict what a missing Data address would mean, then run:

```sh
npm run build --prefix app
python3 examples/environment-boundary/audit_built_outputs.py app/amplify_outputs.json app/dist
```

Use `--forbid-outputs /PATH/TO/separately-reviewed-other_outputs.json` only when another real environment file is available and its distinct destinations must be absent from this build. A value deliberately shared by both files is reported as shared, not forbidden. Missing selected values or the presence of a distinct forbidden value exits 1; an unreadable or invalid input exits 2. The optional file is not an approval record: determine the intended environment, owner and revision separately. Four local tests cover a correct build, missing/copied destination, deliberate sharing and a misleading source map. The check reads `.js` files, not `.js.map` files, and has a 32 MiB inspection limit.

A passing scan means only that the selected literal strings appear somewhere in the local JavaScript files. It does **not** prove that the page loads those files, that the strings are used by `Amplify.configure`, that custom/runtime destinations are absent, that a host serves these bytes, or that the backend allows only intended requests. A build can also transform a value so a literal scan fails even when a connection works. Record the build's identity and source revision, review all destination channels and later verify actual served bytes and allowed/denied requests under the scoped, cost-reviewed cloud path. Ask Codex to find a counterexample where this scan passes but a page still reaches an unintended destination.

## Which JavaScript does the local page actually serve?

Imagine two travel copies of Maya's address book in the build folder. One has the right practice address but is left in a drawer. The page names the other copy, which points to live. Searching the whole drawer finds the right address and reports green; following the page's actual script reference reaches the wrong one.

After the local build above, predict whether a folder scan can pass in that situation. Then run:

```sh
python3 examples/environment-boundary/served_entry_lab.py app/amplify_outputs.json app/dist
python3 -m unittest discover -s examples/environment-boundary -p 'test_*.py' -v
```

The new checker starts a static server bound only to `127.0.0.1`, requests its `index.html`, follows the page's module-script entry paths and compares each returned response with the matching local build file. It reports hashes and selected destination-field booleans without printing the identifiers. A test places all approved values in an **unused** JavaScript file while the served entry lacks them: the old whole-folder scan passes, and this check fails. Another test changes the served response after reading the file and catches the byte mismatch. An external script path is rejected rather than silently treated as part of the local build.

This is a local served-entry check, not a browser execution trace. It does not follow imports or dynamic chunks, observe `Amplify.configure` at runtime, inspect custom settings, verify a real Hosting branch or test backend permission. A matching local response still needs an approved build identity and actual allowed/denied requests before anyone claims environment isolation. Ask Codex to name one value that could arrive at runtime outside the module entry, then point to the source or network observation that would confirm it. Compare your answer with the [assessor](ASSESSOR.md).

`checked_fields_match_supplied_plan` means only that the selected synthetic fields match the synthetic plan. It does not audit every possible output or custom configuration, authenticate the plan, prove what JavaScript was served to a browser, inspect a live backend, test IAM or application authorization, or ensure notification/payment effects are isolated. Do not paste actual account IDs, bucket names, tokens or generated live outputs into this exercise. The personal AWS account is untouched; any later cloud verification needs scoped non-root access, a conservative whole-run estimate, an account-chosen credit reserve and cleanup.
