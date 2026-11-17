"""Behavior checks for the local multi-file publication boundary."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import file_publication_lab as lab


OLD = [[('a', 100), ('b', 200)], []]
NEW = [[('a', 100), ('b', 180)], [('late', 50)]]


class FilePublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.assertEqual(lab.stage(self.root, 'v1', 1, OLD, ['a', 'b']), 'staged')
        self.assertEqual(lab.publish(self.root, 'v1', 0), ('published', 1))

    def tearDown(self):
        self.temp.cleanup()

    def test_failed_stage_keeps_old_complete_view(self):
        with self.assertRaisesRegex(RuntimeError, 'Injected failure'):
            lab.stage(self.root, 'v2', 2, NEW, ['a', 'b', 'late'], fail_after=1)
        self.assertEqual(lab.publish(self.root, 'v2', 1), ('missing_complete_run', 1))
        self.assertEqual(lab.read_view(self.root)['cents'], 300)
        self.assertEqual(lab.stage(self.root, 'v2', 2, NEW, ['a', 'b', 'late']), 'staged')
        self.assertEqual(lab.publish(self.root, 'v2', 1), ('published', 2))
        self.assertEqual(lab.read_view(self.root)['rows'], [('a', 100), ('b', 180), ('late', 50)])

    def test_mutable_latest_exposes_wrong_midwrite_total(self):
        mixed = lab.unsafe_midwrite_view(self.root, OLD, NEW[0])
        self.assertEqual(mixed['rows'], [('a', 100), ('b', 180)])
        self.assertEqual(mixed['cents'], 280)
        self.assertNotIn(mixed['cents'], (300, 330))

    def test_changed_part_is_rejected_before_selection(self):
        lab.stage(self.root, 'v2', 2, NEW, ['a', 'b', 'late'])
        part = self.root / 'candidates/v2/part-2.json'
        part.write_text(json.dumps([['late', 500]]) + '\n')
        with self.assertRaisesRegex(ValueError, 'Selected part changed'):
            lab.publish(self.root, 'v2', 1)
        self.assertEqual(lab.read_view(self.root)['cents'], 300)

    def test_changed_selected_part_is_rejected_by_reader(self):
        lab.stage(self.root, 'v2', 2, NEW, ['a', 'b', 'late'])
        lab.publish(self.root, 'v2', 1)
        part = self.root / 'candidates/v2/part-2.json'
        part.write_text(json.dumps([['late', 500]]) + '\n')
        with self.assertRaisesRegex(ValueError, 'Selected part changed'):
            lab.read_view(self.root)

    def test_lost_reply_retry_finds_new_selection(self):
        lab.stage(self.root, 'v2', 2, NEW, ['a', 'b', 'late'])
        with self.assertRaisesRegex(RuntimeError, 'lost reply'):
            lab.publish(self.root, 'v2', 1, fail_after_pointer=True)
        self.assertEqual(lab.publish(self.root, 'v2', 1), ('already_current', 2))
        self.assertEqual(lab.read_view(self.root)['cents'], 330)

    def test_pinned_old_reader_requires_old_parts_to_remain(self):
        old_pointer = lab.selected(self.root)
        lab.stage(self.root, 'v2', 2, NEW, ['a', 'b', 'late'])
        lab.publish(self.root, 'v2', 1)
        self.assertEqual(lab.read_view(self.root, old_pointer)['cents'], 300)
        (self.root / 'candidates/v1/part-1.json').unlink()
        with self.assertRaises(FileNotFoundError):
            lab.read_view(self.root, old_pointer)
        self.assertEqual(lab.read_view(self.root)['cents'], 330)

    def test_stale_selection_and_changed_run_input_stop(self):
        lab.stage(self.root, 'v2', 2, NEW, ['a', 'b', 'late'])
        self.assertEqual(lab.publish(self.root, 'v2', 0), ('stale_generation', 1))
        with self.assertRaisesRegex(ValueError, 'changed part bytes'):
            lab.stage(self.root, 'v2', 2, [[('a', 100), ('b', 181)], [('late', 50)]],
                      ['a', 'b', 'late'])
        self.assertEqual(lab.read_view(self.root)['cents'], 300)
        self.assertEqual(lab.publish(self.root, 'v2', 1), ('published', 2))
        self.assertEqual(lab.publish(self.root, 'v1', 2), ('stale_source_revision', 2))


if __name__ == '__main__':
    unittest.main()
