"""Validate SAA study traceability and participant separation, not exam readiness."""
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'curriculum/saa-c03'
    baseline = json.loads((folder / 'source-baseline-2026-10-31.json').read_text())
    tasks = set(baseline['tasks'])
    assert len(tasks) == 14
    objectives = baseline['objectives']
    assert len(objectives) == 189
    assert len({row['id'] for row in objectives}) == len(objectives)
    missing_sections = []
    for row in objectives:
        for field in ('teaching_path', 'assessment_path'):
            target = ROOT / row[field].split('#')[0]
            assert target.is_file(), (row['id'], field, target)
        source = (ROOT / row['teaching_path'].split('#')[0]).read_text()
        # Report historical title drift separately; never silently promote a match.
        if row['section_title'].casefold() not in source.casefold():
            missing_sections.append({'id': row['id'], 'title': row['section_title']})
        assert row['existing_coverage'] == 'partial'
    # Historical baseline stays frozen; current cards must use current mappings.
    current = {}
    for kind in ('skill', 'knowledge'):
        for row in csv.DictReader((ROOT / f'curriculum/{kind}-evidence.csv').open()):
            current[row[kind + '_id']] = row
    for objective in objectives:
        row = current[objective['id']]
        assert not row['assessment_path'].startswith(('curriculum/skill-reviews/', 'curriculum/knowledge-reviews/')), objective['id']
        target = ROOT / row['assessment_path'].split('#')[0]
        assert target.is_file(), objective['id']
        card = (folder / 'tasks' / (objective['id'].split(':')[1].replace('.', '-') + '.md')).read_text()
        destination = os.path.relpath(target, folder / 'tasks')
        if '#' in row['assessment_path']:
            destination += '#' + row['assessment_path'].split('#', 1)[1]
        label = objective['id'].split(':')[-1]
        section = re.search(r'^### ' + re.escape(label) + r':.*?(?=^### |\Z)', card, re.M | re.S)
        assert section, objective['id']
        assert f'[Practice]({destination})' in section[0], objective['id']
    practice_bank = json.loads((folder / 'assessor/skill-practice-bank.json').read_text())
    assert len({item['id'] for item in practice_bank['items']}) == len(practice_bank['items'])
    for item in practice_bank['items']:
        document = (folder / 'practice' / (item['id'].split(':')[1].replace('.', '-') + '.md')).read_text()
        assert item['prompt'] in document, item['id']
        assert not re.search(r'Look for|Expected reasoning|Assessor criteria', document), item['id']
        assert 'curriculum/skill-reviews' not in document
    bank = json.loads((folder / 'assessor/question-bank.json').read_text())
    questions = bank['questions']
    assert len(questions) == 28
    assert len({q['id'] for q in questions}) == 28
    assert Counter(q['task'] for q in questions) == Counter({t: 2 for t in tasks})
    participant = (folder / 'DIAGNOSTIC.md').read_text()
    assessor = (folder / 'assessor/DIAGNOSTIC-KEY.md').read_text()
    for q in questions:
        assert q['stem'] in participant
        assert len(q['options']) in (4, 5)
        assert len(q['correct']) == len(set(q['correct']))
        assert set(q['correct']) <= set(q['options'])
        assert len(q['correct']) in (1, 2)
        assert ('Choose TWO' in q['stem']) == (len(q['correct']) == 2)
        assert set(q['rationales']) == set(q['options'])
        assert f"## {q['id']} — task {q['task']}" in assessor
        for letter, text in q['options'].items():
            assert f'**{letter}.** {text}' in participant
            assert q['rationales'][letter] in assessor
            assert q['rationales'][letter] not in participant
    transfer = (folder / 'TRANSFER.md').read_text()
    transfer_tasks = re.findall(r'^## SAA-T\d+ — task (\d+\.\d+)$', transfer, re.M)
    assert len(transfer_tasks) == 14 and set(transfer_tasks) == tasks
    # Markdown targets in the new study source must resolve. Public access is separate.
    for path in list(folder.rglob('*.md')) + [ROOT / 'docs/SAA-C03-JOHN-STUDY-RECORD.md']:
        for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if re.match(r'^[a-z]+:', link) or link.startswith('#'):
                continue
            assert (path.parent / link.split('#')[0]).exists(), (path, link)
    packet = ROOT / 'artifacts/saa-c03-study/AMPLIFY-AWS-SAA-C03-first-attempt.zip'
    if packet.exists():
        with zipfile.ZipFile(packet) as archive:
            assert set(archive.namelist()) == {'START-HERE.md', 'DIAGNOSTIC.md', 'responses.csv', 'manifest.json'}
            assert archive.testzip() is None
            manifest = json.loads(archive.read('manifest.json'))
            for name, digest in manifest['sha256'].items():
                assert hashlib.sha256(archive.read(name)).hexdigest() == digest
            assert archive.read('DIAGNOSTIC.md') == (folder / 'DIAGNOSTIC.md').read_bytes()
    report = {'objectives': len(objectives), 'tasks': len(tasks),
              'diagnostic_questions': len(questions), 'multiple_response': sum(len(q['correct']) == 2 for q in questions),
              'transfer_cases': len(transfer_tasks), 'historical_section_title_drift': missing_sections,
              'scope': 'Structural consistency and packet separation only; no semantic, independent learner, AWS or exam-pass validation.'}
    out = ROOT / 'artifacts/saa-c03-study'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'structural-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if missing_sections:
        raise SystemExit('Review historical section-title drift before claiming complete navigation.')


if __name__ == '__main__':
    main()
