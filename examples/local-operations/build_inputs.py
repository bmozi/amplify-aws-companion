"""Build and inspect synthetic static-site ZIPs; no AWS or external dependencies."""
import hashlib
import io
from pathlib import Path
import shutil
import tempfile
import zipfile


def copy_inputs(source, output):
    output.mkdir(exist_ok=True)
    for item in sorted(source.iterdir()):
        if not item.is_file():
            raise ValueError('This fixture accepts flat regular-file inputs only')
        shutil.copyfile(item, output/item.name)


def package(output):
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w', compression=zipfile.ZIP_STORED) as archive:
        for item in sorted(output.iterdir()):
            info = zipfile.ZipInfo(item.name, date_time=(2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, item.read_bytes())
    return data.getvalue()


def contents(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        assert len(archive.namelist()) == len(set(archive.namelist()))
        return {name: archive.read(name) for name in archive.namelist()}


def clean_build(source, root):
    # A new staging directory, never deletion of a caller's existing output.
    with tempfile.TemporaryDirectory(prefix='stage-', dir=root) as temporary:
        output = Path(temporary)
        copy_inputs(source, output)
        return package(output)


def main():
    with tempfile.TemporaryDirectory(prefix='static-build-') as temporary:
        root = Path(temporary)
        source, reused = root/'source', root/'reused-output'
        source.mkdir()
        (source/'index.html').write_bytes(b'<h1>Repair guide</h1>')
        (source/'expired-offer.html').write_bytes(b'<p>Old offer</p>')
        copy_inputs(source, reused)
        assert 'expired-offer.html' in contents(package(reused))

        (source/'expired-offer.html').unlink()  # Synthetic fixture only.
        (source/'index.html').write_bytes(b'<h1>Current repair guide</h1>')
        (source/'hours.txt').write_bytes(b'Monday 09:00 to 17:00\n')
        copy_inputs(source, reused)
        dirty = contents(package(reused))
        expected = {'index.html': b'<h1>Current repair guide</h1>',
                    'hours.txt': b'Monday 09:00 to 17:00\n'}
        assert dirty['index.html'] == expected['index.html']
        assert set(dirty) == set(expected) | {'expired-offer.html'}
        print('Counterexample: homepage updated, but reused output still packages expired-offer.html.')

        first, second = clean_build(source, root), clean_build(source, root)
        assert contents(first) == expected and contents(second) == expected
        assert first == second
        print('Fresh staging: exact expected paths and bytes; two builds have identical ZIP bytes.')
        print('Fixture artifact SHA256:', hashlib.sha256(first).hexdigest())

        (source/'hours.txt').write_bytes(b'Tuesday 09:00 to 17:00\n')
        changed = clean_build(source, root)
        assert changed != first
        assert contents(changed)['hours.txt'] == b'Tuesday 09:00 to 17:00\n'
        assert contents(first) == expected
        print('Changed input produces a new artifact; previously built bytes remain unchanged.')
    assert not root.exists()
    print('PASS: flat static-file packaging and cleanup only; no compiler or cloud proof.')


if __name__ == '__main__':
    import sys
    if sys.flags.optimize:
        raise SystemExit('Run without Python optimization')
    main()
