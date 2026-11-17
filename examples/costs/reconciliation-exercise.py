"""Fictional billing snapshots, not an AWS billing parser or account evidence."""
from decimal import Decimal

# Snapshots replace the earlier view of these same rows; they are not increments.
SNAPSHOTS = [
    {'observed':'day 1 13:00 UTC','run_usage':'0.80','retained_usage':'0.00','other_usage':'0.40','credits':'-0.60'},
    {'observed':'day 2 13:00 UTC','run_usage':'1.20','retained_usage':'0.10','other_usage':'0.70','credits':'-1.00'},
    {'observed':'day 3 13:00 UTC','run_usage':'1.20','retained_usage':'0.16','other_usage':'0.70','credits':'-1.00'},
]


def amounts(snapshot):
    values = {k:Decimal(snapshot[k]) for k in ('run_usage','retained_usage','other_usage','credits')}
    if any(not v.is_finite() for v in values.values()):
        raise ValueError('Nonfinite amount')
    if any(values[k] < 0 for k in ('run_usage','retained_usage','other_usage')) or values['credits'] > 0:
        raise ValueError('Wrong sign for this bounded fixture')
    usage = values['run_usage'] + values['retained_usage'] + values['other_usage']
    return values['run_usage'] + values['retained_usage'], usage, usage + values['credits']


def main():
    expected = [('0.80','1.20','0.60'),('1.30','2.00','1.00'),('1.36','2.06','1.06')]
    for snapshot, totals in zip(SNAPSHOTS, expected):
        actual = amounts(snapshot)
        assert actual == tuple(map(Decimal,totals))
        print(snapshot['observed'], 'lab usage / account usage / after fixture credit:', *actual)
    latest_lab = amounts(SNAPSHOTS[-1])[0]
    estimate = Decimal('1.50')
    assert estimate-latest_lab == Decimal('0.14')
    wrong_sum = sum((amounts(s)[0] for s in SNAPSHOTS),Decimal(0))
    assert wrong_sum == Decimal('3.46') and wrong_sum != latest_lab
    print('Latest lab usage:',latest_lab,'; below fictional estimate by:',estimate-latest_lab)
    print('Negative control: summing overlapping snapshots incorrectly gives:',wrong_sum)
    # Account adjustments have no supported allocation to this lab in the fixture.
    assert amounts(SNAPSHOTS[-1])[2] != latest_lab
    for field,value in [('run_usage','NaN'),('other_usage','-1'),('credits','1')]:
        bad = dict(SNAPSHOTS[-1]); bad[field] = value
        try: amounts(bad)
        except ValueError: pass
        else: raise AssertionError('Invalid fixture amount accepted')
    print('PASS: arithmetic only; timestamps, attribution and removal need separate evidence.')


if __name__ == '__main__':
    main()
