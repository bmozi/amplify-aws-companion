"""Map exact EPUB SVG placements to current chapters and byte-identical sources.

This is a location and provenance aid for visual review, not a readable-page
inspection or a Kindle release receipt. It fails closed on unlocated media.
"""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
XHTML = '{http://www.w3.org/1999/xhtml}'
SVG = '{http://www.w3.org/2000/svg}'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_index() -> dict[str, list[str]]:
    index = defaultdict(list)
    for directory in ('book', 'curriculum', 'examples'):
        for path in (ROOT / directory).rglob('*.svg'):
            index[sha256(path.read_bytes())].append(path.relative_to(ROOT).as_posix())
    return {digest: sorted(paths) for digest, paths in index.items()}


def text_of(element: ET.Element) -> str:
    return ' '.join(''.join(element.itertext()).split())


def chapter_of(root: ET.Element) -> str | None:
    for heading in root.iter():
        if heading.tag in {XHTML + 'h1', XHTML + 'h2'}:
            label = text_of(heading)
            if re.match(r'^Chapter \d+\s+[—-]\s+', label):
                return label
    return None


def build_map(epub: Path) -> dict:
    sources = source_index()
    placements = []
    media_seen = set()
    documents = []
    errors = []
    with zipfile.ZipFile(epub) as archive:
        members = set(archive.namelist())
        for member in sorted(members):
            if not (member.startswith('EPUB/text/') and member.endswith('.xhtml')):
                continue
            root = ET.fromstring(archive.read(member))
            chapter = chapter_of(root)
            document_images = list(root.iter(XHTML + 'img'))
            documents.append({'xhtml': member, 'chapter': chapter,
                              'svg_placements': len(document_images)})
            for number, img in enumerate(document_images, start=1):
                src = img.get('src', '')
                media = str(PurePosixPath(member).parent.joinpath(src))
                # PurePosixPath retains .., while ZIP members are normalized.
                parts = []
                for part in PurePosixPath(media).parts:
                    if part == '..':
                        if parts:
                            parts.pop()
                    elif part != '.':
                        parts.append(part)
                media = '/'.join(parts)
                if not src.endswith('.svg') or media not in members:
                    errors.append(f'{member} image {number}: missing/non-SVG media {src}')
                    continue
                if not chapter:
                    errors.append(f'{member} image {number}: no printed chapter heading')
                data = archive.read(media)
                digest = sha256(data)
                paths = sources.get(digest, [])
                if not paths:
                    errors.append(f'{member} image {number}: no byte-identical source for {media}')
                svg = ET.fromstring(data)
                title = svg.find(SVG + 'title')
                media_seen.add(media)
                placements.append({
                    'chapter': chapter,
                    'xhtml': member,
                    'position_in_chapter': number,
                    'media': media,
                    'source_paths': paths,
                    'sha256': digest,
                    'alt': img.get('alt', ''),
                    'svg_title': text_of(title) if title is not None else '',
                    'viewBox': svg.get('viewBox', ''),
                })
        packaged_svg = {name for name in members
                        if name.startswith('EPUB/media/') and name.endswith('.svg')}
        for media in sorted(packaged_svg - media_seen):
            errors.append(f'unplaced SVG media: {media}')
    return {
        'scope': 'Exact EPUB chapter/media/source location; no visual quality judgment',
        'epub': str(epub.relative_to(ROOT)) if epub.is_relative_to(ROOT) else str(epub),
        'epub_sha256': sha256(epub.read_bytes()),
        'xhtml_documents': len(documents),
        'svg_placements': len(placements),
        'unique_svg_media': len(media_seen),
        'documents': documents,
        'placements': placements,
        'errors': errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--epub', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    result = build_map(args.epub.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in {'documents', 'placements'}}, indent=2))
    if result['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
