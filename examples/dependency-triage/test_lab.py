import json
from pathlib import Path
import unittest

from lab import summarize


FIXTURE = Path(__file__).with_name('fixture.json')


class AuditTriageTests(unittest.TestCase):
    def test_inherited_package_entries_are_not_new_advisories(self):
        result = summarize(json.loads(FIXTURE.read_text()))
        self.assertEqual(result['affected_package_entries'], 3)
        self.assertEqual(result['unique_advisory_urls'], 1)
        self.assertEqual(result['direct_dependency_entries'], ['parent-tool'])
        self.assertEqual(result['advisories'][0]['root_finding_package_entries'], ['nested-library'])

    def test_incomplete_or_inconsistent_report_is_rejected(self):
        for report in ({'error': 'registry unavailable'},
                       {'metadata': {'vulnerabilities': {'total': 2}},
                        'vulnerabilities': {'a': {'via': []}}},
                       {'metadata': {'vulnerabilities': {'total': 1}},
                        'vulnerabilities': {'a': {'via': ['missing-root']}}}):
            with self.subTest(report=report), self.assertRaises(ValueError):
                summarize(report)

    def test_two_distinct_advisories_remain_two(self):
        report = json.loads(FIXTURE.read_text())
        report['vulnerabilities']['nested-library']['via'].append(
            {'url': 'https://example.invalid/advisory-two'})
        result = summarize(report)
        self.assertEqual(result['unique_advisory_urls'], 2)


if __name__ == '__main__':
    unittest.main()
