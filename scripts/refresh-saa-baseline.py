"""Fetch an ignored SAA-C03 review candidate; never promote coverage or overwrite the accepted baseline."""
import csv,hashlib,json,urllib.request,importlib.util
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]; out=root/'artifacts/saa-c03-refresh'; out.mkdir(parents=True, exist_ok=True)
spec=importlib.util.spec_from_file_location('inv',root/'scripts/inventory-knowledge.py'); inv=importlib.util.module_from_spec(spec);spec.loader.exec_module(inv)
base='https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/'
names=['solutions-architect-associate-03']+[f'solutions-architect-associate-03-domain{i}' for i in range(1,5)]+['saa-03-revisions','saa-03-in-scope-services','saa-03-out-of-scope-services','saa-technologies-concepts']
def get(name):
 url=base+name+'.md'
 with urllib.request.urlopen(url,timeout=40) as r: data=r.read()
 (out/(name+'.md')).write_bytes(data)
 return name,{'url':url,'sha256':hashlib.sha256(data).hexdigest(),'text':data.decode()}
with ThreadPoolExecutor(max_workers=4) as pool: docs=dict(pool.map(get,names))
evidence={}; old={}
for typ,key in [('skill','skill_id'),('knowledge','knowledge_id')]:
 for row in csv.DictReader(open(root/f'curriculum/{typ}-evidence.csv')):
  if row[key].startswith('SAA-C03:'): evidence[row[key]]=row
for row in csv.DictReader(open(root/'curriculum/knowledge-inventory.csv')): old[row['id']]=row
records=[]; tasks=[]
for i in range(1,5):
 doc=docs[f'solutions-architect-associate-03-domain{i}']
 for task,groups in inv.parse_tasks(doc['text']).items():
  tasks.append(task)
  for typ,group in [('knowledge','knowledge'),('skill','skills')]:
   for n,bullet in enumerate(groups[group],1):
    key=f'SAA-C03:{task}:{typ}-{n:02}'; e=evidence.get(key,{})
    sha=hashlib.sha256(bullet.encode()).hexdigest()
    records.append({'id':key,'source_url':doc['url'].replace('.md','.html')+f'#solutions-architect-associate-03-domain{i}-task{task.split(".")[1]}','source_bullet_sha256':sha,'paraphrase':e.get('objective_paraphrase'),'teaching_path':e.get('teaching_path'),'section_title':e.get('section_title'),'assessment_path':e.get('assessment_path'),'existing_coverage':e.get('coverage'),'remaining_work':e.get('remaining_work'),'source_knowledge_unchanged':sha==old.get(key,{}).get('source_bullet_sha256') if typ=='knowledge' else None})
report={'checked_utc':datetime.now(timezone.utc).isoformat(),'exam':'SAA-C03','sources':[{k:v for k,v in x.items() if k!='text'} for x in docs.values()],'tasks':tasks,'objective_count':len(records),'objectives':records,'limits':'Source refresh and existing evidence traceability only; no objective completion, learner, exam-pass or cloud-behavior evidence.'}
(out/'source-baseline.json').write_text(json.dumps(report,indent=2)+'\n')
print('Tasks',len(tasks),'objectives',len(records),'missing',sum(not x['paraphrase'] for x in records),'knowledge changed',sum(x['source_knowledge_unchanged'] is False for x in records))
print('Review candidate:', out/'source-baseline.json')
