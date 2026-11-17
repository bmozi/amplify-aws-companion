"""Summarize npm audit package entries and root advisory URLs without scoring risk."""

import argparse
import json
from pathlib import Path


def summarize(report):
    if not isinstance(report, dict) or not isinstance(report.get('vulnerabilities'), dict):
        raise ValueError('Expected a complete npm audit JSON report with vulnerabilities')
    packages = report['vulnerabilities']
    metadata = report.get('metadata', {}).get('vulnerabilities', {})
    if not isinstance(metadata, dict) or metadata.get('total') != len(packages):
        raise ValueError('Audit metadata and affected-package entries disagree')

    advisories = {}
    for package, finding in packages.items():
        if not isinstance(finding, dict) or not isinstance(finding.get('via'), list):
            raise ValueError(f'Invalid finding for {package}')
        for cause in finding['via']:
            if not isinstance(cause, dict):
                continue  # A string names an inherited affected package, not another advisory.
            url = cause.get('url')
            if not isinstance(url, str) or not url.startswith('https://'):
                raise ValueError(f'Advisory URL missing for {package}')
            advisories.setdefault(url, set()).add(package)
    if packages and not advisories:
        raise ValueError('Affected packages have no root advisory; inspect the report')
    return {
        'affected_package_entries': len(packages),
        'direct_dependency_entries': sorted(name for name, finding in packages.items()
                                            if finding.get('isDirect') is True),
        'unique_advisory_urls': len(advisories),
        'advisories': [{'url': url, 'root_finding_package_entries': sorted(names)}
                       for url, names in sorted(advisories.items())],
        'scope': 'Audit report grouping only; inherited parent entries are not assigned to an advisory here; no exploitability, runtime reachability, safe fix or deployment claim',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audit_json', type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(json.loads(args.audit_json.read_text())), indent=2))


if __name__ == '__main__':
    main()
