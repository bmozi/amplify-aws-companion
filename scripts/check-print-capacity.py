"""Check every page of a working PDF against a chosen print trim and page cap.

This is a format preflight, not a visual review or KDP acceptance check.
The default 8.25 x 11 / 550-page rule applies the author-selected paperback
editorial ceiling, including front and back matter. Hardcover is an optional secondary edition.
Refresh binding, ink, paper and retailer specifications before final release.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess


def pdfinfo(pdf, *options):
    result = subprocess.run(['pdfinfo', *options, str(pdf)], text=True,
                            capture_output=True, check=True)
    return result.stdout


def inspect(pdf, width, height, maximum, cover_template_pages=None):
    header = pdfinfo(pdf)
    count_match = re.search(r'^Pages:\s+(\d+)\s*$', header, re.M)
    if count_match is None:
        raise ValueError('pdfinfo did not report a page count')
    count = int(count_match.group(1))
    detail = pdfinfo(pdf, '-f', '1', '-l', str(count))
    observed = {}
    for line in detail.splitlines():
        match = re.match(r'^Page\s+(\d+)\s+size:\s+([\d.]+) x ([\d.]+) pts', line)
        if match:
            observed[int(match.group(1))] = [float(match.group(2)), float(match.group(3))]
    if set(observed) != set(range(1, count + 1)):
        raise ValueError('pdfinfo did not report every page size')
    expected = [width * 72, height * 72]
    wrong_trim = [number for number, actual in observed.items()
                  if any(abs(actual[index] - expected[index]) > .11 for index in (0, 1))]
    counted_for_cover = count + count % 2
    failures = []
    if wrong_trim:
        failures.append(f'{len(wrong_trim)} pages have the wrong trim')
    if count > maximum or counted_for_cover > maximum:
        failures.append(f'{count} PDF pages require {counted_for_cover} cover-count pages; maximum is {maximum}')
    if cover_template_pages is not None and cover_template_pages != counted_for_cover:
        failures.append(f'cover template uses {cover_template_pages} pages; current count is {counted_for_cover}')
    return {
        'pdf': str(pdf), 'sha256': sha256(pdf.read_bytes()).hexdigest(),
        'pages': count, 'cover_count_pages': counted_for_cover,
        'trim_inches': [width, height], 'maximum_pages': maximum,
        'wrong_trim_pages': wrong_trim,
        'cover_template_pages': cover_template_pages,
        'passed': not failures, 'failures': failures,
        'scope': 'PDF format and template-count preflight only; no readable-page, cover, KDP or physical-proof review',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--width', type=float, default=8.25)
    parser.add_argument('--height', type=float, default=11)
    parser.add_argument('--max-pages', type=int, default=550)
    parser.add_argument('--cover-template-pages', type=int)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if not args.pdf.is_file() or args.width <= 0 or args.height <= 0 or args.max_pages <= 0:
        parser.error('PDF must exist and trim and maximum values must be positive')
    try:
        result = inspect(args.pdf, args.width, args.height,
                         args.max_pages, args.cover_template_pages)
    except (subprocess.CalledProcessError, OSError, ValueError) as error:
        parser.exit(2, f'PDF inspection failed: {error}\n')
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(('PASS' if result['passed'] else 'FAIL') + ': ' +
          f"{result['pages']} PDF pages, {result['cover_count_pages']} cover-count pages, " +
          (', '.join(result['failures']) if result['failures'] else 'trim and page cap match'))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
