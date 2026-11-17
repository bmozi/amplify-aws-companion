"""Render participant questions and separate rationales from the original item bank.

Retains the participant and assessor introductions. Never includes keys in the
participant document. Run package-saa-diagnostic.py after regeneration.
"""
import json
from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parents[1])
b=json.loads(Path('curriculum/saa-c03/assessor/question-bank.json').read_text())
part=Path('curriculum/saa-c03/DIAGNOSTIC.md');intro=part.read_text().split('\n## SAA-D01')[0].rstrip();texts=[intro]
key=Path('curriculum/saa-c03/assessor/DIAGNOSTIC-KEY.md');keys=[key.read_text().split('\n## SAA-D01')[0].rstrip()]
for q in b['questions']:
 texts.append(f"## {q['id']}\n\n{q['stem']}\n\n"+'\n'.join(f'- **{l}.** {t}' for l,t in q['options'].items()))
 keys.append(f"## {q['id']} — task {q['task']}\n\nExpected selection: **{', '.join(q['correct'])}**.\n\n"+'\n'.join(f'- **{l}:** {t}' for l,t in q['rationales'].items())+f"\n\nRemediation: [task {q['task']} work card](../tasks/{q['task'].replace('.','-')}.md). Technical references: "+', '.join(f'[source {i}]({u})' for i,u in enumerate(q['technical_references'],1))+'.')
part.write_text('\n\n'.join(texts)+'\n');key.write_text('\n\n'.join(keys)+'\n')
