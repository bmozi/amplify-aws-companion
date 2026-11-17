"""Local ZIP demonstration of the real publisher's digest and marker checks.

No AWS command, credential, npm install, or application build is run.
"""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
PUBLISHER_PATH = ROOT / 'scripts/deploy-frontend-from-github.py'
COMMIT = 'a' * 40
RUN_ID = '42'
APPROVED_PAGE = b'<h1>Approved lesson</h1>\n'
CHANGED_PAGE = b'<h1>Changed by a hypothetical build step</h1>\n'


def load_publisher():
    spec = importlib.util.spec_from_file_location('actual_frontend_publisher', PUBLISHER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_archive(path, page):
    marker = {'source_commit': COMMIT, 'workflow_run_id': RUN_ID}
    with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
        archive.writestr('index.html', page)
        archive.writestr('deployment.json', json.dumps(marker) + '\n')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publisher_accepts(module, archive, build_digest):
    env = {'SOURCE_COMMIT': COMMIT, 'WORKFLOW_RUN_ID': RUN_ID,
           'EXPECTED_ARCHIVE_SHA256': build_digest}
    with patch.dict(os.environ, env):
        try:
            module.expected_marker(archive)
        except SystemExit:
            return False
    return True


def approved_content_matches(archive):
    with ZipFile(archive) as contents:
        return contents.read('index.html') == APPROVED_PAGE


def results():
    module = load_publisher()
    with tempfile.TemporaryDirectory(prefix='amplify-build-trust-') as folder:
        directory = Path(folder)
        approved = directory / 'approved.zip'
        approved_digest = make_archive(approved, APPROVED_PAGE)
        baseline = (publisher_accepts(module, approved, approved_digest), approved_content_matches(approved))

        tampered = directory / 'changed-after-hash.zip'
        make_archive(tampered, CHANGED_PAGE)
        after_hash = (publisher_accepts(module, tampered, approved_digest), approved_content_matches(tampered))

        changed_in_build = directory / 'changed-in-build.zip'
        changed_digest = make_archive(changed_in_build, CHANGED_PAGE)
        build_changed = (publisher_accepts(module, changed_in_build, changed_digest), approved_content_matches(changed_in_build))
    return {'approved': baseline, 'changed_after_hash': after_hash, 'changed_in_build': build_changed}


if __name__ == '__main__':
    observed = results()
    assert observed == {'approved': (True, True),
                        'changed_after_hash': (False, False),
                        'changed_in_build': (True, False)}
    for name, (publisher_check, content_check) in observed.items():
        print(f'{name}: digest_and_marker={publisher_check} approved_content={content_check}')
