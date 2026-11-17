"""Prove the local release catches a ready candidate with a wrong invoice."""
import lab

original = lab.business_probe
try:
    # Deliberately remove only the business-result gate; keep readiness intact.
    lab.business_probe = lambda _url, _release: True
    try:
        lab.main()
    except lab.BusinessGateFailure:
        print('Negative control detected that readiness alone promoted a wrong invoice.')
    else:
        raise AssertionError('Negative control failed to expose the missing business gate')
finally:
    lab.business_probe = original
