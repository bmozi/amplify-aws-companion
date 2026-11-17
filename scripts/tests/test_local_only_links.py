"""Keep the source packager's local-artifact exception narrowly scoped."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from local_only_links import documented_local_only


class LocalOnlyLinksTests(unittest.TestCase):
    def setUp(self):
        self.base = Path("/synthetic/aws-amplify-lab")
        self.review = self.base / "docs/DOCX-WORKING-REVIEW-2026-10-20-v51.md"

    def test_kindle_study_exception_is_limited_to_four_reports(self):
        review = self.base / 'docs/SIGNED-RELEASE-KINDLE-RASTER-STUDY-2026-10-27.md'
        root = self.base / 'artifacts/signed-release-gate-2026-10-27'
        for flavor in ('raster', 'palette'):
            folder = root / f'kindle-cli-{flavor}'
            self.assertTrue(documented_local_only(self.base, review, folder / 'Summary_Log.csv'))
            self.assertTrue(documented_local_only(
                self.base, review,
                folder / 'Logs' / f'AMPLIFY-AWS-{flavor}-kindle-study_epub_QualityReport.csv'))
            self.assertFalse(documented_local_only(self.base, review, folder / 'private-state.csv'))
        self.assertFalse(documented_local_only(
            self.base, self.base / 'docs/random.md',
            root / 'kindle-cli-palette/Summary_Log.csv'))

    def test_recent_format_review_links_are_tied_to_their_build(self):
        review = self.base / 'docs/FOUR-COMPACT-FIGURES-WORKING-REVIEW-2026-10-26.md'
        correct = self.base / 'artifacts/four-compact-figures-2026-10-26/render/AMPLIFY AWS Print Study.pdf'
        wrong_build = self.base / 'artifacts/network-cost-phone-2026-10-26/render/AMPLIFY AWS Print Study.pdf'
        private_file = self.base / 'artifacts/four-compact-figures-2026-10-26/private-state.json'
        self.assertTrue(documented_local_only(self.base, review, correct))
        self.assertFalse(documented_local_only(self.base, review, wrong_build))
        self.assertFalse(documented_local_only(self.base, review, private_file))

    def test_current_review_may_link_only_to_local_word_candidate(self):
        target = self.base / "artifacts/docx-working/current-2026-10-20-v51/AMPLIFY AWS Working Manuscript.docx"
        self.assertTrue(documented_local_only(self.base, self.review, target))

    def test_print_study_exception_is_exact(self):
        review = self.base / 'docs/PRINT-TRIM-STUDY-2026-10-21.md'
        folder = self.base / 'artifacts/docx-working/print-7x10-study-2026-10-21-v2'
        self.assertTrue(documented_local_only(self.base, review,
                                              folder / 'AMPLIFY AWS 7x10 Print Study.docx'))
        self.assertTrue(documented_local_only(self.base, review,
                                              folder / 'render-150/AMPLIFY AWS 7x10 Print Study.pdf'))
        self.assertFalse(documented_local_only(self.base, review,
                                               folder / 'private.pdf'))

    def test_current_build_record_allows_only_its_three_named_outputs(self):
        record = self.base / "docs/WORKING-FORMAT-BUILD-2026-10-21-v132-v59.md"
        word = self.base / "artifacts/docx-working/current-2026-10-21-v132/AMPLIFY AWS Working Manuscript.docx"
        pdf = self.base / "artifacts/docx-working/current-2026-10-21-v132/render-150/AMPLIFY AWS Working Manuscript.pdf"
        epub = self.base / "artifacts/epub-working/current-2026-10-21-v59/AMPLIFY AWS Working Manuscript.epub"
        for target in (word, pdf, epub):
            self.assertTrue(documented_local_only(self.base, record, target))
        self.assertFalse(documented_local_only(self.base, record,
                         self.base / "artifacts/docx-working/other/AMPLIFY AWS Working Manuscript.docx"))

    def test_v78_supplemental_review_may_link_to_its_word_candidate(self):
        review = self.base / "docs/DOCX-V78-SUPPLEMENTAL-PAGE-REVIEW-2026-10-20.md"
        target = self.base / "artifacts/docx-working/current-2026-10-20-v78/AMPLIFY AWS Working Manuscript.docx"
        self.assertTrue(documented_local_only(self.base, review, target))
        self.assertFalse(documented_local_only(self.base, review,
                                               self.base / "artifacts/private-state.zip"))

    def test_other_document_cannot_claim_word_exception(self):
        target = self.base / "artifacts/docx-working/current-2026-10-20-v51/AMPLIFY AWS Working Manuscript.docx"
        self.assertFalse(documented_local_only(self.base, self.base / "docs/random.md", target))

    def test_review_cannot_link_to_other_local_artifact(self):
        target = self.base / "artifacts/secret-plan.tfplan"
        self.assertFalse(documented_local_only(self.base, self.review, target))

    def test_epub_review_may_link_only_to_named_working_epub(self):
        review = self.base / "docs/EPUB-WORKING-REVIEW-2026-10-20-v1.md"
        epub = self.base / "artifacts/epub-working/current-2026-10-20-v6/AMPLIFY AWS Working Manuscript.epub"
        self.assertTrue(documented_local_only(self.base, review, epub))
        self.assertTrue(documented_local_only(self.base, self.base / "docs/DOCX-HANDOFF.md", epub))
        self.assertFalse(documented_local_only(self.base, self.base / "docs/random.md", epub))
        self.assertFalse(documented_local_only(self.base, review,
                                                self.base / "artifacts/epub-working/secrets.epub"))

    def test_kindle_conversion_note_has_only_named_local_artifacts(self):
        note = self.base / "docs/KINDLE-PREVIEWER-2026-10-20-v1.md"
        folder = self.base / "artifacts/epub-working/current-2026-10-20-v6"
        self.assertTrue(documented_local_only(self.base, note,
                                               folder / "AMPLIFY AWS Working Manuscript.epub"))
        self.assertTrue(documented_local_only(self.base, note,
                                               folder / "Kindle-Previewer-conversion-log.csv"))
        self.assertFalse(documented_local_only(self.base, note, folder / "private-key.json"))

    def test_reader_format_records_allow_only_named_local_files(self):
        review = self.base / "docs/READER-FORMAT-REVIEW-2026-10-21.md"
        diagnostic = self.base / "docs/KINDLE-DIAGNOSTIC-2026-10-21-v69.md"
        decisions = self.base / "docs/READER-FORMAT-DECISIONS.md"
        word = self.base / "artifacts/docx-working/current-2026-10-21-v138/AMPLIFY AWS Working Manuscript.docx"
        epub = self.base / "artifacts/epub-working/current-2026-10-21-v69/AMPLIFY AWS Working Manuscript.epub"
        raster = self.base / "artifacts/epub-working/current-2026-10-21-v69/AMPLIFY AWS Raster Diagnostic.epub"
        self.assertTrue(documented_local_only(self.base, review, word))
        self.assertTrue(documented_local_only(self.base, review, epub))
        self.assertTrue(documented_local_only(self.base, diagnostic, epub))
        self.assertTrue(documented_local_only(self.base, diagnostic, raster))
        self.assertTrue(documented_local_only(
            self.base, decisions, self.base.parent / "BOOK-RELEASE-VISUAL-REVIEW-STANDARD.md"))
        self.assertFalse(documented_local_only(self.base, review, raster))
        self.assertFalse(documented_local_only(self.base, diagnostic, word))
        self.assertFalse(documented_local_only(self.base, decisions, self.base.parent / "private-key.json"))

    def test_continuity_may_link_to_named_private_handoff_but_not_arbitrary_zip(self):
        document = self.base / "docs/CONTINUITY.md"
        handoff = self.base / "artifacts/AMPLIFY-AWS-v69-9d2a258-editable-handoff.zip"
        self.assertTrue(documented_local_only(self.base, document, handoff))
        self.assertFalse(documented_local_only(self.base, document,
                                               self.base / "artifacts/private-state.zip"))

    def test_dated_visual_review_may_reference_format_build_but_not_private_data(self):
        review = self.base / "docs/CACHE-TIMELINE-VISUAL-REVIEW-2026-10-23.md"
        folder = self.base / "artifacts/cache-timeline-working-2026-10-23"
        self.assertTrue(documented_local_only(
            self.base, review, folder / "AMPLIFY AWS Working Manuscript.docx"))
        self.assertTrue(documented_local_only(
            self.base, review, folder / "render-125/AMPLIFY AWS Working Manuscript.pdf"))
        self.assertFalse(documented_local_only(self.base, review, folder / "secrets.epub"))
        self.assertFalse(documented_local_only(self.base, review, folder / "private-key.json"))
        self.assertFalse(documented_local_only(
            self.base, self.base / "docs/random.md", folder / "AMPLIFY AWS Working Manuscript.docx"))

    def test_dated_working_review_may_link_only_to_named_local_formats(self):
        review = self.base / "docs/PRINT-DATABASE-SELECTION-CHAPTER-WORKING-REVIEW-2026-10-24.md"
        word = self.base / "artifacts/docx-working/study/print-8.25x11/AMPLIFY AWS Print Study.docx"
        pdf = self.base / "artifacts/docx-working/study/render/AMPLIFY AWS Print Study.pdf"
        epub = self.base / "artifacts/epub-working/study/AMPLIFY AWS Working Manuscript.epub"
        html = self.base / "artifacts/manuscript/AMPLIFY AWS Working Manuscript.html"
        for target in (word, pdf, epub, html):
            self.assertTrue(documented_local_only(self.base, review, target))
        self.assertFalse(documented_local_only(self.base, review,
                         self.base / "artifacts/docx-working/study/private.pdf"))
        self.assertFalse(documented_local_only(self.base, review,
                         self.base / "artifacts/epub-working/study/secrets.epub"))
        self.assertFalse(documented_local_only(self.base, self.base / "docs/random.md", word))

    def test_october_26_historical_review_paths_are_narrow(self):
        review = self.base / 'docs/PRINT-541-PAGE-MAP-AND-INCIDENT-FIGURE-REVIEW-2026-10-26.md'
        folder = self.base / 'artifacts/incident-print-working-2026-10-26'
        self.assertTrue(documented_local_only(
            self.base, review, folder / 'pdf/AMPLIFY AWS Working Manuscript.pdf'))
        self.assertFalse(documented_local_only(self.base, review, folder / 'private.pdf'))
        self.assertFalse(documented_local_only(
            self.base, self.base / 'docs/random.md',
            folder / 'pdf/AMPLIFY AWS Working Manuscript.pdf'))
        packet_review = self.base / 'docs/CURRENT-READER-PACKET-EXECUTION-REVIEW-2026-10-26.md'
        packet_folder = self.base / 'artifacts/cdk-phone-figure-2026-10-26'
        self.assertTrue(documented_local_only(
            self.base, packet_review, packet_folder / 'reader-boundary-latest-packet.json'))
        self.assertFalse(documented_local_only(
            self.base, packet_review, packet_folder / 'private-state.json'))
        cost_review = self.base / 'docs/AI-AND-ARCHITECTURE-READER-LIMIT-REVIEW-2026-10-26.md'
        cost_folder = self.base / 'artifacts/reader-cost-neutral-2026-10-26'
        self.assertTrue(documented_local_only(
            self.base, cost_review, cost_folder / 'AMPLIFY AWS Working Manuscript.epub'))
        self.assertFalse(documented_local_only(
            self.base, cost_review, cost_folder / 'private-state.epub'))


if __name__ == "__main__":
    unittest.main()
