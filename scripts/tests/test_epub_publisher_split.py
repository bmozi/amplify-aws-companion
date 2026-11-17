"""Structural checks for the two-page publisher illustration in the EPUB."""
import base64
import importlib.util
from pathlib import Path
import re
import struct
import sys
import unittest

builder = Path(__file__).resolve().parents[1] / 'build-working-epub.py'
sys.path.insert(0, str(builder.parent))
spec = importlib.util.spec_from_file_location('publisher_epub_builder', builder)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def png_size(encoded):
    data = base64.b64decode(encoded)
    if data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        raise ValueError('Expected PNG image')
    return struct.unpack('>II', data[16:24])


class PublisherSplitTests(unittest.TestCase):
    def test_slices_cover_original_without_gap_and_keep_descriptions(self):
        original = (module.ROOT / 'book/figures/publisher-role-evidence.svg').read_text()
        source = ('<span class="diagram"><img alt="Read top to bottom. First compare '
                  'the declared GitHub publisher recipe with the account inventory."></span>')
        result = module.split_publisher_figure(source)
        encoded = re.findall(r'data:image/png;base64,([^\"]+)', result)
        self.assertEqual(len(encoded), 2)
        self.assertEqual([png_size(data) for data in encoded], [(1080, 1425), (1080, 1089)])
        for data, box in zip(encoded, ['0 0 360 475', '0 475 360 363']):
            expected = original.replace('viewBox="0 0 360 838"', f'viewBox="{box}"')
            self.assertEqual(base64.b64decode(data), base64.b64decode(module.raster_panel(expected)))
        self.assertIn('Publisher evidence, part one:', result)
        self.assertIn('Publisher evidence, part two:', result)

    def test_missing_or_duplicate_placement_is_rejected(self):
        item = '<span class="diagram"><img alt="Read top to bottom. First compare the declared GitHub publisher recipe"></span>'
        for source in ('', item + item):
            with self.subTest(source=source), self.assertRaises(ValueError):
                module.split_publisher_figure(source)


class ContainerReleaseSplitTests(unittest.TestCase):
    def test_panels_cover_original_in_order_and_preserve_limits(self):
        original = (module.ROOT / 'book/figures/container-release-gates.svg').read_text()
        source = ('<span class="diagram"><img alt="In a local Docker teaching lab, '
                  'a bad-readiness configuration is rejected."></span>')
        result = module.split_container_release_figure(source)
        segments = re.findall(r'data:image/png;base64,([^\"]+)', result)
        boxes = ['0 0 360 228', '0 228 360 152', '0 380 360 220']
        self.assertEqual(len(segments), len(boxes))
        self.assertEqual([png_size(data) for data in segments],
                         [(1080, 684), (1080, 456), (1080, 660)])
        for data, box in zip(segments, boxes):
            expected = original.replace('viewBox="0 0 360 600"', f'viewBox="{box}"')
            self.assertEqual(base64.b64decode(data), base64.b64decode(module.raster_panel(expected)))
        self.assertLess(result.index('outcome one:'), result.index('outcome two:'))
        self.assertLess(result.index('outcome two:'), result.index('outcome three:'))
        self.assertIn('One invoice is one test', result)
        self.assertIn('does not test ECS', result)

    def test_missing_or_duplicate_placement_is_rejected(self):
        item = '<span class="diagram"><img alt="In a local Docker teaching lab, a bad-readiness configuration"></span>'
        for source in ('', item + item):
            with self.subTest(source=source), self.assertRaises(ValueError):
                module.split_container_release_figure(source)


if __name__ == '__main__':
    unittest.main()
