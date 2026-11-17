import importlib.util
from pathlib import Path
import unittest


LAB_PATH = Path(__file__).with_name('build-trust-lab.py')
spec = importlib.util.spec_from_file_location('build_trust_lab', LAB_PATH)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class BuildTrustTests(unittest.TestCase):
    def test_digest_rejects_change_after_build(self):
        self.assertEqual(lab.results()['changed_after_hash'], (False, False))

    def test_builder_can_hash_its_own_changed_output(self):
        self.assertEqual(lab.results()['changed_in_build'], (True, False))

    def test_approved_source_bytes_and_receipt_agree(self):
        self.assertEqual(lab.results()['approved'], (True, True))


if __name__ == '__main__':
    unittest.main()
