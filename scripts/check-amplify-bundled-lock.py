"""Catch the known Amplify/OpenTelemetry bundled-lockfile regression offline.

This checks selected lock metadata needed by npm ci. It does not inspect installed
bytes, vulnerability reachability or every package-lock dependency.
"""

import argparse
import json
from pathlib import Path
import re
import sys


CONSTRUCTS = ('@aws-amplify/data-construct', '@aws-amplify/graphql-api-construct')
CALLERS = ('@opentelemetry/resources', '@opentelemetry/sdk-trace-base')
EXACT_VERSION = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?\Z')


def inspect_lock(lock):
    packages = lock.get('packages')
    if not isinstance(packages, dict):
        raise ValueError('package-lock lacks a packages map')
    observations = []
    defects = []
    for construct in CONSTRUCTS:
        root = f'node_modules/{construct}'
        parent = packages.get(root)
        if not isinstance(parent, dict) or not isinstance(parent.get('version'), str):
            defects.append(f'{construct}: construct record missing')
            continue
        bundled_core = packages.get(root + '/node_modules/@opentelemetry/core')
        root_version = bundled_core.get('version') if isinstance(bundled_core, dict) else None
        for caller in CALLERS:
            caller_path = root + f'/node_modules/{caller}'
            record = packages.get(caller_path)
            if not isinstance(record, dict):
                defects.append(f'{construct}: {caller} bundled record missing; review changed package shape')
                continue
            spec = record.get('dependencies', {}).get('@opentelemetry/core')
            if not isinstance(spec, str) or not EXACT_VERSION.fullmatch(spec):
                defects.append(f'{construct}: {caller} core requirement is not an exact known version')
                continue
            nested = packages.get(caller_path + '/node_modules/@opentelemetry/core')
            nested_version = nested.get('version') if isinstance(nested, dict) else None
            resolved_version = nested_version or root_version
            if resolved_version != spec:
                defects.append(f'{construct}: {caller} needs core {spec}, lock resolves {resolved_version or "none"}')
            observations.append({
                'construct': construct,
                'construct_version': parent['version'],
                'caller': caller,
                'core_requirement': spec,
                'root_core_version': root_version,
                'nested_core_version': nested_version,
                'lock_requirement_satisfied': resolved_version == spec,
            })
    return {'known_paths_checked': len(observations), 'observations': observations,
            'defects': defects, 'passed': not defects,
            'scope': 'selected lock records only; npm ci, installed bytes, audit and backend generation are separate checks'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lockfile', nargs='?', type=Path, default=Path('app/package-lock.json'))
    args = parser.parse_args(argv)
    try:
        report = inspect_lock(json.loads(args.lockfile.read_text()))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f'bundled lock check stopped: {error}', file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
