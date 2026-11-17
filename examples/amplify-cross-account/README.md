# Which account served the page, and which account received the order?

Maya's company has a shared Hosting account, a practice backend account and a production backend account. No accounts, roles or resources are created in this exercise. Read the [chapter lesson](../../reader/BOOK-LOCATORS.md#book-b5e60ed41b77bdf2) and [AWS's Gen 2 example](https://docs.amplify.aws/react/deploy-and-host/amplify-hosting/cross-account-deployments/), then answer each case before opening the [assessor](ASSESSOR.md).

For each case, draw an arrow from source to pipeline, pipeline to backend account, and published browser to backend account. Name the exact receipt for each arrow, one allowed and one denied or failed request, the payer for Hosting and backend usage, and the two cleanup owners. Treat the account names as fictional.

1. **A green website, an absent backend.** The Hosting build reports success for production. The separate backend deployment job failed while assuming its target role. Can the team announce the new private-order feature? What would you inspect before retrying?
2. **The borrowed address book.** The production frontend is built from the right commit but packages `amplify_outputs.json` for practice. A teammate points to the production URL as proof of correct isolation. Where can order requests go? Which comparison would catch the mistake before publication, and which live checks would remain?
3. **A preview with real customers.** A feature preview intentionally uses production backend outputs to avoid another backend. The preview URL is obscure and has a password. What still reaches production, and how would you redesign the test to avoid modifying real customer data? Include the added cost and deletion work.
4. **One green bill.** Hosting metrics are quiet and below the team's limit, but the backend account retains a database, logs and a function after the frontend branch is deleted. Which account owns each charge and off switch? What evidence would support a complete teardown claim after billing has settled?

## Rehearse the address-book mistake locally

The [existing destination lab](../environment-boundary/README.md) has fictional practice, preview and live browser configurations plus a separate approved map. Before running it, predict whether a production-looking page with practice destinations should pass. Then run from the repository root:

```sh
python3 examples/environment-boundary/lab.py
python3 -m unittest discover -s examples/environment-boundary -p 'test_*.py'
```

For an actual **local** Gen 2 outputs file, the [read-only outputs inspector](../environment-boundary/README.md#inspect-a-real-local-address-book-without-publishing-its-identifiers) can report selected destination presence, Regions and a SHA-256 without printing account resource IDs. The [built-output audit](../environment-boundary/README.md#follow-this-local-file-into-this-local-browser-build) checks selected literal destinations in a local browser build. Neither tool proves which account ran `pipeline-deploy`, what the live site served, effective user permissions or the two accounts' bills. That is why the paper exercise still requires separate deploy, publish, allow/deny and cost receipts.

Ask Codex to challenge your answer to case 2 by changing only the generated outputs. It should identify the failed boundary without assuming that a visible sign-in screen proves order ownership. Then ask for a minimum set of account-specific receipts. This is a design rehearsal, not evidence of a real account’s cross-account deployment or current spend headroom.
