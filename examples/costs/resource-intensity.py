"""Fictional attempt accounting, not measured AWS energy, costs or emissions."""
from fractions import Fraction
import sqlite3

REQUIRED = {'report-a', 'report-b', 'report-c', 'report-d'}
DEADLINE = 60  # Minutes after this invented observation window begins.


def summarize(rows):
    # Each row is an attempt: output identity, successful, correct, finish minute,
    # worker-seconds consumed. Failed/late work still consumes resource time.
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE attempts (output TEXT, success INT, correct INT, finish INT, seconds INT)')
        db.executemany('INSERT INTO attempts VALUES (?,?,?,?,?)', rows)
        if db.execute('SELECT count(*) FROM attempts WHERE seconds < 0').fetchone()[0]:
            raise ValueError('Negative resource duration')
        seconds = db.execute('SELECT coalesce(sum(seconds),0) FROM attempts').fetchone()[0]
        accepted = {r[0] for r in db.execute(
            'SELECT DISTINCT output FROM attempts WHERE success=1 AND correct=1 AND finish<=?',
            (DEADLINE,))}
        successful_rows = db.execute('SELECT count(*) FROM attempts WHERE success=1').fetchone()[0]
    return {'seconds': seconds, 'accepted': accepted,
            'seconds_per_output': Fraction(seconds, len(accepted)) if accepted else None,
            'successful_rows': successful_rows}


def main():
    baseline = summarize([(name, 1, 1, 40, 7200) for name in sorted(REQUIRED)])
    efficient_rows = [(name, 1, 1, 40, 1800) for name in sorted(REQUIRED)]
    # Two failed attempts are included in the candidate's total resource work.
    efficient_rows += [('report-a', 0, 0, 10, 1800), ('report-c', 0, 0, 20, 1800)]
    efficient = summarize(efficient_rows)
    assert baseline['accepted'] == efficient['accepted'] == REQUIRED
    assert baseline['seconds'] == 28800 and efficient['seconds'] == 10800
    assert baseline['seconds_per_output'] == 7200 and efficient['seconds_per_output'] == 2700
    assert Fraction(baseline['seconds']-efficient['seconds'], baseline['seconds']) == Fraction(5, 8)

    # Three useful identities; a repeated success, wrong result and late result
    # cannot stand in for the missing on-time correct report-d.
    deceptive_rows = [(name, 1, 1, 40, 900) for name in sorted(REQUIRED - {'report-d'})]
    deceptive_rows += [('report-a', 1, 1, 41, 900), ('report-d', 1, 0, 45, 900),
                       ('report-d', 1, 1, 61, 900)]
    deceptive = summarize(deceptive_rows)
    assert deceptive['successful_rows'] == 6 and len(deceptive['accepted']) == 3
    assert deceptive['seconds'] == 5400 and deceptive['seconds_per_output'] == 1800
    assert deceptive['seconds_per_output'] < efficient['seconds_per_output']
    assert deceptive['accepted'] != REQUIRED  # Lower ratio, failed customer promise.
    wrong_ratio = Fraction(deceptive['seconds'], deceptive['successful_rows'])
    assert wrong_ratio == 900 and wrong_ratio != deceptive['seconds_per_output']

    wrong_population = summarize([(name, 1, 1, 40, 900)
                                  for name in ['report-a', 'report-b', 'report-c', 'report-x']])
    assert len(wrong_population['accepted']) == len(REQUIRED)
    assert wrong_population['accepted'] != REQUIRED  # Counts alone conceal substitution.
    no_output = summarize([('report-a', 0, 0, 10, 900)])
    assert no_output['seconds'] == 900 and no_output['seconds_per_output'] is None
    for name, result in [('baseline', baseline), ('efficient', efficient), ('deceptive', deceptive),
                         ('wrong population', wrong_population), ('no accepted output', no_output)]:
        print(name, 'worker-seconds:', result['seconds'], 'accepted:', sorted(result['accepted']),
              'seconds per accepted output:', result['seconds_per_output'],
              'required outputs preserved:', result['accepted'] == REQUIRED)
    print('PASS: fictional resource-time accounting; 62.5% reduction for the valid candidate; no carbon claim.')


if __name__ == '__main__':
    main()
