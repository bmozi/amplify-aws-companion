# Check a dependency repair at its caller

This optional local check needs the app's locked Node dependencies already installed. It does not install packages, load AWS credentials or call AWS. From the repository root:

```sh
node examples/dependency-compatibility/check.cjs app
```

The check resolves the Relay compiler through the actual GraphQL optimizer dependency, then resolves Immutable from that compiler. This matters because the same installation also has a newer compiler using a separate Immutable 5.x copy. Checking whichever package happens to be at the top level can answer the wrong question.

It also compares that resolved dependency's version with its entry in the supplied app's lockfile. A mismatch fails before the query cases, so a stale installation cannot silently stand in for the selected version. This version comparison does not verify all installed bytes against registry integrity hashes. From the repository root, run `python3 scripts/check-companion.py --app-toolchain` to include this probe and the app build in the standard checkout report. First install the locked app dependencies with `npm ci --ignore-scripts --no-fund --no-audit` inside `app/`, and provide a separately reviewed `app/amplify_outputs.json` as described by the [first Amplify application lesson](../../reader/BOOK-LOCATORS.md#book-e8d9fb108293da29). The command builds locally; it neither deploys nor verifies the backend referenced by that file.

Five fictional queries cover fragment expansion and duplicate fields, an alias with variables, an included field, an excluded field and a missing record. The check runs both optimizer fragment modes. It executes original and optimized operations against an in-memory GraphQL schema and compares both with hand-authored expected results. It also requires rejection of a nonexistent field. No database, server or customer data is involved.

When fragments are requested, the optimizer returns reusable fragment documents separately from inlined operations. The check executes the operations; concatenating every returned fragment into a request creates an unused-fragment validation error. This was caught while developing the probe against the original dependency version and corrected before comparing versions.

The October 18 repair kept Relay compiler 12.0.0 and scoped its Immutable dependency to 3.8.4. The same cases passed with the original 3.7.6 and the patched dependency. That supplies bounded compatibility evidence. It does not test all generator features, the complete Amplify CLI, vulnerability exploitability, cloud permissions or deployed behavior. The checker is optional because the default Python companion suite does not require installing the large app toolchain.

Before looking at the output, predict the result of the query with `show: false`. Then change the expected title in a disposable copy of the checker and confirm that it fails: an optimizer that silently changes an answer must not pass simply because it emits valid GraphQL. Restore the copy afterward.

Ask Codex to trace a different advisory from its direct dependency to its caller. Require version and path evidence, a proposed bounded repair, compatibility checks and a list of untested behavior. A lower advisory count is evidence about the registry's findings, not proof of a safe application.


## Lodash at two legacy helper callers

The main `check.cjs` command also runs [check-lodash.cjs](check-lodash.cjs). It resolves the helper directly and through the older visitor package, then compares each caller's loaded Lodash version with its lockfile location. The supplied app path is canonicalized so filesystem aliases do not produce false version mismatches.

For each helper, three hand-authored expectations check the generated parent-type signature: two nested required fields survive their merge, a field without requirements retains only its key, and disabled federation leaves the signature unchanged. These checks passed with Lodash 4.17.23 and 4.18.1. A disposable negative-control copy that omitted one required field from the expected signature failed. They test compatibility at the observed merge caller, not every Lodash API, complete model generation, the security advisory's exploitation conditions or deployed behavior.

Predict why a newer top-level dependency can coexist with an older caller-resolved copy. Then explain why both an installation command's successful exit and a passing fixture can still be insufficient: the former needs version verification, while the latter only covers the supplied cases. The [dependency field lesson](../../reader/DEPENDENCY-FIELD-LESSON.md) explains how to separate the installed copy, caller path and repair evidence.


## CSV at the SQL-schema importer

The main checker also runs [check-csv.cjs](check-csv.cjs). It resolves the parser from Amplify's actual MySQL schema-string adapter and compares the installed version with the selected lock entry. The probe needs the locked app dependencies; it opens no database connection and makes no AWS call.

Predict how a default containing both a comma and a quote will survive CSV parsing, and how `NULL` differs from the ordinary text default. The fixture imports two tables with three fields in one of them. It checks quoted punctuation, a multiline value, LF/CRLF row separators, null markers, field ordering, length, primary key and model count. Three invalid inputs must fail. The same expectations passed before and after the scoped 5.6.0-to-7.0.3 repair. A disposable copy expecting only one table failed.

This is bounded compatibility at the MySQL string-adapter path, not a connection test, all-dialect importer test, security exploit demonstration or full CLI certification. Ask Codex to identify an untested representation and trace it through the actual adapter before adding a case. Keep advisory evidence and compatibility evidence separate: fewer registry findings cannot establish that every schema still imports correctly.


## Inspect the SQL importer before choosing a driver repair

From the repository root, with trusted installed application dependencies:

```sh
node examples/dependency-compatibility/check-mysql-config.cjs app
```

This probe follows the actual importer through Knex to MySQL2. It checks caller-resolved version against the lock, requested TLS/certificate validation, custom-CA forwarding and disabled compression. It opens no connection and prints no credentials. The synthetic CA is a configuration marker, not a working certificate.

Predict whether a successful result proves that a server certificate was accepted. It does not: no handshake occurred. Then explain why disabled compression narrows a compression-specific advisory without removing other findings in the same package. Ask Codex to identify the next evidence needed, keeping configuration, negotiated behavior, compatibility and exploit testing separate. See the [configuration evidence lesson](../../reader/DEPENDENCY-FIELD-LESSON.md#check-configuration-before-declaring-a-finding-reachable). This optional probe is not yet part of the default companion runner.


## Exercise the actual MySQL importer

The configuration probe checks the recipe. This optional integration probe makes the connection and reads a real synthetic schema. It needs an already-running Docker engine, Python, Node and trusted installed application dependencies. It runs on your computer, not AWS, and uses a disposable server with a 1 GiB memory limit and 512 MiB temporary data filesystem.

From the repository root:

```sh
docker pull mysql@sha256:24989179f58856db763f418010c1169fecc944e3ec1ea7e921572d83eb070f70
python3 examples/dependency-compatibility/run-mysql-server.py --app app
```

The pinned [Docker Official MySQL image](https://hub.docker.com/_/mysql) is the tested fixture, not a promise of perpetual currency. The runner refuses to pull a missing image silently. It creates a uniquely named container with only a loopback port and no host data mounts. Fixture passwords are deliberately public test values; never reuse them. Database root is used only inside the fixture to create tables and a TLS-required SELECT-only reader. This is unrelated to AWS root access.

The importer first attempts a connection without trusting the fixture CA and must reject it. With the public CA supplied, it must read two tables, preserve field order, integer nullability and string length/type, recover the primary and composite index, and construct two models. A session query must report a negotiated TLS cipher; an INSERT must be denied. Read the printed scope: this does not test hostname mismatch, every SQL type, full CLI generation, malicious protocol messages or AWS.

```text
Real importer → Knex → installed MySQL2
                         ↓ TLS
                 disposable MySQL
                         ↓
                schema → model checks
```

The runner removes its container in `finally`, including on ordinary test failure, and checks that it is absent. Temporary CA files and database contents are discarded. The downloaded image remains cached on the computer. If the process is forcibly killed, inspect only containers with the `amplify-mysql-probe-` prefix and verify ownership before cleanup; do not prune unrelated Docker resources.

Predict what changes if the reader receives write permission. The denied-INSERT assertion should fail, even if extraction still works. Explain why both the permitted operation and the rejected operation belong in the lesson. Compare old and proposed drivers in separate trusted installations using the same runner. A passing compatibility fixture supports a bounded upgrade decision; it does not make all dependency findings disappear. These probes remain optional and are not invoked by the default companion suite.


## Check the envelope before reading its contents

A delivery desk can check that an envelope has an address without proving that the letter inside makes sense. Amplify's backend-output schema has a similar boundary: a field can contain a string while the serialized JSON inside that string is invalid.

With trusted locked app dependencies installed, run this optional local probe:

```sh
node examples/dependency-compatibility/check-output-validation.cjs app
```

The probe invokes the installed client-configuration generator with an injected fictional output fetcher and a synthetic configuration contributor. It checks the actual generator, schema and caller-resolved Zod versions against the lockfile. Ordinary socket connections and fetch are blocked; it neither retrieves a stack nor installs a package. It also runs in the companion's optional `--app-toolchain` group.

Before running it, predict which inputs reach the contributor: a valid function-output record; an unknown category added beside it; an unsupported version; a number where a string is required; a missing required field; and a string containing `not JSON`. The current fixture confirms that three invalid shapes are rejected before contribution, the unknown category is removed, and the malformed JSON string survives this shape check. A separate JSON parse then rejects that string. This is a boundary observation, not a claim that Amplify accepts it through every later stage.

The useful engineering question is where each promise is checked. A shape check, JSON parsing, category-specific meaning, and a working deployed service require different evidence. The synthetic contributor does not exercise the real category converters. These six cases establish a local baseline for evaluating a future dependency change; they do not repair Zod, test memory exhaustion, validate every CLI path, or demonstrate a security exploit.

Ask Codex to trace the installed generator's parse call and identify which check owns each promise. Then explain why a future replacement must preserve both accepted output and rejected inputs. In a disposable copy, replace the expected parsed output with an incorrect object and confirm the assertion fails. Passing only the happy path would miss a validator that silently drops a required value.
