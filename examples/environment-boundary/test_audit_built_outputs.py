"""Focused negative controls for redacted local browser-bundle inspection."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest

from audit_built_outputs import audit, main, read_build
from test_inspect_outputs import sample


class BuiltOutputsAuditTests(unittest.TestCase):
    def make_build(self, root, document, omit=(), extra=()):
        target = Path(root) / 'dist'
        (target / 'assets').mkdir(parents=True)
        (target / 'index.html').write_text('<script src="/assets/main.js"></script>')
        values = [document[section][field] for section, field in (
            ('auth', 'user_pool_id'), ('auth', 'user_pool_client_id'),
            ('auth', 'identity_pool_id'), ('data', 'url'), ('storage', 'bucket_name'))]
        (target / 'assets/main.js').write_text('const targets=' + json.dumps(
            [value for value in values if value not in omit] + list(extra)) + ';')
        return target

    def write_outputs(self, root, name, document):
        path = Path(root) / name
        path.write_text(json.dumps(document))
        return path

    def test_real_shape_selected_values_present_without_printing_them(self):
        with tempfile.TemporaryDirectory() as directory:
            document = sample()
            outputs = self.write_outputs(directory, 'outputs.json', document)
            built = self.make_build(directory, document)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main([str(outputs), str(built)]), 0)
            report = json.loads(out.getvalue())
            self.assertTrue(report['local_selected_literal_check_passed'])
            self.assertTrue(all(report['selected_values_found_in_js'].values()))
            for section, field in (('auth', 'user_pool_id'), ('data', 'url'),
                                   ('storage', 'bucket_name')):
                self.assertNotIn(document[section][field], out.getvalue())

    def test_missing_selected_value_and_distinct_forbidden_value_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            document = sample()
            outputs = self.write_outputs(directory, 'outputs.json', document)
            forbidden = deepcopy(document)
            forbidden['data']['url'] = 'https://forbidden.example.invalid/graphql'
            forbidden_path = self.write_outputs(directory, 'forbidden.json', forbidden)
            built = self.make_build(directory, document,
                                    omit=(document['data']['url'],),
                                    extra=(forbidden['data']['url'],))
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main([str(outputs), str(built),
                                       '--forbid-outputs', str(forbidden_path)]), 1)
            report = json.loads(out.getvalue())
            self.assertFalse(report['selected_values_found_in_js']['data.url'])
            self.assertTrue(report['distinct_forbidden_values_found_in_js']['data.url'])
            self.assertNotIn('forbidden.example.invalid', out.getvalue())

    def test_shared_destination_is_not_called_forbidden(self):
        with tempfile.TemporaryDirectory() as directory:
            document = sample()
            built = self.make_build(directory, document)
            contents, digest = read_build(built)
            forbidden = deepcopy(document)
            forbidden['data']['url'] = 'https://another.example.invalid/graphql'
            report = audit(document, 'a' * 64, contents, digest, forbidden, 'b' * 64)
            self.assertTrue(report['local_selected_literal_check_passed'])
            self.assertIsNone(report['distinct_forbidden_values_found_in_js']['auth.user_pool_id'])
            self.assertFalse(report['distinct_forbidden_values_found_in_js']['data.url'])

    def test_sourcemap_does_not_count_as_built_javascript(self):
        with tempfile.TemporaryDirectory() as directory:
            document = sample()
            built = self.make_build(directory, document, omit=(document['storage']['bucket_name'],))
            (built / 'assets/main.js.map').write_text(document['storage']['bucket_name'])
            out = io.StringIO()
            outputs = self.write_outputs(directory, 'outputs.json', document)
            with redirect_stdout(out):
                self.assertEqual(main([str(outputs), str(built)]), 1)
            self.assertFalse(json.loads(out.getvalue())['selected_values_found_in_js']['storage.bucket_name'])


if __name__ == '__main__':
    unittest.main()
