"""Negative controls for the companion media screen."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


spec = spec_from_file_location(
    "media_audit", Path(__file__).resolve().parents[1] / "audit-companion-media.py")
media_audit = module_from_spec(spec)
spec.loader.exec_module(media_audit)


class MediaAuditTests(unittest.TestCase):
    def test_described_vector_is_accepted(self):
        source = b'<svg xmlns="http://www.w3.org/2000/svg"><title>Path</title><desc>Two steps</desc><path d="M0 0L1 1"/></svg>'
        self.assertEqual(media_audit.screen_svg("path.svg", source)["findings"], [])

    def test_external_and_embedded_content_is_reported(self):
        source = b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.invalid/a.png"/><script>bad()</script></svg>'
        findings = media_audit.screen_svg("unsafe.svg", source)["findings"]
        for expected in ("missing title", "missing description", "embedded image",
                         "embedded script", "external or data reference"):
            self.assertIn(expected, findings)

    def test_relative_asset_reference_is_reported(self):
        source = b'<svg xmlns="http://www.w3.org/2000/svg"><title>Path</title><desc>Steps</desc><use href="other.svg#shape"/></svg>'
        self.assertIn("external or data reference",
                      media_audit.screen_svg("relative.svg", source)["findings"])


if __name__ == "__main__":
    unittest.main()
