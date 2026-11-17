# Read a security finding without inventing the incident

Design assessment and local SQL exercise for unit 31. All records below are fictional. Do not activate AWS services, send messages or import these examples as real findings. For each case, write the supported conclusion, unsupported conclusion, next read-only observation, responsible role and evidence needed to finish the review.

1. **Different questions.** A package vulnerability report names image digest A. An unusual-activity report names workload role B. A discovery report identifies sensitive content in S3 export C. Which service context fits each report? Which identities and intervals would you need before asserting that they describe one incident?
2. **The corrected repository.** The source lockfile is repaired and image digest D has a passing application test. The finding names digest A; the running deployment's digest has not been read. The team says production is repaired. Identify the missing link and explain why a new image alone cannot fill it.
3. **The empty result.** Ten of twelve intended resources have recent coverage. A filtered query returns zero findings for those ten. Two resources have unknown coverage. Draft a one-sentence status that preserves both the result and the missing evidence. List two checks before broadening the conclusion.
4. **Sensitive-data sampling.** A bucket is in the inventory and automated discovery selected some representative objects. No sensitive-data finding appears in the retrieved results. A colleague says the entire bucket contains no confidential data. Explain the error without inventing a real leak or labeling the configuration's severity.
5. **Correlation and time.** A threat report arrives at 14:00 for activity at 12:00. A deployment happened at 13:00. A second report describes an exposure on a similarly named resource in another Region. Propose two hypotheses and the identity/time evidence needed to distinguish them. Do not infer that the 13:00 change caused the 12:00 activity.
6. **Three finish lines.** A subsequent assessment no longer reports the package condition on the verified replacement digest. The application passes its required checks. Earlier unusual activity still lacks an explanation. State which conclusions are supported and what remains open. Explain why an automated report should not declare the entire incident resolved.

7. **The wrong security job.** Maya needs customer sign-in and private notes. A teammate proposes using a threat detector as the sign-in service, then treating any signed-in customer as allowed to read any note. Match authentication, record authorization, suspicious-activity detection and sensitive-data discovery to separate responsibilities. Explain what the first Amplify app's ownership rule contributes and why no finding from a detector proves a requested read is authorized.

Transfer: a duplicated finding notification refers to a resource that has since been replaced. Explain how a read-only evidence summary should identify the stale target and why the old event must not authorize an action on the replacement.

Ask Codex for counterexamples only after your first answer. Keep its help disclosed, use synthetic identifiers, and compare against [assessor notes](ASSESSOR.md). This is reasoning practice, not a service test.


## Run the deployment and coverage join

From the repository root:

```sh
python3 examples/security-finding-review/lab.py
```

Predict the first report before executing. Three deployments share the name `booking` and artifact label `image-B`, but they are in different account/Region scopes. Shop A east has no scan for its deployed B; its recent scan and finding concern old image A. Shop A west has a recent B scan and an active B finding. Shop B east has an old B scan and no finding in the supplied snapshot. None deserves a blanket “clean” label.

The program runs real in-memory SQLite joins over fictional records. Its negative controls show two errors: joining only on artifact borrows a finding from the wrong Region; checking only for zero active findings labels two deployments clear despite missing or stale coverage. The correct report preserves exact scope and scan freshness.

Next, the fixture supplies a recent scan for Shop A east's exact deployed artifact. Under its explicit complete-export assumption, only that row changes to `no_active_findings_in_stipulated_snapshot`. An incomplete export still yields unknown when no finding is present. The old A finding stays in the record; no cloud finding is changed or dismissed. The program also preserves identical finding IDs in two Regions and rejects stale/future scan times as recent evidence.

These are simplified teaching records, not AWS API schemas. Image labels stand in for immutable artifact identifiers; the deployment inventory and scan records are trusted inputs. The 20-unit freshness threshold and integer clock are invented. The lab does not fetch paginated findings, authenticate evidence, discover deployments, model concurrent updates, assess exploitability or prove service scanning behavior. Its complete snapshot assumption must be independently established in a real integration.

For transfer, make the findings export incomplete while leaving a positive finding present. Explain why a reported positive finding remains useful but a negative conclusion no longer follows. Then add another account with the same resource name and predict which rows should remain unchanged. Ask Codex to identify every join key and unverified source assumption before proposing an integration.
