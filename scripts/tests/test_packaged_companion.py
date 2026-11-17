"""Check archive rejection boundaries without executing any archive source."""
import hashlib
import importlib.util
import io
from pathlib import Path
import stat
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('package_check', Path(__file__).resolve().parents[1]/'check-packaged-companion.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
NAME = 'scripts/check-companion.py'
BODY = b'# inert fixture, never executed\n'
MANIFEST = (hashlib.sha256(BODY).hexdigest()+'  '+NAME+'\n').encode()


def archive(extra=(), payload=BODY, manifest=MANIFEST, include_manifest=True):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as output:
        output.writestr(NAME, payload)
        if include_manifest:
            output.writestr(MODULE.MANIFEST, manifest)
        for name, data in extra:
            output.writestr(name, data)
    return stream.getvalue()


class PackageBoundaries(unittest.TestCase):
    def test_complete_manifest(self):
        self.assertEqual(MODULE.verified_contents(archive())[NAME], BODY)

    def test_uncompressed_size_limit_still_rejects_oversize_archive(self):
        with patch.object(MODULE, 'MAX_SOURCE_BYTES', len(BODY)):
            with self.assertRaisesRegex(ValueError, 'bounded source-package size'):
                MODULE.verified_contents(archive())

    def test_rejected_archives(self):
        link = zipfile.ZipInfo('link')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK|0o777)<<16
        cases = {'changed': archive(payload=b'changed'),
                 'missing_manifest': archive(include_manifest=False),
                 'unlisted': archive(extra=[('extra.txt', b'unlisted')]),
                 'traversal': archive(extra=[('../outside', b'no')]),
                 'case_collision': archive(extra=[('SCRIPTS/check-companion.py', BODY)]),
                 'symlink': archive(extra=[(link, b'target')]),
                 'git_override': archive(extra=[('.git/config', b'no')]),
                 'duplicate_manifest': archive(manifest=MANIFEST+MANIFEST)}
        for name, payload in cases.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                MODULE.verified_contents(payload)


if __name__ == '__main__':
    unittest.main()
