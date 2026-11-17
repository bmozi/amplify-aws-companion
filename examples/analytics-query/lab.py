"""Real local Parquet queries: preserve the answer while reducing file scans."""
from datetime import datetime
import json
from pathlib import Path
import tempfile
import duckdb

START, END = '2026-01-01 00:00:00', '2026-01-02 00:00:00'


def scans(node):
    found = []
    if node.get('extra_info', {}).get('Function') == 'READ_PARQUET':
        found.append(node)
    for child in node.get('children', []):
        found.extend(scans(child))
    return found


def measured(connection, query, parameters):
    result = connection.execute(query, parameters).fetchone()
    # ANALYZE executes again against these unchanged local files.
    profile = json.loads(connection.execute('EXPLAIN (ANALYZE, FORMAT JSON) ' + query,
                                            parameters).fetchone()[1])
    operators = scans(profile)
    assert len(operators) == 1, 'Review profile parsing if the engine/plan changes'
    details = operators[0]['extra_info']
    return {'events': result[0], 'cents': result[1],
            'files_read': int(details['Total Files Read']),
            'file_filter': details.get('File Filters', 'none'),
            'scanning_files': details.get('Scanning Files', 'not reported')}


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    assert duckdb.__version__ == '1.4.3', 'Use the pinned requirements or revalidate the profiles'
    rows = []
    for day in range(1, 4):
        date = f'2026-01-0{day}'
        rows.extend((f'{day}-{i}', datetime.fromisoformat(date+'T12:00:00'),
                     100, date, date) for i in range(1000))
    rows.append(('late', datetime(2026,1,1,23,59,0), 2500, '2026-01-02', '2026-01-01'))
    expected = [r for r in rows if datetime.fromisoformat(START) <= r[1] < datetime.fromisoformat(END)]
    expected_result = len(expected), sum(r[2] for r in expected)
    assert expected_result == (1001, 102500)
    with tempfile.TemporaryDirectory(prefix='amplify-analytics-') as temporary:
        root = Path(temporary)
        with duckdb.connect(config={'threads':1, 'memory_limit':'64MB',
                                    'autoinstall_known_extensions':False,
                                    'autoload_known_extensions':False}) as connection:
            connection.execute('CREATE TABLE events (id VARCHAR, occurred TIMESTAMP, cents BIGINT, '
                               'arrival_day VARCHAR, event_day VARCHAR)')
            connection.executemany('INSERT INTO events VALUES (?,?,?,?,?)', rows)
            layouts = {}
            for key in ['arrival_day','event_day']:
                destination = root/key
                connection.execute(f'COPY events TO ? (FORMAT PARQUET, PARTITION_BY ({key}))',
                                   [str(destination)])
                assert len(list(destination.rglob('*.parquet'))) == 3
                layouts[key] = str(destination/'*'/'*.parquet')
            select = ('SELECT count(*), coalesce(sum(cents),0) '
                      'FROM read_parquet(?, hive_partitioning=true) '
                      'WHERE occurred >= ?::TIMESTAMP AND occurred < ?::TIMESTAMP')
            baseline = measured(connection, select, [layouts['arrival_day'],START,END])
            incorrect = measured(connection, select + ' AND arrival_day = ?::DATE',
                                 [layouts['arrival_day'],START,END,'2026-01-01'])
            corrected = measured(connection, select + ' AND event_day = ?::DATE',
                                 [layouts['event_day'],START,END,'2026-01-01'])
            assert (baseline['events'],baseline['cents']) == expected_result
            assert (incorrect['events'],incorrect['cents']) == (1000,100000)
            assert (corrected['events'],corrected['cents']) == expected_result
            assert baseline['files_read'] == 3
            assert incorrect['files_read'] == corrected['files_read'] == 1
            # Independent row-membership check guards against equal totals hiding wrong IDs.
            actual = connection.execute('SELECT id FROM read_parquet(?, hive_partitioning=true) '
                                        'WHERE occurred >= ?::TIMESTAMP AND occurred < ?::TIMESTAMP '
                                        'AND event_day = ?::DATE',
                                        [layouts['event_day'],START,END,'2026-01-01']).fetchall()
            assert {r[0] for r in actual} == {r[0] for r in expected}
            print(json.dumps({'engine':duckdb.__version__, 'source_rows':len(rows),
                              'baseline':baseline,'incorrect_arrival_filter':incorrect,
                              'correct_event_partition':corrected,
                              'scope':'local engine file counts; not disk bytes, Athena billing or source completeness'},indent=2))
    assert not root.exists()
    print('Removed temporary Parquet datasets; no AWS calls.')


if __name__ == '__main__':
    main()
