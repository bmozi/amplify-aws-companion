"""Run the trusted importer against a disposable loopback-only MySQL fixture."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import tempfile
import time
import uuid

IMAGE = 'mysql@sha256:24989179f58856db763f418010c1169fecc944e3ec1ea7e921572d83eb070f70'
SQL = """
CREATE DATABASE teaching;
CREATE TABLE teaching.shops (id INT NOT NULL PRIMARY KEY);
CREATE TABLE teaching.notes (
 id INT NOT NULL PRIMARY KEY, shop_id INT NOT NULL,
 title VARCHAR(80), amount DECIMAL(10,2),
 INDEX by_shop_title (shop_id, title)
);
CREATE USER 'reader'@'%' IDENTIFIED BY 'fixture-reader-only' REQUIRE SSL;
GRANT SELECT ON teaching.* TO 'reader'@'%';
"""

def run(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, timeout=120, **kwargs)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', default='app')
    args = parser.parse_args()
    app = Path(args.app).resolve(strict=True)
    name = 'amplify-mysql-probe-' + uuid.uuid4().hex[:12]
    # The image must be deliberately pulled first; never silently fetch arbitrary code.
    inspected = run(['docker', 'image', 'inspect', IMAGE], check=True)
    image_id = json.loads(inspected.stdout)[0]['Id']
    with tempfile.TemporaryDirectory(prefix='amplify-mysql-probe-') as directory:
        try:
            run(['docker', 'run', '--detach', '--name', name, '--memory', '1g',
                 '--cpus', '1', '--pids-limit', '256', '--tmpfs', '/var/lib/mysql:rw,size=512m',
                 '-p', '127.0.0.1::3306', '-e', 'MYSQL_ROOT_PASSWORD=fixture-root-only',
                 '-e', 'MYSQL_INITDB_SKIP_TZINFO=1', IMAGE], check=True)
            deadline = time.monotonic() + 90
            while True:
                state = json.loads(run(['docker', 'inspect', name], check=True).stdout)[0]
                assert state['State']['Running'], 'Fixture server stopped during initialization'
                ready = run(['docker', 'exec', name, 'mysql', '--protocol=TCP',
                             '-h127.0.0.1', '-uroot', '-pfixture-root-only', '-e', 'SELECT 1'])
                if ready.returncode == 0:
                    break
                if time.monotonic() >= deadline:
                    raise TimeoutError('Fixture MySQL did not become ready within 90 seconds')
                time.sleep(1)
            run(['docker', 'exec', '-i', name, 'mysql', '-uroot', '-pfixture-root-only'],
                input=SQL, check=True)
            ca = Path(directory) / 'ca.pem'
            ca.write_text(run(['docker', 'exec', name, 'cat', '/var/lib/mysql/ca.pem'], check=True).stdout)
            binding = state['NetworkSettings']['Ports']['3306/tcp'][0]
            assert binding['HostIp'] == '127.0.0.1'
            env = {k: v for k, v in os.environ.items() if not k.startswith('AWS_')}
            checked = run(['node', str(Path(__file__).with_name('check-mysql-server.cjs')),
                           str(app), binding['HostPort'], str(ca)], env=env)
            print(checked.stdout, end='')
            if checked.returncode:
                print(checked.stderr, end='')
                raise RuntimeError('Importer probe failed')
            print(json.dumps({'image': IMAGE, 'image_id': image_id,
                              'scope': 'Disposable local server; synthetic schema and credentials'}))
        finally:
            removed = run(['docker', 'rm', '--force', '--volumes', name])
            remaining = run(['docker', 'container', 'ls', '--all', '--filter', 'name=^/' + name + '$', '--quiet'], check=True)
            if remaining.stdout.strip():
                raise RuntimeError('Fixture container cleanup failed: ' + removed.stderr)
            print('Fixture container removed; tmpfs data and temporary CA discarded.')

if __name__ == '__main__':
    main()
