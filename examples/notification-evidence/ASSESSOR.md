# Author key: notification evidence

These are expected reasoning boundaries, not observed learner answers or live AWS results.

1. An AWS-accepted API request is one request, not a delivered offer. A later provider rejection is a failed delivery outcome in this fictional trail. Count it in a failure measure, retain the correlated message/recipient IDs and investigate a real provider reason and event pipeline before claiming delivery. AWS's actual event semantics must be checked for the selected route.
2. Stop before send because consent is missing, even with a token. A real implementation needs an authoritative, current consent decision at the send boundary and a defined response to revocation/in-flight work; the JSON snapshot cannot prove consent freshness, identity, device validity or races.
3. “App open recorded” is the supported narrower statement. It is an independent observation: it can coexist with missing consent or a rejected push. A read metric would need a clearly defined event tied to the notification and recipient, careful duplicate/correlation handling and privacy/consent review. An open alone does not identify its cause or prove attention.
4. A private in-app offer page could use an authenticated request and order-level authorization under the existing app architecture, with a negative test for another customer. It is a bespoke page, not Pinpoint in-app messaging or an automatic migration. Push needs device/channel delivery; a marketing campaign also needs audience, schedule, consent, templates and measurement. Pinpoint engagement features and in-app messaging end after October 30, 2026; the continued direct Push API does not preserve them. Price and provision only a selected, eligible path after account and credit review.

No real recipient, provider, IAM policy, AWS account, Region, price or billing result was tested here. The model's evidence sequence is intentionally simplified and cannot validate AWS delivery semantics.
