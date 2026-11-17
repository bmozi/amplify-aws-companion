"""Check this teaching specimen's stated shape, not effective AWS authorization."""
import json
from pathlib import Path

BASE = Path(__file__).parent
OBJECT = "arn:aws:s3:::amplify-aws-example-private/exports/weekly.json"
ROLE = "arn:aws:iam::111122223333:role/ExampleExportReader"


def check():
    reader = json.loads((BASE / "reader-role.json").read_text())
    key = json.loads((BASE / "key-policy.json").read_text())
    assert reader["Version"] == key["Version"] == "2012-10-17"
    s3 = {s["Sid"]: s for s in reader["Statement"]}
    assert len(s3) == 3
    allow = s3["ReadOnlyTheApprovedVersion"]
    assert (allow["Effect"], allow["Action"], allow["Resource"]) == (
        "Allow", "s3:GetObjectVersion", OBJECT)
    assert allow["Condition"] == {"StringEquals": {"s3:VersionId": "ApprovedVersionA"}}
    deny_version = s3["RejectOtherVersionsOfThisObject"]
    assert (deny_version["Effect"], deny_version["Action"], deny_version["Resource"]) == (
        "Deny", "s3:GetObjectVersion", OBJECT)
    assert deny_version["Condition"] == {
        "StringNotEquals": {"s3:VersionId": "ApprovedVersionA"}}
    deny_current = s3["RejectUnversionedReadOfThisObject"]
    assert (deny_current["Effect"], deny_current["Action"], deny_current["Resource"]) == (
        "Deny", "s3:GetObject", OBJECT)
    assert "Condition" not in deny_current
    kms = {s["Sid"]: s for s in key["Statement"]}
    assert len(kms) == 2
    admin = kms["KeepAccountPolicyRecovery"]
    assert admin["Principal"]["AWS"] == "arn:aws:iam::111122223333:root"
    assert set(admin["Action"]) == {
        "kms:GetKeyPolicy", "kms:PutKeyPolicy", "kms:DescribeKey"}
    grant = kms["ReaderMayDecryptOnlyThroughS3ForThisObject"]
    assert grant["Principal"]["AWS"] == ROLE
    assert (grant["Effect"], grant["Action"], grant["Resource"]) == (
        "Allow", "kms:Decrypt", "*")
    assert grant["Condition"] == {"StringEquals": {
        "kms:ViaService": "s3.us-east-2.amazonaws.com",
        "kms:EncryptionContext:aws:s3:arn": OBJECT}}
    print("Two JSON policies match the bounded teaching specimen; no IAM evaluation occurred.")


if __name__ == "__main__":
    check()
