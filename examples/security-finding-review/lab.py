"""Join fictional deployment, scan coverage and findings in SQLite. No AWS APIs."""
import json
import sqlite3


QUERY = '''
SELECT d.account, d.region, d.name, d.artifact, s.checked_at,
       (SELECT count(*) FROM findings f
        WHERE f.account=d.account AND f.region=d.region
          AND f.artifact=d.artifact AND f.source='package-scanner'
          AND f.state='active') AS active_findings
FROM deployments d LEFT JOIN scans s
 ON s.account=d.account AND s.region=d.region AND s.artifact=d.artifact
ORDER BY d.account,d.region,d.name
'''


def report(db, now=100, max_age=20, snapshot_complete=True):
    """Times and complete export are trusted fixture inputs, not inferred from rows."""
    if type(now) is not int or type(max_age) is not int or now < 0 or max_age < 0:
        raise ValueError('Invalid fictional review interval')
    if type(snapshot_complete) is not bool:
        raise ValueError('Export completeness must be explicit')
    rows = []
    for account, region, name, artifact, checked, findings in db.execute(QUERY):
        if checked is None:
            coverage = 'missing'
        elif checked > now:
            coverage = 'future_timestamp'
        elif now - checked > max_age:
            coverage = 'stale'
        else:
            coverage = 'recent'
        # A positive observation survives incomplete coverage; absence needs more evidence.
        if findings:
            conclusion = 'reported_active_findings'
        elif coverage == 'recent' and snapshot_complete:
            conclusion = 'no_active_findings_in_stipulated_snapshot'
        else:
            conclusion = 'unknown'
        rows.append(dict(account=account, region=region, deployment=name, artifact=artifact,
                         coverage=coverage, active_findings=findings, conclusion=conclusion))
    return rows


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    db = sqlite3.connect(':memory:')
    try:
        db.executescript('''
        CREATE TABLE deployments(account TEXT,region TEXT,name TEXT,artifact TEXT,
          PRIMARY KEY(account,region,name));
        CREATE TABLE scans(account TEXT,region TEXT,artifact TEXT,checked_at INTEGER NOT NULL,
          PRIMARY KEY(account,region,artifact));
        CREATE TABLE findings(source TEXT,account TEXT,region TEXT,id TEXT,artifact TEXT,state TEXT,
          PRIMARY KEY(source,account,region,id));
        ''')
        db.executemany('INSERT INTO deployments VALUES (?,?,?,?)', [
            ('shop-a','east','booking','image-B'),
            ('shop-a','west','booking','image-B'),
            ('shop-b','east','booking','image-B'),
        ])
        db.executemany('INSERT INTO scans VALUES (?,?,?,?)', [
            ('shop-a','east','image-A',95),
            ('shop-a','west','image-B',95),
            ('shop-b','east','image-B',50),
        ])
        db.executemany('INSERT INTO findings VALUES (?,?,?,?,?,?)', [
            ('package-scanner','shop-a','east','finding-7','image-A','active'),
            ('package-scanner','shop-a','west','finding-7','image-B','active'),
        ])
        before = report(db)
        assert [r['conclusion'] for r in before] == ['unknown','reported_active_findings','unknown']
        assert [r['coverage'] for r in before] == ['missing','recent','stale']
        assert [r['active_findings'] for r in before] == [0,1,0]
        assert db.execute('SELECT count(*) FROM findings').fetchone()[0] == 2
        # Negative controls show why artifact-only and no-findings-only joins mislead.
        wrong = db.execute('''SELECT count(*) FROM deployments d JOIN findings f
            ON d.artifact=f.artifact WHERE d.account='shop-a' AND d.region='east'
            AND f.state='active' ''').fetchone()[0]
        assert wrong == 1 and before[0]['active_findings'] == 0
        naive_clear = [r['deployment'] for r in before if r['active_findings'] == 0]
        assert len(naive_clear) == 2 and all(r['conclusion'] != 'no_active_findings_in_stipulated_snapshot' for r in before)
        # Supply the missing exact-target scan evidence, with the complete snapshot assumption.
        db.execute('INSERT INTO scans VALUES (?,?,?,?)',('shop-a','east','image-B',100))
        after = report(db)
        assert after[0]['conclusion'] == 'no_active_findings_in_stipulated_snapshot'
        assert after[1:] == before[1:]
        assert report(db, snapshot_complete=False)[0]['conclusion'] == 'unknown'
        assert report(db, snapshot_complete=False)[1]['conclusion'] == 'reported_active_findings'
        assert report(db, now=121)[0]['coverage'] == 'stale'
        assert report(db, now=99)[0]['coverage'] == 'future_timestamp'
        # Old artifact findings stay in the record; they are not reassigned to image B.
        assert db.execute("SELECT count(*) FROM findings WHERE artifact='image-A'").fetchone()[0] == 1
        print(json.dumps({'scope':'fictional SQL snapshot joins; not Inspector or live inventory',
            'before_exact_target_scan':before, 'after_exact_target_scan':after,
            'artifact_only_join_wrongly_attributes_findings':wrong,
            'naive_zero_count_clear_labels':len(naive_clear),
            'incomplete_snapshot_prevents_negative_conclusion':True,
            'same_finding_id_in_two_regions_preserved':True,
            'stale_and_future_scan_times_not_recent':True}, indent=2))
    finally:
        db.close()


if __name__ == '__main__':
    main()
