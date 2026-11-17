# Backend toolchain remains a separate review

The original authoring repository installs Amplify backend/CDK development tools. A November 17, 2026 audit found 49 affected dependency entries (37 high, 11 moderate, one low; no critical). These are dependency-tree entries, not 49 demonstrated exploits. The browser runtime audit reported zero.

A semver-compatible lockfile-only remediation was attempted without --force. It reduced the immediate audit to 45 entries (37 high and eight moderate), but that intermediate npm audit-fix lockfile failed npm ci because of missing peer entries. npm install --package-lock-only repaired lock consistency; the valid synced full-toolchain audit still reported 48 affected entries (37 high and 11 moderate). Those findings remain recorded separately and are not declared fixed. No incompatible dependency override or forced major/downgrade was applied.

Root advisory families include [GraphQL Tools mergeDeep prototype pollution](https://github.com/advisories/GHSA-7mx3-vvmw-hjmv), [Zod oversized-collection memory exhaustion](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5), and [OpenTelemetry baggage allocation](https://github.com/advisories/GHSA-8988-4f7v-96qf), plus glob/minimatch path-processing concerns. Upstream patched versions do not automatically satisfy the older dependency ranges selected by the Amplify toolchain.

The public companion therefore installs only its browser build dependencies. Backend files remain readable specimens, with no supported backend compile, synthesis or deployment path. This boundary removes unused backend tooling from the public installation; it does not repair or conceal the private toolchain's upstream issues. Review and test that toolchain separately before any authorized backend work.
