"""Local dashboard evidence review over the existing fictional SQLite report.

No AWS connection, authenticated reader, dashboard service, or staffing action.
"""
from contextlib import closing
from fractions import Fraction
import json
import sqlite3

from lab import report


def fixture_database():
    db = sqlite3.connect(':memory:')
    db.executescript('''
      CREATE TABLE orders(shop TEXT,id TEXT,cents INTEGER,due INTEGER,
                          delivered INTEGER,canceled INTEGER,PRIMARY KEY(shop,id));
      CREATE TABLE tags(shop TEXT,order_id TEXT,tag TEXT,PRIMARY KEY(shop,order_id,tag));
    ''')
    db.executemany('INSERT INTO orders VALUES(?,?,?,?,?,?)', [
        ('A','1',1000,100,90,0), ('A','2',1000,100,110,0),
        ('A','3',1000,100,None,0), ('A','4',9000,100,None,1),
        ('B','1',2000,100,80,0)])
    db.executemany('INSERT INTO tags VALUES(?,?,?)', [
        ('A','1','gift'),('A','1','priority'),('A','2','gift'),
        ('A','4','canceled'),('B','1','international')])
    return db


def review_decision(snapshot, *, expected_keys, allowed_shops,
                    displayed_rate, latest_source_change_minute,
                    import_success_minute, opened_minute,
                    maximum_import_age_minutes=60):
    """Return evidence gaps, never an automatic staffing recommendation.

    Minutes and permissions are supplied fixture claims. A real source, reader
    identity, import lineage, and delivery outcome need separate verification.
    """
    for name, value in [('latest_source_change_minute', latest_source_change_minute),
                        ('import_success_minute', import_success_minute),
                        ('opened_minute', opened_minute),
                        ('maximum_import_age_minutes', maximum_import_age_minutes)]:
        if type(value) is not int or value < 0:
            raise ValueError(f'{name} must be a nonnegative whole minute')
    if maximum_import_age_minutes == 0 or import_success_minute > opened_minute:
        raise ValueError('Import age policy and observation time must be valid')
    if not isinstance(expected_keys, (list, tuple)) or not isinstance(allowed_shops, (list, tuple, set)):
        raise ValueError('Expected keys and allowed shops must be supplied collections')
    if len(expected_keys) != len(set(map(tuple, expected_keys))):
        raise ValueError('Expected business identities must be unique')
    reasons = []
    actual_keys = [tuple(key) for key in snapshot['keys']]
    if actual_keys != [tuple(key) for key in expected_keys]:
        reasons.append('order_identity_mismatch')
    if not set(shop for shop, _ in actual_keys).issubset(set(allowed_shops)):
        reasons.append('fixture_scope_mismatch')
    if snapshot['orders'] == 0:
        reasons.append('no_qualifying_orders')
        true_rate = None
    else:
        true_rate = Fraction(snapshot['confirmed_on_time'], snapshot['orders'])
        if snapshot['known'] != snapshot['orders']:
            reasons.append('delivery_outcomes_missing')
    if not isinstance(displayed_rate, str):
        raise ValueError('Displayed rate must be an exact rational string')
    try:
        shown = Fraction(displayed_rate)
    except (ValueError, TypeError, ZeroDivisionError) as error:
        raise ValueError('Displayed rate must be an exact rational number') from error
    if true_rate is None or shown != true_rate:
        reasons.append('displayed_denominator_or_value_mismatch')
    if latest_source_change_minute > import_success_minute:
        reasons.append('source_newer_than_import')
    age = opened_minute - import_success_minute
    if age > maximum_import_age_minutes:
        reasons.append('import_too_old_for_decision')
    return {
        'status': 'ready_for_human_review' if not reasons else 'hold_for_investigation',
        'reasons': reasons,
        'confirmed_on_time': snapshot['confirmed_on_time'],
        'known_outcomes': snapshot['known'],
        'eligible_orders': snapshot['orders'],
        'order_level_rate': None if true_rate is None else str(true_rate),
        'import_age_minutes': age,
        'scope_evidence': 'supplied local allowlist only; no authenticated service denial',
        'customer_outcome_evidence': 'supplied SQLite timestamps only',
        'staffing_action_taken': False,
        'aws_called': False,
    }


def run():
    with closing(fixture_database()) as db:
        expected = [('A','1'),('A','2'),('A','3')]
        before = report(db, 'A')
        stale = review_decision(before, expected_keys=expected, allowed_shops=['A'],
                                displayed_rate='1/2', latest_source_change_minute=490,
                                import_success_minute=480, opened_minute=540)
        db.execute("UPDATE orders SET delivered=95 WHERE shop='A' AND id='3'")
        after = report(db, 'A')
        checked = review_decision(after, expected_keys=expected, allowed_shops=['A'],
                                  displayed_rate='2/3', latest_source_change_minute=490,
                                  import_success_minute=500, opened_minute=540)
        assert stale['status'] == 'hold_for_investigation'
        assert checked['status'] == 'ready_for_human_review'
        print(json.dumps({'nine_oclock_green_chart': stale,
                          'after_source_and_import_review': checked}, indent=2))


if __name__ == '__main__':
    run()
