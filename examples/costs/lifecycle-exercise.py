"""Fictional cost arithmetic: no AWS prices, billing reads, credentials or resources."""
from decimal import Decimal
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('estimator', ROOT / 'scripts/estimate-lab-cost.py')
estimator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(estimator)


def worksheet(hours):
    # All rates and quantities are invented. The date is the fixture authoring date.
    return {'currency':'USD','region':'fictional-teaching-region','checked_date':'2026-10-18',
            'contingency_percent':50,'limitations':['Invented arithmetic; not AWS prices or a deployable estimate'],
            'items':[
                {'name':'Fictional running capacity','quantity':hours,'unit':'hour','usd_per_unit':'0.05','source_url':'https://example.invalid/invented-rate'},
                {'name':'Fictional retained storage','quantity':3,'unit':'day','usd_per_unit':'0.02','source_url':'https://example.invalid/invented-rate'},
                {'name':'Fictional request processing','quantity':500000,'unit':'request','usd_per_unit':'0.0000002','source_url':'https://example.invalid/invented-rate'}]}


def cost_per_outcome(cost, completed):
    amount = Decimal(cost)
    if not amount.is_finite() or amount < 0 or type(completed) is not int or completed < 0:
        raise ValueError('Use nonnegative finite usage cost and an integer completion count')
    return amount / completed if completed else None


def fictional_cost_shapes(completed):
    """Equivalent accepted units; invented rates, not a service pricing model."""
    if type(completed) is not int or completed < 0:
        raise ValueError('Use a nonnegative integer accepted-outcome count')
    return Decimal('40') + Decimal('0.002') * completed, Decimal('0.01') * completed


def compare_outcomes():
    # Fictional comparison periods, not an authorized AWS run or service quote.
    cases = [('baseline','100',1000), ('smaller_bill_fewer_results','70',500),
             ('same_results_less_cost','90',1000), ('growth','180',2000)]
    expected = [Decimal('0.10'),Decimal('0.14'),Decimal('0.09'),Decimal('0.09')]
    for (label,cost,completed),unit_cost in zip(cases,expected):
        actual = cost_per_outcome(cost,completed)
        assert actual == unit_cost
        print(label, 'fictional usage cost=',cost,'completed=',completed,'USD per completion=',actual)
    assert cost_per_outcome('12',0) is None  # no successful work is not zero unit cost
    # OUTCOME-REVIEW changes acceptance: completion alone is insufficient.
    assert cost_per_outcome('72',900) == Decimal('0.08')
    assert cost_per_outcome('72',600) == Decimal('0.12')
    assert cost_per_outcome('72',1200) == Decimal('0.06')
    print('Acceptance fixture: $72 / 900 completed = $0.08; / 600 accepted = $0.12; / 1200 attempts = $0.06')
    for cost,count in [('NaN',1),('Infinity',1),('-1',1),('1',-1),('1',True),('1',1.5)]:
        try:cost_per_outcome(cost,count)
        except ValueError:pass
        else:raise AssertionError('Invalid cost or count accepted')
    # Same work across two invented cost shapes, ignoring service-specific limits.
    fixed, variable, usage_only = Decimal('40'), Decimal('0.002'), Decimal('0.01')
    crossing = fixed / (usage_only-variable)
    assert crossing == 5000
    for count,expected_fixed,expected_usage in [(0,'40','0'),(1000,'42','10'),(5000,'50','50'),(10000,'60','100')]:
        fixed_total, usage_total = fictional_cost_shapes(count)
        assert (fixed_total,usage_total)==(Decimal(expected_fixed),Decimal(expected_usage))
        print('Fictional completed units=',count,'fixed-plus-variable=',fixed_total,'usage-only=',usage_total)
    # Attempts incur work while the denominator counts completed business outcomes.
    total = Decimal('12') + 1500*Decimal('0.01') + Decimal('3')
    assert total == 30 and cost_per_outcome(str(total),1000)==Decimal('0.03')
    assert cost_per_outcome(str(total),1500)==Decimal('0.02')
    print('Retry fixture: 1500 attempts, 1000 completions; cost=',total,
          'per completion=',cost_per_outcome(str(total),1000),'per attempt=',cost_per_outcome(str(total),1500))
    shared = Decimal('30')
    proportional = [shared*900/1000, shared*100/1000]
    equal = [shared/2,shared/2]
    assert proportional == [Decimal('27'),Decimal('3')]
    assert equal == [Decimal('15'),Decimal('15')]
    assert sum(proportional)==sum(equal)==shared
    print('Shared-cost policy comparison: proportional=',proportional,'equal=',equal,'unchanged total=',shared)


def run():
    if sys.flags.optimize:
        raise SystemExit('Run without -O')
    planned = estimator.estimate(worksheet(2))
    forgotten = estimator.estimate(worksheet(72))
    assert Decimal(planned['subtotal_usd']) == Decimal('0.26')
    assert Decimal(planned['with_contingency_usd']) == Decimal('0.39')
    assert Decimal(forgotten['subtotal_usd']) == Decimal('3.76')
    assert Decimal(forgotten['with_contingency_usd']) == Decimal('5.64')
    print('INVENTED RATES: not AWS prices, not current account evidence')
    for label,result in [('2 hours',planned),('72 hours',forgotten)]:
        estimated = Decimal(result['with_contingency_usd'])
        # Learner-owned comparison values from the chapter's invented example.
        after = Decimal('80') - estimated
        within_run = estimated <= Decimal('4')
        preserves_reserve = after >= Decimal('75')
        print(label, 'subtotal=',result['subtotal_usd'],'with 50% contingency=',estimated,
              'fictional remaining credit=',after,'within invented $4 run limit=',within_run,
              'invented $75 reserve preserved=',preserves_reserve)
        assert (within_run,preserves_reserve) == ((True,True) if label=='2 hours' else (False,False))
    wrong = worksheet(2)
    wrong['items'][2]['usd_per_unit'] = '0.20'  # Deliberate per-million/per-request mistake.
    erroneous = estimator.estimate(wrong)
    assert Decimal(erroneous['items'][2]['usd']) == Decimal('100000')
    print('Unit-error control: entering $0.20 per million as $0.20 per request produces $100000 for requests')
    missing = worksheet(2)
    missing['items'][0]['usd_per_unit'] = None
    try:
        estimator.estimate(missing)
    except ValueError:
        print('PASS: missing price rejected')
    else:
        raise AssertionError('Missing price accepted')
    print('PASS: calculations checked; a calculator cannot verify source prices, completeness or enforce a spending cap')
    compare_outcomes()


if __name__ == '__main__':
    run()
