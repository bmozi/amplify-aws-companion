"""Offline CIDR governance rehearsal, not an AWS IPAM or route evaluator."""

from ipaddress import IPv4Network
import json


def cidr(value):
    if not isinstance(value, str):
        raise ValueError('CIDR must be a string')
    result = IPv4Network(value, strict=True)
    if not result.subnet_of(IPv4Network('10.0.0.0/8')):
        raise ValueError('This fictional exercise uses 10/8 only')
    return result


def review(request, records, pool):
    """Hold a proposal on a known conflict; never claim an AWS allocation."""
    proposal = cidr(request['cidr'])
    parent = cidr(pool['cidr'])
    if not proposal.subnet_of(parent):
        return {'decision': 'HOLD', 'reason': 'outside the selected pool'}
    if request['region'] != pool['locale']:
        return {'decision': 'HOLD', 'reason': 'pool locale differs from request Region'}
    if request['tags'].get('Environment') != pool['required_environment']:
        return {'decision': 'HOLD', 'reason': 'required Environment tag is absent or different'}
    if not pool['min_prefix'] <= proposal.prefixlen <= pool['max_prefix']:
        return {'decision': 'HOLD', 'reason': 'requested size violates the pool rule'}

    conflicts = []
    for record in records:
        existing = cidr(record['cidr'])
        # A distinct scope is a possible separate routing domain, not proof of one.
        if proposal.overlaps(existing) and record['scope'] == request['scope']:
            conflicts.append({'name': record['name'], 'state': record['state']})
    if conflicts:
        return {'decision': 'HOLD', 'reason': 'overlap in the proposed routing scope',
                'conflicts': conflicts}
    if any(cidr(record['cidr']).overlaps(proposal) for record in records):
        if not request.get('disconnected_domain_evidence', False):
            return {'decision': 'HOLD', 'reason': 'other-scope overlap needs isolation evidence'}
    return {'decision': 'REVIEW_WITH_IPAM_AND_ROUTE_EVIDENCE',
            'reason': 'paper rules fit; allocation, discovery, routes and access remain unobserved'}


POOL = {'cidr': '10.20.0.0/16', 'locale': 'us-west-2',
        'required_environment': 'prod', 'min_prefix': 24, 'max_prefix': 24}
RECORDS = [
    {'name': 'repair-vpc', 'cidr': '10.20.0.0/24', 'scope': 'connected', 'state': 'managed'},
    {'name': 'legacy-vpc', 'cidr': '10.20.4.0/24', 'scope': 'connected', 'state': 'unmanaged'},
    {'name': 'paused-review', 'cidr': '10.20.6.0/24', 'scope': 'connected', 'state': 'ignored'},
    {'name': 'isolated-training', 'cidr': '10.20.8.0/24', 'scope': 'isolated', 'state': 'managed'},
]


def proposal(value, **changes):
    item = {'cidr': value, 'region': 'us-west-2',
            'tags': {'Environment': 'prod'}, 'scope': 'connected'}
    item.update(changes)
    return item


def main():
    cases = {
        'overlap_managed': proposal('10.20.0.0/24'),
        'overlap_unmanaged': proposal('10.20.4.0/24'),
        'overlap_ignored': proposal('10.20.6.0/24'),
        'wrong_region': proposal('10.20.2.0/24', region='us-east-1'),
        'different_scope_unknown': proposal('10.20.8.0/24'),
        'different_scope_evidenced': proposal('10.20.8.0/24', disconnected_domain_evidence=True),
        'clear_paper': proposal('10.20.2.0/24'),
    }
    for name, item in cases.items():
        print(json.dumps({'case': name, **review(item, RECORDS, POOL)}))


if __name__ == '__main__':
    main()
