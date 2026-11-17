"""Local complete-set publication with trusted approval fixtures; no media codec or AWS."""
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import threading


def digest(value):
    return hashlib.sha256(value).hexdigest()


def publish(db, objects, manifest, approval, expected_generation, fail=False):
    encoded = json.dumps(manifest, sort_keys=True)
    if approval != digest(encoded.encode()):
        return 'approval mismatch'
    if set(manifest['variants']) != {'thumbnail', 'large'}:
        return 'incomplete set'
    for variant, item in manifest['variants'].items():
        # This fixed fixture namespace is not a general path-sanitization API.
        if item['key'] != f"published/{manifest['revision']}/{variant}":
            return 'invalid publication path'
        if item['key'] not in objects or digest(objects[item['key']]) != item['digest']:
            return 'missing or changed output'
    db.execute('BEGIN IMMEDIATE')
    try:
        generation, current_revision = db.execute('SELECT generation, revision FROM current').fetchone()
        if generation != expected_generation:
            db.rollback()
            return 'stale publication'
        if manifest['revision'] <= current_revision:
            db.rollback()
            return 'older or duplicate revision'
        db.execute('UPDATE current SET generation=?,revision=?,manifest=?',
                   (generation + 1, manifest['revision'], encoded))
        if fail:
            raise RuntimeError('injected before commit')
        db.commit()
        return 'published'
    except Exception:
        db.rollback()
        raise


def main():
    objects = {'private/original': b'fictional original with private annotation'}

    def candidate(revision):
        variants = {}
        for name in ('thumbnail', 'large'):
            key = f'published/{revision}/{name}'
            objects[key] = f'synthetic {name} from revision {revision}'.encode()
            variants[name] = {'key': key, 'digest': digest(objects[key])}
        return {'revision': revision, 'source_digest': digest(objects['private/original']),
                'recipe': 'synthetic-v1', 'variants': variants}

    def approve(manifest):
        return digest(json.dumps(manifest, sort_keys=True).encode())

    with tempfile.TemporaryDirectory(prefix='amplify-media-') as folder:
        db = sqlite3.connect(Path(folder) / 'publication.sqlite', isolation_level=None)
        try:
            db.execute('CREATE TABLE current (generation INTEGER, revision INTEGER, manifest TEXT)')
            db.execute("INSERT INTO current VALUES (0,0,'{}')")
            old = candidate(7)
            assert publish(db, objects, old, approve(old), 0) == 'published'

            def observed():
                # Independent read path through a fresh connection, as a visitor-record fixture.
                with closing(sqlite3.connect(Path(folder) / 'publication.sqlite')) as reader:
                    return reader.execute('SELECT generation, revision, manifest FROM current').fetchone()

            prior = observed()
            new = candidate(8)
            missing = objects.pop('published/8/large')
            assert publish(db, objects, new, approve(new), 1) == 'missing or changed output'
            assert observed() == prior
            objects['published/8/large'] = missing
            incomplete = dict(new, variants={'thumbnail': new['variants']['thumbnail']})
            assert publish(db, objects, incomplete, approve(incomplete), 1) == 'incomplete set'
            assert observed() == prior
            assert publish(db, objects, new, approve(old), 1) == 'approval mismatch'
            assert observed() == prior
            objects['published/8/large'] = b'changed after review'
            assert publish(db, objects, new, approve(new), 1) == 'missing or changed output'
            assert observed() == prior
            objects['published/8/large'] = missing
            try:
                publish(db, objects, new, approve(new), 1, fail=True)
            except RuntimeError as error:
                assert str(error) == 'injected before commit'
            else:
                raise AssertionError('Expected injected failure')
            assert observed() == prior
            assert publish(db, objects, new, approve(new), 1) == 'published'
            current = observed()
            assert current[:2] == (2, 8)
            visible = json.loads(current[2])
            assert set(visible['variants']) == {'thumbnail', 'large'}
            assert all(b'revision 8' in objects[v['key']] for v in visible['variants'].values())
            assert all(objects[v['key']] != objects['private/original'] for v in visible['variants'].values())
            assert publish(db, objects, old, approve(old), 1) == 'stale publication'
            assert publish(db, objects, old, approve(old), 2) == 'older or duplicate revision'
            assert publish(db, objects, new, approve(new), 2) == 'older or duplicate revision'
            assert observed() == current

            # Two independently approved jobs observed generation 2. Each opens
            # its own connection; only one can commit that expected-generation transition.
            contenders = [candidate(9), candidate(10)]
            barrier = threading.Barrier(2)

            def compete(manifest):
                with closing(sqlite3.connect(Path(folder) / 'publication.sqlite',
                                             isolation_level=None, timeout=10)) as publisher:
                    barrier.wait(timeout=10)
                    return manifest['revision'], publish(publisher, objects, manifest,
                                                        approve(manifest), 2)

            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(compete, contenders))
            assert sorted(result for _, result in outcomes) == ['published', 'stale publication']
            winner = next(revision for revision, result in outcomes if result == 'published')
            loser = next(revision for revision, result in outcomes if result == 'stale publication')
            raced = observed()
            assert raced[:2] == (3, winner)
            raced_manifest = json.loads(raced[2])
            assert raced_manifest == next(m for m in contenders if m['revision'] == winner)
            assert all(f'revision {winner}'.encode() in objects[v['key']]
                       for v in raced_manifest['variants'].values())
            print('Competing revisions:', outcomes, '; selected complete revision:', winner,
                  '; rejected job requires review:', loser)
        finally:
            db.close()
    assert not Path(folder).exists()
    print('PASS: missing/incomplete/changed outputs and wrong approval preserve prior publication;')
    print('injected pre-commit failure rolls back; complete revision publishes; stale/duplicate jobs reject.')
    print('Separate-connection contention permits one generation transition; temporary database removed.')
    print('Synthetic bytes and trusted approval; no codec, IAM, object-mutation or cache proof.')


if __name__ == '__main__':
    main()
