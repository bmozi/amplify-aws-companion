"""Check both the allowed case and fail-closed changed conditions."""

import unittest

from demo import run


class SignedReleaseGateTest(unittest.TestCase):
    def test_exact_artifact_and_report_are_required(self):
        result = run()
        self.assertEqual(result["signed_and_current"], "ALLOW: local evidence gate passed")
        self.assertEqual(result["known_nonblocking_findings"], "ALLOW: local evidence gate passed")
        for name in ("unsigned", "changed_artifact", "changed_report", "wrong_signer",
                     "stale_signed_scan", "open_high_finding", "os_only_coverage",
                     "signed_incomplete_scan", "signed_scan_of_A", "unknown_severity", "unknown_status"):
            with self.subTest(name=name):
                self.assertTrue(result[name].startswith("HOLD:"), result[name])
        self.assertEqual(len(result), 13)


if __name__ == "__main__":
    unittest.main()
