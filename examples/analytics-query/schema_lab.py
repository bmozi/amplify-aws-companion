"""Convert a small contracted CSV to typed Parquet and verify every value locally."""
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import tempfile
import duckdb

HEADER = ['event_id', 'occurred_utc', 'amount', 'currency']


def validated_rows(source):
    rows, seen = [], set()
    with source.open(newline='', encoding='utf-8') as stream:
        reader = csv.reader(stream, strict=True)
        if next(reader, None) != HEADER:
            raise ValueError('Unexpected CSV header or version')
        for fields in reader:
            if len(fields) != 4:
                raise ValueError('Every row needs exactly four fields')
            event_id, occurred, amount, currency = fields
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', event_id) or event_id in seen:
                raise ValueError('Missing invalid or duplicate event identity')
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', occurred, re.ASCII):
                raise ValueError('Timestamp must use the contracted UTC second precision')
            timestamp = datetime.strptime(occurred, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
            if not re.fullmatch(r'-?(0|[1-9][0-9]*)\.[0-9]{2}', amount) or currency != 'USD':
                raise ValueError('This contract requires exact two-decimal USD amounts')
            whole, fraction = amount.lstrip('-').split('.')
            cents = (int(whole)*100 + int(fraction)) * (-1 if amount.startswith('-') else 1)
            if not -(2**63) <= cents < 2**63:
                raise ValueError('Amount exceeds signed 64-bit cents')
            seen.add(event_id)
            rows.append((event_id, timestamp, cents, currency))
    if not rows:
        raise ValueError('An empty batch needs a separate explicit contract')
    return rows


def convert(source, destination):
    if destination.exists():
        raise FileExistsError('Do not overwrite an existing output')
    rows = validated_rows(source)  # Validate the entire small batch before writing.
    with duckdb.connect(config={'threads': 1, 'memory_limit': '64MB',
                                'autoinstall_known_extensions': False,
                                'autoload_known_extensions': False}) as connection:
        connection.execute("SET TimeZone='UTC'")
        connection.execute('CREATE TABLE converted (event_id VARCHAR NOT NULL, '
                           'occurred_utc TIMESTAMPTZ NOT NULL, cents BIGINT NOT NULL, currency VARCHAR NOT NULL)')
        connection.executemany('INSERT INTO converted VALUES (?,?,?,?)', rows)
        connection.execute('COPY converted TO ? (FORMAT PARQUET)', [str(destination)])
        actual = connection.execute("SELECT event_id, strftime(occurred_utc, '%Y-%m-%dT%H:%M:%SZ'), "
                                    'cents, currency FROM read_parquet(?) ORDER BY event_id', [str(destination)]).fetchall()
        schema = connection.execute('DESCRIBE SELECT * FROM read_parquet(?)', [str(destination)]).fetchall()
    return actual, [(column[0], column[1]) for column in schema]


def write_csv(path, rows, header=HEADER):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    assert duckdb.__version__ == '1.4.3'
    valid = [['001', '2026-01-01T00:00:00Z', '12.30', 'USD'],
             ['refund', '2026-01-02T00:00:00Z', '-2.30', 'USD'],
             ['NULL', '2026-01-01T23:59:59Z', '0.10', 'USD']]
    expected = [('001', '2026-01-01T00:00:00Z', 1230, 'USD'),
                ('NULL', '2026-01-01T23:59:59Z', 10, 'USD'),
                ('refund', '2026-01-02T00:00:00Z', -230, 'USD')]
    with tempfile.TemporaryDirectory(prefix='amplify-schema-') as temporary:
        root = Path(temporary)
        source, output = root/'source.csv', root/'converted.parquet'
        write_csv(source, valid)
        actual, schema = convert(source, output)
        assert actual == expected, 'Conversion changed contracted values'
        assert schema == [('event_id','VARCHAR'), ('occurred_utc','TIMESTAMP WITH TIME ZONE'),
                          ('cents','BIGINT'), ('currency','VARCHAR')]
        assert sum(row[2] for row in actual) == 1010
        original = output.read_bytes()
        try:
            convert(source, output)
        except FileExistsError:
            pass
        else:
            raise AssertionError('Existing result was overwritten')
        assert output.read_bytes() == original
        invalid = []
        for field, value in [(0,''), (1,'2026-02-30T00:00:00Z'), (1,'2026-01-01T00:00:00'),
                             (1,'2026-01-01T01:00:00+01:00'), (2,''), (2,'0.001'),
                             (2,'1e2'), (2,'NaN'), (2,'92233720368547758.08'), (3,'EUR')]:
            changed = valid[0].copy();changed[field]=value
            invalid.append([valid[1], changed])
        invalid.extend([[valid[0], valid[0]], [valid[0][:-1]], [valid[0]+['extra']], []])
        for index, rows in enumerate(invalid):
            candidate = root/f'rejected-{index}.parquet'
            write_csv(source, rows)
            try:
                convert(source, candidate)
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid batch was converted')
            assert not candidate.exists(), 'Rejected batch produced an output'
        write_csv(source, valid, ['id', *HEADER[1:]])
        try:
            convert(source, root/'wrong-header.parquet')
        except ValueError:
            pass
        else:
            raise AssertionError('Unknown header accepted')
        assert not (root/'wrong-header.parquet').exists()
        print(json.dumps({'engine':duckdb.__version__, 'rows':len(actual), 'cents':1010,
                          'preserved_ids':[r[0] for r in actual], 'schema':schema,
                          'rejected_batches':len(invalid)+1,
                          'scope':'Local contracted CSV to Parquet; no cloud schema evolution or atomic dataset publication'},indent=2))
    assert not root.exists()
    print('Removed temporary CSV and Parquet files; no AWS calls.')


if __name__ == '__main__':
    main()
