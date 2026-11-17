import copy
import json
from pathlib import Path
import unittest

from prepare_model_packet import prepare

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text())


class ModelPacketBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.packet = load("cases.json")
        self.state = load("trusted-state.json")

    def test_denied_and_stale_text_never_enters_model_input(self):
        prepared = prepare(self.packet, self.state)
        sent = json.dumps(prepared)
        self.assertNotIn("School B retains", sent)
        self.assertNotIn("essay text appeared", sent)
        self.assertNotIn("Old rule: completed exports", sent)
        self.assertNotIn("source_note", sent)
        by_id = {case["id"]: case for case in prepared["cases"]}
        self.assertEqual([item["document_id"] for item in by_id["rank-is-not-grant"]["evidence"]],
                         ["a-export"])
        self.assertEqual(by_id["revoked-after-search"]["evidence"], [])
        self.assertEqual(by_id["stale-rule-with-tempting-answer"]["evidence"], [])

    def test_untrusted_source_flags_cannot_grant_access(self):
        for case in self.packet["cases"]:
            for item in case["evidence"]:
                item["authorized"] = True
                item["current"] = True
        sent = json.dumps(prepare(self.packet, self.state))
        self.assertNotIn("School B retains", sent)
        self.assertNotIn("Old rule: completed exports", sent)

    def test_mismatched_or_ambiguous_state_fails_closed(self):
        state = copy.deepcopy(self.state)
        state["cases"]["rank-is-not-grant"]["allowed_current"] = ["missing@v1"]
        with self.assertRaisesRegex(ValueError, "trusted source missing"):
            prepare(self.packet, state)
        state = copy.deepcopy(self.state)
        del state["cases"]["revoked-after-search"]
        with self.assertRaisesRegex(ValueError, "case IDs"):
            prepare(self.packet, state)
        packet = copy.deepcopy(self.packet)
        packet["cases"][0]["evidence"].append(copy.deepcopy(packet["cases"][0]["evidence"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate source"):
            prepare(packet, self.state)


if __name__ == "__main__":
    unittest.main()
