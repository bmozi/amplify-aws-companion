"""Changed cases for the local build-to-response destination boundary."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from audit_built_outputs import audit as whole_folder_audit, read_build
from served_entry_lab import inspect, main, read_response
from test_inspect_outputs import sample


def make_case(directory, entry_values=None, decoy_values=None, script_source="/assets/main.js"):
    root = Path(directory)
    built = root / "dist"
    (built / "assets").mkdir(parents=True)
    (built / "index.html").write_text(
        f'<html><script type="module" src="{script_source}"></script></html>')
    document = sample()
    values = [document[section][field] for section, field in (
        ("auth", "user_pool_id"), ("auth", "user_pool_client_id"),
        ("auth", "identity_pool_id"), ("data", "url"), ("storage", "bucket_name"))]
    (built / "assets/main.js").write_text("const values=" + json.dumps(
        values if entry_values is None else entry_values) + ";")
    if decoy_values is not None:
        (built / "assets/unused.js").write_text("const unused=" + json.dumps(decoy_values) + ";")
    outputs = root / "outputs.json"
    outputs.write_text(json.dumps(document))
    return document, outputs, built, values


class ServedEntryTests(unittest.TestCase):
    def test_real_loopback_response_contains_selected_values_without_printing_them(self):
        with tempfile.TemporaryDirectory() as directory:
            document, outputs, built, values = make_case(directory)
            stream = io.StringIO()
            with redirect_stdout(stream):
                self.assertEqual(main([str(outputs), str(built)]), 0)
            report = json.loads(stream.getvalue())
            self.assertTrue(report["local_served_entry_check_passed"])
            self.assertEqual(report["response_matches_local_build"], [True])
            self.assertTrue(all(report["selected_values_found_in_served_entries"].values()))
            for value in values:
                self.assertNotIn(value, stream.getvalue())

    def test_unused_decoy_makes_folder_scan_green_but_served_entry_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            document, _, built, values = make_case(
                directory, entry_values=["https://wrong.example.invalid/graphql"],
                decoy_values=sample_values(sample()))
            contents, digest = read_build(built)
            self.assertTrue(whole_folder_audit(document, "a" * 64, contents, digest)
                            ["local_selected_literal_check_passed"])
            report = inspect(document, "a" * 64, built)
            self.assertFalse(report["local_served_entry_check_passed"])
            self.assertFalse(report["selected_values_found_in_served_entries"]["data.url"])
            self.assertEqual(len(values), 5)

    def test_changed_server_response_fails_byte_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            document, _, built, _ = make_case(directory)
            def changed_response(url, maximum):
                body = read_response(url, maximum)
                return body + b"\n// changed in transit" if url.endswith(".js") else body
            with patch("served_entry_lab.read_response", side_effect=changed_response):
                report = inspect(document, "a" * 64, built)
            self.assertFalse(report["local_served_entry_check_passed"])
            self.assertEqual(report["response_matches_local_build"], [False])

    def test_distinct_forbidden_data_value_fails_while_shared_auth_is_neutral(self):
        with tempfile.TemporaryDirectory() as directory:
            document, _, built, values = make_case(directory)
            forbidden = deepcopy(document)
            forbidden["data"]["url"] = "https://other.example.invalid/graphql"
            (built / "assets/main.js").write_text("const values=" + json.dumps(
                values + [forbidden["data"]["url"]]) + ";")
            report = inspect(document, "a" * 64, built, forbidden, "b" * 64)
            self.assertFalse(report["local_served_entry_check_passed"])
            self.assertTrue(report["distinct_forbidden_values_found_in_served_entries"]["data.url"])
            self.assertIsNone(report["distinct_forbidden_values_found_in_served_entries"]["auth.user_pool_id"])

    def test_external_module_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            document, _, built, _ = make_case(
                directory, script_source="https://other.example.invalid/main.js")
            with self.assertRaisesRegex(ValueError, "same-origin"):
                inspect(document, "a" * 64, built)


def sample_values(document):
    return [document[section][field] for section, field in (
        ("auth", "user_pool_id"), ("auth", "user_pool_client_id"),
        ("auth", "identity_pool_id"), ("data", "url"), ("storage", "bucket_name"))]


if __name__ == "__main__":
    unittest.main()
