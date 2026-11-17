"""Check overlapping local publishers and reader-visible complete revisions."""

from pathlib import Path
from contextlib import closing
from tempfile import TemporaryDirectory
import unittest

import competing_publishers_lab as lab


class CompetingPublishersTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        lab.staged_fixture(self.root)
        self.db_path = self.root / 'selection.sqlite3'
        lab.initialize(self.db_path)

    def tearDown(self):
        self.temp.cleanup()

    def test_overlapping_publishers_select_one_complete_revision(self):
        outcomes = lab.race(self.root, self.db_path)
        self.assertEqual(sorted(result[0] for result in outcomes.values()),
                         ['published', 'stale_generation'])
        view = lab.read_view(self.db_path, self.root)
        winner = view['pointer']['run_id']
        self.assertEqual(view['pointer']['generation'], 2)
        self.assertEqual(outcomes[winner], ('published', 2))
        self.assertEqual(view['cents'], {'v2': 330, 'v3': 340}[winner])
        self.assertEqual(len(view['rows']), 3)

    def test_missing_manifest_and_stale_revision_leave_old_selected(self):
        self.assertEqual(lab.publish(self.db_path, self.root, 'missing', 1),
                         ('missing_complete_run', 1))
        self.assertEqual(lab.publish(self.db_path, self.root, 'v1', 1),
                         ('already_current', 1))
        self.assertEqual(lab.read_view(self.db_path, self.root)['cents'], 300)

    def test_old_reader_can_stay_pinned_after_selection(self):
        with closing(lab.connect(self.db_path)) as db:
            pinned = lab.selection(db)
        self.assertEqual(lab.publish(self.db_path, self.root, 'v2', 1), ('published', 2))
        self.assertEqual(lab.files.read_view(self.root, pinned)['cents'], 300)
        self.assertEqual(lab.read_view(self.db_path, self.root)['cents'], 330)


if __name__ == '__main__':
    unittest.main()
