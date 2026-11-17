"""Narrow exceptions for documented workspace-local files outside source handoffs."""
from pathlib import Path
import re


def documented_local_only(base: Path, document: Path, target: Path) -> bool:
    relative = document.relative_to(base).as_posix()
    # Exact historical review links refer to ignored working evidence, not source.
    historical_evidence = {
        ('docs/AMPLIFY-550-HARDCOVER-CAP-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/navigation.json'),
        ('docs/AMPLIFY-550-HARDCOVER-CAP-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/safe-areas.json'),
        ('docs/AMPLIFY-550-HARDCOVER-CAP-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/cloudformation-six-case-validation.json'),
        ('docs/CLINIC-INTAKE-PROMISE-2026-10-28.md', 'artifacts/clinic-packet-2026-10-28/lab-only.zip'),
        ('docs/CLINIC-INTAKE-PROMISE-2026-10-28.md', 'artifacts/clinic-packet-2026-10-28/covered-working.epub'),
        ('docs/GOVERNANCE-SCALABLE-TEXT-WORKING-2026-10-28.md', 'artifacts/governance-scalable-2026-10-28/corrected.docx'),
        ('docs/GOVERNANCE-SCALABLE-TEXT-WORKING-2026-10-28.md', 'artifacts/governance-scalable-2026-10-28/render/corrected.pdf'),
        ('docs/GOVERNANCE-SCALABLE-TEXT-WORKING-2026-10-28.md', 'artifacts/governance-scalable-2026-10-28/corrected.epub'),
        ('docs/PRINT-550-PAGES-165-184-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/page-review-165-184-manifest.json'),
        ('docs/PRINT-550-PAGES-185-204-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/page-review-185-204-manifest.json'),
        ('docs/PRINT-550-PAGES-205-244-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/page-review-205-244-manifest.json'),
        ('docs/PRINT-550-PAGES-205-244-WORKING-REVIEW-2026-10-28.md', 'artifacts/cloudformation-security-2026-10-28/current-source-validation-2026-10-28-review-followup.json'),
        ('docs/PRINT-550-PAGES-245-264-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/page-review-245-264-manifest.json'),
        ('docs/PRINT-550-PAGES-265-284-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/page-review-265-284-manifest.json'),
        ('docs/PRINT-550-PAGES-285-304-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/page-review-285-304-manifest.json'),
        ('docs/PRINT-550-PAGES-305-324-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/page-review-305-324-manifest.json'),
        ('docs/PRINT-550-PAGES-325-344-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/page-review-325-344-manifest.json'),
        ('docs/PRINT-550-PAGES-345-364-WORKING-REVIEW-2026-10-28.md', 'artifacts/hardcover-cap-review-2026-10-28/page-review-345-364-manifest.json'),
        ('docs/READER-CONTEXT-SECURITY-2026-10-28.md', 'artifacts/security-context-2026-10-28/manuscript.docx'),
        ('docs/READER-CONTEXT-SECURITY-2026-10-28.md', 'artifacts/security-context-2026-10-28/render/manuscript.pdf'),
        ('docs/READER-CONTEXT-SECURITY-2026-10-28.md', 'artifacts/security-context-2026-10-28/manuscript.epub'),
    }
    if (relative, target.relative_to(base).as_posix() if target.is_relative_to(base) else "") in historical_evidence:
        return True
    # The Kindle conversion study cites four ignored CLI reports as local
    # evidence. They are not reader-source members or generic CSV exceptions.
    if relative == 'docs/SIGNED-RELEASE-KINDLE-RASTER-STUDY-2026-10-27.md':
        report_root = base / 'artifacts/signed-release-gate-2026-10-27'
        for flavor in ('raster', 'palette'):
            folder = report_root / f'kindle-cli-{flavor}'
            if target in {
                folder / 'Summary_Log.csv',
                folder / 'Logs' / f'AMPLIFY-AWS-{flavor}-kindle-study_epub_QualityReport.csv',
            }:
                return True
    # These four dated visual receipts intentionally point to ignored working
    # builds. Keep the exception tied to the exact review, build root and
    # format names; the source archive still rejects other missing links.
    recent_format_reviews = {
        'COMPACT-IDENTITY-KINDLE-WORKING-REVIEW-2026-10-26.md': 'compact-identity-2026-10-26',
        'FOUR-COMPACT-FIGURES-WORKING-REVIEW-2026-10-26.md': 'four-compact-figures-2026-10-26',
        'FOUR-PHONE-FIGURES-WORKING-REVIEW-2026-10-26.md': 'four-phone-figures-2026-10-26',
        'NETWORK-COST-PHONE-FIGURE-WORKING-REVIEW-2026-10-26.md': 'network-cost-phone-2026-10-26',
    }
    if (relative.startswith('docs/') and
            recent_format_reviews.get(document.name) and
            target.is_relative_to(base/'artifacts'/recent_format_reviews[document.name]) and
            target.name in {'AMPLIFY AWS Working Manuscript.epub',
                            'AMPLIFY AWS Print Study.docx',
                            'AMPLIFY AWS Print Study.pdf'}):
        return True
    # Historical October 26 review receipts link to ignored, local build bytes.
    # Keep each exception bound to its review and output directory so an
    # unrelated source link or private file cannot disappear from the archive.
    historical_builds = {
        'DNS-CACHE-RECOVERY-WORKING-REVIEW-2026-10-26.md': 'dns-cache-timeline-working-2026-10-26',
        'PRINT-541-PAGE-MAP-AND-INCIDENT-FIGURE-REVIEW-2026-10-26.md': 'incident-print-working-2026-10-26',
        'PRINT-542-PAGE-MAP-AND-EXPORT-AUDIT-REVIEW-2026-10-26.md': 'export-audit-print-working-2026-10-26',
        'PRINT-544-PAGE-MAP-AND-STATE-REVIEW-2026-10-26.md': 'terraform-state-print-working-2026-10-26',
        'PRINT-545-PAGE-MAP-AND-EARLY-REVIEW-2026-10-26.md': 'amplify-routes-print-working-2026-10-26',
        'SEARCH-HINT-ORDER-WORKING-REVIEW-2026-10-26.md': 'search-hint-order-working-2026-10-26',
    }
    if (relative.startswith('docs/') and
            historical_builds.get(document.name) and
            target.is_relative_to(base/'artifacts'/historical_builds[document.name]) and
            target.name in {'AMPLIFY AWS Working Manuscript.docx',
                            'AMPLIFY AWS Working Manuscript.pdf',
                            'AMPLIFY AWS Working Manuscript.epub'}):
        return True
    historical_json = {
        'CURRENT-READER-PACKET-EXECUTION-REVIEW-2026-10-26.md':
            ('cdk-phone-figure-2026-10-26',
             {'publication-inventory-latest-packet.json', 'reader-boundary-latest-packet.json'}),
        'READER-IDENTIFIER-AUDIT-2026-10-26.md':
            ('epub-wide-figure-review-2026-10-26',
             {'owner-context-five-identifier-audit.json', 'account-neutral-private-study.audit.json'}),
    }
    if relative.startswith('docs/') and document.name in historical_json:
        folder, allowed_names = historical_json[document.name]
        if target.parent == base/'artifacts'/folder and target.name in allowed_names:
            return True
    if (relative == 'docs/AI-AND-ARCHITECTURE-READER-LIMIT-REVIEW-2026-10-26.md' and
            target == base/'artifacts/reader-cost-neutral-2026-10-26/AMPLIFY AWS Working Manuscript.epub'):
        return True
    # Later dated working-format receipts link to ignored output bytes. Permit
    # only named book builds in their expected local output trees.
    if re.fullmatch(r'docs/[A-Z0-9-]+-WORKING-REVIEW-\d{4}-\d{2}-\d{2}\.md', relative):
        if (target == base/'artifacts/manuscript/AMPLIFY AWS Working Manuscript.html' or
                (target.is_relative_to(base/'artifacts/docx-working') and
                 (target.name in {'AMPLIFY AWS Print Study.docx',
                                  'AMPLIFY AWS Print Study.pdf'})) or
                (target.is_relative_to(base/'artifacts/epub-working') and
                 target.name == 'AMPLIFY AWS Working Manuscript.epub')):
            return True
    # Dated format and visual receipts point to large ignored working builds.
    # They are intentionally not part of the source ZIP; keep this exception
    # limited to review documents and known non-source artifact formats.
    if (relative.startswith('docs/') and
            ('VISUAL' in document.name or document.name.startswith(
                ('TOPIC-FINDER-', 'COVER-V16-', 'KINDLE-PREVIEWER-TOPIC-FINDER-',
                 'OIDC-TRUST-BOUNDARY-WORKING-REVIEW-'))) and
            target.is_relative_to(base/'artifacts') and
            (target.name.startswith('AMPLIFY AWS ') or target.name == 'Summary_Log.csv') and
            target.suffix.lower() in {'.docx', '.pdf', '.epub', '.csv', '.kpf'}):
        return True
    if (relative.startswith('docs/') and
            target == base.parent/'BOOK-RELEASE-VISUAL-REVIEW-STANDARD.md'):
        return True
    if (relative in {'docs/READER-FORMAT-DECISIONS.md',
                     'docs/PRINT-TRIM-STUDY-2026-10-21.md'} and
            target == base.parent/'BOOK-RELEASE-VISUAL-REVIEW-STANDARD.md'):
        return True
    if (relative == 'docs/READER-FORMAT-REVIEW-2026-10-21.md' and
            target in {
                base/'artifacts/docx-working/current-2026-10-21-v138/AMPLIFY AWS Working Manuscript.docx',
                base/'artifacts/epub-working/current-2026-10-21-v69/AMPLIFY AWS Working Manuscript.epub',
            }):
        return True
    if (relative == 'docs/KINDLE-DIAGNOSTIC-2026-10-21-v69.md' and
            target in {
                base/'artifacts/epub-working/current-2026-10-21-v69/AMPLIFY AWS Working Manuscript.epub',
                base/'artifacts/epub-working/current-2026-10-21-v69/AMPLIFY AWS Raster Diagnostic.epub',
            }):
        return True
    if (relative == 'docs/WORKING-FORMAT-BUILD-2026-10-21-v132-v59.md' and
            target in {
                base/'artifacts/docx-working/current-2026-10-21-v132/AMPLIFY AWS Working Manuscript.docx',
                base/'artifacts/docx-working/current-2026-10-21-v132/render-150/AMPLIFY AWS Working Manuscript.pdf',
                base/'artifacts/epub-working/current-2026-10-21-v59/AMPLIFY AWS Working Manuscript.epub',
            }):
        return True
    if ((relative in {'docs/DOCX-HANDOFF.md', 'docs/BOOK-BLUEPRINT.md',
                      'docs/MANUSCRIPT-BUILD.md'} or
         re.fullmatch(r'docs/DOCX-WORKING-REVIEW-\d{4}-\d{2}-\d{2}-v\d+\.md', relative) or
         relative == 'docs/DOCX-V78-SUPPLEMENTAL-PAGE-REVIEW-2026-10-20.md') and
            target.is_relative_to(base/'artifacts/docx-working') and
            target.name == 'AMPLIFY AWS Working Manuscript.docx'):
        return True
    if (re.fullmatch(r'docs/DOCX-WORKING-REVIEW-\d{4}-\d{2}-\d{2}-v\d+\.md', relative) and
            target.is_relative_to(base/'artifacts/docx-working') and
            target.parent.name == 'render-150' and
            target.name == 'AMPLIFY AWS Working Manuscript.pdf'):
        return True
    if (relative == 'docs/PRINT-TRIM-STUDY-2026-10-21.md' and
            target in {
                base/'artifacts/docx-working/print-7x10-study-2026-10-21-v2/AMPLIFY AWS 7x10 Print Study.docx',
                base/'artifacts/docx-working/print-7x10-study-2026-10-21-v2/render-150/AMPLIFY AWS 7x10 Print Study.pdf',
            }):
        return True
    if ((relative == 'docs/DOCX-HANDOFF.md' or
         re.fullmatch(r'docs/(?:EPUB-WORKING-REVIEW|KINDLE-PREVIEWER)-\d{4}-\d{2}-\d{2}-v\d+\.md', relative)) and
            target.is_relative_to(base/'artifacts/epub-working') and
            target.name == 'AMPLIFY AWS Working Manuscript.epub'):
        return True
    if (re.fullmatch(r'docs/KINDLE-PREVIEWER-\d{4}-\d{2}-\d{2}-v\d+\.md', relative) and
            target.is_relative_to(base/'artifacts/epub-working') and
            target.name == 'Kindle-Previewer-conversion-log.csv'):
        return True
    if (relative in {'docs/DOCX-HANDOFF.md', 'docs/VERIFICATION.md', 'docs/CONTINUITY.md'} and
            target.parent == base/'artifacts' and
            re.fullmatch(r'AMPLIFY-AWS-v\d+-[0-9a-f]{7}-editable-handoff\.zip', target.name)):
        return True
    return (relative in {'docs/DOCX-WORKING-REVIEW-2026-10-19-v12.md',
                         'docs/DOCX-WORKING-REVIEW-2026-10-19-v13.md',
                         'docs/DOCX-WORKING-REVIEW-2026-10-19-v14.md',
                         'docs/DOCX-WORKING-REVIEW-2026-10-19-v16.md',
                         'docs/DOCX-WORKING-REVIEW-2026-10-19-v18.md'} and
            target == base.parent/'BOOK-RELEASE-VISUAL-REVIEW-STANDARD.md')
