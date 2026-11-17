# Trace the Field Lab without deploying it

Maya can see a notebook page in her browser. Does that mean a note is saved, private and recoverable? Use the [chapter walkthrough](../../reader/BOOK-LOCATORS.md#book-e8d9fb108293da29) and the repository source to answer before opening the [assessor notes](ASSESSOR.md). This is a cloud-free source investigation. It does not create users, send requests to AWS or prove deployed authorization.

## Run the local note boundary

Before running the exercise, predict whether Bob can read Alice's known `note-1` when his note **list** is empty. Run the three fixture modes:

```sh
python3 examples/amplify-walkthrough/note_boundary_lab.py
python3 -m unittest discover -s examples/amplify-walkthrough -p 'test_*.py' -v
```

The script opens an ephemeral HTTP server on `127.0.0.1`, makes requests, and closes it. Its synthetic note lives only in process memory. In `unsafe_list_filter_only`, the list path filters by the claimed actor but the direct note path omits the owner check. In `server_owner_check`, both paths check the owner. Compare Bob's `GET /notes` with Bob's direct `GET /notes/note-1`, then compare Alice's and the anonymous direct request. Write which status and body actually distinguish privacy from an empty screen.

The `X-Lab-Actor` header is a **forgeable label**. The `bob_claims_alice_header_get` result deliberately shows why even this guarded local handler cannot authenticate a caller. The lab models one authorization decision; it is not Amplify, Cognito, AppSync, a persistent database or a deployed security test. To claim effective Field Lab isolation, use two separate test-user sign-ins against the intended deployed backend and directly test the API. See the [assessor](ASSESSOR.md) after making your prediction.

### Can a denied response reveal a record exists?

Suppose Alice's note ID itself is sensitive. Before looking at the output, predict whether Bob can distinguish an existing forbidden ID from an unknown ID. In `server_owner_check`, compare `bob_direct_get` for `note-1` with `bob_unknown_get` for `not-a-note`. The first returns 403 and an owner-denial message; the second returns 404 and an unknown-note message. Bob does not receive the note text, but the different responses disclose which of these guessed IDs exists in this fixture. A hidden list and a denied body do not automatically hide existence.

For a changed design, write a policy for what unauthorized callers may learn about record existence. If existence must stay private, consider matching external responses for forbidden and nonexistent records while preserving a useful allowed-owner result and restricted internal diagnostics. Compare status, body and other observable behavior, and test both known and nonexistent synthetic IDs. A shared status alone is not proof that timing, headers, logs or other paths cannot distinguish them. Some applications deliberately disclose existence; choose from their privacy and usability needs rather than assuming every 403 is a defect.
The third output, `owner_check_matching_response`, is a small local example of that candidate: Bob receives the same 404 and JSON body for both IDs, while Alice's claimed label still reads her note. Compare those results to `server_owner_check` and write what changed. An unlabelled request remains 401. This fixture checks only selected status and body values; it does not establish indistinguishable timing, headers, logs or other routes. The actor label can still be forged, so the alternative does not authenticate Alice or establish real privacy. It does not test an AWS service.

## Make an evidence map

For each case, record four things: **your prediction**, the **source file and symbol** that support it, the **observation a real run would still need**, and the **claim you can safely make now**. Keep source intent separate from actual service behavior. Use the [learning record](../../curriculum/LEARNING-RECORD.md) if you want to save the attempt.

1. **Save a note.** Find the Save handler, the `Entry` definition and its authorization rule. A teammate points to a React state change as proof of durability. Trace the path that must succeed and name the read that would test persistence after a refresh.
2. **Use a second identity.** Identify the application sign-in identity, the identity used to scope private file paths and the AWS deployment role. Could the email printed in the screen serve as the deployment credential or storage path identifier? Explain why.
3. **Move the frontend.** A local dev server uses outputs copied from a live lab. Where would Save requests go? Identify the configuration field or file to inspect before making a request. Does `localhost` prove that no cloud meter can move?
4. **Bypass the screen.** A different client uploads a file larger than the browser's 5 MiB limit. Which file contains that check, and what evidence would establish a backend rejection? Compare it with the text inspector's 10,000-character check.
5. **Diagnose a green deployment.** Hosting reports success, but sign-in fails. Give two distinct causes and one safe observation that distinguishes them. State what the Hosting job did prove.
6. **Plan a category field.** Maya wants to group old and new notes by category. Identify schema, client and test changes. Decide how old records without a category should behave before you decide whether the field is required.
7. **Choose only needed parts.** A bakery begins with a public menu, then adds private orders and customer photo uploads. Draw both stages. For each stage, choose from Hosting, Backend, Frontend Libraries and UI Libraries; name the resource owner, an access check and one cost driver. Explain whether a catalog listing means that a resource already exists.
8. **Separate saving from publishing.** A heading change reaches `main`, the publication flag is false and visitors still see the old heading. Which receipt exists, and which release step did not start? Now suppose a deliberately started workflow serves a marker matching the commit, but a second synthetic user can read the first user's note through the API. Classify the result, propose the correct enforcement boundary and name what remains after the publication flag is switched off.

## Change one fact before checking the key

Repeat case 8 with a different result: the second user's list screen is empty, but a direct API read has not been attempted. Can you now claim owner isolation? Write the minimum additional test and the result that would change your judgment. This change distinguishes a hidden item from a denied operation.

**Ownership change:** The current owner asks to transfer a note. Does the product promise allow that? If the promise forbids transfers, inspect whether the schema protects the owner field itself. AWS's [Gen 2 owner guide](https://docs.amplify.aws/react/build-a-backend/data/customize-authz/per-user-per-owner-data-access/) describes the default reassignment behavior and a field-level restriction. Do not infer immutable ownership from the list screen or the local HTTP fixture.

Compare your answer with [the assessor notes](ASSESSOR.md) only after making your own map. For deeper capability choices, try the [four changed-condition cases](../amplify-capability-choice/README.md). For a future authorized live reproduction, record account, Region, scoped role, commit, build and Hosting job, actual backend destination, owner-positive and unrelated-user-negative API results, file create/read/delete, mailbox observations, cleanup inventory and later billing. Never fill an unexecuted field with an expected value.
