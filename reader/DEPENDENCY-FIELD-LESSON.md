# A dependency finding is a question about a particular build

Imagine a repair shop replacing a part in the machine that prints customer receipts. A parts catalog says one version may jam. The shop owner still needs to learn which machine has that part, whether it handles customer input, what power it has while running, and whether a replacement prints the same correct receipt. A count of warnings answers none of those questions by itself.

An application has similar parts. A **dependency** is code another package supplies. Some dependencies run in the customer's browser. Others run only while a developer builds, tests or deploys the application. A build-only tool can still matter: it may read source and configuration, write the files visitors receive, or run in a job with cloud authority. Draw the path the package actually takes before calling it harmless or reachable.

## Work through four different observations

| Observation | What it can tell you | What it cannot tell you alone |
| --- | --- | --- |
| Current advisory and lockfile | Which named versions are reported as affected in the recorded dependency tree | Whether that code path executes with a risky input in this application |
| Clean installed tree | Which versions the selected package manager actually places where a caller resolves them | Whether the replacement preserves application behavior |
| Build and runtime path | Which process loads a package, what inputs it sees and what authority that process holds | Whether a hypothetical attack succeeds |
| Focused behavior check | Whether the chosen caller still performs the promised task on stated cases | Whether every case, environment or future update is safe |

Keep the report date, lockfile digest, tool version and command beside the result. Registry advisory status can change after the code is committed. A production-only audit and a full development-tree audit inspect different scopes. A lower count can reflect a changed advisory database, a different command, a removed package or a real repair; compare the trees and the root advisory before attributing the change.

## An override is a request, not a repair

Suppose a top-level package asks for a newer parser, but a bundled tool still declares and resolves an older nested parser. The edited override is a proposal. A successful `npm ci` says the selected installation command completed; it does not prove which copy the vulnerable caller loads or that the builder still works. Inspect the lockfile, the clean installed tree and the exact caller-resolved version. Repeat the audit against that tree. Then run the behavior that the builder or application must preserve. If any of those observations conflict, leave the repair claim open.

Try the [dependency triage exercise](../examples/dependency-triage/README.md) with its fictional report. Record the root advisory, affected dependency path, proposed change, installed-version evidence and one behavior check. Keep its [assessor](../examples/dependency-triage/ASSESSOR.md) closed until after your first answer. The [caller compatibility probe](../examples/dependency-compatibility/README.md) gives a second case in which a declaration and a real caller may differ. These local exercises do not inspect today's AWS account or prove an exploit.

### When the patched part does not fit the selected machine

Imagine a replacement part that fixes a jam but fits the next model of receipt printer. The repair notice is real; installing that part in today's machine without checking its fittings may stop receipts entirely. On October 25, the app's Amplify CLI and output-schema packages selected Zod **3.25.17**. The current [Zod advisory](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5) lists **4.6.6** as patched. Those numbers cross a major-version boundary and the output-schema package declares the older exact peer. A blanket override could make an audit line disappear while breaking schema generation or output parsing. It has not been applied here.

The useful next test is a disposable candidate, not a large malicious input. Inspect the resolved copies and peer constraints, exercise the exact backend generation and CLI operations the project uses, compare generated files with an accepted baseline, then build the frontend. Keep the builder's input and authority narrow while the compatible upstream route is unresolved. The presence of Zod in a development tool does not establish that a stranger can feed the advisory's oversized collection into this project's running website. The [changed Zod case](../examples/dependency-triage/README.md#changed-cases-before-the-assessor) asks you to defend both claims separately. Never run an unbounded memory-exhaustion payload merely to make the lesson vivid.

## Check configuration before declaring a finding reachable

Consider a database driver with an advisory about one optional feature. The driver appearing in a lockfile shows that its version is present. To decide whether the feature matters to a particular importer, trace the importer's configuration, the client call and the negotiated behavior where applicable. A local fake response can test how the importer handles data; it cannot prove a real server handshake used the same settings. The [compatibility probe](../examples/dependency-compatibility/README.md) practices keeping those claims separate.

When a fix changes the importer, test the business promise as well as the package version: does the same input produce the same accepted rows, rejected rows and error receipt? A version number is not a substitute for that result.

## Give the builder only the authority it needs

Before installing packages in a release workflow, list what the installation and build processes can read and write. A static-file builder needs source and permitted browser configuration; it does not need a general AWS deployment role. A separate publisher can receive the reviewed artifact and a scoped, short-lived role after the build and cost review. This arrangement reduces the authority exposed to build tools, but a compromised builder could still put wrong content into an artifact and hash that content itself. Review the source, selected dependencies, emitted files and served customer task as separate evidence.

The [build-trust drill](../examples/frontend-publisher/BUILD-TRUST.md) demonstrates that a digest detects a change **after** hashing but does not judge whether the builder made the correct page. The [field publishing lesson](GITHUB-TO-AMPLIFY-FIELD-LESSON.md) follows the GitHub-to-Amplify authority and cost gates. Neither local drill proves a real GitHub run or an AWS publication.

## Practice the decision before asking AI

Write a one-page record with five rows: affected package and path; current advisory source and observation time; actual caller and input; proposed repair and compatibility test; remaining uncertainty and release owner. First decide whether you would continue a local test, hold a publication, or gather one more read-only fact. Then ask Codex: “Challenge my dependency decision. Which sentence confuses a declared version, installed version, reachable behavior, or customer result? Give the smallest observation that would change it.” Provide sanitized paths and reports, never tokens or account secrets. Check every suggested package or advisory claim against the current upstream source and the actual installed tree.

A useful conclusion names its evidence boundary: “This version is present,” “this caller loaded the replacement in the local fixture,” or “this customer task worked after a reviewed release” are three different statements. The last one requires the actual release and customer-path observation.
