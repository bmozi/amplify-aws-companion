# Browser application source

This public companion installs a frontend-only dependency tree. It follows the separate frontend-publisher boundary from the book: Vite transforms browser source into static files; it does not compile, typecheck, synthesize or deploy the Amplify backend. The schema type import is erased by bundling. A successful browser bundle does not establish full TypeScript correctness or AWS behavior.

For a local build rehearsal, install with `npm ci --ignore-scripts`, create a temporary `amplify_outputs.json` containing `{}`, then run `npm run build`. The empty configuration is an intentionally non-account build placeholder. Do not host or use that result as an authenticated application. Remove the placeholder and `dist/` after the rehearsal. `npm test` runs a mocked two-user journey; it makes no AWS requests.

An actual configured app needs separately authorized backend outputs and real allowed/forbidden user checks. Its cloud source under `amplify/` is inspection-only here. The public install intentionally omits AWS backend/CDK tooling; see [backend toolchain status](BACKEND-TOOLCHAIN-STATUS.md) for the separate unresolved upstream advisories. Do not add those packages or enable cloud commands merely to make an editor resolve types.
