"""Changed-condition checks for the local A10 authority choice."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('job_authority_lab', HERE / 'job_authority_lab.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class JobAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.lab = MODULE.JobAuthority(Path(self.tmp.name) / 'jobs.sqlite')

    def test_revoked_delegation_stops_even_after_early_green_preview(self):
        job = self.lab.submit('alice', 'shop-a', 'same-id', 'personal_report')
        self.assertTrue(self.lab.preview(job))
        self.lab.revoke('alice', 'shop-a')
        with self.assertRaises(PermissionError):
            self.lab.execute(job)
        self.assertEqual([], self.lab.effects())

    def test_separately_accepted_workflow_survives_user_revocation_once(self):
        job = self.lab.submit('alice', 'shop-a', 'same-id', 'repair_followup')
        self.lab.revoke('alice', 'shop-a')
        self.assertEqual('done', self.lab.execute(job))
        self.assertEqual('already_done', self.lab.execute(job))
        self.assertEqual([(job, 'shop-a')], self.lab.effects())

    def test_rejoining_does_not_reanimate_old_delegated_job(self):
        old = self.lab.submit('alice', 'shop-a', 'same-id', 'personal_report')
        self.lab.revoke('alice', 'shop-a')
        self.lab.reinstate('alice', 'shop-a')
        with self.assertRaises(PermissionError):
            self.lab.execute(old)
        new = self.lab.submit('alice', 'shop-a', 'same-id', 'personal_report')
        self.assertEqual('done', self.lab.execute(new))
        self.assertEqual([(new, 'shop-a')], self.lab.effects())

    def test_tenant_closure_stops_both_authority_modes(self):
        jobs = [self.lab.submit('alice', 'shop-a', 'same-id', action)
                for action in ('personal_report', 'repair_followup')]
        self.lab.close_tenant('shop-a')
        for job in jobs:
            with self.assertRaises(PermissionError):
                self.lab.execute(job)
        self.assertEqual([], self.lab.effects())

    def test_colliding_id_and_forged_tenant_cannot_cross(self):
        with self.assertRaises(PermissionError):
            self.lab.submit('alice', 'shop-b', 'same-id', 'repair_followup')
        a = self.lab.submit('alice', 'shop-a', 'same-id', 'repair_followup')
        b = self.lab.submit('bob', 'shop-b', 'same-id', 'personal_report')
        self.lab.revoke('alice', 'shop-a')
        self.assertEqual('done', self.lab.execute(a))
        self.assertEqual('done', self.lab.execute(b))
        self.assertEqual([(a, 'shop-a'), (b, 'shop-b')], self.lab.effects())

    def test_no_new_submission_after_revocation_or_unknown_authority(self):
        with self.assertRaises(ValueError):
            self.lab.submit('alice', 'shop-a', 'same-id', 'magic')
        self.lab.revoke('alice', 'shop-a')
        with self.assertRaises(PermissionError):
            self.lab.submit('alice', 'shop-a', 'same-id', 'repair_followup')

    def test_stored_authority_cannot_be_relabelled_as_workflow(self):
        job = self.lab.submit('alice', 'shop-a', 'same-id', 'personal_report')
        import sqlite3
        with sqlite3.connect(self.lab.path) as db:
            db.execute('UPDATE jobs SET authority=? WHERE id=?', ('accepted_workflow', job))
        self.lab.revoke('alice', 'shop-a')
        with self.assertRaises(PermissionError):
            self.lab.execute(job)
        self.assertEqual([], self.lab.effects())


if __name__ == '__main__':
    unittest.main()
