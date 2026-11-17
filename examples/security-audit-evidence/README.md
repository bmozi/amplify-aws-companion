# Security audit evidence join

This cloud-free lab practices a narrow but important security task: connect a finding to other records without accidentally connecting the wrong account, Region, resource or time. Imagine two customers both have a bucket called `uploads`. A bucket name alone is not enough to combine their evidence.

The JSON fixture uses a deliberately small, fictional normalized teaching format. Its `synthetic-detector` label is a placeholder, not an AWS finding type. It is not the schema of CloudTrail, AWS Config, VPC Flow Logs, GuardDuty, Inspector or IAM Access Analyzer. It includes an invented alert rule so you can see one candidate and several near-matches. No AWS SDK, credentials, network call or live AWS resource is used.

## Run it

```sh
python3 examples/security-audit-evidence/lab.py
python3 -m unittest discover -s examples/security-audit-evidence -p 'test_*.py' -v
```

For each finding, the report lists only evidence with the exact account, Region and resource identity, inside the finding's stated **event-time** window, and from an expected source. It separately lists excluded records and coverage states; a coverage declaration is also bound to the exact resource. The later `observed_at` clock is displayed but does not pull an old event into the window. The alert evaluation shows whether a synthetic rule matches, why a near-match does not, and which owner, read-only check and delivery-failure route the design names. `unknown` means this input cannot support a complete answer; it does not mean the resource is safe. A fixture declaration of complete coverage is only an input assertion. The rule is a plain local predicate, not an EventBridge or CloudWatch implementation.

## Change the case

Copy `fixture.json`, then change one field at a time: a resource ARN, Region, timestamp, expected source, a source's coverage state or the alert rule's category/severity. Run the lab again and explain why the result changed. In particular, try adding an event for the same bucket name in another account, and mark Config coverage `partial` while leaving the other records unchanged.

Do not add real account identifiers, event exports, IP addresses, secrets or customer records to this public teaching fixture.
