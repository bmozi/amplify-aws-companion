"""Emulated S3 version-read recovery for one fictional booking; no AWS calls."""

from hashlib import sha256
import json

import boto3
from moto import mock_aws


BUCKET = "amplify-recovery-fixture"
OWNER = "shop-a"
NEIGHBOR = "shop-b"
BOOKING = "B111"
EXPECTED_PHOTO = b"photo for booking B111\n"
WRONG_PHOTO = b"wrong replacement photo\n"
NEIGHBOR_PHOTO = b"shop b photo\n"


def client():
    """Use explicit fictional credentials only inside Moto's mock_aws context."""
    return boto3.client(
        "s3", region_name="us-east-2",
        aws_access_key_id="testing", aws_secret_access_key="testing",
    )


def key_for(owner):
    if owner not in (OWNER, NEIGHBOR):
        raise ValueError("Unknown fixture owner")
    return f"photos/{owner}/{BOOKING}"


def seed(s3):
    s3.create_bucket(Bucket=BUCKET,
                     CreateBucketConfiguration={"LocationConstraint": "us-east-2"})
    s3.put_bucket_versioning(Bucket=BUCKET, VersioningConfiguration={"Status": "Enabled"})
    first = s3.put_object(Bucket=BUCKET, Key=key_for(OWNER), Body=EXPECTED_PHOTO)["VersionId"]
    wrong = s3.put_object(Bucket=BUCKET, Key=key_for(OWNER), Body=WRONG_PHOTO)["VersionId"]
    neighbor = s3.put_object(Bucket=BUCKET, Key=key_for(NEIGHBOR), Body=NEIGHBOR_PHOTO)["VersionId"]
    marker = s3.delete_object(Bucket=BUCKET, Key=key_for(OWNER))["VersionId"]
    if len({first, wrong, neighbor, marker}) != 4:
        raise AssertionError("Emulator did not create distinct version IDs")
    return {"confirmed_version": first, "wrong_version": wrong,
            "neighbor_version": neighbor, "delete_marker": marker}


def exact_versions(s3, key):
    """A Prefix listing can include other keys, so retain only this exact key."""
    versions, markers = [], []
    paginator = s3.get_paginator("list_object_versions")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=key):
        versions.extend(row for row in page.get("Versions", []) if row["Key"] == key)
        markers.extend(row for row in page.get("DeleteMarkers", []) if row["Key"] == key)
    return versions, markers


def read_version(s3, actor, owner, version_id):
    """Fixture application guard; this is not an IAM or bucket-policy test."""
    if actor != owner:
        raise PermissionError("Fixture actor cannot read another owner's photo")
    if not isinstance(version_id, str) or not version_id:
        raise ValueError("An exact version ID is required")
    with s3.get_object(Bucket=BUCKET, Key=key_for(owner), VersionId=version_id)["Body"] as body:
        return body.read()


def stage_confirmed_photo(s3, *, actor, version_id, confirmed_version, confirmation_digest):
    """Copy only verified bytes to a separate candidate key; never change the original."""
    if not confirmation_digest:
        raise ValueError("Independent confirmation digest is required")
    if version_id != confirmed_version:
        raise ValueError("Selected version disagrees with the confirmed database point")
    body = read_version(s3, actor, OWNER, version_id)
    if sha256(body).hexdigest() != confirmation_digest:
        raise ValueError("Object bytes disagree with independent confirmation")
    target = f"recovery-candidates/{OWNER}/{BOOKING}"
    s3.put_object(Bucket=BUCKET, Key=target, Body=body)
    return target


@mock_aws
def run():
    s3 = client()
    ids = seed(s3)
    key = key_for(OWNER)
    versions, markers = exact_versions(s3, key)
    assert {row["VersionId"] for row in versions} == {
        ids["confirmed_version"], ids["wrong_version"]}
    assert [row["VersionId"] for row in markers] == [ids["delete_marker"]]
    assert markers[0]["IsLatest"] is True
    target = stage_confirmed_photo(
        s3, actor=OWNER, version_id=ids["confirmed_version"],
        confirmed_version=ids["confirmed_version"],
        confirmation_digest=sha256(EXPECTED_PHOTO).hexdigest(),
    )
    with s3.get_object(Bucket=BUCKET, Key=target)["Body"] as body:
        assert body.read() == EXPECTED_PHOTO
    assert read_version(s3, NEIGHBOR, NEIGHBOR, ids["neighbor_version"]) == NEIGHBOR_PHOTO
    assert exact_versions(s3, key)[1][0]["IsLatest"] is True
    return {
        "confirmed_version_read": True,
        "wrong_version_retained": True,
        "delete_marker_still_current": True,
        "separate_candidate_staged": True,
        "neighbor_unchanged": True,
        "scope": "Moto S3 API and fixture actor guard only; no AWS IAM, KMS, lifecycle, live cost or customer recovery",
    }


def main():
    print(json.dumps(run(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
