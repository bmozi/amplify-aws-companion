"""Check curriculum structure, not teaching quality or certification readiness."""
import csv
from collections import Counter
from pathlib import Path
import re
import subprocess

base=Path(__file__).resolve().parents[1]
fragment_ids={}
def reference_path(value):
    relative, separator, fragment = value.partition('#')
    path=(base/relative).resolve()
    assert path.is_relative_to(base) and path.is_file(), value
    if separator:
        assert fragment, value
        if path not in fragment_ids:
            rendered=subprocess.check_output(['pandoc','-f','gfm','-t','html',str(path)],text=True)
            fragment_ids[path]=set(re.findall(r'\bid="([^"]+)"',rendered))
        assert fragment in fragment_ids[path], value
    return path
def read(name):
    with (base/'curriculum'/name).open() as f:return list(csv.DictReader(f))
tasks=read('coverage.csv');skills=read('skill-inventory.csv');questions=read('well-architected.csv')
assert Counter(t['exam'] for t in tasks)=={'SAA-C03':14,'SOA-C03':13,'DOP-C02':19,'SAP-C02':20}
assert len({t['id'] for t in tasks})==len(tasks)==66
assert len({s['id'] for s in skills})==len(skills)==310
assert len({q['question_id'] for q in questions})==len(questions)==57
exercises=(base/'curriculum/EXERCISES.md').read_text()
anchors=set(re.findall(r'<a id="(e\d+)"></a>',exercises));assert len(anchors)==32
bytask={t['id']:t for t in tasks}
for t in tasks:
    assert t['exercise'].lower() in anchors
    assert all(1<=int(c)<=34 for c in t['chapters'].split(';'))
    assert all(re.fullmatch(r'A(?:0[1-9]|1[0-9]|2[0-4])',a) for a in t['architectures'].split(';'))
    assert t['source_url'].startswith('https://docs.aws.amazon.com/aws-certification/')
for s in skills:assert s['task_id'] in bytask and s['exercise']==bytask[s['task_id']]['exercise']
counts=Counter(s['task_id'] for s in skills)
for t in tasks:assert counts[t['id']]==int(t['skill_count'])
for q in questions:assert q['exercise'].lower() in anchors
print(f'Validated 66 task rows, 310 skill inventory rows, 57 framework questions and {len(anchors)} exercise links.')
print('This establishes structural consistency only; skill-level evidence and reader review remain separate.')

chapters=read('chapter-evidence.csv')
assert {int(c['chapter']) for c in chapters}==set(range(1,35)) and len(chapters)==34
for c in chapters:
    assert c['chapter_status'] in {'partial','draft_complete','reviewed'}
    assert c['learner_review'] in {'pending','recorded'}
    assert c['evidence_scope'].strip() and c['next_required_work'].strip()
    for field in ['teaching_paths','evidence_paths']:
        for value in c[field].split(';'):
            path=(base/value).resolve()
            assert path.is_relative_to(base) and path.is_file(), (c['chapter'],value)
    assert all(e.lower() in anchors for e in c['exercises'].split(';'))
print('Validated 34 chapter evidence rows and their local artifact links; no chapter completion inferred.')

# The back-of-book finder uses reader chapter numbers, not stable unit filenames.
reader_index=(base/'book/README.md').read_text()
chapter_paths={int(number):path for number,path in re.findall(
    r'^([0-9]+)\. \[[^]]+\]\((units/[^)]+\.md)\)',reader_index,re.M)}
assert set(chapter_paths)==set(range(1,35))
finder=(base/'book/TOPIC-FINDER.md').read_text()
topic_rows=[line for line in finder.splitlines() if line.startswith('- **')]
assert topic_rows
referenced=[]
for line in topic_rows:
    links=re.findall(r'\[Chapter (\d+)\]\((units/[^)]+\.md)\)',line)
    assert len(links)==2, line
    for number,path in links:
        assert chapter_paths.get(int(number))==path, (number,path)
        referenced.append(int(number))
assert set(referenced)==set(chapter_paths), 'Topic finder omits a reader chapter'
print(f'Validated {len(topic_rows)} topic-finder entries and {len(referenced)} chapter references; no page-index or reader-use claim inferred.')

# Keep the reader-facing sequence synchronized with the checked dependency graph.
import subprocess
import sys
subprocess.run([sys.executable,str(base/'scripts/build-prerequisite-guide.py'),'--check'],check=True)
subprocess.run([sys.executable,str(base/'scripts/build-current-task-entrypoints.py'),'--check'],check=True)

individual=read('skill-evidence.csv')
known_skills={s['id'] for s in skills}
assert len({r['skill_id'] for r in individual})==len(individual)
for row in individual:
    assert row['skill_id'] in known_skills
    assert row['coverage'] in {'partial','draft_complete','reviewed'}
    assert row['learner_review'] in {'pending','recorded'}
    assert row['objective_paraphrase'].strip() and row['evidence_scope'].strip() and row['remaining_work'].strip()
    for field in ['teaching_path','assessment_path']:
        path=reference_path(row[field])
        assert path.is_relative_to(base) and path.is_file(), (row['skill_id'],field)
    headings={line.lstrip('#').strip() for line in (base/row['teaching_path']).read_text().splitlines() if line.startswith('#')}
    assert row['section_title'] in headings, (row['skill_id'],row['section_title'])
reviewed_ids={row['skill_id'] for row in individual}
assert {s['id'] for s in skills if s['coverage'].startswith('individual evidence reviewed')}==reviewed_ids
remaining_skill_assignments=len(known_skills-reviewed_ids)
print(f'Validated {len(individual)} individual skill evidence mappings; {remaining_skill_assignments} skills remain task-level assignments. Individual mappings do not prove skill completion.')

# Knowledge lists are inventoried separately; counts never imply assessed understanding.
import json
knowledge=read('knowledge-inventory.csv')
knowledge_sources=json.loads((base/'curriculum/knowledge-sources.json').read_text())
assert len(knowledge)==len({r['id'] for r in knowledge})==knowledge_sources['knowledge_entries']==259
assert Counter(r['task_id'].split(':')[0] for r in knowledge)=={'SAA-C03':107,'DOP-C02':59,'SAP-C02':93}
source_tasks={r['task_id']:r for r in knowledge_sources['tasks']}
assert set(source_tasks)==set(bytask) and len(knowledge_sources['tasks'])==66
assert {r['url'] for r in knowledge_sources['sources']}=={t['source_url'].split('#')[0].replace('.html','.md') for t in tasks}
for row in knowledge:
    task=bytask[row['task_id']]
    assert row['id']==row['task_id']+f":knowledge-{int(row['ordinal']):02}"
    assert row['source_url']==task['source_url'] and row['chapters']==task['chapters'] and row['exercise']==task['exercise']
    assert re.fullmatch('[0-9a-f]{64}',row['source_bullet_sha256'])
    assert row['coverage'] in {'inventory only; individual teaching and assessment review pending','individual evidence reviewed; partial; see knowledge-evidence.csv'}
for task_id,source in source_tasks.items():
    ordinals=sorted(int(row['ordinal']) for row in knowledge if row['task_id']==task_id)
    assert ordinals==list(range(1,source['knowledge_count']+1))
    assert source['skill_count']==int(bytask[task_id]['skill_count'])
    assert bool(ordinals)==(bytask[task_id]['exam']!='SOA-C03')
knowledge_evidence=read('knowledge-evidence.csv')
known_knowledge={row['id']:row for row in knowledge}
assert len({row['knowledge_id'] for row in knowledge_evidence})==len(knowledge_evidence)
for row in knowledge_evidence:
    assert row['knowledge_id'] in known_knowledge
    assert row['source_bullet_sha256']==known_knowledge[row['knowledge_id']]['source_bullet_sha256']
    assert row['coverage']=='partial' and row['learner_review']=='pending'
    assert all(row[key].strip() for key in ['objective_paraphrase','evidence_scope','remaining_work','checked_date'])
    for field in ['teaching_path','assessment_path']:
        path=reference_path(row[field])
        assert path.is_relative_to(base) and path.is_file()
    headings={line.lstrip('#').strip() for line in (base/row['teaching_path']).read_text().splitlines() if line.startswith('#')}
    assert row['section_title'] in headings
assert {row['knowledge_id'] for row in knowledge_evidence}=={row['id'] for row in knowledge if row['coverage'].startswith('individual evidence reviewed')}
remaining_knowledge_assignments=len(known_knowledge)-len(knowledge_evidence)
print(f'Validated 259 knowledge entries and {len(knowledge_evidence)} partial individual mappings; {remaining_knowledge_assignments} entries remain inventory only.')

# Developer Associate was added after the four-exam ledger above. These
# counts describe the guide snapshot, not a claim about exam coverage.
dva=read('DVA-C03-SKILL-INVENTORY.csv')
dva_expected={'1.1':10,'1.2':4,'1.3':4,'2.1':7,'2.2':7,'2.3':5,
              '3.1':5,'3.2':5,'3.3':9,'4.1':5,'4.2':5,'4.3':6}
expected_ids={f'{task}.{n}' for task,count in dva_expected.items() for n in range(1,count+1)}
assert len(dva)==72 and {r['skill_id'] for r in dva}==expected_ids, 'DVA skill IDs differ from the recorded guide snapshot'
for row in dva:
    skill=row['skill_id'];task='.'.join(skill.split('.')[:2]);domain=skill.split('.')[0]
    assert row['task_id']==task, skill
    assert row['official_domain_url']==f'https://docs.aws.amazon.com/aws-certification/latest/developer-associate-03/developer-associate-03-domain{domain}.html', skill
    assert row['assessment'] in {'partial','not assessed'}, skill
    assert row['limit'].strip(), skill
    if row['assessment']=='partial':
        target=(base/'curriculum'/row['local_evidence']).resolve()
        assert row['local_evidence'] and target.is_relative_to(base) and target.is_file(), skill
    else:
        assert not row['local_evidence'], skill
summary=(base/'curriculum/DVA-C03-SKILL-INVENTORY.md').read_text()
for domain,label in [('1','Development'),('2','Security'),('3','Testing and deployment'),('4','Troubleshooting and optimization')]:
    group=[r for r in dva if r['skill_id'].startswith(domain+'.')]
    partial=sum(r['assessment']=='partial' for r in group)
    assert f'| {label} | {len(group)} | {partial} | {len(group)-partial} |' in summary, label
partial=sum(r['assessment']=='partial' for r in dva)
assert f'| **Total** | **{len(dva)}** | **{partial}** | **{len(dva)-partial}** |' in summary
print(f'Validated {len(dva)} DVA-C03 skill IDs and summary rows; {partial} partial starting points, not demonstrated mastery or current AWS behavior.')
