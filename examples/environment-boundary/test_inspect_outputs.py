"""Checks for the read-only Gen 2 outputs inspection exercise."""

from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest

from inspect_outputs import inspect, load_outputs, main


def sample():
    return {
        'version': '1.5',
        'auth': {'aws_region': 'us-east-2', 'user_pool_id': 'fixture-pool-secret-looking',
                 'user_pool_client_id': 'fixture-client-secret-looking',
                 'identity_pool_id': 'fixture-identity-pool',
                 'unauthenticated_identities_enabled': False},
        'data': {'aws_region': 'us-east-2', 'url': 'https://fixture-data.example.invalid/graphql',
                 'default_authorization_type': 'AMAZON_COGNITO_USER_POOLS'},
        'storage': {'aws_region': 'us-east-2', 'bucket_name': 'fixture-private-bucket'},
    }


class OutputsInspectionTests(unittest.TestCase):
    def write(self, directory, name, document):
        path = Path(directory) / name
        path.write_text(json.dumps(document))
        return path

    def test_same_and_mixed_destination_comparison_without_identifier_output(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.write(directory, 'first.json', sample())
            same = self.write(directory, 'same.json', sample())
            changed = deepcopy(sample())
            changed['data']['url'] = 'https://different.example.invalid/graphql'
            changed['auth']['user_pool_id'] = 'another-fixture-pool'
            second = self.write(directory, 'second.json', changed)
            document, digest = load_outputs(first)
            same_report = inspect(document, digest, load_outputs(same)[0])
            self.assertTrue(all(same_report['same_destinations_as_comparison'].values()))
            self.assertEqual(same_report['outputs_version'], '1.5')
            changed_report = inspect(document, digest, load_outputs(second)[0])
            self.assertFalse(changed_report['same_destinations_as_comparison']['data.url'])
            self.assertFalse(changed_report['same_destinations_as_comparison']['auth.user_pool_id'])
            self.assertTrue(changed_report['same_destinations_as_comparison']['storage.bucket_name'])
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main([str(first), '--compare', str(second)]), 0)
            self.assertEqual(json.loads(out.getvalue())['comparison_outputs_sha256'], load_outputs(second)[1])
            self.assertNotIn('fixture-pool-secret-looking', json.dumps(changed_report))
            self.assertNotIn('fixture-private-bucket', json.dumps(changed_report))
            self.assertNotIn('fixture-data.example.invalid', json.dumps(changed_report))

    def test_missing_field_and_unsupported_version_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = sample()
            del missing['storage']['bucket_name']
            with self.assertRaisesRegex(ValueError, 'storage.bucket_name'):
                load_outputs(self.write(directory, 'missing.json', missing))
            future = sample()
            future['version'] = '2'
            with self.assertRaisesRegex(ValueError, 'major version 1'):
                load_outputs(self.write(directory, 'future.json', future))

    def test_region_difference_is_reported_not_assumed_wrong(self):
        with tempfile.TemporaryDirectory() as directory:
            mixed = sample()
            mixed['storage']['aws_region'] = 'us-west-2'
            document, digest = load_outputs(self.write(directory, 'mixed.json', mixed))
            report = inspect(document, digest)
            self.assertFalse(report['regions_match_each_other'])
            self.assertEqual(report['regions']['storage'], 'us-west-2')

    def test_separately_reviewed_digest_changes_cli_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, 'outputs.json', sample())
            _, digest = load_outputs(path)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main([str(path), '--expected-sha256', digest]), 0)
            self.assertTrue(json.loads(out.getvalue())['matches_separately_reviewed_digest'])
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main([str(path), '--expected-sha256', '0' * 64]), 1)
            self.assertFalse(json.loads(out.getvalue())['matches_separately_reviewed_digest'])
            err = io.StringIO()
            with redirect_stderr(err):
                self.assertEqual(main([str(path), '--expected-sha256', 'bad']), 2)
            self.assertIn('expected SHA-256', err.getvalue())


if __name__ == '__main__':
    unittest.main()
