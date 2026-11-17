"""Render original skill prompts separately from internal assessor criteria."""
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'curriculum/saa-c03'
OUT = FOLDER / 'practice'


def main():
    bank = json.loads((FOLDER / 'assessor/skill-practice-bank.json').read_text())
    tasks = {}
    for item in bank['items']:
        assert not re.search(r'Look for|Expected reasoning|Assessor criteria', item['prompt'])
        tasks.setdefault(item['id'].split(':')[1], []).append(item)
    OUT.mkdir(exist_ok=True)
    index = ['# Skill practice before assessor review\n\nThese original prompts supplement the diagnostic. They are not a calibrated mock exam. Read the linked book lesson, then answer without AI or the assessor. Record your decision, evidence, rejected alternative, uncertainty and changed-case reasoning. Save your first answer before checking it.\n']
    key = ['# Skill practice assessor routes\n\nOpen only after saving the learner attempt. The linked internal review documents contain provisional criteria and evidence limits, not validated scoring rules.\n']
    for task, items in sorted(tasks.items()):
        name = task.replace('.', '-') + '.md'
        lines = [f'# Task {task} skill practice\n\nAttempt these cases before consulting assessor material. Record your decision, rejected alternative, changed-case reasoning and uncertainty. Note any assistance or prior exposure.\n']
        index.append(f'- [Task {task}]({name})\n')
        for item in sorted(items, key=lambda x: x['id']):
            number = item['id'].rsplit('-', 1)[1]
            prompt = item['prompt']
            source = ROOT / item['source_review']
            def rebase(match):
                target = match[1]
                if re.match(r'^[a-z]+:', target) or target.startswith('#'):
                    return match[0]
                bare, sep, fragment = target.partition('#')
                return '](' + os.path.relpath(source.parent / bare, OUT) + (sep + fragment if sep else '') + ')'
            prompt = re.sub(r'\]\(([^)]+)\)', rebase, prompt)
            lines.append(f'## Skill {number}\n\n{item["title"]}\n\n{prompt}\n')
            key.append(f'- {item["id"]}: [{item["source_heading"]}]({os.path.relpath(source, FOLDER / "assessor")}).\n')
        (OUT / name).write_text('\n'.join(lines))
    (OUT / 'README.md').write_text(''.join(index))
    (FOLDER / 'assessor/SKILL-PRACTICE-KEY.md').write_text(''.join(key))
    print(f'Rendered {len(bank["items"])} prompts across {len(tasks)} tasks; criteria remain separate.')


if __name__ == '__main__':
    main()
