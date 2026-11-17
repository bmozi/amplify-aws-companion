import importlib.util
import io
import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
SPEC = importlib.util.spec_from_file_location('epub_builder', Path(__file__).resolve().parents[1] / 'build-working-epub.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LessonDestinationTests(unittest.TestCase):
    def audit(self, target, label='1 · First lesson', href='chapter.xhtml#first'):
        buffer = io.BytesIO()
        wrap = lambda body: '<html xmlns="http://www.w3.org/1999/xhtml"><body>' + body + '</body></html>'
        with ZipFile(buffer, 'w') as z:
            z.writestr('EPUB/text/map.xhtml', wrap(f'<a href="{href}">{label}</a>'))
            z.writestr('EPUB/text/chapter.xhtml', wrap(target))
        with ZipFile(buffer) as z:
            return MODULE.audit_lesson_destinations(z, 1)

    def test_correct_section_heading(self):
        self.assertEqual(self.audit('<section id="first"><h2>Chapter 1 — First</h2></section>'), 1)

    def test_existing_empty_anchor_is_not_a_chapter_destination(self):
        with self.assertRaisesRegex(ValueError, 'does not target'):
            self.audit('<p><span id="first"/></p>')

    def test_wrong_chapter_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'does not target'):
            self.audit('<section id="first"><h2>Chapter 2 — Second</h2></section>')

    def test_missing_fragment_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'does not target'):
            self.audit('<h2 id="other">Chapter 1 — First</h2>')

    def test_missing_outcome_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'one outcome'):
            self.audit('<h2 id="first">Chapter 1 — First</h2>', label='Unnumbered')

    def test_conversion_targets_heading_instead_of_empty_anchor(self):
        source = '<nav>contents</nav><section id="section-0"><h2 id="intro">Intro</h2><a href="#section-1">Next</a></section><section id="section-1"><h2 id="first">First</h2></section>'
        result = MODULE.convert_reader_html(source, 2)
        self.assertIn('href="#first"', result)
        self.assertNotIn('<span', result)
        with self.assertRaisesRegex(ValueError, 'identified h2'):
            MODULE.convert_reader_html(source.replace('id="first"', ''), 2)


if __name__ == '__main__':
    unittest.main()
