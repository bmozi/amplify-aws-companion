"""Show the drain test catches the former daemon-thread behavior in an isolated copy."""
from pathlib import Path
import shutil
import tempfile
import lab

original = lab.BASE
try:
    with tempfile.TemporaryDirectory(prefix='amplify-drain-negative-') as folder:
        root = Path(folder)
        for name in ['Dockerfile', '.dockerignore', 'service.py']:
            shutil.copyfile(original / name, root / name)
        service = root / 'service.py'
        text = service.read_text()
        assert text.count('daemon_threads = False') == 1
        service.write_text(text.replace('daemon_threads = False', 'daemon_threads = True'))
        lab.BASE = root
        try:
            lab.main()
        except lab.DrainFailure:
            print('Negative control detected the abandoned in-flight request.')
        else:
            raise AssertionError('Negative control failed to detect the shutdown regression')
finally:
    lab.BASE = original
