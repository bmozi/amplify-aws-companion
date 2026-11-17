"""Local multi-file publication lesson; no AWS calls or cloud-atomicity claim."""

import hashlib
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def run_path(root, run_id):
    if not isinstance(run_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', run_id):
        raise ValueError('Run ID must be a bounded path-safe label')
    return Path(root) / 'candidates' / run_id


def stage(root, run_id, revision, parts, expected_ids, fail_after=None):
    """Write immutable parts and the manifest last; partial output remains unselected."""
    if type(revision) is not int or revision <= 0:
        raise ValueError('Source revision must be positive')
    parts = [list(part) for part in parts]
    expected_ids = list(expected_ids)
    rows = [row for part in parts for row in part]
    ids = [row[0] for row in rows if isinstance(row, (list, tuple)) and len(row) == 2]
    if (len(parts) != 2 or len(rows) != len(ids) or not rows or
            any(type(row[0]) is not str or not row[0] or type(row[1]) is not int
                or not -(2**63) <= row[1] < 2**63 for row in rows) or
            len(ids) != len(set(ids)) or len(expected_ids) != len(set(expected_ids)) or
            set(ids) != set(expected_ids)):
        raise ValueError('Two complete parts must match distinct expected IDs and integer cents')
    folder = run_path(root, run_id)
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {'run_id': run_id, 'source_revision': revision,
                'expected_ids': sorted(expected_ids), 'parts': []}
    for index, rows_in_part in enumerate(parts, 1):
        name = f'part-{index}.json'
        blob = encoded(rows_in_part)
        path = folder / name
        if path.exists():
            if path.read_bytes() != blob:
                raise ValueError('Run ID reused with changed part bytes')
        else:
            with path.open('xb') as output:
                output.write(blob)
        manifest['parts'].append({'name': name, 'sha256': digest(blob)})
        if fail_after == index:
            raise RuntimeError('Injected failure after writing an unselected part')
    manifest_bytes = encoded(manifest)
    path = folder / 'manifest.json'
    if path.exists():
        if path.read_bytes() != manifest_bytes:
            raise ValueError('Run ID reused with changed manifest')
        return 'already_staged'
    with path.open('xb') as output:
        output.write(manifest_bytes)
    return 'staged'


def candidate(root, run_id):
    folder = run_path(root, run_id)
    manifest = json.loads((folder / 'manifest.json').read_text())
    if manifest['run_id'] != run_id or [item['name'] for item in manifest['parts']] != ['part-1.json', 'part-2.json']:
        raise ValueError('Unexpected manifest identity or part names')
    rows = []
    for item in manifest['parts']:
        blob = (folder / item['name']).read_bytes()
        if digest(blob) != item['sha256']:
            raise ValueError('Selected part changed after manifest creation')
        rows.extend(tuple(row) for row in json.loads(blob))
    ids = [event_id for event_id, _ in rows]
    if len(ids) != len(set(ids)) or sorted(ids) != manifest['expected_ids']:
        raise ValueError('Selected rows do not match the declared source IDs')
    return manifest, sorted(rows)


def selected(root):
    path = Path(root) / 'selected.json'
    return json.loads(path.read_text()) if path.exists() else {
        'generation': 0, 'run_id': None, 'source_revision': 0}


def publish(root, run_id, expected_generation, fail_after_pointer=False):
    """Sequential local selection. This is not a distributed compare-and-swap."""
    if type(expected_generation) is not int or expected_generation < 0:
        raise ValueError('Expected generation must be nonnegative')
    prior = selected(root)
    if prior['run_id'] == run_id:
        candidate(root, run_id)
        return 'already_current', prior['generation']
    if prior['generation'] != expected_generation:
        return 'stale_generation', prior['generation']
    if not (run_path(root, run_id) / 'manifest.json').exists():
        return 'missing_complete_run', prior['generation']
    manifest, _ = candidate(root, run_id)
    if manifest['source_revision'] <= prior['source_revision']:
        return 'stale_source_revision', prior['generation']
    next_pointer = {'generation': prior['generation'] + 1, 'run_id': run_id,
                    'source_revision': manifest['source_revision']}
    temp = Path(root) / 'selected.json.tmp'
    temp.write_bytes(encoded(next_pointer))
    os.replace(temp, Path(root) / 'selected.json')
    if fail_after_pointer:
        raise RuntimeError('Injected lost reply after local pointer replacement')
    return 'published', next_pointer['generation']


def read_view(root, pointer=None):
    pointer = selected(root) if pointer is None else pointer
    if pointer['run_id'] is None:
        return {'pointer': pointer, 'rows': [], 'cents': 0}
    manifest, rows = candidate(root, pointer['run_id'])
    if manifest['source_revision'] != pointer['source_revision']:
        raise ValueError('Pointer and manifest source revisions differ')
    return {'pointer': pointer, 'rows': rows, 'cents': sum(cents for _, cents in rows)}


def unsafe_midwrite_view(root, old_parts, replacement_first_part):
    """Actually overwrite one file in a mutable folder before reading both."""
    folder = Path(root) / 'unsafe-latest'
    folder.mkdir(parents=True, exist_ok=True)
    for index, part in enumerate(old_parts, 1):
        (folder / f'part-{index}.json').write_bytes(encoded(part))
    (folder / 'part-1.json').write_bytes(encoded(replacement_first_part))
    rows = [tuple(row) for index in (1, 2)
            for row in json.loads((folder / f'part-{index}.json').read_text())]
    return {'rows': sorted(rows), 'cents': sum(cents for _, cents in rows)}


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization so fixture assertions execute')
    with TemporaryDirectory() as directory:
        root = Path(directory)
        assert stage(root, 'day1-v1', 1, [[('a', 100), ('b', 200)], []], ['a', 'b']) == 'staged'
        assert publish(root, 'day1-v1', 0) == ('published', 1)
        pinned_old = selected(root)
        assert read_view(root)['cents'] == 300
        try:
            stage(root, 'day1-v2', 2, [[('a', 100), ('b', 180)], [('late', 50)]],
                  ['a', 'b', 'late'], fail_after=1)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Expected injected staging failure')
        assert read_view(root)['cents'] == 300
        assert stage(root, 'day1-v2', 2, [[('a', 100), ('b', 180)], [('late', 50)]],
                     ['a', 'b', 'late']) == 'staged'
        try:
            publish(root, 'day1-v2', 1, fail_after_pointer=True)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Expected injected lost reply')
        assert publish(root, 'day1-v2', 1) == ('already_current', 2)
        assert read_view(root)['cents'] == 330
        assert read_view(root, pinned_old)['cents'] == 300
        assert publish(root, 'day1-v1', 1) == ('stale_generation', 2)
        unsafe_mixed_total = unsafe_midwrite_view(
            root, [[('a', 100), ('b', 200)], []], [('a', 100), ('b', 180)])['cents']
        assert unsafe_mixed_total == 280 and unsafe_mixed_total not in (300, 330)
        print(json.dumps({'old_complete_cents': 300, 'failed_stage_kept_old': True,
                          'new_complete_cents': 330, 'old_pinned_reader_cents': 300,
                          'unsafe_in_place_midwrite_cents': unsafe_mixed_total,
                          'lost_reply_retry': 'already_current',
                          'scope': 'same-host local files; no S3, Glue, Athena or distributed CAS'}, indent=2))


if __name__ == '__main__':
    main()
