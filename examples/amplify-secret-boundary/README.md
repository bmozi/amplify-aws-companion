# Follow a value until it reaches the visitor

Maya's bakery needs to call a supplier. A teammate names the supplier's private key `VITE_SUPPLIER_KEY` and says the Hosting environment variable is encrypted, so it is safe. Another teammate places the key in `public/partner.json` because the frontend build needs it. Both choices put the value on a path to a visitor's browser. Encryption of a build setting and privacy of a served file are different questions.

This lab uses four **invented markers**, never a real key or account output. Its two tiny Vite builds run in temporary folders. One deliberately places a fictional key in a `VITE_` variable and a second fictional key in a public file. It fetches the resulting JavaScript and file from a loopback HTTP server. The other build has a public destination and a separately named server-only marker; the served files contain the public destination but neither fictional key. The server-only marker's absence from these files is a narrow observation, **not** proof that a deployed function can use a secret safely.

Read [the illustrated lesson](../../reader/BOOK-LOCATORS.md#book-a6882a4f1274431c), predict the four booleans below, then run from the repository root after installing the app's locked dependencies:

```sh
cd app && npm ci --ignore-scripts --no-audit --no-fund && cd ..
python3 examples/amplify-secret-boundary/lab.py
```

The npm step downloads packages and changes only local installation state. The Python step calls the installed Vite 8 CLI, builds two disposable static sites, serves selected files on `127.0.0.1`, inspects the responses and removes its temporary folders. It uses no AWS credentials, backend, secret manager or paid service. The default companion suite leaves this check `not_requested`; `python3 scripts/check-companion.py --app-toolchain` runs it with the other installed-app checks after the app's documented local configuration is present.

| Prediction | What to decide before running |
| --- | --- |
| Unsafe build JavaScript | Will the invented `VITE_` key appear in the bytes a visitor receives? |
| Unsafe build public file | Will a file copied from `public/` be reachable even though it was not referenced by JavaScript? |
| Safe build JavaScript | Will the public destination appear while the server-only marker stays absent? |
| Release after discovery | Would publishing a corrected build alone invalidate a supplier key already exposed by the old one? |

Compare your answer with the [separate assessor](ASSESSOR.md) only after preserving your first attempt. The lab reports booleans and SHA-256 identities, not marker values. Check the actual `lab.py` paths so you know what was built and fetched; a passing self-check does not inspect arbitrary future apps.

## Change one condition

### Follow the value through a local server

The static build answers only where a value lands in visitor files. A second, independent question is what a **server returns** after using a private value. Run `python3 examples/amplify-secret-boundary/server_lab.py` from the repository root. It uses only Python's standard library and a loopback HTTP server; no npm install or AWS access is needed. All callers and the supplier key are invented.

Predict three requests to `/availability/F-42`: a fixture caller, another fixture caller and a missing caller. The normal handler checks the caller, uses its invented server-only key in a simulated supplier step, and returns only `available` or `not allowed`. A deliberately unsafe debug mode adds the key to the authorized response. The script fetches the actual local HTTP responses and reports **booleans**, not the marker value. It also checks its small in-memory event trail. This shows why putting a key on a server is only the beginning: caller authorization, response shaping, error paths, logs and rotation still need review.

The caller check here is a fixed string, **not authentication**. The supplier call is a fixture, **not an integration**. The safe local result does not prove Amplify Gen 2 secret provisioning, IAM, Cognito/AppSync authorization, Lambda behavior, log redaction or a real partner's revocation. For a cloud implementation, require one allowed and one denied request through the actual deployed API, inspect the exact response and logs without publishing the key, and record the secret's environment and rotation owner under the approved run plan.

1. The site is built in this repository's **GitHub manual ZIP workflow**, while an operator changes a variable only in the Amplify Hosting console. Will that value enter the GitHub builder automatically? Identify the build process that would have to receive it and the reviewed input it could change.
2. The supplier key moves to a Gen 2 function using `secret('SUPPLIER_KEY')`. Does this lab prove the function deployment, runtime access, caller authorization or response/log safety? Draw the extra evidence path.
3. A developer renames `VITE_SUPPLIER_KEY` to `SUPPLIER_KEY` but leaves `public/partner.json`. Which served path still leaks? Why is “no `VITE_` prefix” an incomplete audit?
4. The key appeared in yesterday's hosted artifact. Today a clean build replaces it. State the immediate supplier-side action, old-artifact/cache inspection and later evidence needed before calling the exposure contained.
5. The server keeps the key out of the browser build but adds a `debug_supplier_key` field only when the caller is allowed. Is authorization enough to make that response safe? Identify the recipient and the first downloadable response to inspect.
6. The fixture's denied path returns no key. Suppose an exception handler logs the complete supplier request, including the key. Which additional reader now matters, and what real evidence would establish safe logging?

Ask Codex to classify each value as public client configuration, backend-only secret or undecided. Require it to trace **source → builder → artifact → caller** and identify which claim comes from this local build versus current AWS documentation. Give it invented markers only. A model's advice does not inspect your served bytes or revoke a provider key.

[Vite's environment guide](https://vite.dev/guide/env-and-mode) documents client exposure of `VITE_` values. [Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/environment-variables.html) warns against treating build environment variables as secrets. [Amplify Gen 2's function guide](https://docs.amplify.aws/react/build-a-backend/functions/environment-variables-and-secrets/) distinguishes plaintext function environment values from `secret()` references resolved for runtime use. [Sandbox guidance](https://docs.amplify.aws/react/deploy-and-host/sandbox-environments/features/) explains that a sandbox secret and a hosted branch secret are configured separately. None of these sources makes a secret reference an application authorization rule. A live experiment needs a scoped identity, current account plan, whole-run estimate against account-chosen spending and reserve limits, and cleanup plan. This local lab needs none of them.
