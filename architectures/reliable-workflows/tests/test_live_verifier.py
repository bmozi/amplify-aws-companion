"""Local emulation of outage ownership, not live DynamoDB or IAM evidence."""
import sys
import json
import tempfile
import time
from pathlib import Path
import unittest
from unittest.mock import patch, Mock

import boto3
from botocore.exceptions import EndpointConnectionError
from moto import mock_aws

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify_live


class LiveIdentityBoundaryTests(unittest.TestCase):
    def test_root_rejected_before_any_workload_client(self):
        with tempfile.TemporaryDirectory() as folder:
            cfg = Path(folder) / 'outputs.json'
            cfg.write_text(json.dumps({'name': 'amplify-patterns-fixture', 'region': 'us-east-2',
                'expires_at_epoch': time.time() + 1200, 'account': '123456789012'}))
            session = Mock()
            session.client.return_value.get_caller_identity.return_value = {
                'Account': '123456789012', 'Arn': 'arn:aws:iam::123456789012:root'}
            with patch.object(verify_live.boto3, 'Session', return_value=session), patch.object(
                sys, 'argv', ['verify_live.py', '--profile', 'fixture', '--outputs', str(cfg),
                              '--evidence', str(Path(folder) / 'evidence.json')]):
                with self.assertRaisesRegex(ValueError, 'temporary assumed-role'):
                    verify_live.main()
            self.assertEqual([call.args[0] for call in session.client.call_args_list], ['sts'])
            session.resource.assert_not_called()


@mock_aws
class OutageOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.db = boto3.resource('dynamodb', region_name='us-east-2').meta.client
        self.db.create_table(TableName='fixture',
            KeySchema=[{'AttributeName': 'pk', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'pk', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST')

    def marker(self):
        return self.db.get_item(TableName='fixture', Key={'pk': 'control#scheduler'}).get('Item')

    def test_own_marker_removed_and_repeat_cleanup_harmless(self):
        verify_live.claim_outage(self.db, 'fixture', 'run-a')
        self.assertTrue(self.marker()['unavailable'])
        self.assertTrue(verify_live.release_outage(self.db, 'fixture', 'run-a'))
        self.assertIsNone(self.marker())
        self.assertFalse(verify_live.release_outage(self.db, 'fixture', 'run-a'))

    def test_existing_outage_survives_failed_claim_and_cleanup(self):
        verify_live.claim_outage(self.db, 'fixture', 'run-a')
        before = self.marker()
        with self.assertRaises(self.db.exceptions.ConditionalCheckFailedException):
            verify_live.claim_outage(self.db, 'fixture', 'run-b')
        self.assertFalse(verify_live.release_outage(self.db, 'fixture', 'run-b'))
        self.assertEqual(self.marker(), before)

    def test_legacy_unowned_marker_is_not_deleted(self):
        self.db.put_item(TableName='fixture', Item={'pk': 'control#scheduler', 'unavailable': True})
        self.assertFalse(verify_live.release_outage(self.db, 'fixture', 'run-a'))
        self.assertIsNotNone(self.marker())

    def test_lost_claim_reply_can_be_cleaned_by_owner(self):
        put = self.db.put_item
        def lost_reply(**kwargs):
            put(**kwargs)
            raise EndpointConnectionError(endpoint_url='https://fixture.invalid')
        with patch.object(self.db, 'put_item', side_effect=lost_reply):
            with self.assertRaises(EndpointConnectionError):
                verify_live.claim_outage(self.db, 'fixture', 'run-a')
        self.assertTrue(verify_live.release_outage(self.db, 'fixture', 'run-a'))
        self.assertIsNone(self.marker())

    def test_cleanup_transport_failure_is_not_reported_as_absence(self):
        with patch.object(self.db, 'delete_item', side_effect=EndpointConnectionError(endpoint_url='https://fixture.invalid')):
            with self.assertRaises(EndpointConnectionError):
                verify_live.release_outage(self.db, 'fixture', 'run-a')


if __name__ == '__main__':
    unittest.main()
