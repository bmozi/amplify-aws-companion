# One booking needs three kinds of recovery evidence

Maya confirms booking B111 at 10:03 for 4,400 cents and attaches a photo. A technician dispatch D111 is sent. The database has a clean 10:10 point, but a bad edit at 10:11 changes the amount and photo reference. The object key is later overwritten and then given a delete marker. These are **fictional** events; the independent confirmation in `lab.py` is supplied, not discovered by the program.

Before running the model, choose a database point, object version and whether to repeat dispatch. Explain how you know the choice honors the customer promise. Then run from the repository root:

```sh
python3 examples/integrated-restore/lab.py
python3 -m unittest discover -s examples/integrated-restore -p 'test_lab.py' -v
```

The first two commands use the Python standard library. The clean combination is the 10:10 database point, object version `v1` and **no** dispatch replay. The assessor explains why. The program compares booking ID and amount, the database's version reference, actual object bytes against the independent digest, and the already-sent external effect. It is a read-only decision model; it does not restore a database, read S3, call AWS Backup, or send a dispatch. The timestamps do not measure RTO/RPO or prove that a real cloud service offers these exact points.

## Ask a versioned S3 API for the photo

The first model keeps `v1`, `v2` and the delete marker in a Python dictionary. The [emulated S3 continuation](s3_version_lab.py) gives them **opaque API version IDs** instead. Think of an object key as a book title and a version ID as the exact edition: the title's current shelf card can say “deleted” while an older edition still exists. The exercise creates one versioned bucket inside Moto, writes the confirmed photo, overwrites it with wrong bytes and issues an ordinary delete. A normal GET fails; an exact-version GET returns the original bytes. It also creates a second shop's same booking ID under a separate key.

Use the repository's pinned Moto and boto3 environment, or install the pinned `architectures/reliable-workflows/requirements-dev.txt` into a separate virtual environment. From the repository root:

```sh
.venv-labs/bin/python examples/integrated-restore/s3_version_lab.py
.venv-labs/bin/python -m unittest discover -s examples/integrated-restore -p 'test_*.py' -v
```

The added tests check five changed outcomes: a current delete marker hides but does not erase earlier versions; a wrong version or missing independent digest cannot be staged; the fixture's other-shop actor is denied; a valid candidate is copied to a **separate recovery key** while the original marker and other shop remain unchanged; and permanent removal of the confirmed old version blocks this recovery route. The staging write itself creates another stored version and request; it does not reopen the booking or replay the technician dispatch. Verify the database and external effect separately before any customer acceptance.

The actor check is **application fixture code**, not Moto proof of IAM or a bucket policy. The test client has broad mock authority, and a direct client call can bypass that guard. A real design needs scoped `s3:GetObjectVersion`, `s3:ListBucketVersions` only where required, protected transport, encryption at rest, version-aware denial tests and a reviewed recovery operator role. The emulator does not model KMS permission, lifecycle timing, retention law, cross-account access, actual S3 propagation or an AWS bill. Count both retained full versions and the staged copy, GET/PUT/list requests, possible transfer and key operations in a live cost worksheet. [AWS versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html), [version deletion](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeletingObjectVersions.html), [S3 security](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html), [S3 pricing](https://aws.amazon.com/s3/pricing/).

The [version-to-cost bridge](../storage-cost/versioned-read-path/README.md#connect-the-recovery-inventory-to-the-cost-worksheet) reads the fixture's retained sizes and stages the same photo, then prices only declared, selected meters under a fictional 30-day schedule. It keeps the old-version recovery promise and the staged-copy promise distinct. Use it to practice a cost decision; it is not an account forecast.

Work the following changes before opening [assessor reasoning](ASSESSOR.md):

1. The 10:10 point is unavailable. What can the 10:00 and 10:11 points prove, and what additional trusted evidence would allow a repair?
2. The database references `v1`, but a normal object read sees the current delete marker. Which exact version must be requested? What if versioning was never enabled or `v1` was permanently removed?
3. The confirmation ledger is lost. Can a plausible amount or AI-generated photo hash stand in for it?
4. Dispatch D111 has already been sent. Does restoring the database authorize sending it again? What evidence would you need if the external system's status were uncertain?
5. A team proposes hourly backups of its database but no object-version retention. Does that protect a booking with a photo? Name resource assignment, recovery-point schedule/retention, access/key requirements, restore validation and the recurring storage cost that belong in the plan.
6. Compare backup-and-restore with pilot light, warm standby and active/active for a regional outage. Which components and external effects must be prepared in each? Which strategy would you provision only after a complete cost estimate and measured drill?
7. Shop B learns Shop A's object key and version ID. The local route denies the read, but a broad raw emulator client can bypass the route. What exact live role and bucket-policy denials would you test before calling the recovery path private?

Ask Codex to critique your selected point, independently sourced evidence and no-duplicate-effect rule. Require it to distinguish a supported service behavior from this fictional model. For a live exercise, first verify a scoped non-root identity, exact Region/resource support, a whole-run estimate within the account owner's chosen limit, a verified credit reserve, stop/cleanup steps and delayed-billing review. No live run is required for this lesson.

Service references: [AWS Backup plans](https://docs.aws.amazon.com/aws-backup/latest/devguide/about-backup-plans.html), [RDS point-in-time restore](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html), [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html), [AWS disaster-recovery planning](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html).
