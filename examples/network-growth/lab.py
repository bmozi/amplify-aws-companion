"""Strict IPv4 address-plan arithmetic; no AWS, DNS, sockets or route changes."""
from ipaddress import IPv4Network
import json


PRIVATE = tuple(IPv4Network(x) for x in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'))


def network(cidr):
    if not isinstance(cidr, str):
        raise ValueError('Supply a canonical private IPv4 CIDR string')
    result = IPv4Network(cidr, strict=True)
    if not 16 <= result.prefixlen <= 28:
        raise ValueError('This exercise supports /16 through /28 only')
    if not any(result.subnet_of(parent) for parent in PRIVATE):
        raise ValueError('This exercise supports RFC 1918 ranges only; no BYOIP')
    return result


def available(cidr):
    return network(cidr).num_addresses - 5


def validate_plan(parent_cidr, subnet_cidrs):
    parent = network(parent_cidr)
    if not subnet_cidrs:
        raise ValueError('At least one subnet is required')
    subnets = [network(cidr) for cidr in subnet_cidrs]
    for index, subnet in enumerate(subnets):
        if not subnet.subnet_of(parent):
            raise ValueError('Subnet is outside the parent range')
        if any(subnet.overlaps(other) for other in subnets[:index]):
            raise ValueError('Subnet ranges overlap')
    # Address-space remaining, not usable addresses in hypothetical future subnets.
    return parent.num_addresses - sum(subnet.num_addresses for subnet in subnets)


def assess(cidr, *, active, replacement, fixed, reserve):
    counts = (active, replacement, fixed, reserve)
    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError('Address demands must be nonnegative integers, not instance counts')
    usable = available(cidr)
    occupied = active + replacement + fixed
    return {'usable': usable, 'occupied': occupied,
            'free_after_occupancy': usable - occupied,
            'required_reserve': reserve,
            'margin_after_reserve': usable - occupied - reserve,
            'fits': occupied + reserve <= usable}


def must_reject(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError('Invalid plan or demand was accepted')


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    assert available('10.20.0.0/28') == 11
    assert available('10.20.0.0/25') == 123
    assert available('10.20.0.0/24') == 251
    assert validate_plan('10.20.0.0/24', ['10.20.0.0/25', '10.20.0.128/25']) == 0
    assert available('10.20.0.0/25') + available('10.20.0.128/25') == 246
    assert validate_plan('10.20.0.0/23', ['10.20.0.0/25', '10.20.0.128/25']) == 256
    cidr = '10.20.0.0/25'
    normal = assess(cidr, active=50, replacement=0, fixed=20, reserve=10)
    deploy = assess(cidr, active=50, replacement=50, fixed=20, reserve=10)
    recovery = assess(cidr, active=100, replacement=0, fixed=20, reserve=10)
    overlap = assess(cidr, active=100, replacement=50, fixed=20, reserve=10)
    assert (normal['free_after_occupancy'], normal['margin_after_reserve'], normal['fits']) == (53, 43, True)
    assert (deploy['free_after_occupancy'], deploy['margin_after_reserve'], deploy['fits']) == (3, -7, False)
    assert recovery == deploy  # different causes; same fictional address demand
    assert (overlap['free_after_occupancy'], overlap['margin_after_reserve'], overlap['fits']) == (-47, -57, False)
    assert assess(cidr, active=103, replacement=0, fixed=10, reserve=10)['fits']
    assert not assess(cidr, active=104, replacement=0, fixed=10, reserve=10)['fits']
    assert assess('10.20.0.0/24', active=100, replacement=50, fixed=20, reserve=10)['margin_after_reserve'] == 71
    for operation in [
        lambda: available('10.20.0.1/25'),  # reject silent normalization
        lambda: available('2001:db8::/64'),
        lambda: available('10.20.0.0/29'),
        lambda: available('8.8.0.0/16'),
        lambda: validate_plan('10.20.0.0/24', []),
        lambda: validate_plan('10.20.0.0/24', ['10.20.1.0/25']),
        lambda: validate_plan('10.20.0.0/24', ['10.20.0.0/25', '10.20.0.64/26']),
        lambda: validate_plan('10.20.0.0/24', ['10.20.0.0/25', '10.20.0.0/25']),
        lambda: assess(cidr, active=-1, replacement=0, fixed=0, reserve=0),
        lambda: assess(cidr, active=True, replacement=0, fixed=0, reserve=0),
        lambda: assess(cidr, active=1.5, replacement=0, fixed=0, reserve=0),
    ]:
        must_reject(operation)
    print(json.dumps({'normal': normal, 'deployment_overlap': deploy,
                      'zone_recovery': recovery, 'recovery_during_deployment': overlap,
                      'scope': 'Fictional private IPv4 address arithmetic only; no AWS allocation, service limits, performance or cost verification'}, indent=2))


if __name__ == '__main__':
    main()
