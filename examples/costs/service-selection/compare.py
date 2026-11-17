"""Exact arithmetic for the fictional COST 05 teaching case; no AWS calls."""
from decimal import Decimal
import json
from pathlib import Path


def money(value):
    return Decimal(str(value))


def evaluate(case):
    required = {'fixed', 'per_job', 'storage', 'transfer', 'logs', 'ops_hours', 'license'}
    common = case['common']
    if set(common) != {'ops_hourly_rate'}:
        raise ValueError('The operations hourly rate must be explicit')
    output = {}
    for phase in case['phases']:
        months = int(phase['months'])
        jobs = int(phase['jobs_per_month'])
        if months <= 0 or jobs < 0:
            raise ValueError('Months must be positive and jobs cannot be negative')
        totals = {}
        for name, design in case['designs'].items():
            if set(design) != required:
                raise ValueError(f'{name}: missing or extra cost meter')
            rates = {key: money(value) for key, value in design.items()}
            if any(value < 0 for value in rates.values()):
                raise ValueError('Negative cost input')
            monthly = (rates['fixed'] + rates['per_job'] * jobs + rates['storage']
                       + rates['transfer'] + rates['logs']
                       + rates['ops_hours'] * money(common['ops_hourly_rate'])
                       + rates['license'])
            totals[name] = {'monthly': monthly, 'phase': monthly * months}
        output[phase['name']] = totals
    return output


def main():
    case = json.loads((Path(__file__).with_name('fictional-case.json')).read_text())
    results = evaluate(case)
    for phase, designs in results.items():
        print(phase)
        for name, values in designs.items():
            print(f"  {name}: ${values['monthly']:.2f}/month; ${values['phase']:.2f}/phase")
    for name in case['designs']:
        total = sum((phase[name]['phase'] for phase in results.values()), Decimal(0))
        print(f'{name} lifecycle: ${total:.2f}')


if __name__ == '__main__':
    main()
