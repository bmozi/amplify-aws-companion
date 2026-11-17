"""Local event-time accounting; trusted synthetic producer, no AWS calls."""
from contextlib import closing
import json
import sqlite3


def database():
    db = sqlite3.connect(':memory:')
    db.executescript('''
        CREATE TABLE events (producer TEXT NOT NULL, id TEXT NOT NULL, body TEXT NOT NULL,
                             occurred INTEGER NOT NULL, cents INTEGER NOT NULL,
                             PRIMARY KEY (producer,id));
        CREATE TABLE deliveries (producer TEXT, arrival INTEGER, outcome TEXT, raw TEXT);
    ''')
    return db


def ingest(db, event, arrival, *, producer="fixture"):
    # This argument is trusted fixture context, not authentication.
    if not isinstance(producer, str) or not producer:
        raise ValueError("A trusted nonempty producer scope is required")
    raw = json.dumps(event, sort_keys=True, separators=(',', ':'))
    valid = (isinstance(event, dict) and set(event) == {'id','version','occurred','cents'}
             and isinstance(event['id'], str) and bool(event['id'])
             and type(event['version']) is int and event['version'] == 1
             and type(event['occurred']) is int and 0 <= event['occurred'] <= arrival
             and type(event['cents']) is int and 0 <= event['cents'] <= 1_000_000)
    with db:
        if not valid:
            outcome = 'quarantined'
        else:
            prior = db.execute('SELECT body FROM events WHERE producer=? AND id=?', (producer,event['id'])).fetchone()
            if prior:
                outcome = 'duplicate' if prior[0] == raw else 'conflict'
            else:
                db.execute('INSERT INTO events VALUES (?,?,?,?,?)',
                           (producer, event['id'], raw, event['occurred'], event['cents']))
                outcome = 'accepted'
        db.execute('INSERT INTO deliveries VALUES (?,?,?,?)', (producer, arrival, outcome, raw))
    return outcome


def report(db, start, end):
    return db.execute('SELECT count(*), coalesce(sum(cents),0) FROM events '
                      'WHERE occurred >= ? AND occurred < ?', (start,end)).fetchone()


def event(identifier, occurred, cents):
    return dict(id=identifier, version=1, occurred=occurred, cents=cents)


def main():
    with closing(database()) as db:
        a, b, c = event('a',10,1000), event('b',50,2000), event('c',60,500)
        assert ingest(db,a,11) == 'accepted'
        assert ingest(db,a,12) == 'duplicate'
        assert ingest(db,c,61) == 'accepted'
        assert report(db,0,60) == (1,1000)
        # Independent producer manifest says a and b belong to the first minute.
        expected_ids = {'a','b'}
        actual_ids = {r[0] for r in db.execute('SELECT id FROM events WHERE occurred < 60')}
        assert expected_ids - actual_ids == {'b'}
        assert ingest(db,b,130) == 'accepted'  # Late arrival, earlier event-time window.
        assert report(db,0,60) == (2,3000)
        assert report(db,60,120) == (1,500)  # Boundary event goes into next window.
        assert ingest(db,event('a',10,9999),131) == 'conflict'
        assert ingest(db,dict(a,version=2,id='v2'),132) == 'quarantined'
        assert ingest(db,dict(a,cents=True,id='boolean'),133) == 'quarantined'
        assert ingest(db,event('future',999,100),134) == 'quarantined'
        assert report(db,0,60) == (2,3000)
        # Restart/replay model: same persisted destination, reordered redelivery.
        for item in (c,b,a):
            assert ingest(db,item,140) == 'duplicate'
        assert report(db,0,120) == (3,3500)
        actual_ids = {r[0] for r in db.execute('SELECT id FROM events WHERE occurred < 60')}
        assert actual_ids == expected_ids
        outcomes = dict(db.execute('SELECT outcome,count(*) FROM deliveries GROUP BY outcome'))
        assert outcomes == {'accepted':3,'duplicate':4,'conflict':1,'quarantined':3}
        print(json.dumps({'first_minute_before_late_event_cents':1000,
                          'first_minute_after_late_event_cents':3000,
                          'second_minute_cents':500,'delivery_outcomes':outcomes,
                          'scope':'local SQLite; no cloud, concurrent consumers or source completeness proof'},indent=2))


if __name__ == '__main__':
    main()
