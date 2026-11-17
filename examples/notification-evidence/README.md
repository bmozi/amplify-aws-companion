# A send request is not a message someone read

Imagine the bakery tells Maya, “Your cake is ready.” The app calls a sending service and gets a successful response. Can the bakery truthfully say Maya saw the message? No. That response tells us about the **request**, not her screen or attention. A push provider may later accept or reject the message. Even an app-open event does not prove that Maya read this particular notification.

This local exercise uses invented people and evidence. It makes no AWS call. Its event names are **teaching labels**, not a claim that AWS emits this exact sequence or schema. AWS's [Push setup guide](https://docs.aws.amazon.com/end-user-messaging/latest/userguide/nx-push.html) says End User Messaging Push still uses the Amazon Pinpoint `SendMessages` API for direct sends. Its [monitoring guide](https://docs.aws.amazon.com/end-user-messaging/latest/userguide/nx-push-scale-monitoring.html) describes per-message events and distinguishes a push service accepting or rejecting a message from API activity. The [Amplify migration guide](https://docs.amplify.aws/react/build-a-backend/add-aws-services/pinpoint-migration/) separately retires the old Pinpoint-backed Amplify analytics and notification paths. These are different facts: a surviving send API does not preserve a campaign, endpoint store, or old client integration.

Run the four fictional cases:

```sh
python3 examples/notification-evidence/lab.py examples/notification-evidence/cases.json
python3 -m unittest discover -s examples/notification-evidence -p 'test_lab.py' -v
```

Before running, predict which case is blocked by consent, which stops at AWS acceptance and which has provider rejection. Notice that the app can open in **both** the blocked and rejected cases. The fixture records app activity as a separate boolean, not a step in the push-send trail or a message-linked read receipt. Compare each output's **bounded claim** with the business statement “the customer read the offer.” The test suite changes the evidence: a wrong recipient, an orphan event, a contradictory outcome and a send trail without a registered device must all be refused rather than turned into a cheerful delivery claim.

| Fictional observation | What it supports | What it does not prove |
| --- | --- | --- |
| Consent and device recorded in the fixture | This model permits a send request | Current real consent, a valid token, AWS permission or a successful send |
| AWS accepted request | The example crossed one API boundary | Push provider acceptance or a person receiving/reading it |
| Push provider accepted | The provider accepted the message in the example | Device display, attention or reading |
| App open recorded independently | The example app opened, even if the push was blocked or rejected | The notification caused the open or its content was read |
| Push provider rejected | Delivery claim must stop | Why it failed without a real diagnostic |

## Choose the product path before the pipeline

Use the [three-route diagram and changed-condition decision packet](ROUTE-CHOICE.md) to compare a direct push, today's Connect Customer Profiles-backed Amplify device registration, and a custom signed-in offer page. The [Amplify setup guide](https://docs.amplify.aws/react/build-a-backend/add-aws-services/notifications/set-up-notifications/) says the default `defineNotifications()` setup can create a Connect instance and Customer Profiles domain, so source-level convenience does not imply a small or free backend. A campaign remains a separate design and cost decision.

An **order-ready push** is a message sent outside the app. It needs an eligible, consented recipient, a device/channel route, an authorized sender, a send result and delivery evidence. For current implementation details, inspect the selected platform, Region, provider credentials, quotas, costs and AWS's current Push guide. A **marketing campaign** adds audience selection, consent policy, schedule, templates and campaign measurements; a direct `SendMessages` call does not supply those things. AWS's [Pinpoint end-of-support guide](https://docs.aws.amazon.com/pinpoint/latest/userguide/migrate.html) says stored Pinpoint endpoints, segments, campaigns, journeys and analytics end after October 30, 2026, even though direct push-sending APIs continue.

An **offer shown after sign-in** can instead be designed as an ordinary authorized app page backed by selected Auth/Data services. That is a custom product design, **not** a drop-in replacement for Pinpoint in-app campaigns: it lacks their targeting, timing, analytics and orchestration unless separately built and proved. AWS explicitly says Pinpoint in-app messaging is unsupported after October 30 and is not available in Connect Customer. In this repo, the offer-page design is paper-only; the Field Lab does not declare notification resources or a campaign.

Before choosing a live path, estimate its whole run rather than just its send count. A direct push design may need provider credentials, message calls, an event destination and its logs or downstream processing. A campaign design adds profile, audience, orchestration and measurement resources. A custom offer page uses the app's API, data, hosting and logs, and may retain offer records after the page is hidden. Record each selected service's current Region/account price, expected volume, end date and cleanup owner; none of these paths has been priced or approved for a live run. Choose whole-run spending and reserve limits from the account that would host it.

## Changed-case assessment

Write a short decision for each case before opening [the author key](ASSESSOR.md):

1. The API says success, but the provider reports rejection. Marketing wants to count one “delivered offer.” What can be counted, and what evidence is missing?
2. Maya opted out yesterday, but a stored token still exists. A teammate says registration is enough. Where must the attempt stop? What would a real system need to check that this static fixture cannot?
3. The app records that Maya opened it after a provider-accepted push. The product manager wants a “read notification” metric. Name a valid narrower metric and a separate instrumentation/consent design for the larger claim.
4. The bakery wants an offer to appear only on Maya's private order page after sign-in. Compare a custom Auth/Data page with a push send and a marketing campaign. Which pieces of the Pinpoint-era tutorial cannot simply be carried forward?

Ask Codex to review your answer for overclaims. Require it to name the exact observation, identity and consent boundary, resource owner, selected-service cost meter and stop/cleanup action. Do not let a model invent a delivery receipt or price.
