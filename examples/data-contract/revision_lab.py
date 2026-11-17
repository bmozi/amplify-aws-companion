"""Real SQLite stale-write checks with a controlled interleaving, not a load test."""
from contextlib import closing
from pathlib import Path
import json
import sqlite3
import tempfile

from lab import apply_update


PRICE = b'{"version":1,"part_id":"0012","price_cents":45}'
NOTE = b'{"version":1,"part_id":"0012","note":"Inspect seal"}'


def read(db):
    row = db.execute('SELECT part_id,price_cents,note,revision FROM parts').fetchone()
    return dict(zip(('part_id', 'price_cents', 'note', 'revision'), row))


def save(db, snapshot, payload, *, guarded=True):
    proposed = apply_update(snapshot, payload)
    # Deliberately writes the complete edited snapshot, as a form might do.
    sql = 'UPDATE parts SET price_cents=?,note=?,revision=revision+1 WHERE part_id=?'
    parameters = [proposed['price_cents'], proposed['note'], proposed['part_id']]
    if guarded:
        sql += ' AND revision=?'
        parameters.append(snapshot['revision'])
    with db:
        changed = db.execute(sql, parameters).rowcount
    return 'saved' if changed == 1 else 'conflict'


def scenario(path, first_payload, second_payload, *, guarded):
    with closing(sqlite3.connect(path)) as first, closing(sqlite3.connect(path)) as second:
        first.execute('CREATE TABLE parts(part_id TEXT PRIMARY KEY,price_cents INTEGER,'
                      'note TEXT,revision INTEGER NOT NULL)')
        first.execute('INSERT INTO parts VALUES(?,?,?,?)', ('0012', 30, 'Keep dry', 1))
        first.commit()
        first_read, second_read = read(first), read(second)
        assert first_read == second_read and first_read['revision'] == 1
        assert save(first, first_read, first_payload, guarded=guarded) == 'saved'
        after_first = read(second)
        result = save(second, second_read, second_payload, guarded=guarded)
        if not guarded:
            assert result == 'saved'
            lost = read(first)
            assert lost['revision'] == 3
            if second_payload == NOTE:
                assert lost['price_cents'] == 30, 'expected the unsafe stale-price overwrite'
            else:
                assert lost['note'] == 'Keep dry', 'expected the unsafe stale-note overwrite'
            return {'unsafe_final': lost}
        assert result == 'conflict', 'stale update must be rejected'
        assert read(first) == after_first, 'conflict must preserve the first committed edit'
        # A repeated stale request still cannot silently overwrite the record.
        assert save(second, second_read, second_payload) == 'conflict'
        assert read(first) == after_first
        # Explicit fixture decision: these two independent edits may be combined.
        # A real UI must obtain/review that decision, not blindly retry every edit.
        fresh = read(second)
        assert save(second, fresh, second_payload) == 'saved'
        expected = {'part_id': '0012', 'price_cents': 45,
                    'note': 'Inspect seal', 'revision': 3}
        assert read(first) == expected
        return {'stale_result': result, 'reviewed_combination': expected}


def run():
    with tempfile.TemporaryDirectory(prefix='record-revisions-') as directory:
        root = Path(directory)
        results = []
        for label, first, second in [('price_first', PRICE, NOTE), ('note_first', NOTE, PRICE)]:
            for guarded in (False, True):
                path = root / f'{label}-{guarded}.sqlite'
                results.append({'order': label, 'guarded': guarded,
                                **scenario(path, first, second, guarded=guarded)})
    assert not root.exists()
    print(json.dumps(results))


if __name__ == '__main__':
    run()
