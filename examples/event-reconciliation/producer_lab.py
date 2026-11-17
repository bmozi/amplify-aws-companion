"""Producer-scoped event identities with trusted fixture actors; no authentication."""
from contextlib import closing
import json

from lab import database, event, ingest, report


def run():
    with closing(database()) as db:
        a = event('42', 10, 1000)
        b = event('42', 20, 2000)
        expected = {('shop-a', '42'), ('shop-b', '42')}
        assert ingest(db, a, 11, producer='shop-a') == 'accepted'
        present = set(db.execute('SELECT producer,id FROM events'))
        assert expected - present == {('shop-b', '42')}
        # Comparing unscoped IDs would wrongly report no missing source event.
        assert {identifier for _, identifier in expected} == {identifier for _, identifier in present}
        assert ingest(db, b, 21, producer='shop-b') == 'accepted'
        assert set(db.execute('SELECT producer,id FROM events')) == expected
        assert report(db, 0, 60) == (2, 3000)
        for producer, payload in [('shop-b', b), ('shop-a', a)]:
            assert ingest(db, payload, 30, producer=producer) == 'duplicate'
        assert ingest(db, event('42', 10, 9999), 31, producer='shop-a') == 'conflict'
        assert ingest(db, dict(a, producer='shop-b'), 32, producer='shop-a') == 'quarantined'
        # Rejected producer context never reaches the accepted-event ledger.
        for invalid in ['', None, True]:
            try:
                ingest(db, a, 33, producer=invalid)
            except ValueError:
                pass
            else:
                raise AssertionError('invalid producer context accepted')
        assert list(db.execute('SELECT producer,id,cents FROM events ORDER BY producer')) == [
            ('shop-a', '42', 1000), ('shop-b', '42', 2000)]
        assert report(db, 0, 60) == (2, 3000)
        outcomes = dict(db.execute('SELECT outcome,count(*) FROM deliveries GROUP BY outcome'))
        assert outcomes == {'accepted': 2, 'duplicate': 2, 'conflict': 1, 'quarantined': 1}
    # Deliberately show the trust limit: this function cannot verify a real actor.
    with closing(database()) as untrusted_demo:
        assert ingest(untrusted_demo, a, 11, producer='claimed-shop') == 'accepted'
        trusted_context_limit = 'Caller-supplied producer labels are accepted; authentication is outside this fixture'
    result = {'accepted_events': 2, 'total_cents': 3000,
              'unscoped_manifest_false_complete': True,
              'scoped_manifest_detected_missing_shop_b': True,
              'delivery_outcomes': outcomes,
              'identity_limit': trusted_context_limit,
              'scope': 'Sequential in-memory SQLite; no IAM, authenticated sender, stream or concurrency test'}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    run()
