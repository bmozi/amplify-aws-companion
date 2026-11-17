"""Read mixed Parquet contracts without silently changing units or inventing history."""
import hashlib
import json
from pathlib import Path
import re
import tempfile

import duckdb


def normalize(rows):
    accepted, seen = [], set()
    for version, event_id, cents, amount, currency, channel in rows:
        if type(version) is not int or version not in (1, 2):
            raise ValueError('Unknown contract version')
        if not isinstance(event_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', event_id) or event_id in seen:
            raise ValueError('Invalid or duplicate identity across the source set')
        if currency != 'USD':
            raise ValueError('This canonical total is USD only')
        if version == 1:
            if type(cents) is not int or amount is not None or channel is not None:
                raise ValueError('Version 1 requires integer cents and has no amount/channel')
        else:
            if cents is not None or not isinstance(amount, str) or not re.fullmatch(r'-?(0|[1-9][0-9]*)\.[0-9]{2}', amount):
                raise ValueError('Version 2 requires exact decimal USD text, not cents')
            if channel is not None and channel not in ('web', 'counter'):
                raise ValueError('Unrecognized channel')
            whole, fraction = amount.lstrip('-').split('.')
            cents = (int(whole)*100 + int(fraction)) * (-1 if amount.startswith('-') else 1)
        if not -(2**63) <= cents < 2**63:
            raise ValueError('Cents outside signed 64-bit range')
        seen.add(event_id)
        accepted.append((event_id, cents, currency, channel, version))
    if not accepted:
        raise ValueError('Empty source set requires a separate contract')
    return sorted(accepted)


def migrate(connection, sources, destination):
    if destination.exists():
        raise FileExistsError('Existing canonical output must not be overwritten')
    rows = connection.execute('SELECT version,event_id,cents,amount,currency,channel '
                              'FROM read_parquet(?, union_by_name=true)', [list(map(str, sources))]).fetchall()
    accepted = normalize(rows)  # Whole bounded source set validated before any output write.
    connection.execute('CREATE OR REPLACE TABLE canonical '
                       '(event_id VARCHAR, cents BIGINT, currency VARCHAR, channel VARCHAR, source_version INTEGER)')
    connection.executemany('INSERT INTO canonical VALUES (?,?,?,?,?)', accepted)
    connection.execute('COPY canonical TO ? (FORMAT PARQUET)', [str(destination)])
    return connection.execute('SELECT * FROM read_parquet(?) ORDER BY event_id', [str(destination)]).fetchall()


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    assert duckdb.__version__ == '1.4.3'
    with tempfile.TemporaryDirectory(prefix='amplify-evolution-') as temporary:
        root = Path(temporary)
        with duckdb.connect(config={'threads':1, 'memory_limit':'64MB',
                                    'autoinstall_known_extensions':False,
                                    'autoload_known_extensions':False}) as connection:
            connection.execute('CREATE TABLE old (version INTEGER,event_id VARCHAR,cents BIGINT,currency VARCHAR)')
            connection.execute("INSERT INTO old VALUES (1,'001',1230,'USD')")
            connection.execute('CREATE TABLE new (version INTEGER,event_id VARCHAR,amount VARCHAR,currency VARCHAR,channel VARCHAR)')
            connection.execute("INSERT INTO new VALUES (2,'refund','-2.30','USD','web'),(2,'small','0.10','USD',NULL)")
            sources = [root/'old.parquet', root/'new.parquet']
            for table, path in zip(('old','new'),sources):
                connection.execute(f'COPY {table} TO ? (FORMAT PARQUET)', [str(path)])
            original = [hashlib.sha256(p.read_bytes()).hexdigest() for p in sources]
            naive = connection.execute('SELECT sum(cents) FROM read_parquet(?, union_by_name=true)',
                                       [list(map(str,sources))]).fetchone()[0]
            assert naive == 1230  # A successful query silently leaves out version 2 money.
            destination = root/'canonical.parquet'
            expected = [('001',1230,'USD',None,1), ('refund',-230,'USD','web',2), ('small',10,'USD',None,2)]
            actual = migrate(connection,sources,destination)
            assert actual == expected
            assert sum(r[1] for r in actual) == 1010 and naive != 1010
            saved = destination.read_bytes()
            try:migrate(connection,sources,destination)
            except FileExistsError:pass
            else:raise AssertionError('Output replaced')
            assert destination.read_bytes() == saved
            # Every malformed row is written to a real Parquet source and mixed with v1.
            invalid = [(3,'future','1.00','USD',None), (2,'precision','0.001','USD',None),
                       (2,'eur','1.00','EUR',None), (2,'missing',None,'USD',None),
                       (2,'001','12.30','USD',None), (2,'001','99.00','USD',None),
                       (2,'overflow','92233720368547758.08','USD',None),
                       (2,'badchannel','1.00','USD','guessed')]
            for index,row in enumerate(invalid):
                connection.execute('DELETE FROM new')
                connection.execute('INSERT INTO new VALUES (?,?,?,?,?)',row)
                bad_source, output = root/f'bad-{index}.parquet', root/f'rejected-{index}.parquet'
                connection.execute('COPY new TO ? (FORMAT PARQUET)',[str(bad_source)])
                try:migrate(connection,[sources[0],bad_source],output)
                except ValueError:pass
                else:raise AssertionError('Unsupported mixed batch accepted')
                assert not output.exists()
            assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in sources] == original
            print(json.dumps({'engine':duckdb.__version__, 'naive_cents':int(naive),
                              'canonical_rows':actual, 'canonical_cents':1010,
                              'rejected_batches':len(invalid), 'source_bytes_unchanged':True,
                              'scope':'Local trusted bounded mixed-version Parquet; no concurrent publication or AWS migration'},indent=2))
    assert not root.exists()
    print('Removed temporary inputs and outputs; no AWS calls.')


if __name__ == '__main__':
    main()
