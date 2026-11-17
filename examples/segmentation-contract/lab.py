"""Small fictional traffic-contract checker. It makes no network or AWS calls."""
import argparse
import copy
import json
from pathlib import Path

DEFAULT = Path(__file__).with_name('topology.json')
INTERNAL = {'alb', 'app', 'db', 'worker'}


def triples(rows):
    return {tuple(row) for row in rows}


def explain(topology, flow):
    source, destination, port = flow
    reasons = []
    routes = triples(topology['routes'])
    candidate_routes = {via for src, dst, via in routes if src == source and dst == destination}
    if not candidate_routes:
        reasons.append('route')
    if source != 'browser' and (source, destination, port) not in triples(topology['egress']):
        reasons.append('source-egress')
    if destination in INTERNAL and (source, destination, port) not in triples(topology['ingress']):
        reasons.append('destination-ingress')
    if source in INTERNAL and (source, destination, port) not in triples(topology['nacl_forward']):
        reasons.append('subnet-forward')
    if source in INTERNAL and (destination, source) not in triples(topology['nacl_reply']):
        reasons.append('subnet-reply')
    if destination == 's3':
        if 'gateway-endpoint' not in candidate_routes:
            reasons.append('s3-gateway-route')
        for gate in ('endpoint_policy', 'identity_permission', 'bucket_permission'):
            if (source, destination) not in triples(topology[gate]):
                reasons.append(gate.replace('_', '-'))
    if destination == 'supplier' and 'nat' not in candidate_routes:
        reasons.append('supplier-egress-route')
    return reasons


def audit(topology):
    required = {tuple(flow): explain(topology, flow) for flow in topology['required']}
    forbidden = {tuple(flow): explain(topology, flow) for flow in topology['forbidden']}
    passed = all(not reasons for reasons in required.values()) and all(reasons for reasons in forbidden.values())
    return {'passed': passed,
            'required': {'->'.join(map(str, key)): value for key, value in required.items()},
            'forbidden': {'->'.join(map(str, key)): value for key, value in forbidden.items()}}


def demonstration(topology):
    cases = {}
    cases['baseline'] = audit(topology)
    no_nat = copy.deepcopy(topology)
    no_nat['routes'] = [r for r in no_nat['routes'] if r != ['worker', 'supplier', 'nat']]
    cases['remove_supplier_route'] = audit(no_nat)
    no_reply = copy.deepcopy(topology)
    no_reply['nacl_reply'].remove(['db', 'app'])
    cases['remove_db_reply'] = audit(no_reply)
    no_policy = copy.deepcopy(topology)
    no_policy['endpoint_policy'].remove(['worker', 's3'])
    cases['remove_s3_endpoint_permission'] = audit(no_policy)
    no_identity = copy.deepcopy(topology)
    no_identity['identity_permission'].remove(['worker', 's3'])
    cases['remove_s3_identity_permission'] = audit(no_identity)
    no_bucket = copy.deepcopy(topology)
    no_bucket['bucket_permission'].remove(['worker', 's3'])
    cases['remove_s3_bucket_permission'] = audit(no_bucket)
    broad = copy.deepcopy(topology)
    broad['egress'].append(['worker', 'db', 5432])
    broad['ingress'].append(['worker', 'db', 5432])
    cases['open_worker_to_db'] = audit(broad)
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, default=DEFAULT)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    topology = json.loads(args.fixture.read_text())
    cases = demonstration(topology)
    if args.json:
        print(json.dumps(cases, indent=2))
    else:
        for name, result in cases.items():
            print(name, 'PASS' if result['passed'] else 'EXPECTED FAILURE')
            if name != 'baseline':
                print('  rejected gates:', {key: gates for key, gates in result['required'].items() if gates},
                      'unwanted openings:', {key: gates for key, gates in result['forbidden'].items() if not gates})
    if not cases['baseline']['passed'] or any(cases[name]['passed'] for name in cases if name != 'baseline'):
        raise SystemExit('Contract check failed: baseline or a negative control has the wrong result')
    print('PASS: local contract mutations exposed; no AWS or external network calls')


if __name__ == '__main__':
    main()
