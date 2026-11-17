import json
import tempfile
import unittest
from pathlib import Path

from export_cases import CASES, export_cases
from review import BASELINE, proposed_template, review


class ChangeReviewTests(unittest.TestCase):
    def test_replacement_stays_on_hold_with_retained_data_unobserved(self):
        result = review("name")
        self.assertEqual(result["decision"], "HOLD")
        self.assertEqual(result["documented_property_update_behavior"]["BucketName"], "Replacement")
        self.assertIsNone(result["new_bucket_object_count_observed"])
        resources = proposed_template("name")["Resources"]
        self.assertEqual(resources["ArchiveBucket"]["UpdateReplacePolicy"], "Retain")
        self.assertEqual(resources["TransportPolicy"]["DeletionPolicy"], "Retain")
        self.assertEqual(resources["TransportPolicy"]["UpdateReplacePolicy"], "Retain")

    def test_security_regression_holds_even_without_replacement(self):
        result = review("public")
        self.assertEqual(result["documented_property_update_behavior"]["PublicAccessBlockConfiguration"], "No interruption")
        self.assertEqual(result["decision"], "HOLD")

    def test_unknown_property_never_receives_a_safe_guess(self):
        self.assertEqual(review("unknown")["decision"], "HOLD")
        self.assertIn("Unknown", review("unknown")["documented_property_update_behavior"]["UnfamiliarFutureProperty"])

    def test_bucket_policy_change_cannot_hide_behind_unchanged_bucket_properties(self):
        result = review("transport")
        self.assertEqual(result["changed_bucket_properties"], [])
        self.assertEqual(result["changed_other_resources"], ["TransportPolicy"])
        self.assertEqual(result["decision"], "HOLD")
        self.assertEqual(proposed_template("transport")["Resources"]["TransportPolicy"]["Properties"]["PolicyDocument"]["Statement"], [])

    def test_study_does_not_edit_the_baseline(self):
        before = BASELINE.read_bytes()
        self.assertEqual(review("tag")["decision"], "REVIEW_WITH_CHANGE_SET")
        self.assertEqual(json.loads(before)["Resources"]["ArchiveBucket"]["Properties"].get("BucketName"), None)
        self.assertEqual(BASELINE.read_bytes(), before)

    def test_exported_templates_are_the_reviewed_cases_and_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as scratch:
            destination = Path(scratch) / "cases"
            paths = export_cases(destination)
            self.assertEqual({p.stem for p in paths}, {"baseline", *CASES})
            for case in CASES:
                self.assertEqual(json.loads((destination / f"{case}.json").read_text()), proposed_template(case))
            with self.assertRaises(FileExistsError):
                export_cases(destination)


if __name__ == "__main__":
    unittest.main()
