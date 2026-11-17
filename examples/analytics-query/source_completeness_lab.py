"""Show why a correct candidate manifest cannot certify its source population."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import file_publication_lab as publication


REGISTER = Path(__file__).with_name('intake-register.json')


def rows_by_id(rows):
    result = {}
    for row in rows:
        if (not isinstance(row, (list, tuple)) or len(row) != 2 or
                not isinstance(row[0], str) or not row[0] or
                type(row[1]) is not int or row[0] in result):
            raise ValueError('Rows need distinct text IDs and integer cents')
        result[row[0]] = row[1]
    return result


def reconcile(view, register):
    """Compare a selected view to supplied independent fixture controls."""
    if register is None:
        return {'status': 'unknown_no_independent_register'}
    expected = rows_by_id(register['receipts'])
    observed = rows_by_id(view['rows'])
    count = register['closing_count']
    total = register['closing_total_cents']
    if type(count) is not int or type(total) is not int or count < 0:
        raise ValueError('Closing controls need valid integer units')
    register_controls_agree = len(expected) == count and sum(expected.values()) == total
    missing = sorted(set(expected) - set(observed))
    unexpected = sorted(set(observed) - set(expected))
    changed = sorted(key for key in set(expected) & set(observed)
                     if expected[key] != observed[key])
    controls_match_view = len(observed) == count and sum(observed.values()) == total
    status = ('matches_supplied_register' if register_controls_agree and controls_match_view
              and not (missing or unexpected or changed) else 'hold_for_reconciliation')
    return {'status': status, 'register_controls_agree': register_controls_agree,
            'view_matches_closing_controls': controls_match_view,
            'missing_receipt_ids': missing, 'unexpected_receipt_ids': unexpected,
            'changed_receipt_ids': changed,
            'scope': 'supplied fictional register, not authenticated producer completeness'}


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization so fixture assertions execute')
    register = json.loads(REGISTER.read_text())
    with TemporaryDirectory(prefix='analytics-source-check-') as directory:
        root = Path(directory)
        publication.stage(root, 'missing-sale', 2, [[('a', 100), ('b', 180)], []], ['a', 'b'])
        assert publication.publish(root, 'missing-sale', 0) == ('published', 1)
        incomplete = publication.read_view(root)
        manifest, _ = publication.candidate(root, 'missing-sale')
        assert manifest['expected_ids'] == ['a', 'b'] and incomplete['cents'] == 280
        first = reconcile(incomplete, register)
        assert first['status'] == 'hold_for_reconciliation'
        assert first['missing_receipt_ids'] == ['late']
        publication.stage(root, 'complete-sale', 3,
                          [[('a', 100), ('b', 180)], [('late', 50)]],
                          ['a', 'b', 'late'])
        assert publication.publish(root, 'complete-sale', 1) == ('published', 2)
        corrected = publication.read_view(root)
        second = reconcile(corrected, register)
        assert corrected['cents'] == 330 and second['status'] == 'matches_supplied_register'
        print(json.dumps({
            'self_consistent_manifest_for_incomplete_report': True,
            'incomplete_report_cents': incomplete['cents'],
            'independent_register_check': first,
            'corrected_report_cents': corrected['cents'],
            'corrected_register_check': second,
        }, indent=2))


if __name__ == '__main__':
    main()
