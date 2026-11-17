"""Check that the EPUB-only table fallback retains every comparison value."""

import importlib.util
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET


BUILDER = Path(__file__).resolve().parents[1] / "build-working-epub.py"
sys.path.insert(0, str(BUILDER.parent))
SPEC = importlib.util.spec_from_file_location("build_working_epub_reflow", BUILDER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ComparisonTableReflowTests(unittest.TestCase):
    def test_wide_table_keeps_headers_values_and_inline_markup(self):
        source = (
            '<div class="table-scroll" role="region"><table><thead><tr>'
            '<th>Case</th><th>Capacity</th><th>Requests</th><th>With contingency</th>'
            '</tr></thead><tbody><tr><td>Stop early</td><td>$0.10</td>'
            '<td><em>500,000</em></td><td>$0.39</td></tr></tbody></table></div>'
        )
        result, count = MODULE.reflow_comparison_tables(source)
        self.assertEqual(count, 1)
        self.assertNotIn("<table>", result)
        root = ET.fromstring(result)
        self.assertEqual(len(root.findall(".//p")), 4)
        for expected in ("Case:", "Stop early", "Capacity:", "$0.10",
                         "Requests:", "500,000", "With contingency:", "$0.39"):
            self.assertIn(expected, "".join(root.itertext()))
        self.assertEqual(len(root.findall(".//em")), 1)

    def test_two_column_table_becomes_paired_records_and_ragged_table_fails(self):
        paired = ('<div class="table-scroll"><table><thead><tr><th>A</th><th>B</th>'
                  '</tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table></div>')
        converted, count = MODULE.reflow_comparison_tables(paired)
        self.assertEqual(count, 1)
        self.assertNotIn('<table>', converted)
        self.assertIn('<strong>A:</strong> 1', converted)
        self.assertIn('<strong>B:</strong> 2', converted)
        three = ('<div class="table-scroll"><table><thead><tr><th>Case</th>'
                 '<th>Promise</th><th>Evidence</th></tr></thead><tbody><tr>'
                 '<td>A</td><td>One hour</td><td>Timed drill</td>'
                 '</tr></tbody></table></div>')
        converted, count = MODULE.reflow_comparison_tables(three)
        self.assertEqual(count, 1)
        self.assertNotIn('<table>', converted)
        self.assertIn('Timed drill', converted)
        ragged = ('<div class="table-scroll"><table><thead><tr>'
                  '<th>A</th><th>B</th><th>C</th><th>D</th></tr></thead>'
                  '<tbody><tr><td>1</td></tr></tbody></table></div>')
        with self.assertRaisesRegex(ValueError, "ragged"):
            MODULE.reflow_comparison_tables(ragged)


if __name__ == "__main__":
    unittest.main()
