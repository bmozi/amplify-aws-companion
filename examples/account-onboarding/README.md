# Account onboarding: review the request before an account action

Use this local companion after cases 21–26 in the [governance review](../governance-review/README.md). It checks two fictional post-provisioning evidence packets—one for a newly created member account and one for an invited existing account—then proves that missing owner approval, an unaccepted invitation, duplicate request ID, failed access evidence and an organization request aimed at the protected trial fixture are stopped.

Run:

```bash
python3 examples/account-onboarding/lab.py
```

## What it does

The reviewer checks whether the request names its accountable owner, purpose, cost owner and envelope, data class, allowed Regions and OU, account email, access group and permission set, baseline, recovery owner and acceptance evidence. The create-new branch checks a completed fictional account-creation record, email uniqueness and the powerful default role. The existing-account branch requires invitation acceptance, owner consent, discovery and a separately verified access plan. Both must show baseline evidence, intended and unrelated access results, an application smoke check and a recovery check. The run contains two positive packets and eight blocked changed cases.

The packet is considered **ready for owner acceptance review**, not authorized to deploy. These sample packets represent a later evidence checkpoint, after fictional account creation/invitation, baseline and access checks; they do not validate the pre-provision approval form. The program contains no AWS SDK/CLI calls, credentials, network access, account creation or policy changes. It does not emulate AWS Organizations, IAM Identity Center, Control Tower, AFT or their failure behavior. The fixture account IDs and approvals are made up.

The supplied local guard rejects an organization-level request in this example and checks the run limit and credit reserve recorded in its fixture. Those are case inputs, not default limits for a reader. The checks do not enforce AWS billing limits or prove any current credit balance.
