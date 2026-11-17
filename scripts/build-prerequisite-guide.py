"""Validate the curriculum dependency graph and render its reader-facing guide."""
import argparse
import csv
import json
import re
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]


def current_book_chapters():
    """Map lesson source paths to the current reading-copy chapter labels."""
    source=(BASE/'book/UNIT-OUTCOMES.md').read_text()
    rows=re.findall(r'^\| (\d+) \| \[([^]]+)\]\(units/([^)]+)\)',source,re.M)
    if len(rows)!=34 or {int(number) for number,_,_ in rows}!=set(range(1,35)):
        raise ValueError('Current book chapter table is incomplete or duplicated')
    paths={}
    for number,label,filename in rows:
        path='book/units/'+filename
        if path in paths:raise ValueError(f'Duplicate current book source: {path}')
        short_label=re.sub(r'^\d+\s*·\s*','',label)
        paths[path]=(int(number),short_label)
    return paths


def validate_and_order(chapters, targets):
    by_id={c['chapter']:c for c in chapters}
    if len(by_id)!=len(chapters):raise ValueError('Duplicate chapter')
    visiting=set();done=set();order=[]
    def visit(number):
        if number not in by_id:raise ValueError(f'Missing prerequisite {number}')
        if number in visiting:raise ValueError(f'Prerequisite cycle at {number}')
        if number in done:return
        visiting.add(number)
        for prerequisite in by_id[number]['prerequisites']:visit(prerequisite)
        visiting.remove(number);done.add(number);order.append(number)
    for target in targets:visit(target)
    return order


def render(data=None, ledger=None):
    if data is None:
        data=json.loads((BASE/'curriculum/prerequisites.json').read_text())
    chapters=data['chapters']
    assert len(chapters)==34 and {c['chapter'] for c in chapters}==set(range(1,35))
    validate_and_order(chapters,range(1,35))
    for c in chapters:
        assert all(c[field].strip() for field in ['outcome','exit_challenge','evidence'])
        assert len(c['prerequisites'])==len(set(c['prerequisites']))
    if ledger is None:
        with (BASE/'curriculum/chapter-evidence.csv').open() as f:
            rows=list(csv.DictReader(f))
        if len(rows)!=34:
            raise ValueError('Planning-step evidence ledger must have 34 rows')
        ledger={int(r['chapter']):r for r in rows}
    if set(ledger)!=set(range(1,35)):
        raise ValueError('Planning-step evidence ledger is incomplete or duplicated')
    book_chapters=current_book_chapters()
    out=['# What to learn first, and how to show it',
         '', 'Generated from `prerequisites.json`, `chapter-evidence.csv` and the [current book chapter map](../book/UNIT-OUTCOMES.md). The numbered learning steps below are an earlier dependency plan, **not** the book\'s chapter numbers. Each step links to its actual book chapters. These are proposed learning dependencies and original assessment prompts, not verified learner outcomes.',
         '', '## Use the map like a driving lesson', '',
         'Before driving on a busy road, a learner should be able to steer, stop and explain the signs. Reading the steering chapter alone does not demonstrate that ability. Here, a prerequisite names a capability to check before adding complexity. A reader with prior experience can demonstrate it rather than reread every page.', '',
         'Start with the file/Git/JSON checks in [learning routes](LEARNING-ROUTES.md). Choose a route below. For each learning step, inspect its linked current book chapters and evidence scope, attempt the exit challenge, then record what you actually demonstrated. If the needed lesson or implementation is missing, mark that requirement pending; an outline is not a substitute.', '',
         'Local or design-only evidence supports only that level of practice. A successful local permission fixture does not waive the scoped-role prerequisite for AWS deployment. Organization-dependent exercises stay design-only until the required account and authority exist. Before a live run, identify the account, Region, identity, service eligibility, complete estimate, spending limit and credit reserve chosen for that account, stop conditions and cleanup owner.', '',
         '## Route order', '',
         'These sequences include the transitive prerequisites of their targets. They are editorial recommendations, not official AWS certification prerequisites. Repeated topics can be demonstrated once and revisited when the changed scenario exposes a weakness.', '',
         '| Route | Learning steps in dependency order | Exit steps |', '| --- | --- | --- |']
    for name,route in data['routes'].items():
        order=validate_and_order(chapters,route['targets'])
        assert set(route['exit_chapters'])<=set(order)
        out.append('| '+name.replace('_',' ').title()+' | '+', '.join(map(str,order))+' | '+', '.join(map(str,route['exit_chapters']))+' |')
    out+=['', 'Read the step numbers in this table against the step headings below, where each one names its current book chapters. The certification-review sequence is only a starting diagnostic. Add the practical route matching the selected exam and the official task/skill ledger; completing learning step 33 does not establish advanced exam coverage. The architect route includes operating foundations because a design must account for deployment, failure and recovery.', '',
          '## Record a bounded learning result', '',
          'Use the [learning-record worksheet](LEARNING-RECORD.md) for a copyable form and a worked example. For every attempt, record learning step and current book chapter, challenge variant, source revision, environment, assistance used, observations, explanation and unresolved limitations. Use these four decisions instead of a single optimistic completion percentage:', '',
          '| Dimension | Sufficient for this practice attempt | Needs another attempt |', '| --- | --- | --- |',
          '| Explain | Predict the outcome and explain the relevant boundary in your own words | Repeat service names or an AI answer without explaining the mechanism |',
          '| Demonstrate | Supply the named evidence at the declared local/design/live scope | Supply a screenshot or green check that does not test the claim |',
          '| Transfer | Update the decision when the challenge changes a constraint | Copy the original solution despite a changed invariant |',
          '| Bound the claim | Name untested behavior, data/access limits, costs and cleanup | Claim cloud enforcement, recovery or learning from an unrelated local test |', '',
          'Do not average away a material failure. Unauthorized disclosure, an unbounded live experiment, or invented evidence requires correction before that attempt can count as sufficient. These are provisional assessment criteria, not statistically validated scoring thresholds. A self-assessment and an independent assessor judgment are separate records.', '',
          'Use Codex for the guided pass: ask it to explain one concept, then ask you to predict a result before revealing the answer. For the exit attempt, withhold the worked solution, disclose assistance, and separate your unaided explanation from generated code. An assessor should ask a follow-up that changes one requirement.', '',
          '## Learning-step checks', '',
          'Each linked starting point exists today. It may cover only part of the challenge. The [planning-step artifact map](chapter-evidence.csv) lists supporting files and remaining work; each step\'s current status is reproduced below to avoid presenting this map as delivered instruction.']
    for c in chapters:
        row=ledger[c['chapter']]
        links=[]
        actual=[]
        for source in row['teaching_paths'].split(';'):
            links.append(f'[{Path(source).name}](../{source})')
            if source.startswith('book/units/'):
                if source not in book_chapters:raise ValueError(f'Unknown current book source: {source}')
                number,label=book_chapters[source]
                if number not in [item[0] for item in actual]:actual.append((number,label,source))
        if not actual:raise ValueError(f"Learning step {c['chapter']} has no current book chapter")
        actual_links=', '.join(f'[Chapter {number}: {label}](../{source})' for number,label,source in actual)
        prerequisites=', '.join(map(str,c['prerequisites'])) or 'Entry file/Git/JSON checks'
        out+=['',f"### Learning step {c['chapter']}: {row['title']}", '',
              f"Current book chapters: {actual_links}.", '',
              f"Prerequisite steps: {prerequisites}. Current teaching status: **{row['chapter_status']}**; independent learner review: **{row['learner_review']}**.", '',
              '**Outcome:** '+c['outcome'], '', '**Changed-case challenge:** '+c['exit_challenge'], '',
              '**Evidence to supply:** '+c['evidence'], '', 'Current starting material: '+', '.join(links)+'.']
    out+=['', '## Maintain the dependency decisions', '',
          'Edit the JSON source or evidence map, then run `python3 scripts/build-prerequisite-guide.py`. The companion checker verifies the graph has no cycles or missing steps, checks the current chapter links and confirms that this guide matches its source. It cannot validate pedagogical ordering, test a learner or infer completion. Revisit a prerequisite when reader observations show it is unnecessary or missing; record the reason in continuity rather than silently promising an easier route.', '']
    return '\n'.join(out)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    output=BASE/'curriculum/PREREQUISITES-AND-EXIT-CHECKS.md';content=render()
    if args.check:
        if not output.exists() or output.read_text()!=content:raise SystemExit('Prerequisite guide is stale; rebuild it')
        print('Validated 34 learning-step dependencies, four route orders and current-book links; no learner result inferred.')
    else:
        output.write_text(content);print(output)


if __name__=='__main__':main()
