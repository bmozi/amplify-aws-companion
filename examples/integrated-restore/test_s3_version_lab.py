"""Changed-outcome checks for the emulated versioned object path."""

from hashlib import sha256
import unittest

from botocore.exceptions import ClientError
from moto import mock_aws

from s3_version_lab import (
    BOOKING, BUCKET, EXPECTED_PHOTO, NEIGHBOR, NEIGHBOR_PHOTO, OWNER,
    client, exact_versions, key_for, read_version, seed, stage_confirmed_photo,
)


class S3VersionRecoveryTests(unittest.TestCase):
    def setUp(self):
        context = mock_aws()
        context.start()
        self.addCleanup(context.stop)
        self.s3 = client()
        self.ids = seed(self.s3)
        self.digest = sha256(EXPECTED_PHOTO).hexdigest()

    def stage(self, version_id=None, digest=None, actor=OWNER):
        return stage_confirmed_photo(
            self.s3, actor=actor,
            version_id=self.ids["confirmed_version"] if version_id is None else version_id,
            confirmed_version=self.ids["confirmed_version"],
            confirmation_digest=self.digest if digest is None else digest,
        )

    def test_delete_marker_hides_current_but_retains_exact_versions(self):
        with self.assertRaises(ClientError) as caught:
            self.s3.get_object(Bucket=BUCKET, Key=key_for(OWNER))
        self.assertEqual(caught.exception.response["Error"]["Code"], "NoSuchKey")
        versions, markers = exact_versions(self.s3, key_for(OWNER))
        self.assertEqual({row["VersionId"] for row in versions},
                         {self.ids["confirmed_version"], self.ids["wrong_version"]})
        self.assertEqual([row["VersionId"] for row in markers], [self.ids["delete_marker"]])
        self.assertTrue(markers[0]["IsLatest"])
        self.assertEqual(read_version(self.s3, OWNER, OWNER, self.ids["confirmed_version"]),
                         EXPECTED_PHOTO)

    def test_wrong_version_and_missing_confirmation_cannot_be_staged(self):
        with self.assertRaisesRegex(ValueError, "confirmed database point"):
            self.stage(version_id=self.ids["wrong_version"])
        with self.assertRaisesRegex(ValueError, "Independent confirmation"):
            self.stage(digest="")
        with self.assertRaisesRegex(ValueError, "Object bytes disagree"):
            self.stage(digest="0" * 64)
        with self.assertRaises(ClientError):
            self.s3.get_object(Bucket=BUCKET, Key=f"recovery-candidates/{OWNER}/{BOOKING}")

    def test_other_actor_is_denied_by_fixture_guard(self):
        with self.assertRaises(PermissionError):
            read_version(self.s3, NEIGHBOR, OWNER, self.ids["confirmed_version"])
        with self.assertRaises(PermissionError):
            self.stage(actor=NEIGHBOR)
        self.assertEqual(self.s3.get_object(Bucket=BUCKET, Key=key_for(OWNER),
                                            VersionId=self.ids["confirmed_version"])["Body"].read(),
                         EXPECTED_PHOTO)  # broad mock client bypasses the fixture route
        self.assertEqual(read_version(self.s3, NEIGHBOR, NEIGHBOR,
                                      self.ids["neighbor_version"]), NEIGHBOR_PHOTO)

    def test_stage_keeps_original_marker_and_neighbor_unchanged(self):
        target = self.stage()
        self.assertEqual(self.s3.get_object(Bucket=BUCKET, Key=target)["Body"].read(),
                         EXPECTED_PHOTO)
        self.assertTrue(exact_versions(self.s3, key_for(OWNER))[1][0]["IsLatest"])
        self.assertEqual(read_version(self.s3, NEIGHBOR, NEIGHBOR,
                                      self.ids["neighbor_version"]), NEIGHBOR_PHOTO)

    def test_permanently_removed_old_version_cannot_be_recovered(self):
        self.s3.delete_object(Bucket=BUCKET, Key=key_for(OWNER),
                              VersionId=self.ids["confirmed_version"])
        with self.assertRaises(ClientError):
            self.stage()
        versions, _ = exact_versions(self.s3, key_for(OWNER))
        self.assertNotIn(self.ids["confirmed_version"],
                         {row["VersionId"] for row in versions})


if __name__ == "__main__":
    unittest.main()
