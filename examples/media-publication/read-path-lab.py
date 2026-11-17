"""Exercise the museum visitor route with real loopback HTTP requests."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
from urllib.error import HTTPError
from urllib.request import urlopen

from lab import digest, publish
from read_path import visitor_server, withdraw


def get(url):
    try:
        with urlopen(url, timeout=3) as response:
            return response.status, response.read(), dict(response.headers)
    except HTTPError as error:
        return error.code, error.read(), dict(error.headers)


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    objects = {'private/original': b'fictional original with private annotation'}

    def candidate(revision):
        variants = {}
        for name in ('thumbnail', 'large'):
            key = f'published/{revision}/{name}'
            value = f'synthetic {name} from revision {revision}'.encode()
            objects[key] = value
            variants[name] = {'key': key, 'digest': digest(value)}
        return {'revision': revision, 'source_digest': digest(objects['private/original']),
                'recipe': 'synthetic-v1', 'variants': variants}

    def approve(manifest):
        return digest(json.dumps(manifest, sort_keys=True).encode())

    with tempfile.TemporaryDirectory(prefix='amplify-media-read-') as folder:
        db_path = Path(folder) / 'publication.sqlite'
        with closing(sqlite3.connect(db_path, isolation_level=None)) as db:
            db.execute('CREATE TABLE current (generation INTEGER, revision INTEGER, manifest TEXT)')
            db.execute("INSERT INTO current VALUES (0,0,'{}')")
            server = visitor_server(db_path, objects)
            worker = threading.Thread(target=server.serve_forever)
            worker.start()
            base = f'http://127.0.0.1:{server.server_port}'
            try:
                assert get(base + '/current')[0] == 410
                assert get(base + '/private/original')[0] == 404
                old = candidate(7)
                assert publish(db, objects, old, approve(old), 0) == 'published'
                status, body, _ = get(base + '/current')
                assert status == 200
                catalog = json.loads(body)
                assert catalog == {'revision': 7, 'variants': {
                    'thumbnail': '/media/7/thumbnail', 'large': '/media/7/large'}}
                assert get(base + catalog['variants']['thumbnail'])[:2] == (
                    200, objects['published/7/thumbnail'])

                new = candidate(8)
                large = objects.pop('published/8/large')
                assert publish(db, objects, new, approve(new), 1) == 'missing or changed output'
                assert json.loads(get(base + '/current')[1]) == catalog
                assert get(base + '/media/8/thumbnail')[0] == 404
                objects['published/8/large'] = large
                assert publish(db, objects, new, approve(new), 1) == 'published'
                assert json.loads(get(base + '/current')[1])['revision'] == 8
                assert get(base + '/media/7/thumbnail')[0] == 404
                assert get(base + '/media/8/thumbnail')[:2] == (
                    200, objects['published/8/thumbnail'])
                assert get(base + '/media/8/large')[:2] == (200, large)
                assert get(base + '/media/8/large')[2]['Cache-Control'] == 'no-store'
                assert get(base + '/private/original')[0] == 404

                objects['published/8/large'] = b'changed after publication'
                assert get(base + '/media/8/large')[0] == 503
                assert get(base + '/media/8/thumbnail')[0] == 200
                objects['published/8/large'] = large
                assert withdraw(db, 1) == 'stale withdrawal'
                assert get(base + '/current')[0] == 200
                assert withdraw(db, 2) == 'withdrawn'
                assert get(base + '/current')[0] == 410
                assert get(base + '/media/8/large')[0] == 404
                assert get(base + '/private/original')[0] == 404
                assert publish(db, objects, old, approve(old), 3) == 'older or duplicate revision'
                print('PASS: loopback visitor saw only the selected complete revision;')
                print('missing candidate stayed hidden, changed bytes failed, stale withdrawal rejected,')
                print('and withdrawal removed the local pointer without exposing the private original.')
                print('No S3, CloudFront, cache propagation, browser copy or direct-origin test.')
            finally:
                server.shutdown()
                worker.join(timeout=3)
                server.server_close()
                assert not worker.is_alive()


if __name__ == '__main__':
    main()
