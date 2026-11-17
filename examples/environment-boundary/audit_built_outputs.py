"""Check selected Amplify destinations in local browser JavaScript, without printing them.

This checks literal values in one local build. It cannot prove which bytes a host serves.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from inspect_outputs import FIELDS, load_outputs, read_value


MAX_JS_BYTES = 32 * 1024 * 1024


def read_build(directory):
    root = Path(directory)
    if not root.is_dir() or root.is_symlink() or not (root / 'index.html').is_file():
        raise ValueError('expected a local build directory with index.html')
    paths = sorted(root.rglob('*.js'))
    if not paths:
        raise ValueError('no built JavaScript files found')
    hasher = hashlib.sha256()
    contents = []
    total = 0
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError('built JavaScript must be regular files')
        data = path.read_bytes()
        total += len(data)
        if total > MAX_JS_BYTES:
            raise ValueError('built JavaScript exceeds local inspection size limit')
        relative = path.relative_to(root).as_posix().encode()
        hasher.update(len(relative).to_bytes(4, 'big') + relative)
        hasher.update(len(data).to_bytes(8, 'big') + data)
        contents.append(data)
    return contents, hasher.hexdigest()


def audit(document, outputs_digest, contents, build_digest, forbidden=None, forbidden_digest=None):
    expected = {name: read_value(document, path) for name, path in FIELDS.items()}
    selected = {name: any(value.encode() in data for data in contents)
                if value is not None else None for name, value in expected.items()}
    distinct = {}
    if forbidden is not None:
        for name, path in FIELDS.items():
            value = read_value(forbidden, path)
            if value is None or value == expected[name]:
                distinct[name] = None
            else:
                distinct[name] = any(value.encode() in data for data in contents)
    passed = all(value is not False for value in selected.values()) and not any(
        value is True for value in distinct.values())
    return {
        'outputs_sha256': outputs_digest,
        'built_js_sha256': build_digest,
        'js_file_count': len(contents),
        'selected_values_found_in_js': selected,
        'distinct_forbidden_values_found_in_js': distinct if forbidden is not None else None,
        'forbidden_outputs_sha256': forbidden_digest,
        'local_selected_literal_check_passed': passed,
        'scope': 'selected literal values in local JS only; no build provenance, exhaustive config, served bytes, access or AWS proof',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outputs', type=Path)
    parser.add_argument('built_directory', type=Path)
    parser.add_argument('--forbid-outputs', type=Path,
                        help='A separately reviewed outputs file whose distinct destinations must be absent')
    args = parser.parse_args(argv)
    try:
        document, digest = load_outputs(args.outputs)
        contents, build_digest = read_build(args.built_directory)
        forbidden, forbidden_digest = (load_outputs(args.forbid_outputs)
                                       if args.forbid_outputs else (None, None))
        report = audit(document, digest, contents, build_digest, forbidden, forbidden_digest)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f'built outputs audit stopped: {error}', file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['local_selected_literal_check_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
