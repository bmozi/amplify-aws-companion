"""Synthetic evidence gate for a CloudFormation-to-Terraform ownership handoff.

This does not parse a real change set or Terraform plan, call AWS, or approve one.
"""

from copy import deepcopy


def assess(evidence):
    """Return separate import-readiness and customer-acceptance decisions."""
    reasons = []
    old = evidence.get('old_owner') or {}
    target = evidence.get('terraform_target') or {}
    for label in ('account', 'region', 'physical_id'):
        if not isinstance(old.get(label), str) or not old[label].strip() or not isinstance(target.get(label), str) or not target[label].strip():
            reasons.append(f'{label} evidence is missing')
    if old.get('account') != target.get('account') or old.get('region') != target.get('region'):
        reasons.append('account or Region differs')
    if old.get('physical_id') != target.get('physical_id'):
        reasons.append('physical resource ID differs')
    if old.get('stack_membership') != 'released':
        reasons.append('old stack ownership is not verified released')
    if old.get('release_action') != 'retain':
        reasons.append('physical retention is not verified')
    if old.get('next_backend_deploy') != 'does_not_manage':
        reasons.append('next backend deployment may manage the table again')
    if target.get('plan_action') != 'import_only':
        reasons.append('Terraform plan is not import only')
    if target.get('configuration_reviewed') is not True:
        reasons.append('Terraform configuration is not reviewed against the object')
    ready_to_import = not reasons
    acceptance = evidence.get('customer_acceptance')
    complete = ready_to_import and evidence.get('import_observed') is True and acceptance == 'passed'
    if ready_to_import and evidence.get('import_observed') is not True:
        reasons.append('import has not been observed')
    if ready_to_import and acceptance != 'passed':
        reasons.append('customer read and write acceptance has not passed')
    return {'ready_to_import': ready_to_import, 'handoff_complete': complete, 'reasons': reasons}


def baseline():
    return {
        'old_owner': {'account': '111122223333', 'region': 'us-east-2',
                      'physical_id': 'orders-practice-42', 'stack_membership': 'released',
                      'release_action': 'retain', 'next_backend_deploy': 'does_not_manage'},
        'terraform_target': {'account': '111122223333', 'region': 'us-east-2',
                             'physical_id': 'orders-practice-42', 'plan_action': 'import_only',
                             'configuration_reviewed': True},
        'import_observed': False,
        'customer_acceptance': 'not_run',
    }


def cases():
    cases = [('reviewed release, before import', baseline(), (True, False))]
    double_owner = deepcopy(baseline())
    double_owner['old_owner']['stack_membership'] = 'managed'
    cases.append(('two managers', double_owner, (False, False)))
    deletion = deepcopy(baseline())
    deletion['old_owner']['release_action'] = 'delete'
    cases.append(('deletion change', deletion, (False, False)))
    wrong_region = deepcopy(baseline())
    wrong_region['terraform_target']['region'] = 'us-west-2'
    cases.append(('wrong Region', wrong_region, (False, False)))
    replacement = deepcopy(baseline())
    replacement['terraform_target']['plan_action'] = 'replace'
    cases.append(('Terraform replacement', replacement, (False, False)))
    reclaimed = deepcopy(baseline())
    reclaimed['old_owner']['next_backend_deploy'] = 'unknown'
    cases.append(('future backend ownership unknown', reclaimed, (False, False)))
    failed_customer = deepcopy(baseline())
    failed_customer['import_observed'] = True
    failed_customer['customer_acceptance'] = 'failed'
    cases.append(('infrastructure moved, customer failed', failed_customer, (True, False)))
    accepted = deepcopy(baseline())
    accepted['import_observed'] = True
    accepted['customer_acceptance'] = 'passed'
    cases.append(('observed import and customer acceptance', accepted, (True, True)))
    return cases


if __name__ == '__main__':
    for name, evidence, expected in cases():
        result = assess(evidence)
        actual = (result['ready_to_import'], result['handoff_complete'])
        assert actual == expected, (name, actual, expected)
        print(f'{name}: import_ready={actual[0]} complete={actual[1]} reasons={result["reasons"]}')
