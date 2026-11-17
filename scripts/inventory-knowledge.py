"""Build candidate knowledge inventory from official Markdown; never mark coverage complete."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import urllib.request

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'artifacts/curriculum-research'


def parse_tasks(source):
    sections = {}
    for match in re.finditer(r'^## Task(?: Statement)? (\d+\.\d+):[^\n]*\n(.*?)(?=^## Task|\Z)', source, re.M | re.S):
        task, body = match.groups()
        if task in sections:
            raise ValueError('Duplicate task section: ' + task)
        mode = None
        groups = {'knowledge': [], 'skills': []}
        for line in body.splitlines():
            heading = line.lstrip('# ').strip()
            if heading == 'Knowledge of:':
                mode = 'knowledge'
            elif heading == 'Skills in:':
                mode = 'skills'
            elif line.startswith('+ Skill '):
                groups['skills'].append(line[2:].strip())
            elif line.startswith('+ '):
                if mode is None:
                    raise ValueError('Unclassified bullet in task ' + task)
                groups[mode].append(line[2:].strip())
            elif re.match(r'^\s+[+*-] ', line):
                raise ValueError('Nested bullet requires manual review: ' + task)
        sections[task] = groups
    if not sections:
        raise ValueError('No task sections detected')
    return sections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Fetch official Markdown and replace ignored research cache')
    args = parser.parse_args()
    with (BASE/'curriculum/coverage.csv').open() as stream:
        tasks = list(csv.DictReader(stream))
    urls = sorted({row['source_url'].split('#')[0].replace('.html', '.md') for row in tasks})
    OUT.mkdir(parents=True, exist_ok=True)
    def fetch(url):
        path = OUT / url.rsplit('/', 1)[-1]
        if args.refresh:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = response.read()
            source = data.decode('utf-8')
            parse_tasks(source)  # Reject error/login pages before accepting a response.
            path.write_bytes(data)
        else:
            data = path.read_bytes()
        return url, data
    # Independent documentation reads, bounded concurrency; no AWS account APIs.
    with ThreadPoolExecutor(max_workers=4) as pool:
        fetched = dict(pool.map(fetch, urls))
    fetch_record = OUT / 'fetch-metadata.json'
    hashes = {url: hashlib.sha256(data).hexdigest() for url, data in fetched.items()}
    if args.refresh:
        fetch_record.write_text(json.dumps({'fetched_utc': datetime.now(timezone.utc).isoformat(), 'sha256': hashes}, indent=2)+'\n')
    provenance = json.loads(fetch_record.read_text())
    if provenance['sha256'] != hashes:
        raise ValueError('Cached source differs from fetch record; refresh or investigate')
    parsed = {url: parse_tasks(data.decode('utf-8')) for url, data in fetched.items()}
    expected = {url: {r['task'] for r in tasks if r['source_url'].split('#')[0].replace('.html','.md') == url} for url in urls}
    for url in urls:
        if set(parsed[url]) != expected[url]:
            raise ValueError('Task baseline changed: ' + url)
    rows, summaries = [], []
    for task in tasks:
        url = task['source_url'].split('#')[0].replace('.html', '.md')
        groups = parsed[url][task['task']]
        if bool(groups['knowledge']) != (task['exam'] != 'SOA-C03'):
            raise ValueError('Knowledge-list structure changed: ' + task['id'])
        if len(groups['skills']) != int(task['skill_count']):
            raise ValueError('Skill count baseline changed: ' + task['id'])
        summaries.append({'task_id': task['id'], 'knowledge_count': len(groups['knowledge']),
                          'skill_count': len(groups['skills']),
                          'knowledge_structure': 'separate list' if groups['knowledge'] else 'no separate list in checked task'})
        for index, bullet in enumerate(groups['knowledge'], 1):
            rows.append({'id': task['id']+f':knowledge-{index:02}', 'task_id': task['id'],
                         'ordinal': index, 'source_url': task['source_url'],
                         'source_bullet_sha256': hashlib.sha256(bullet.encode()).hexdigest(),
                         'chapters': task['chapters'], 'exercise': task['exercise'],
                         'coverage': 'inventory only; individual teaching and assessment review pending'})
    fields = ['id','task_id','ordinal','source_url','source_bullet_sha256','chapters','exercise','coverage']
    with (OUT/'knowledge-inventory.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    report={'generated_utc': datetime.now(timezone.utc).isoformat(), 'fetched_this_run': args.refresh, 'source_fetch_utc': provenance['fetched_utc'],
            'sources': [{'url':url,'sha256':hashlib.sha256(data).hexdigest()} for url,data in fetched.items()],
            'tasks': summaries,'knowledge_entries':len(rows),
            'by_exam':dict(Counter(row['task_id'].split(':')[0] for row in rows)),
            'scope':'Editorial ordinal inventory; source hashes detect change, not semantic coverage. No learner or certification readiness claim.'}
    (OUT/'knowledge-sources.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['knowledge_entries','by_exam','scope']},indent=2))


if __name__ == '__main__':
    main()
