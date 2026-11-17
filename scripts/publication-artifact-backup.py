"""Upload immutable private working-artifact bundles, or restore the current one."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
POINTER = ROOT / 'docs/CURRENT-PUBLICATION-ARTIFACTS.json'
REPO = 'bmozi/aws-capabilities-lab'

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def gh_json(*args):
    return json.loads(subprocess.check_output(['gh', *args], text=True))

def verify(archive, manifest):
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise SystemExit('ZIP CRC verification failed')
        expected = {r['path']: r for r in manifest['files']}
        if len(expected) != len(manifest['files']) or set(z.namelist()) != set(expected) | {'BUNDLE-MANIFEST.json'}:
            raise SystemExit('Bundle inventory mismatch')
        if json.loads(z.read('BUNDLE-MANIFEST.json')) != manifest:
            raise SystemExit('Embedded manifest mismatch')
        for name, row in expected.items():
            if Path(name).is_absolute() or '..' in Path(name).parts:
                raise SystemExit('Unsafe archive path')
            data = z.read(name)
            if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise SystemExit('File verification failed: ' + name)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    up = sub.add_parser('upload')
    up.add_argument('--selection', type=Path, required=True)
    up.add_argument('--tag', required=True)
    up.add_argument('--name', required=True)
    down = sub.add_parser('restore')
    down.add_argument('--destination', type=Path, required=True)
    a = p.parse_args()
    if a.action == 'restore':
        pointer = json.loads(POINTER.read_text())
        destination = a.destination.resolve()
        if destination.exists():
            raise SystemExit('Choose a new destination; existing files will not be overwritten')
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run(['gh', 'release', 'download', pointer['tag'], '--repo', pointer['repository'], '--pattern', pointer['asset_name'], '--dir', temp], check=True)
            archive = Path(temp) / pointer['asset_name']
            if digest(archive) != pointer['sha256']:
                raise SystemExit('Downloaded archive hash mismatch')
            verify(archive, pointer['manifest'])
            destination.mkdir(parents=True)
            with zipfile.ZipFile(archive) as z:
                z.extractall(destination)
        print('Restored and hash-verified:', destination)
        return
    if Path(a.name).name != a.name or not a.name.endswith('.zip'):
        raise SystemExit('Asset name must be a ZIP basename')
    repo = gh_json('api', 'repos/' + REPO)
    if not repo['private']:
        raise SystemExit('Private repository required')
    releases = gh_json('api', 'repos/' + REPO + '/releases?per_page=100')
    release = next((r for r in releases if r['tag_name'] == a.tag), None)
    if not release or not release['draft']:
        raise SystemExit('An existing private draft release is required')
    if any(x['name'] == a.name for x in release['assets']):
        raise SystemExit('Asset already exists; choose a new immutable name')
    manifest = json.loads(a.selection.read_text())
    for row in manifest['files']:
        path = (ROOT / row['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise SystemExit('Invalid selected file: ' + row['path'])
        if digest(path) != row['sha256'] or path.stat().st_size != row['bytes']:
            raise SystemExit('Selected file changed: ' + row['path'])
    output = ROOT / 'artifacts/publication-backups' / a.name
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for row in manifest['files']:
            z.write(ROOT / row['path'], row['path'])
        z.writestr('BUNDLE-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    verify(output, manifest)
    sha = digest(output)
    subprocess.run(['gh', 'release', 'upload', a.tag, str(output), '--repo', REPO], check=True)
    remote = gh_json('api', f'repos/{REPO}/releases/{release["id"]}')
    asset = next(x for x in remote['assets'] if x['name'] == a.name)
    if asset['size'] != output.stat().st_size or asset.get('digest') != 'sha256:' + sha:
        raise SystemExit('Remote digest/size mismatch; current pointer not updated')
    pointer = dict(repository=REPO, tag=a.tag, release_id=release['id'], release_draft=True,
                   asset_name=a.name, asset_id=asset['id'], bytes=asset['size'], sha256=sha,
                   server_digest_verified=True, manifest=manifest)
    POINTER.write_text(json.dumps(pointer, indent=2) + '\n')
    print('Uploaded and server-hash-verified:', a.name, flush=True)

if __name__ == '__main__':
    main()
