"""Negative controls for exact vector-to-Kindle artifact continuity."""

import importlib.util
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "build-kindle-raster-diagnostic.py"
SPEC = importlib.util.spec_from_file_location("kindle_raster", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@unittest.skipUnless(shutil.which("rsvg-convert"), "rsvg-convert is required")
class ExactPairTest(unittest.TestCase):
    def write_vector(self, path: Path, color: str = "#123456", sentence: str = "One dataset.") -> None:
        members = {
            "mimetype": b"application/epub+zip",
            "EPUB/content.opf": b'<item href="media/file0.svg" media-type="image/svg+xml"/>',
            "EPUB/text/ch001.xhtml": f'<p>{sentence}</p><img src="../media/file0.svg" alt="Two doors"/>'.encode(),
            "EPUB/media/file0.svg": f'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320"><rect width="320" height="320" fill="{color}"/></svg>'.encode(),
        }
        with zipfile.ZipFile(path, "w") as output:
            for name, data in members.items():
                output.writestr(name, data, compress_type=zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED)

    def test_exact_pair_rejects_stale_prose_and_figure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            vector = root / "vector.epub"
            raster = root / "raster.epub"
            self.write_vector(vector)
            MODULE.build(vector, raster, 320, True)
            self.assertEqual(MODULE.verify_pair(vector, raster, 320, True), 1)
            self.write_vector(vector, sentence="A changed lesson.")
            with self.assertRaisesRegex(ValueError, "differs from exact source"):
                MODULE.verify_pair(vector, raster, 320, True)
            self.write_vector(vector, color="#654321")
            with self.assertRaisesRegex(ValueError, "differs from exact source"):
                MODULE.verify_pair(vector, raster, 320, True)


if __name__ == "__main__":
    unittest.main()
