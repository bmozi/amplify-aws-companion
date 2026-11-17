"""Verify and run a trusted companion ZIP in a temporary extraction on this host."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat
import subprocess
import sys
import tempfile
import zipfile

BASE = Path(__file__).resolve().parents[1]
MANIFEST = 'SOURCE-MANIFEST.sha256'
MAX_SOURCE_BYTES = 300_000_000


def verified_contents(payload):
    """Reject ambiguous extraction paths and verify every file before execution."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        entries = archive.infolist()
        if len(entries) > 10000 or sum(info.file_size for info in entries) > MAX_SOURCE_BYTES:
            raise ValueError('Archive exceeds this verifier\'s bounded source-package size')
        names, folded = set(), set()
        for info in entries:
            name = info.filename
            path = PurePosixPath(name)
            mode = stat.S_IFMT(info.external_attr >> 16)
            if (not name or '\\' in name or path.is_absolute() or
                any(part in {'.', '..', '.git'} for part in path.parts) or
                path.as_posix() != name or info.is_dir() or ':' in name or
                mode not in (0, stat.S_IFREG) or info.flag_bits & 1):
                raise ValueError('Unsupported or unsafe archive member: '+name)
            if name in names or name.casefold() in folded:
                raise ValueError('Duplicate or case-colliding archive member: '+name)
            names.add(name);folded.add(name.casefold())
        if MANIFEST not in names:
            raise ValueError('Missing source manifest')
        contents = {name: archive.read(name) for name in names}
    expected = {}
    for line in contents[MANIFEST].decode('utf-8').splitlines():
        digest, separator, name = line.partition('  ')
        if not separator or not re.fullmatch('[0-9a-f]{64}', digest) or not name or name in expected:
            raise ValueError('Invalid or duplicate manifest entry')
        expected[name] = digest
    if set(expected) != names - {MANIFEST}:
        raise ValueError('Archive members and manifest entries differ')
    for name, digest in expected.items():
        if hashlib.sha256(contents[name]).hexdigest() != digest:
            raise ValueError('Source bytes differ from manifest: '+name)
    if 'scripts/check-companion.py' not in expected:
        raise ValueError('Missing companion check runner')
    return contents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=BASE/'artifacts/aws-amplify-lab-source.zip')
    parser.add_argument('--analytics-python', type=Path)
    parser.add_argument('--domain-python', type=Path)
    parser.add_argument('--check-timeout', type=int, default=300,
                        help='Seconds allowed for the companion suite (default: 300)')
    parser.add_argument('--app-config', type=Path,
                        help='Opt in to fresh npm ci and app checks using this separately supplied Amplify client JSON')
    args = parser.parse_args()
    if not 30 <= args.check_timeout <= 3600:
        parser.error('--check-timeout must be between 30 and 3600 seconds')
    if sys.flags.optimize:
        raise SystemExit('Run without Python optimization')
    report = {'started_utc': datetime.now(timezone.utc).isoformat(),
              'host': platform.platform(), 'python': sys.version,
              'scope': 'Temporary extraction on this existing host; trusted source only; not a sandbox, fresh OS, AWS test or book review',
              'status': 'failed', 'checks_started': False}
    root = None
    try:
        payload = args.archive.read_bytes()
        report['archive_sha256'] = hashlib.sha256(payload).hexdigest()
        contents = verified_contents(payload)
        report['source_files'] = len(contents)-1
        report['manifest_sha256'] = hashlib.sha256(contents[MANIFEST]).hexdigest()
        with tempfile.TemporaryDirectory(prefix='amplify-package-check-') as temporary:
            root = Path(temporary)
            for name, data in contents.items():
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            command = [sys.executable, 'scripts/check-companion.py']
            if args.app_config:
                config = args.app_config.read_bytes()
                if not isinstance(json.loads(config), dict):
                    raise ValueError('App client configuration must be a JSON object')
                report['app_config_sha256'] = hashlib.sha256(config).hexdigest()
                (root/'app/amplify_outputs.json').write_bytes(config)
                # Installation is explicit, in the temporary extraction, without lifecycle scripts.
                # This is trusted-source verification, not a sandbox for arbitrary npm packages.
                install_env = {k: v for k, v in os.environ.items() if not k.startswith('AWS_')}
                install_env.update(AWS_CONFIG_FILE=str(root/'empty-aws-config'),
                                   AWS_SHARED_CREDENTIALS_FILE=str(root/'empty-aws-credentials'),
                                   AWS_EC2_METADATA_DISABLED='true')
                installed = subprocess.run(['npm', 'ci', '--ignore-scripts', '--no-audit', '--no-fund'],
                                           cwd=root/'app', env=install_env, text=True,
                                           capture_output=True, timeout=300)
                report['app_install'] = {'returncode': installed.returncode,
                                         'stdout': installed.stdout, 'stderr': installed.stderr}
                if installed.returncode:
                    raise ValueError('Fresh locked app install failed; see app_install in report')
                command += ['--app-toolchain']
            for option in ['analytics_python', 'domain_python']:
                value = getattr(args, option)
                if value:
                    # Preserve virtual-environment executable paths, including symlinks.
                    command += ['--'+option.replace('_','-'), str(value.absolute())]
            report['checks_started'] = True
            result = subprocess.run(command, cwd=root, text=True, capture_output=True,
                                    timeout=args.check_timeout)
            report['returncode'] = result.returncode
            report['stdout'], report['stderr'] = result.stdout, result.stderr
            evidence = root/'artifacts/companion-checks.json'
            if evidence.exists():
                report['companion'] = json.loads(evidence.read_text())
            if args.app_config and result.returncode == 0:
                publisher = root/'app/frontend-publisher'
                installed = subprocess.run(['npm', 'ci', '--ignore-scripts', '--no-audit', '--no-fund'],
                                           cwd=publisher, env=install_env, text=True,
                                           capture_output=True, timeout=300)
                report['publisher_install'] = {'returncode': installed.returncode,
                                               'stdout': installed.stdout, 'stderr': installed.stderr}
                if installed.returncode:
                    raise ValueError('Fresh locked publisher install failed; see publisher_install')
                staged = subprocess.run([sys.executable, 'scripts/stage-frontend-publisher.py'],
                                        cwd=root, text=True, capture_output=True, timeout=60)
                if staged.returncode:
                    report['publisher_stage'] = {'stdout': staged.stdout, 'stderr': staged.stderr}
                    raise ValueError('Publisher source staging failed; see publisher_stage')
                (publisher/'amplify_outputs.json').write_bytes(config)
                audit = subprocess.run(['npm', 'audit', '--audit-level=moderate', '--json'],
                                       cwd=publisher, env=install_env, text=True,
                                       capture_output=True, timeout=120)
                try:
                    audit_data = json.loads(audit.stdout)
                    counts = audit_data['metadata']['vulnerabilities']
                except (ValueError, KeyError, TypeError) as error:
                    raise ValueError('Publisher npm audit did not return usable advisory metadata') from error
                report['publisher_audit'] = {'returncode': audit.returncode, 'counts': counts}
                if audit.returncode or counts.get('total'):
                    raise ValueError('Publisher toolchain audit reported findings or failed')
                built = subprocess.run(['npm', 'run', 'build'], cwd=publisher, env=install_env,
                                       text=True, capture_output=True, timeout=120)
                report['publisher_build'] = {'returncode': built.returncode,
                                             'stdout': built.stdout, 'stderr': built.stderr}
                if built.returncode:
                    raise ValueError('Publisher frontend build failed; see publisher_build')
                def file_hashes(directory):
                    return {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in directory.rglob('*') if path.is_file()}
                comparison = file_hashes(root/'app/dist') == file_hashes(publisher/'dist')
                report['publisher_dist_matches_app'] = comparison
                if not comparison:
                    raise ValueError('Publisher browser files differ from full app build')
            if (result.returncode == 0 and report.get('companion', {}).get('all_requested_passed')
                    and report['companion'].get('source_basis') == 'verified-archive-manifest'):
                report['status'] = 'passed'
        report['temporary_extraction_removed'] = not root.exists()
    except (OSError, ValueError, zipfile.BadZipFile, subprocess.TimeoutExpired) as error:
        report['error'] = str(error)
    if root is not None:
        report['temporary_extraction_removed'] = not root.exists()
    output = BASE/'artifacts/package-checks.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({key: value for key, value in report.items()
                      if key not in {'companion','stdout','stderr','app_install',
                                     'publisher_install','publisher_build'}}, indent=2))
    print('Report:', output)
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
