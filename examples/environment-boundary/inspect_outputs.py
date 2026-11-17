"""Compare Amplify Gen 2 client outputs without printing resource identifiers.

This is a local configuration inspection, not an AWS inventory or access test.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


FIELDS = {
    'auth.user_pool_id': ('auth', 'user_pool_id'),
    'auth.user_pool_client_id': ('auth', 'user_pool_client_id'),
    'auth.identity_pool_id': ('auth', 'identity_pool_id'),
    'data.url': ('data', 'url'),
    'storage.bucket_name': ('storage', 'bucket_name'),
}
REGIONS = {name: (name, 'aws_region') for name in ('auth', 'data', 'storage')}
MAX_BYTES = 4 * 1024 * 1024


def read_value(document, path):
    current = document
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current if isinstance(current, str) and current.strip() else None


def load_outputs(path):
    data = Path(path).read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError('configuration exceeds the local inspection size limit')
    document = json.loads(data)
    if (not isinstance(document, dict) or
            not isinstance(document.get('version'), str) or
            not re.fullmatch(r'1(?:\.[0-9]+)?', document['version'])):
        raise ValueError('expected a Gen 2 outputs object in major version 1')
    for name, location in FIELDS.items():
        # This lab explicitly uses Auth, Data and Storage. Other Amplify apps
        # may intentionally omit categories and need a different checklist.
        if name == 'auth.identity_pool_id':
            continue
        if read_value(document, location) is None:
            raise ValueError(f'missing required Field Lab field: {name}')
    for name, location in REGIONS.items():
        if read_value(document, location) is None:
            raise ValueError(f'missing required Field Lab region: {name}')
    return document, hashlib.sha256(data).hexdigest()


def inspect(document, digest, other=None, expected_sha256=None, other_digest=None):
    if expected_sha256 is not None and (len(expected_sha256) != 64 or
                                        any(c not in '0123456789abcdef' for c in expected_sha256)):
        raise ValueError('expected SHA-256 must be 64 lowercase hexadecimal characters')
    region_values = {name: read_value(document, path) for name, path in REGIONS.items()}
    result = {
        'outputs_sha256': digest,
        'outputs_version': document['version'],
        'matches_separately_reviewed_digest': (digest == expected_sha256 if expected_sha256 else None),
        'fields_present': {name: read_value(document, path) is not None for name, path in FIELDS.items()},
        'regions': region_values,
        'regions_match_each_other': len(set(region_values.values())) == 1,
        'unauthenticated_identities_enabled': document.get('auth', {}).get('unauthenticated_identities_enabled'),
        'data_default_authorization_type': document.get('data', {}).get('default_authorization_type'),
        'other_root_sections_need_review': sorted(set(document) - {'version', 'auth', 'data', 'storage'}),
        'scope': 'local client configuration only; no AWS inventory, permission, served-byte or cost proof',
    }
    if other is not None:
        result['comparison_outputs_sha256'] = other_digest
        result['same_destinations_as_comparison'] = {
            name: read_value(document, path) == read_value(other, path)
            if read_value(document, path) is not None and read_value(other, path) is not None else None
            for name, path in FIELDS.items()
        }
        result['same_regions_as_comparison'] = {
            name: read_value(document, path) == read_value(other, path)
            for name, path in REGIONS.items()
        }
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outputs', type=Path)
    parser.add_argument('--compare', type=Path, help='Another outputs file to compare field by field')
    parser.add_argument('--expected-sha256', help='Digest from a separate, reviewed release record')
    args = parser.parse_args(argv)
    try:
        document, digest = load_outputs(args.outputs)
        other, other_digest = load_outputs(args.compare) if args.compare else (None, None)
        report = inspect(document, digest, other, args.expected_sha256, other_digest)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f'outputs inspection stopped: {error}', file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report['matches_separately_reviewed_digest'] is False else 0


if __name__ == '__main__':
    raise SystemExit(main())
