"""Check fictional capstone consistency; does not score learner reasoning."""
import json
from pathlib import Path
p=Path(__file__).with_name('incident.json');e=json.loads(p.read_text())
assert len({j['id'] for j in e['jobs']})==len(e['jobs'])==6
summary={}
for snapshot,field in [('incident','completed_at_incident'),('followup','completed_at_followup')]:
    now=e[snapshot+'_snapshot_at'];due=good=completed=0
    for job in e['jobs']:
        assert 0<=job['accepted']<=now
        done=job[field]
        assert done is None or job['accepted']<=done<=now
        completed+=done is not None
        if job['accepted']+e['completion_deadline_seconds']<=now:
            due+=1;good+=done is not None and done-job['accepted']<=e['completion_deadline_seconds']
    summary[snapshot]={'accepted':6,'completed':completed,'unfinished':6-completed,'mature_cohort':due,'on_time':good,'late_or_missing':due-good}
assert summary['incident']=={'accepted':6,'completed':3,'unfinished':3,'mature_cohort':5,'on_time':2,'late_or_missing':3}
assert summary['followup']=={'accepted':6,'completed':6,'unfinished':0,'mature_cohort':6,'on_time':2,'late_or_missing':4}
assert sorted(e['followup_business_receipts'])==[f'assignment-r{i}' for i in range(1,7)]
ids={j['id'] for j in e['jobs']}
assert all(o['job'] in ids for o in e['worker_observations'])
print(json.dumps({'fictional_fixture_consistent':True,'computed_outcomes':summary,'learner_assessment':'not performed'},indent=2))
