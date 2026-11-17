# A small workshop for the static website

This directory holds a **separate locked browser-build toolchain** for the gated GitHub publisher. It does not replace `app/package.json`: the larger app tree still supports Amplify backend generation and TypeScript checking. The publisher build intentionally contains only React, Amplify browser libraries, Vite and its React plugin. It cannot deploy or verify the backend.

The [workflow](../../examples/github-workflows/amplify-publish.yml) performs three jobs: typecheck with the full tree and a non-account `{}` output placeholder; build the browser files here without AWS credentials; then give the ZIP to a separate narrowly scoped publisher job. It requires a manual `yes` on `main` and an enabled repository variable. A push alone does not run it.

To reproduce the browser build locally from the repository root with a **previously obtained, non-credential** `app/amplify_outputs.json`:

```sh
npm ci --ignore-scripts --prefix app/frontend-publisher
npm audit --audit-level=moderate --prefix app/frontend-publisher
python3 scripts/stage-frontend-publisher.py
cp app/amplify_outputs.json app/frontend-publisher/amplify_outputs.json
npm run build --prefix app/frontend-publisher
```

The install and audit run before the browser configuration is copied. `src/`, `public/`, `index.html`, `vite.config.ts`, the copied output JSON, `node_modules/` and `dist/` are ignored generated inputs/results here. Do not commit the copied output JSON. The staging script refuses symlink source and destination entries; it does not prove source provenance or prevent a malicious reviewed-main commit from changing the build script.

To see why the [publisher estimate](../../scripts/publisher-run-estimate.py) now binds the browser configuration as well as the `app/` tree, run the separate [built-destination local lab](../../examples/frontend-publisher/config-build-lab.py):

```sh
python3 examples/frontend-publisher/config-build-lab.py
```

It uses the already installed publisher dependencies and copies the real browser source into a temporary directory. Three builds use invented destinations: practice with practice configuration, practice with a copied live destination, and live with that same live configuration. The second build changes both the configuration digest and site files but fails the practice destination check; the third has the same files and passes only because its approved target is live. This is a narrow check for synthetic host markers in JavaScript, not a complete route inventory. It never uses `app/amplify_outputs.json` or AWS. In the actual disabled GitHub workflow, the build checks the configuration fingerprint before and after compilation, writes `config.sha256` into the ZIP, and the publisher compares it with the human-reviewed record before requesting an AWS role. A matching fingerprint identifies bytes; it cannot prove that the selected backend, authorization, forecast or customer behavior is right.

The full companion checker runs this optional exercise with `python3 scripts/check-companion.py --frontend-publisher-toolchain` when this directory's locked dependencies are installed. Its separate `--app-toolchain` option continues to cover the larger app tree and does not require this publisher install.

On October 19, 2026, a local `npm ci --ignore-scripts` installed 177 packages. `npm audit` reported zero findings for this **publisher lockfile**, while the separate full development lockfile still reported 44 affected entries. The publisher's 20 generated files had byte-for-byte matching SHA-256 hashes with the full app build on the same macOS host and client configuration. Neither audit count proves exploitability or future safety. The GitHub Ubuntu workflow has not run; no AWS resource, role or hosting publication was tested by this comparison. Repeat the audit, file comparison and customer-path checks after any source or dependency change.
