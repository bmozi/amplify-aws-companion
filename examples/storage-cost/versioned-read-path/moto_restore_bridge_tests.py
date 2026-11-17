"""Negative controls for the emulated-version to priced-worksheet bridge."""

from decimal import Decimal as D
import unittest

from emulated_restore_bridge import project, run


class MotoRestoreCostBridgeTests(unittest.TestCase):
    def test_inventory_flows_to_selected_cost_and_remains_unapproved(self):
        result = run()
        sizes = result["emulated_inventory_bytes"]
        self.assertEqual(sizes, {"confirmed_original": 23, "wrong_replacement": 24,
                                 "staged_candidate": 23})
        self.assertEqual(sizes["confirmed_original"], sizes["staged_candidate"])
        self.assertEqual(result["retained_through_day_30"]["version_byte_days"],
                         sum(row["bytes"] * (row["removed_day"] - row["created_day"])
                             for row in result["assumed_lifetimes"]))
        self.assertGreater(result["selected_storage_difference_usd"], D(0))
        self.assertEqual(result["retained_through_day_30"]["components_usd"]["internet_out"], D(0))
        self.assertFalse(result["approved_to_deploy"])
        self.assertFalse(result["retained_through_day_30"]["approved_to_deploy"])

    def test_missing_marker_or_candidate_fails_before_pricing(self):
        from priced_lab import SNAPSHOT
        import json
        snapshot = json.loads(SNAPSHOT.read_text())
        ids = {"confirmed_version": "a", "wrong_version": "b", "delete_marker": "m"}
        source = [{"VersionId": "a", "Size": 23}, {"VersionId": "b", "Size": 24}]
        candidate = [{"VersionId": "c", "Size": 23}]
        marker = [{"VersionId": "m", "IsLatest": True}]
        with self.assertRaisesRegex(ValueError, "marker"):
            project(source_versions=source, candidate_versions=candidate, marker_rows=[],
                    ids=ids, snapshot=snapshot)
        with self.assertRaisesRegex(ValueError, "inventory"):
            project(source_versions=source, candidate_versions=[], marker_rows=marker,
                    ids=ids, snapshot=snapshot)
        with self.assertRaisesRegex(ValueError, "size"):
            project(source_versions=source, candidate_versions=[{"VersionId": "c", "Size": 999}],
                    marker_rows=marker, ids=ids, snapshot=snapshot)


if __name__ == "__main__":
    unittest.main()
