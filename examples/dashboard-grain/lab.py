"""Real SQLite joins and reporting denominators over fictional orders; no AWS calls."""
from contextlib import closing
from fractions import Fraction
import json
import sqlite3

# One row is one order within a shop. Canceled orders are excluded by this fixture's policy.


def rows(db, shop):
    # Aggregate the many-side BEFORE joining, retaining one row per business identity.
    return db.execute('''
      WITH tag_counts AS (
        SELECT shop,order_id,COUNT(*) AS tags FROM tags GROUP BY shop,order_id
      )
      SELECT o.shop,o.id,o.cents,o.due,o.delivered,COALESCE(t.tags,0)
      FROM orders o LEFT JOIN tag_counts t ON t.shop=o.shop AND t.order_id=o.id
      WHERE o.shop=? AND o.canceled=0 ORDER BY o.id
    ''', (shop,)).fetchall()


def report(db, shop):
    records = rows(db, shop)
    keys = [(r[0], r[1]) for r in records]
    assert len(keys) == len(set(keys)), 'Repeated business identity in report input'
    known = [r for r in records if r[4] is not None]
    on_time = sum(r[4] <= r[3] for r in known)
    def ratio(numerator, denominator):
        return str(Fraction(numerator, denominator)) if denominator else None
    return {'keys': keys, 'cents': sum(r[2] for r in records),
            'orders': len(records), 'known': len(known), 'unknown': len(records)-len(known),
            'confirmed_on_time': on_time,
            'on_time_among_known': ratio(on_time, len(known)),
            'confirmed_on_time_among_all': ratio(on_time, len(records)),
            'outcome_coverage': ratio(len(known), len(records))}


def main():
    with closing(sqlite3.connect(':memory:')) as db:
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
        # Negative controls execute successfully but violate the intended report meaning.
        left = db.execute('''SELECT o.shop,o.id,o.cents FROM orders o LEFT JOIN tags t
          ON t.shop=o.shop AND t.order_id=o.id WHERE o.shop='A' AND o.canceled=0''').fetchall()
        inner = db.execute('''SELECT o.shop,o.id,o.cents FROM orders o JOIN tags t
          ON t.shop=o.shop AND t.order_id=o.id WHERE o.shop='A' AND o.canceled=0''').fetchall()
        assert sum(r[2] for r in left) == 4000 and len(left) == 4
        assert sum(r[2] for r in inner) == 3000  # Looks correct; duplicate and omission cancel!
        expected_keys = {('A','1'),('A','2'),('A','3')}
        assert {(r[0],r[1]) for r in inner} != expected_keys
        distinct_amount = db.execute('''SELECT SUM(DISTINCT o.cents) FROM orders o LEFT JOIN tags t
          ON t.shop=o.shop AND t.order_id=o.id WHERE o.shop='A' AND o.canceled=0''').fetchone()[0]
        assert distinct_amount == 1000  # Discards legitimate equal sales.
        before = report(db,'A')
        assert before == {'keys':[('A','1'),('A','2'),('A','3')], 'cents':3000,
            'orders':3,'known':2,'unknown':1,'confirmed_on_time':1,
            'on_time_among_known':'1/2','confirmed_on_time_among_all':'1/3','outcome_coverage':'2/3'}
        assert [r[-1] for r in rows(db,'A')] == [2,1,0]
        assert report(db,'B')['keys'] == [('B','1')] and report(db,'B')['cents']==2000
        empty = report(db,'missing')
        assert empty['orders']==0 and empty['cents']==0
        assert all(empty[k] is None for k in ['on_time_among_known','confirmed_on_time_among_all','outcome_coverage'])
        # Late evidence changes the known outcome, not the order count or sales amount.
        db.execute("UPDATE orders SET delivered=95 WHERE shop='A' AND id='3'")
        after=report(db,'A')
        assert after['cents']==3000 and after['orders']==3 and after['unknown']==0
        assert after['on_time_among_known']=='2/3' and after['outcome_coverage']=='1'
        print(json.dumps({'wrong_left_join_cents':sum(r[2] for r in left),'deceptive_inner_join_cents':sum(r[2] for r in inner),
            'wrong_distinct_amount_cents':distinct_amount,'before':before,'after':after,
            'scope':'Local sequential SQL fixture; shop parameter is not authenticated identity'},indent=2))


if __name__=='__main__':
    main()
