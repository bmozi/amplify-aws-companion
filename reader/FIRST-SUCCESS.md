# See why an empty list does not make a note private

Maya has a private repair note. Alice owns it; Bob's note list is empty. Before studying the whole application, you can test one question: **can Bob still open Alice's note if he knows its address?**

You need a trusted copy of this repository and Python 3 with its standard library. This exercise opens a temporary HTTP server on your own computer. It uses invented users and an in-memory note, then closes the server. It does not contact AWS or save the note for another session. If terminals or file paths are new, first use [the one-command cost exercise](../docs/FIRST-LOCAL-EXERCISE.md).

## Predict, then run

From the repository root, write your prediction for each question before running the command:

1. Bob's list is empty. Does that tell us whether a direct read will be denied?
2. Where should the owner check happen if another client can bypass the list screen?
3. If someone can simply claim to be Alice, what is still missing?

Run:

```sh
python3 examples/amplify-walkthrough/note_boundary_lab.py
```

Compare `bob_direct_get` under `unsafe_list_filter_only` and `server_owner_check`. Then find `bob_claims_alice_header_get`. Keep the returned status and body beside each prediction. Successful execution finishes with exit status zero; preserve an error rather than changing the exercise to make it pass.

## Explain the result

The unsafe handler hides Alice's note from Bob's list but still returns it through the direct path. The guarded handler checks the owner on that path too. However, the fixture accepts a forgeable `X-Lab-Actor` label: Bob can claim Alice's name. An owner comparison is useful only when its caller identity comes from a trustworthy authentication boundary. The lab isolates that distinction; it does not implement real sign-in.

Draw this path: **caller → identity → requested note → owner decision → response**. Put a question mark beside identity in the local fixture. In the later Amplify app, Cognito sign-in and backend data authorization have separate jobs along that path.

## Try a new case without the explanation visible

A school hides another family's document from search, but a parent can paste its download address into a new browser tab. What must be checked at that second entrance? Explain why hiding a link and requiring a login can each be insufficient. Record one allowed read, one denied read and what makes the caller identity trustworthy. Compare your answer with the [note-boundary assessor](../examples/amplify-walkthrough/ASSESSOR.md) after preserving it.

You have now observed a real local request and explained one access failure. Continue with [Chapter 1](BOOK-LOCATORS.md#book-16b52b3769a877e6), then follow the core chapter routes. Return to [the full application walkthrough](../examples/amplify-walkthrough/README.md) when you reach Chapter 6.
