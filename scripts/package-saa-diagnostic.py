"""Create an explicitly allowlisted, answer-free local SAA first-attempt packet."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'curriculum/saa-c03/DIAGNOSTIC.md'
    # Read participant source only. Do not include the private study record or answer bank.
    import re
    ids = re.findall(r'^## (SAA-D\d+)$', source.read_text(), re.M)
    assert len(ids) == 28 and len(set(ids)) == 28
    responses = io.StringIO()
    writer = csv.writer(responses, lineterminator='\n')
    writer.writerow(['question_id', 'choices', 'reason', 'confidence', 'elapsed_minutes', 'prior_exposure', 'assistance'])
    writer.writerows([item, '', '', '', '', '', ''] for item in ids)
    start = '''# Your first SAA-C03 study attempt

You may start with Chapter 1 and attempt DIAGNOSTIC.md later. Record which chapters
you have already studied; a post-study first attempt is not a pre-study baseline.
Save choices and reasoning in responses.csv or a separate document. Do not consult
a key, AI or the book during the attempt. Unknown answers are useful; this is not
a pass/fail examination.
There is no imposed deadline. Record elapsed time and any prior exposure.

This packet contains 28 original fictional questions and no answer key. It is not
an official AWS assessment or a calibrated mock exam. It does not reproduce the
official domain weighting. After saving your first answers, return them for review
and use the book's task route to study the gaps. Never record recalled exam items.
'''
    members = {'START-HERE.md': start.encode(), 'DIAGNOSTIC.md': source.read_bytes(),
               'responses.csv': responses.getvalue().encode()}
    manifest = {'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_has_local_edits': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).strip()),
                'sha256': {name: hashlib.sha256(data).hexdigest() for name, data in members.items()},
                'scope': 'Author-learner first attempt; no answers, result, independent validation or public-release approval.'}
    out = ROOT / 'artifacts/saa-c03-study'
    out.mkdir(parents=True, exist_ok=True)
    packet = out / 'AMPLIFY-AWS-SAA-C03-first-attempt.zip'
    with zipfile.ZipFile(packet, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in members.items():
            archive.writestr(name, data)
        archive.writestr('manifest.json', json.dumps(manifest, indent=2) + '\n')
    (out / 'packet-receipt.json').write_text(json.dumps({'path': str(packet), 'archive_sha256': hashlib.sha256(packet.read_bytes()).hexdigest(), **manifest}, indent=2) + '\n')
    print(packet)


if __name__ == '__main__':
    main()
