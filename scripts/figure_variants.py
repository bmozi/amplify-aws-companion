"""Validate the explicit ebook SVG catalog without changing print numbering."""
import hashlib
import json
from pathlib import PurePosixPath
from xml.etree import ElementTree


def validate_variants(base):
    catalog = base / 'book/figures/ebook-inventory.json'
    if not catalog.exists():
        return set()
    entries = json.loads(catalog.read_text())
    if not isinstance(entries, list):
        raise ValueError('Ebook figure catalog must be a list')
    result = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'file', 'sha256'}:
            raise ValueError('Invalid ebook figure catalog entry')
        name = entry['file']
        if not isinstance(name, str):
            raise ValueError('Invalid ebook figure path')
        parts = PurePosixPath(name).parts
        if len(parts) != 3 or parts[:2] != ('book', 'figures') or not parts[2].endswith('-ebook.svg'):
            raise ValueError('Unsafe ebook figure path: ' + name)
        if name in result:
            raise ValueError('Duplicate ebook figure: ' + name)
        path = base / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Ebook figure missing or not a regular file: ' + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Ebook figure hash is stale: ' + name)
        if ElementTree.parse(path).getroot().tag != '{http://www.w3.org/2000/svg}svg':
            raise ValueError('Ebook figure is not an SVG: ' + name)
        result.add(name)
    return result
