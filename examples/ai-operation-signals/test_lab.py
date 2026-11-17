import copy
import json
import unittest

from lab import HERE, summarize


class AIOperationSignalsTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((HERE / "observations.json").read_text())

    def test_normal_latency_does_not_hide_review_signal(self):
        report = summarize(self.payload)
        self.assertTrue(report["review_signal"])
        self.assertEqual(report["current"]["unsupported"], 2)
        self.assertEqual(report["current"]["reviewed"], 4)
        self.assertLess(report["current"]["latency_mean_ms"], report["baseline"]["latency_mean_ms"])

    def test_unreviewed_is_not_a_supported_answer(self):
        changed = copy.deepcopy(self.payload)
        changed["windows"]["current"][3]["review"] = "unreviewed"
        report = summarize(changed)
        self.assertEqual(report["current"]["reviewed"], 3)
        self.assertFalse(report["review_signal"])

    def test_missing_source_version_is_rejected(self):
        changed = copy.deepcopy(self.payload)
        del changed["windows"]["current"][0]["source_version"]
        with self.assertRaises(ValueError):
            summarize(changed)

    def test_duplicate_observation_is_rejected(self):
        changed = copy.deepcopy(self.payload)
        changed["windows"]["current"][0]["id"] = "b1"
        with self.assertRaises(ValueError):
            summarize(changed)


if __name__ == "__main__":
    unittest.main()
