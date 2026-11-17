"""Synthetic customer-outcome arithmetic. No CloudWatch emulation or network calls."""
from fractions import Fraction
import json


def summarize(windows, target=Fraction(99, 100)):
    if not 0 < target < 1:
        raise ValueError('Target must be between zero and one')
    for total, bad in windows:
        if type(total) is not int or type(bad) is not int or not 0 <= bad <= total:
            raise ValueError('Counts must be integers with 0 <= bad <= total')
    total = sum(t for t, _ in windows)
    bad = sum(b for _, b in windows)
    if not total:
        return {'status': 'no_observations', 'total': 0, 'bad': 0}
    rate = Fraction(bad, total)
    allowance = (1 - target) * total
    return {'status': 'within_target' if rate <= 1 - target else 'outside_target',
            'total': total, 'bad': bad, 'bad_fraction': str(rate),
            'allowed_bad_count': str(allowance),
            'remaining_bad_allowance': str(allowance - bad),
            'budget_consumption_multiple': str(rate / (1 - target))}


def due_outcomes(jobs, now, deadline):
    """Each synthetic job is (accepted time, completion time or None)."""
    if deadline <= 0:raise ValueError('Positive deadline required')
    result={'not_yet_due': 0, 'on_time': 0, 'late_or_missing': 0}
    for accepted, completed in jobs:
        if accepted > now or (completed is not None and not accepted <= completed <= now):
            raise ValueError('Invalid event chronology')
        # Cohort uses accepted jobs whose full allowed completion interval has elapsed.
        if accepted + deadline > now:result['not_yet_due'] += 1
        elif completed is not None and completed <= accepted + deadline:result['on_time'] += 1
        else:result['late_or_missing'] += 1
    return result


def dashboard_mix():
    """Original synthetic acceptance counts; same acceptance rule in both periods."""
    return {'Earlier': {'Web': (90,100), 'Counter': (1,10)},
            'Later': {'Web': (19,20), 'Counter': (20,100)}}


def main():
    if not __debug__:raise SystemExit('Run without Python optimization')
    windows=[(10, 5), (990, 5)]
    combined=summarize(windows)
    assert combined['bad_fraction']=='1/100' and combined['status']=='within_target'
    incorrect_average=(Fraction(5,10)+Fraction(5,990))/2
    assert incorrect_average != Fraction(10,1000)
    breach=summarize([(1000,20)])
    assert breach['budget_consumption_multiple']=='2' and breach['remaining_bad_allowance']=='-10'
    assert summarize([])['status']=='no_observations'
    assert summarize([(0,0)])['status']=='no_observations'
    jobs=[(0,20),(0,40),(0,None),(50,None)]
    cohort=due_outcomes(jobs,now=60,deadline=30)
    assert cohort=={'not_yet_due':1,'on_time':1,'late_or_missing':2}
    invalid_rejected=0
    for invalid in [[(10,11)],[(-1,0)],[(10,-1)],[(True,0)],[(1.5,0)]]:
        try:summarize(invalid)
        except ValueError:invalid_rejected+=1
        else:raise AssertionError('Invalid count accepted')
    try:due_outcomes([(50,20)],60,30)
    except ValueError:invalid_rejected+=1
    else:raise AssertionError('Invalid chronology accepted')
    mix=dashboard_mix()
    rates={period:{channel:Fraction(good,total) for channel,(good,total) in channels.items()}
           for period,channels in mix.items()}
    overall={period:Fraction(sum(g for g,t in channels.values()),sum(t for g,t in channels.values()))
             for period,channels in mix.items()}
    assert rates=={'Earlier':{'Web':Fraction(9,10),'Counter':Fraction(1,10)},
                   'Later':{'Web':Fraction(19,20),'Counter':Fraction(1,5)}}
    assert overall=={'Earlier':Fraction(91,110),'Later':Fraction(13,40)}
    assert all(rates['Later'][c]>rates['Earlier'][c] for c in rates['Earlier'])
    assert overall['Later']<overall['Earlier']
    print(json.dumps({'scope':'synthetic arithmetic, not CloudWatch state or notification testing',
          'weighted_request_outcomes':combined,'incorrect_unweighted_bad_fraction':str(incorrect_average),
          'breach':breach,'completion_cohort':cohort,'invalid_cases_rejected':invalid_rejected,
          'dashboard_mix':mix,'overall_acceptance':{k:str(v) for k,v in overall.items()},
          'interpretation':'Both channel rates improve while the overall rate falls as workload mix changes; no causal proof'},indent=2))

if __name__=='__main__':main()
