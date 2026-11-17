"""Generate navigation from the accepted SAA baseline without promoting objective status."""
from pathlib import Path
import csv,json,os,re,subprocess
root=Path(__file__).resolve().parents[1];folder=root/'curriculum/saa-c03'; out=folder/'tasks'
b=json.loads((folder/'source-baseline-2026-10-31.json').read_text())
# Preserve the dated official baseline; route learners through current evidence.
current={}
for kind in ('skill','knowledge'):
 for row in csv.DictReader((root/f'curriculum/{kind}-evidence.csv').open()):
  current[row[kind+'_id']]=row
for objective in b['objectives']:
 row=current[objective['id']]
 for field in ('teaching_path','section_title','assessment_path','remaining_work'):
  objective[field]=row[field]
titles={'1.1':'Access and delegated authority','1.2':'Workload protection','1.3':'Data security and recovery access','2.1':'Decoupling and scaling','2.2':'Availability and recovery','3.1':'Storage interfaces and performance','3.2':'Compute and elasticity','3.3':'Database performance and correctness','3.4':'Network performance','3.5':'Data ingestion and transformation','4.1':'Storage cost','4.2':'Compute cost','4.3':'Database cost','4.4':'Network cost'}
supplemental=json.loads((folder/'supplemental-teaching.json').read_text())
headers={}
def txt(node):
 if isinstance(node,list):return ''.join(txt(x) for x in node)
 if not isinstance(node,dict):return ''
 if node['t']=='Str':return node['c']
 if node['t'] in ('Space','SoftBreak','LineBreak'):return ' '
 return txt(node.get('c',[]))
for rel in sorted({x['teaching_path'].split('#')[0] for x in b['objectives']} | {x['path'] for items in supplemental.values() for x in items}):
 doc=json.loads(subprocess.check_output(['pandoc','-f','gfm','-t','json',str(root/rel)]))
 headers[rel]={txt(x['c'][2]).casefold():x['c'][1][0] for x in doc['blocks'] if x['t']=='Header'}
out.mkdir(parents=True,exist_ok=True)
index=['# SAA-C03 task work cards\n\nUse one card while studying or reviewing a chapter, then return to a new case after time away. Every line is an existing partial teaching/assessment mapping, not an automatic completion. Keep your unaided answer, uncertainty, source and later correction. The checked source baseline has 14 tasks, 82 skills and 107 knowledge items.\n']
missing=[]
for num,task in enumerate(b['tasks'],1):
 rows=[r for r in b['objectives'] if r['id'].split(':')[1]==task]
 title=titles[task]; name=task.replace('.','-')+'.md';index.append(f'- [Task {task}: {title}](tasks/{name})\n')
 content=f'# Task {task}: {title}\n\nRead the mechanism, attempt its linked exercise and explain the strongest alternative before checking the assessor. Use the task route to connect this work to the complete chapter. Do not mark a line learned because you opened a link.\n\n[Official task]({rows[0]["source_url"]}) · [Study route](../README.md) · [All task cards](../TASK-CARDS.md)\n\n'
 content+=f'Diagnostic items: SAA-D{num*2-1:02} and SAA-D{num*2:02}. Delayed transfer: SAA-T{num:02}. Save first answers before opening keys. These items sample the task; they do not test every line below.\n\n'
 for typ in ('knowledge','skill'):
  content+=f'## {"Knowledge to explain" if typ=="knowledge" else "Decisions and skills to practice"}\n\n'
  for r in rows:
   if ':'+typ+'-' not in r['id']:continue
   path=r['teaching_path'].split('#')[0];anchor=headers[path].get(r['section_title'].casefold())
   if not anchor:missing.append((r['id'],r['section_title']))
   dest=os.path.relpath(root/path,out)+('#'+anchor if anchor else '')
   ass=os.path.relpath(root/r['assessment_path'].split('#')[0],out)
   if '#' in r['assessment_path']:ass+='#'+r['assessment_path'].split('#')[1]
   content+=f'### {r["id"].split(":")[-1]}: {r["paraphrase"]}\n\n[Teaching: {r["section_title"]}]({dest}) · [Practice]({ass})\n\nRecord: first explanation, rejected alternative, changed case and assistance. Existing remaining evidence: {r["remaining_work"]}.\n\n'
   for extra in supplemental.get(r['id'],[]):
    extra_anchor=headers[extra['path']].get(extra['heading'].casefold())
    if not extra_anchor:raise ValueError((r['id'],extra))
    extra_dest=os.path.relpath(root/extra['path'],out)+'#'+extra_anchor
    content+=f'Also read: [{extra["heading"]}]({extra_dest}). This supplies another part of this objective.\n\n'
 (out/name).write_text(content.rstrip()+'\n')
(folder/'TASK-CARDS.md').write_text(''.join(index))
print('Created 14 task cards. Unmatched exact headings:',missing)
