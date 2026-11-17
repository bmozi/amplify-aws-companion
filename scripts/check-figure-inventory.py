"""Check source SVGs, their catalog and the builder's manual list without rendering."""

import ast
import json
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree
from figure_variants import validate_variants


BASE = Path(__file__).resolve().parents[1]
SVG_NS = '{http://www.w3.org/2000/svg}'


def check_inventory(base: Path) -> int:
    folder = base / 'book' / 'figures'
    entries = json.loads((folder / 'inventory.json').read_text())
    if not isinstance(entries, list) or not entries:
        raise ValueError('Figure inventory must be a nonempty list')

    actual = {}
    for path in folder.glob('*.svg'):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Figure source is not a regular file: {path.name}')
        actual[path.relative_to(base).as_posix()] = path

    listed = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('file'), str):
            raise ValueError('Figure inventory entry has no file path')
        name = entry['file']
        parts = PurePosixPath(name).parts
        if len(parts) != 3 or parts[:2] != ('book', 'figures') or not parts[2].endswith('.svg'):
            raise ValueError(f'Unsafe or non-figure inventory path: {name}')
        if name in listed:
            raise ValueError(f'Duplicate figure inventory entry: {name}')
        listed.add(name)
        if name not in actual:
            raise ValueError(f'Listed SVG is missing: {name}')
        root = ElementTree.parse(actual[name]).getroot()
        if root.tag != SVG_NS + 'svg':
            raise ValueError(f'Figure is not an SVG root: {name}')
        for field, element in [('title', 'title'), ('description', 'desc')]:
            value = entry.get(field)
            source = root.find(SVG_NS + element)
            source_text = ''.join(source.itertext()).strip() if source is not None else ''
            if not isinstance(value, str) or not value.strip() or value.strip() != source_text:
                raise ValueError(f'Figure {field} is absent or stale: {name}')

    variants = validate_variants(base)
    if listed & variants:
        raise ValueError("Ebook variants must not change print figure numbering")
    unlisted = set(actual) - listed - variants
    if unlisted:
        raise ValueError('Unlisted SVG source: ' + ', '.join(sorted(unlisted)))

    builder = ast.parse((base / 'scripts' / 'build-book-figures.py').read_text())
    assignments = [node for node in builder.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == 'manual_figures'
                           for target in node.targets)]
    if len(assignments) != 1:
        raise ValueError('Expected one literal manual_figures list in the figure builder')
    manual_names = ast.literal_eval(assignments[0].value)
    if not isinstance(manual_names, list) or not all(isinstance(name, str) for name in manual_names):
        raise ValueError('Figure builder manual_figures must be a literal filename list')
    builder_manual = {f'book/figures/{name}' for name in manual_names}
    if len(builder_manual) != len(manual_names):
        raise ValueError('Duplicate filename in figure builder manual list')
    catalog_manual = {entry['file'] for entry in entries
                      if entry.get('source') == 'hand-authored SVG; edit this file directly'}
    if builder_manual != catalog_manual:
        raise ValueError('Figure builder manual list differs from catalog: '
                         f'builder_only={sorted(builder_manual - catalog_manual)}, '
                         f'catalog_only={sorted(catalog_manual - builder_manual)}')
    return len(listed)


if __name__ == '__main__':
    count = check_inventory(BASE)
    print(f'Figure inventory: {count} SVG sources cataloged with matching metadata and builder manual list; structural check only')
