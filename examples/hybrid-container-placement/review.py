"""Fictional hybrid placement decisions; no AWS or container runtime calls."""

import json


PLATFORMS = {
    'ecs_anywhere': {'control_plane': 'regional', 'inbound_elb': False},
    'eks_hybrid_nodes': {'control_plane': 'regional', 'inbound_elb': None},
    'eks_anywhere': {'control_plane': 'local', 'inbound_elb': None},
    'eks_outposts_local_cluster': {'control_plane': 'local', 'inbound_elb': None},
}


def review(case):
    """Return a teaching hold or a request for a real disconnected drill."""
    platform = case['platform']
    if platform not in PLATFORMS:
        raise ValueError('Unknown platform; check current service documentation')
    if type(case['required_outage_minutes']) is not int or case['required_outage_minutes'] < 0:
        raise ValueError('Required outage minutes must be a nonnegative integer')
    if case['needs_new_work_while_offline'] and case['required_outage_minutes'] == 0:
        raise ValueError('Offline new-work requirement needs a nonzero outage')

    facts = PLATFORMS[platform]
    if platform == 'ecs_anywhere' and case['expects_aws_elb_for_local_inbound']:
        return {'decision': 'HOLD', 'reason': 'ECS external instances do not support ECS service load balancing'}
    if (case['required_outage_minutes'] and case['needs_new_work_while_offline']
            and facts['control_plane'] == 'regional'):
        return {'decision': 'HOLD', 'reason': 'new work depends on a regional control plane during WAN loss'}
    if case['required_outage_minutes']:
        missing = [name for name in ('local_images', 'local_identity', 'local_data',
                                     'local_ingress', 'local_power') if not case[name]]
        if missing:
            return {'decision': 'HOLD', 'reason': 'offline customer path has a remote or missing dependency',
                    'missing': missing}
    return {'decision': 'REVIEW_WITH_DISCONNECTION_DRILL',
            'reason': 'placement is a candidate; task lifecycle, customer result, recovery and cost are unobserved',
            'control_plane': facts['control_plane']}


def case(platform, **changes):
    result = {'platform': platform, 'required_outage_minutes': 15,
              'needs_new_work_while_offline': True,
              'expects_aws_elb_for_local_inbound': False,
              'local_images': True, 'local_identity': True, 'local_data': True,
              'local_ingress': True, 'local_power': True}
    result.update(changes)
    return result


def main():
    samples = {
        'ecs_new_work': case('ecs_anywhere'),
        'eks_hybrid_new_work': case('eks_hybrid_nodes'),
        'eks_anywhere_local': case('eks_anywhere'),
        'eks_anywhere_remote_image': case('eks_anywhere', local_images=False),
        'eks_anywhere_remote_identity': case('eks_anywhere', local_identity=False),
        'outposts_local_cluster': case('eks_outposts_local_cluster'),
        'ecs_inbound_elb': case('ecs_anywhere', required_outage_minutes=0,
                                needs_new_work_while_offline=False,
                                expects_aws_elb_for_local_inbound=True),
    }
    for name, item in samples.items():
        print(json.dumps({'case': name, **review(item)}))


if __name__ == '__main__':
    main()
