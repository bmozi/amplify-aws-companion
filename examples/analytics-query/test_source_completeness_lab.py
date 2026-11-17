"""Negative controls for self-consistent but incomplete analytics output."""

import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import file_publication_lab as publication
import source_completeness_lab as lab


REGISTER = json.loads(Path(lab.REGISTER).read_text())


class SourceCompletenessTests(unittest.TestCase):
    def test_manifest_can_pass_while_separate_register_finds_missing_sale(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            publication.stage(root, 'missing-sale', 2, [[('a', 100), ('b', 180)], []], ['a', 'b'])
            self.assertEqual(publication.publish(root, 'missing-sale', 0), ('published', 1))
            self.assertEqual(publication.candidate(root, 'missing-sale')[0]['expected_ids'], ['a', 'b'])
            result = lab.reconcile(publication.read_view(root), REGISTER)
            self.assertEqual(result['status'], 'hold_for_reconciliation')
            self.assertEqual(result['missing_receipt_ids'], ['late'])
            self.assertFalse(result['view_matches_closing_controls'])

    def test_corrected_report_matches_supplied_register(self):
        view = {'rows': [('a', 100), ('b', 180), ('late', 50)]}
        self.assertEqual(lab.reconcile(view, REGISTER)['status'], 'matches_supplied_register')

    def test_equal_count_and_total_do_not_hide_wrong_identity(self):
        view = {'rows': [('a', 100), ('b', 180), ('other', 50)]}
        result = lab.reconcile(view, REGISTER)
        self.assertTrue(result['view_matches_closing_controls'])
        self.assertEqual(result['status'], 'hold_for_reconciliation')
        self.assertEqual(result['missing_receipt_ids'], ['late'])
        self.assertEqual(result['unexpected_receipt_ids'], ['other'])

    def test_register_list_can_conflict_with_separate_closing_controls(self):
        register = copy.deepcopy(REGISTER)
        register['receipts'].pop()
        result = lab.reconcile({'rows': [('a', 100), ('b', 180)]}, register)
        self.assertFalse(result['register_controls_agree'])
        self.assertEqual(result['status'], 'hold_for_reconciliation')

    def test_missing_register_stays_unknown(self):
        self.assertEqual(lab.reconcile({'rows': [('a', 100)]}, None)['status'],
                         'unknown_no_independent_register')


if __name__ == '__main__':
    unittest.main()
