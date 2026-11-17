"""Check the build-input boundary, including paths that would evade a cost count."""

import tempfile
from pathlib import Path
import unittest

from bundle_size import measure


class BundleSizeTests(unittest.TestCase):
    def test_counts_each_referenced_file_once_and_changes_with_asset(self):
        with tempfile.TemporaryDirectory() as temp:
            dist = Path(temp)
            (dist / "index.html").write_text(
                '<script src="/assets/app.js"></script>'
                '<script src="/assets/app.js"></script>'
                '<link rel="stylesheet" href="/assets/app.css">', encoding="utf-8")
            (dist / "assets").mkdir()
            (dist / "assets/app.js").write_text("let n=1;", encoding="utf-8")
            (dist / "assets/app.css").write_text("body{}", encoding="utf-8")
            first = measure(dist)
            self.assertEqual([row["path"] for row in first["files"]],
                             ["index.html", "assets/app.js", "assets/app.css"])
            (dist / "later.html").write_text("later route", encoding="utf-8")
            with_later_route = measure(dist)
            self.assertEqual(with_later_route["raw_entry_bytes"], first["raw_entry_bytes"])
            self.assertEqual(with_later_route["all_static_raw_bytes"] - first["all_static_raw_bytes"], 11)
            (dist / "assets/app.js").write_text("let n=1;" + "x" * 200, encoding="utf-8")
            second = measure(dist)
            self.assertEqual(second["raw_entry_bytes"] - first["raw_entry_bytes"], 200)
            self.assertEqual(second["all_static_raw_bytes"] - with_later_route["all_static_raw_bytes"], 200)
            self.assertNotEqual(second["files"][1]["sha256"], first["files"][1]["sha256"])

    def test_external_missing_and_escape_refs_refuse_measurement(self):
        with tempfile.TemporaryDirectory() as temp:
            dist = Path(temp)
            for reference in ("https://cdn.example/app.js", "/missing.js", "../outside.js"):
                (dist / "index.html").write_text(f'<script src="{reference}"></script>', encoding="utf-8")
                with self.subTest(reference=reference), self.assertRaises(ValueError):
                    measure(dist)


if __name__ == "__main__":
    unittest.main()
