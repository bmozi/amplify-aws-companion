"""Audit fictional frontend bundles against an approved destination map.

This is local configuration comparison, not AWS inventory or access proof.
"""

from copy import deepcopy
import json
import re


PATHS = {
    'user_pool': ('outputs', 'auth', 'user_pool_id'),
    'user_pool_client': ('outputs', 'auth', 'user_pool_client_id'),
    'data': ('outputs', 'data', 'url'),
    'data_default_auth': ('outputs', 'data', 'default_authorization_type'),
    'files': ('outputs', 'storage', 'bucket_name'),
    'notifications': ('external', 'notification_endpoint'),
}
DESTINATIONS = {'user_pool', 'user_pool_client', 'data', 'files', 'notifications'}


def value(record, path):
    current = record
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current if isinstance(current, str) and current.strip() else None


def audit(bundles, approved):
    """Return observations; exact matches remain only matches to supplied policy."""
    mismatches = []
    sharing = []
    if set(bundles) != set(approved):
        mismatches.append({'scope': 'inventory', 'reason': 'bundle and policy names differ'})
    names = sorted(set(bundles) & set(approved))
    for name in names:
        bundle = bundles[name]
        version = value(bundle, ('outputs', 'version'))
        if version is None or re.fullmatch(r'1(?:\.[0-9]+)?', version) is None:
            mismatches.append({'scope': name, 'reason': 'missing or unsupported outputs version'})
        for component, path in PATHS.items():
            actual = value(bundle, path)
            expected = approved[name].get(component)
            if not actual or not expected or actual != expected:
                mismatches.append({'scope': name, 'component': component,
                                   'reason': ('missing or different destination' if component in DESTINATIONS
                                              else 'missing or different setting')})
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            for component in sorted(DESTINATIONS):
                path = PATHS[component]
                left_value, right_value = value(bundles[left], path), value(bundles[right], path)
                if left_value and left_value == right_value:
                    permitted = approved[left].get(component) == approved[right].get(component) == left_value
                    sharing.append({'frontends': [left, right], 'component': component,
                                    'kind': 'declared_shared' if permitted else 'unexpected_shared'})
                    if not permitted:
                        mismatches.append({'scope': f'{left}/{right}', 'component': component,
                                           'reason': 'unexpected shared destination'})
    return {'result': 'checked_fields_match_supplied_plan' if not mismatches else 'review_required',
            'mismatches': mismatches, 'sharing': sharing,
            'scope': 'fictional config comparison only; no effective access or live resource check'}


def fixture():
    practice = {
        'frontend_url': 'https://practice.example.invalid',
        'outputs': {'version': '1.5',
                    'auth': {'aws_region': 'us-east-2', 'user_pool_id': 'us-east-2_practiceFixture',
                             'user_pool_client_id': 'practiceClient'},
                    'data': {'aws_region': 'us-east-2', 'url': 'https://practice.example.invalid/graphql',
                             'default_authorization_type': 'AMAZON_COGNITO_USER_POOLS',
                             'authorization_types': ['AMAZON_COGNITO_USER_POOLS']},
                    'storage': {'aws_region': 'us-east-2', 'bucket_name': 'fixture-practice-files'}},
        'external': {'notification_endpoint': 'practice-inbox-fixture'},
    }
    live = deepcopy(practice)
    live['frontend_url'] = 'https://live.example.invalid'
    live['outputs']['auth']['user_pool_id'] = 'us-east-2_liveFixture'
    live['outputs']['auth']['user_pool_client_id'] = 'liveClient'
    live['outputs']['data']['url'] = 'https://live.example.invalid/graphql'
    live['outputs']['storage']['bucket_name'] = 'fixture-live-files'
    live['external']['notification_endpoint'] = 'live-sender-fixture'
    preview = deepcopy(practice)
    preview['frontend_url'] = 'https://preview.example.invalid'
    bundles = {'practice': practice, 'live': live, 'preview': preview}
    approved = {name: {component: value(bundle, path) for component, path in PATHS.items()}
                for name, bundle in bundles.items()}
    return bundles, approved


def run():
    bundles, approved = fixture()
    baseline = audit(bundles, approved)
    assert baseline['result'] == 'checked_fields_match_supplied_plan'
    assert any(s['frontends'] == ['practice', 'preview'] and s['kind'] == 'declared_shared'
               for s in baseline['sharing'])
    print('Preview explicitly shares practice; it is not an isolated backend.')

    copied = deepcopy(bundles)
    copied['practice']['outputs'] = deepcopy(bundles['live']['outputs'])
    copied['practice']['external'] = deepcopy(bundles['live']['external'])
    result = audit(copied, approved)
    assert result['result'] == 'review_required'
    assert {m.get('component') for m in result['mismatches']} >= DESTINATIONS
    print('A practice URL with copied live destinations fails the checked boundaries.')

    mixed = deepcopy(bundles)
    mixed['practice']['outputs']['data']['url'] = bundles['live']['outputs']['data']['url']
    result = audit(mixed, approved)
    assert result['result'] == 'review_required'
    assert any(m.get('component') == 'data' for m in result['mismatches'])
    print('A mixed bundle fails even though its sign-in and file destinations remain practice.')
    print(json.dumps({'baseline': baseline['result'], 'copied': audit(copied, approved)['result'],
                      'mixed': result['result']}, sort_keys=True))


if __name__ == '__main__':
    import sys
    if sys.flags.optimize:
        raise SystemExit('Run without Python optimization; this drill uses assertions.')
    run()
