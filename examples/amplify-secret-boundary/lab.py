"""Build and serve fictional Vite files to test the browser/secret boundary locally."""

from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import tempfile
from threading import Thread
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[2]
VITE = ROOT / 'app/node_modules/vite/bin/vite.js'
PUBLIC_VALUE = 'FICTIONAL_PUBLIC_DESTINATION_8419'
MISLABELED_SECRET = 'FICTIONAL_BROWSER_KEY_2718'
SERVER_ONLY_SECRET = 'FICTIONAL_SERVER_ONLY_KEY_3141'
COPIED_SECRET = 'FICTIONAL_COPIED_FILE_KEY_1618'


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def served_bytes(directory, path):
    handler = partial(QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f'http://127.0.0.1:{server.server_port}/{path}', timeout=5) as response:
            if response.status != 200:
                raise AssertionError('Local static file was not served')
            return response.read()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def build_case(work, *, unsafe):
    (work / 'src').mkdir(parents=True)
    (work / 'public').mkdir()
    (work / 'node_modules').symlink_to(ROOT / 'app/node_modules', target_is_directory=True)
    (work / 'package.json').write_text('{"private":true,"type":"module"}\n')
    (work / 'index.html').write_text('<!doctype html><div id="app"></div><script type="module" src="/src/main.js"></script>\n')
    if unsafe:
        (work / '.env.production').write_text(
            f'VITE_SAMPLE_KEY={MISLABELED_SECRET}\nSERVER_ONLY_KEY={SERVER_ONLY_SECRET}\n')
        (work / 'src/main.js').write_text(
            "document.querySelector('#app').textContent = import.meta.env.VITE_SAMPLE_KEY;\n")
        (work / 'public/partner.json').write_text(json.dumps({'key': COPIED_SECRET}) + '\n')
    else:
        (work / '.env.production').write_text(
            f'VITE_PUBLIC_DESTINATION={PUBLIC_VALUE}\nSERVER_ONLY_KEY={SERVER_ONLY_SECRET}\n')
        (work / 'src/main.js').write_text(
            "document.querySelector('#app').textContent = import.meta.env.VITE_PUBLIC_DESTINATION;\n")
    built = subprocess.run(['node', str(VITE), 'build'], cwd=work,
                           text=True, capture_output=True, timeout=60)
    if built.returncode:
        raise RuntimeError('Vite local build failed: ' + built.stderr[-1200:])
    scripts = list((work / 'dist/assets').glob('*.js'))
    if len(scripts) != 1:
        raise AssertionError('Expected one browser JavaScript file in the tiny fixture')
    browser = served_bytes(work / 'dist', 'assets/' + scripts[0].name)
    copied = served_bytes(work / 'dist', 'partner.json') if unsafe else None
    if unsafe:
        assert MISLABELED_SECRET.encode() in browser
        assert COPIED_SECRET.encode() in copied
    else:
        assert PUBLIC_VALUE.encode() in browser
        assert MISLABELED_SECRET.encode() not in browser
        assert COPIED_SECRET.encode() not in browser
        assert not (work / 'dist/partner.json').exists()
    assert SERVER_ONLY_SECRET.encode() not in browser
    if copied is not None:
        assert SERVER_ONLY_SECRET.encode() not in copied
    return {'browser_sha256': sha256(browser).hexdigest(),
            'fictional_browser_key_served': MISLABELED_SECRET.encode() in browser,
            'fictional_copied_file_key_served': copied is not None and COPIED_SECRET.encode() in copied,
            'fictional_server_only_key_served': SERVER_ONLY_SECRET.encode() in browser or
                                                 (copied is not None and SERVER_ONLY_SECRET.encode() in copied)}


def run():
    if not VITE.is_file():
        raise RuntimeError('Install the locked app dependencies before this optional Vite exercise')
    with tempfile.TemporaryDirectory(prefix='amplify-secret-boundary-') as folder:
        root = Path(folder)
        unsafe = build_case(root / 'unsafe', unsafe=True)
        safe = build_case(root / 'safe', unsafe=False)
        assert unsafe['browser_sha256'] != safe['browser_sha256']
        assert unsafe['fictional_browser_key_served'] and unsafe['fictional_copied_file_key_served']
        assert not safe['fictional_browser_key_served'] and not safe['fictional_copied_file_key_served']
        return {'unsafe': unsafe, 'safe': safe,
                'scope': 'two local Vite builds and loopback-served fictional files; no Amplify secret(), AWS resource, credential or real customer'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
