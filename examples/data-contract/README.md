# Agree on what the bytes mean

Run `python3 examples/data-contract/lab.py` from the repository root. This standard-library exercise parses actual UTF-8 JSON and validates a deliberately small update contract. It makes no network or AWS calls and writes no files.

The fictional record identifies a part as `"0012"`, prices it in integer **USD cents**, and stores an optional note. This is trusted local fixture data; matching a part identifier is not authentication or authorization.

## Start with one update

If this is your first terminal exercise, complete [the local cost walkthrough](../../docs/FIRST-LOCAL-EXERCISE.md) first. It explains the repository root, Python command and exit status. Here you need only the existing Python installation and trusted source. No packages or AWS credentials are required. The recorded checks use Python 3.12 on macOS; a different operating system still needs its own verification. Run without `-O`, which disables the assertions used by these teaching scripts.

Imagine the shop gives away a replacement part. Its existing price is 30 cents. The update should set the price to zero and leave “Keep dry” alone. Copy these three predictions into a note before running anything:

- The saved identifier will be ___ because ___.
- The new price will be ___ cents because ___.
- The old note will ___ because the submitted update ___ .

The request being tested is `{"version":1,"part_id":"0012","price_cents":0}`. Read its names aloud. `version` describes the message contract; `part_id` selects the fixture record; `price_cents` declares the amount and its unit. There is no `note` field in this request. Do not read omission as a request to erase it.

From the repository root, run:

```sh
python3 examples/data-contract/lab.py
```

The output is one JSON object. Long output may wrap across terminal lines without changing its meaning. Find the named sections rather than trying to match the screen's line breaks:

| Output name | What to look for | What it establishes |
| --- | --- | --- |
| `valid_zero` | `part_id` remains `"0012"`, price is `0`, note remains `"Keep dry"` | This fixture accepts zero and preserves an omitted note |
| `explicit_clear` | Note becomes `null` | A separate explicit clear has a different result |
| `empty_note` | Note becomes `""`; price stays `30` | An empty string is a value distinct from `null`; this case starts from the original record |
| `rejected_payloads` | `22` | All 22 supplied invalid cases raised the expected validation error |
| `original_unchanged` | Original price `30` and note `"Keep dry"` | The original fixture was not overwritten by constructing the returned copies |

The program ends with exit status zero when its assertions pass; it does not print a separate `PASS` banner. A traceback means the run failed. Preserve the error and the source version instead of removing a check to make the output look right. If Python cannot find the file, check that you are in the repository root. If it cannot import SQLite when you later run the revision extension, that interpreter's SQLite support is a prerequisite to resolve; it is not an AWS connectivity error.

Twenty-two rejected examples do not prove all possible invalid inputs are handled. Likewise, the successful result is local behavior, not a saved cloud record. Your own explanation should say why the values changed, not merely that the command ran.

### Carry the idea into a cloud design

Imagine Maya's shop adds a web form so two employees can update parts from different computers. The local function is one possible check along that journey. Draw the path from the form to an API, through validation, to stored data and back to the form. At each step, write what evidence would answer these separate questions:

1. **Meaning:** Did `"0012"` remain a string, and did the request distinguish an omitted note from `null` and `""`?
2. **Authority:** Who is making the request, and are they allowed to change this shop's part? A matching part ID alone does not answer either question.
3. **Freshness:** Did someone else change the record after the form loaded? A valid request can still contain a stale edit.
4. **Outcome:** Was the intended change actually saved, and what should the client do if the response is lost?

Try two requests with the same well-formed update: one from an authorized employee and one from someone outside the shop. Predict the allowed and denied outcomes, then mark both as **not tested** by this parser. Next, have both employees edit the same original record and predict how a stale form could overwrite a newer change. The [revision exercise](#two-editors-one-record) makes a local version of that failure observable; it still does not establish cloud identity or customer authorization. Ask Codex to challenge your drawing by finding one missing boundary, then check its suggestion against the exercise and identify what evidence you would need from an actual deployment.

Before running, predict these outcomes:

| Input change | Question |
| --- | --- |
| Set `price_cents` to `0` | Does zero mean absent, or a valid free item? |
| Omit `note` | Should the old note survive? |
| Send `note: null` | Should the note be cleared? |
| Send `note: ""` | Is an empty string the same stored value as null? |
| Send numeric part ID `12` | Can the program recover the lost leading zeros? |
| Send `price_cents: true` | Should a boolean count as one cent? |

The chosen contract preserves omitted fields, explicitly clears a note with null, and preserves an empty string as a distinct value. It accepts zero cents, rejects booleans/numeric strings/fractional representations for price, requires version 1 and an exact string identifier, and rejects unknown or duplicate fields. A request is limited to 1024 encoded bytes; the note limit separately uses Python's `len`, counting Unicode code points for the valid emoji fixture. Those are teaching constraints, not AWS limits or a universal schema. The [two-language extension](#follow-the-same-bytes-into-node) shows why another runtime needs that unit stated explicitly.

The lab validates before returning a copied record, checks serialization round-trip, and confirms that rejected updates leave the original unchanged. Duplicate JSON object names are rejected explicitly rather than allowing a parser to silently keep one value. It also rejects malformed encoding, incomplete JSON and non-finite numeric tokens. This small parser is not a production resource-exhaustion defense, concurrent datastore transaction or complete API implementation.

## Change the rule before changing the code

1. The business now supports another currency. Explain why renaming `price_cents` to `amount` is insufficient. Specify currency, scale, bounds and conversion/rounding ownership before implementing anything.
2. A client sends `delivery_note` instead of `note`. Explain why silently ignoring it could create a false success. Compare strict rejection with an explicit versioned compatibility rule.
3. A future field permits null, zero and omission. Write three expected results before extending the validator. Preserve the existing rejection cases.
4. The API becomes public. Name the missing authentication, authorization, concurrent-update and request-size enforcement boundaries. Do not call this lab's identifier comparison an access control.

Ask Codex to generate a counterexample after writing your own predictions. Require it to explain why `type(value) is int` is intentional here: Python booleans are instances of `int`, but this contract excludes them. Keep schema-version meaning separate from a record revision used to prevent concurrent overwrites. No learner or cloud result is implied by the passing script.

## Follow the same bytes into Node

The first lab had one Python reader. A real application often has a second program in another language. This extension uses Python 3 and Node.js locally, with no packages, network calls or AWS credentials. Node 22.23.2 was used for the recorded result. The Python script sends the exact JSON text of five small cases to [`interop_consumer.mjs`](interop_consumer.mjs); it checks both results before printing a summary.

Before running, predict: Will both readers preserve a zero-cent update with an omitted note? Will a large *numeric* event ID keep its last digit? Which price survives a repeated JSON name? Does a 200-emoji note have the same length according to both runtimes? Write the reason for each prediction.

```sh
python3 examples/data-contract/interop_lab.py
```

Find these observations in the one-line JSON result:

| Case | Tested observation | Contract decision |
| --- | --- | --- |
| Safe update | Both readers see `"0012"` and zero; the note was absent on the wire | Preserve identifier text and distinguish zero from omission |
| Numeric event ID | Python reads `9007199254740993`; Node reads `9007199254740992` | Send exact comparison IDs as strings before any lossy conversion |
| Text event ID | Node preserves the quoted digits | Validate an ID's shape as text; do not cast it to `Number` first |
| Repeated `price_cents` | Our strict Python hook rejects; Node `JSON.parse` keeps 20 | Reject duplicate names while raw text is still available |
| 200 truck emoji | Python counts 200 code points; Node reports 400 UTF-16 units and 800 UTF-8 note bytes | State whether the limit measures bytes, code points or reader-perceived characters |

The large ID is a separate fictional event identifier, not a valid value for the earlier price field, which is capped at one million cents. The duplicate case demonstrates the behavior of these two parser configurations. Node's ordinary parsed object no longer contains both occurrences, so a field validator run afterward cannot detect the ambiguity. A production cross-language API needs a deliberately chosen duplicate-name rule at ingress.

Try three changed cases on paper before editing code: (1) a JavaScript producer turns the text event ID into `Number` before serialization; (2) the note uses a base letter plus a combining mark instead of truck emoji; (3) a second client rejects duplicate names before constructing an object. For each, identify what can be decided from the wire bytes, what was already lost upstream, and which unit or parser policy the contract needs. Then read the separate [assessor reasoning](INTEROP-ASSESSOR.md). Continue to the Unicode-policy lab below for an executed combining-mark case. Ask Codex to challenge your answers with another case, but keep your original predictions beside the assisted explanation. Passing these authored local cases is not independent learner validation or a deployed API test.

## Two spellings of one label

Imagine two suppliers enter the label “Café.” One keyboard sends a single `é`; another sends `e` plus a combining accent. A person may see the same word, while the stored strings and UTF-8 bytes differ. Maya must choose a rule **for this human-entered label** before using it as a lookup key. This example chooses Unicode NFC, checks for an existing canonical key, and rejects a second record rather than silently replacing the first. It does not apply the rule to opaque part IDs or authorization subjects.

Before running, predict whether the two labels have equal raw strings, equal NFC keys, and equal UTF-8 lengths. Also predict whether compatibility normalization (`NFKC`) would preserve a circled-digit ID `①` as distinct from ASCII `1`.

```sh
python3 examples/data-contract/unicode_lab.py
```

The standard-library Python script sends six actual strings through JSON to the local [Node reader](unicode_consumer.mjs). It checks both runtimes' NFC and NFKC results and reports their Unicode database versions. The recorded run observed Python Unicode 15.0.0 and Node Unicode 17.0; other installations may report different versions. The chosen long-established characters are checked locally, but this is not a universal runtime compatibility certificate.

### Put the label rule where two writers meet

The first Unicode exercise catches a duplicate in one Python dictionary. Now imagine two registration desks. Both check an empty list before either saves. A check at each desk cannot reserve the name. The shared database must refuse the second save.

Run `python3 examples/data-contract/unicode_store_lab.py` from the repository root. It needs only Python's standard library and makes a temporary SQLite file that it removes afterward. Before running, predict whether a database `UNIQUE` rule on the **raw** label accepts both spellings; whether both connections can initially see no canonical key; and which supplier remains after both attempt to insert.

The lab first shows that raw-byte uniqueness accepts two separate rows. Its second table stores the original display spelling and an NFC `label_key` with a database `UNIQUE` constraint. Two independent connections both see no matching key; the first saves supplier A; the second gets a constraint error and rolls back. A lookup using the second spelling finds A, but that lookup does **not** give B permission to act as A. Inspect `raw_only_distinct_rows`, `both_prior_reads_empty`, `second_insert`, and `stored_supplier_ids` in the JSON result. See the [separate assessor](UNICODE-STORE-ASSESSOR.md) after writing your explanation.

This is an ordered two-connection SQLite case, not a simultaneous distributed race. The application must use the *same field-specific key rule* on every write path, protect or recompute the key so a bypass cannot insert inconsistent raw/key pairs, and decide what to do with existing collisions before adding a constraint to a populated store. SQLite's `UNIQUE` constraint checks the stored key; it does not normalize text itself. A service should translate the collision into a deliberate registration response, never silently merge identities. Ask Codex to propose a third spelling or a legacy-data migration conflict, then test the actual key and explain who decides ownership. The exercise proves only the local database behavior, not an AWS database, cross-runtime policy for all Unicode versions, or real supplier identity.

| Observation | Meaning for this fictional contract |
| --- | --- |
| The two raw labels differ; NFC makes both `Café` | Use the chosen canonical key for this field before lookup and uniqueness checks |
| Raw labels measure 4/5 code points and 5/6 UTF-8 bytes | State whether a limit applies to raw input or the canonical stored label, and separately cap whole-message bytes |
| The second NFC-equivalent insertion is rejected; the first remains | A collision needs an explicit business decision, not a last-write-wins dictionary assignment |
| `①` and `1` stay distinct under NFC but merge under NFKC | Do not compatibility-fold an opaque ID unless its owner deliberately defines that identity rule |
| Latin `a` and Cyrillic `а` remain distinct under NFC | NFC is not a visual-spoofing detector or authorization check |

Changed case: a supplier already owns the decomposed spelling, and a different supplier submits the composed spelling. Explain why a display match cannot establish that they are the same supplier. Then choose a policy for case changes and visually confusable names *separately*; this lab does not define either policy. Read the [assessor reasoning](UNICODE-ASSESSOR.md) after your own answer. Ask Codex to produce a counterexample to “normalizing all strings is safe,” and ask it to name the exact field and identity authority. Check its proposed Unicode behavior with real runtime output before trusting it. [Unicode normalization forms](https://www.unicode.org/reports/tr15/), [Python normalization API](https://docs.python.org/3/library/unicodedata.html), [JavaScript normalization API](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/normalize).

## Two editors, one record

Continue here after you can explain zero versus omission. This second exercise adds persistence and stale edits; it is not required to understand the first parser exercise.

Run `python3 examples/data-contract/revision_lab.py`. Two independent SQLite connections read the same row revision before a controlled sequence of writes. Both price-first and note-first orders run. The unsafe variant accepts a complete stale form and loses the first change; the guarded variant conditions its update on the observed revision and reports a conflict without changing the committed row. A repeated stale request also conflicts. After an explicit fixture decision to combine these independent edits, a fresh read and update preserves both values.

The database files live in a temporary directory, all connections close, and the directory is removed. There are no threads, cloud calls or timing claims: the interleaving is intentionally ordered. SQLite execution is real; the employees and business decision are fictional. The function's `guarded=False` option exists only to demonstrate the incorrect behavior.

Explain the observations before changing the code:

1. Why does valid JSON fail to prevent the lost update?
2. Why must the revision condition belong to the UPDATE itself?
3. Both employees now edit the price. What business decision is missing before retrying?
4. A save commits but its response is lost. Why does a revision conflict alone fail to establish the original request's outcome?

Expected reasoning: validation and freshness are separate; a separate read/check can become stale; competing business intentions need review rather than blind overwrite; and stable request identity/outcome recovery is distinct from a row revision. No UI, identity service, multi-record invariant, deletion/recreation policy, distributed transaction or independent learner validation is implemented here.

### Read the four outcomes

The output is a list of four result objects. Match each by `order` and `guarded`, rather than relying on its position. In the unsafe price-first case, the final price falls back to 30; in unsafe note-first, the final note falls back to “Keep dry.” Each shows the earlier edit being lost. In both guarded cases, `stale_result` is `"conflict"`, followed by the explicitly reviewed combination: price 45, note “Inspect seal,” revision 3. That final combination does not mean the stale save succeeded. It came from a later fresh read and a separate accepted update after the fixture's review decision.

Explain that distinction without looking at the output. Then record a changed case: both employees choose different prices. State why the same automatic combination would be inappropriate and what the person reviewing the conflict needs to see.

## Two authorized clients, one HTTP record

The SQLite revision exercise ordered two connections directly. This continuation adds a real loopback HTTP request boundary and two independently dispatched client requests. Python's standard library is enough; no AWS credentials, packages or public port are used. Run:

```sh
python3 examples/data-contract/http_revision_lab.py
```

The script creates a temporary SQLite record owned by fictional Maya and two random bearer tokens held only in this process. One token maps to Maya and the other to Lee. It starts an HTTP server bound to `127.0.0.1` on an OS-selected port, performs the checks, stops the server and removes the database. It does **not** integrate Cognito or prove a real person's identity. Use it only as a local fixture, not as a public server template.

Before running, predict the HTTP result and the final record for each step:

| Request | Expected local result | Why it matters |
| --- | --- | --- |
| GET without a token | 401 | The fixture has no recognized caller |
| GET or PUT with Lee's token | 403 | A recognized caller is not this record's owner |
| Maya PUT without `If-Match` | 428 | This lab requires the version returned by GET |
| Maya PUT with a weak ETag or boolean price | 400 | The fixture rejects that precondition form or update shape |
| Maya PUT with a future ETag `"2"` while the record is at `"1"` | 412 | A tag for a revision this request did not read cannot authorize an update based on the older record |
| Two Maya clients PUT different edits using ETag `"1"` | One 200 and one 412 | One conditional SQLite update advances to revision 2; the other is stale |
| Maya rereads and explicitly accepts the independent other edit | 200 with ETag `"3"` | The merge is a reviewed new action, not the stale request succeeding |
| Retry the old request using ETag `"1"` | 412 | A stale precondition cannot silently replace revision 3 |

The code uses a `threading.Barrier` only to put both valid requests at the interesting race point. Either one can win. The handler first checks that the supplied tag matches the record it read: it builds the proposed values from that record, so a guessed future tag must not authorize that older copy if another writer advances the row. That first check alone is not enough: the accepted write and revision increment also occur in one SQLite `UPDATE ... WHERE part_id = ? AND owner = ? AND revision = ?` statement. A different write after the read makes this conditional update change zero rows, which produces 412. A controlled test hook would advance the row at the update edge if the future-tag request reached it; the fixed handler rejects that request first. This is a fixture test, not a measurement of real traffic. The `ETag` here is a strong quoted revision value because **every mutation through this fixture advances that revision**. A bypassing writer or delete/recreate path would invalidate that assumption and needs separate design and tests. The server handles only a narrow GET/PUT route and one strong ETag; it is not a complete implementation of all HTTP conditional-request forms. [HTTP `If-Match` semantics](https://www.rfc-editor.org/rfc/rfc9110.html#name-if-match), [SQLite conditional UPDATE](https://www.sqlite.org/lang_update.html).

After you observe the result, answer these changed cases before reading the [assessor](HTTP-REVISION-ASSESSOR.md):

1. Both clients change the *price* differently. Should the losing client automatically retry with its old intention?
2. The first PUT commits but its response disappears. The client repeats it with ETag `"1"` and receives 412. What can it conclude, and what separate request-identity record would it need?
3. A maintenance script changes the row without incrementing `revision`, or deletes and recreates it at revision 1. Which ETag assumption breaks?
4. Lee knows the part ID and guesses Maya's ETag. Does that grant Lee write access? Which check stops the request?

Ask Codex to challenge your answers without treating a passing run as proof of cloud behavior. Record the command, interpreter, observed outcomes, the source revision and one limitation. The ten repeated local runs in the project review check for fixture stability only; they do not measure load or AWS concurrency.

## Keep a small learning record

Write the source revision or archive identity, interpreter version, prediction, observed output, process result and one changed-case explanation. Add assistance received and a limitation. A useful limitation here is “I observed a controlled local stale write; I did not test a public authenticated API.” Do not write “mastered concurrency” because four authored cases passed.

Ask Codex: “Tutor me using this lab. Ask one prediction at a time, wait for my explanation, and then compare it with the code. Do not run cloud commands or reveal the next answer early.” Keep your original explanation beside the assisted revision. The learning record is evidence to review; this repository has not yet collected independent learner attempts.
