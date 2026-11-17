import importlib.util
from pathlib import Path
from datetime import datetime,timedelta,timezone
from decimal import Decimal
import unittest
spec=importlib.util.spec_from_file_location('credit',Path(__file__).resolve().parents[3]/'scripts/credit-check.py')
credit=importlib.util.module_from_spec(spec);spec.loader.exec_module(credit)
run_spec=importlib.util.spec_from_file_location('runner',Path(__file__).resolve().parents[1]/'run.py')
runner=importlib.util.module_from_spec(run_spec);run_spec.loader.exec_module(runner)
class CreditTests(unittest.TestCase):
    now=datetime(2026,10,18,tzinfo=timezone.utc)
    end=now+timedelta(hours=2)
    def state(self):return {'accountPlanType':'FREE','accountPlanStatus':'ACTIVE','accountPlanRemainingCredits':{'amount':'148.8','unit':'USD'},'accountPlanExpirationDate':'2027-03-21T18:57:53Z'}
    def test_preserves_reserve(self):
        r=credit.assess(self.state(),Decimal('100'),Decimal('5'),self.now,self.end)
        self.assertEqual(r['decision'],'within_credit_policy');self.assertEqual(Decimal(r['headroom_after_estimate_usd']),Decimal('43.8'))
        self.assertEqual(r['planned_lab_end'],self.end.isoformat())
    def test_limits_and_expiry(self):
        for reserve,estimate in [('145','5'),('100','6')]:self.assertEqual(credit.assess(self.state(),Decimal(reserve),Decimal(estimate),self.now,self.end)['decision'],'review_required')
        s=self.state();s['accountPlanExpirationDate']='2026-01-01T00:00:00Z'
        self.assertEqual(credit.assess(s,Decimal('100'),Decimal('1'),self.now,self.end)['decision'],'review_required')
        s['accountPlanExpirationDate']=(self.now+timedelta(hours=1)).isoformat()
        self.assertIn('Free plan expires before the planned lab end',credit.assess(s,Decimal('100'),Decimal('1'),self.now,self.end)['reasons'])
        self.assertIn('A live estimate needs a planned lab end',credit.assess(self.state(),Decimal('100'),Decimal('1'),self.now)['reasons'])
    def test_missing_credit_or_invalid_input_fails(self):
        s=self.state();s['accountPlanRemainingCredits']={}
        with self.assertRaises(ValueError):credit.assess(s,Decimal('100'),Decimal('1'),self.now,self.end)
        with self.assertRaises(ValueError):credit.assess(self.state(),Decimal('100'),Decimal('NaN'),self.now,self.end)
        with self.assertRaises(ValueError):credit.assess(self.state(),Decimal('99'),Decimal('1'),self.now,self.end)
        with self.assertRaises(ValueError):credit.assess(self.state(),Decimal('100'),Decimal('1'),self.now,self.now)
        self.assertEqual(credit.assess(self.state(),Decimal('100'),Decimal('0'),self.now)['decision'],'within_credit_policy')
    def test_paid_plan_requires_review(self):
        s=self.state();s['accountPlanType']='PAID'
        self.assertEqual(credit.assess(s,Decimal('100'),Decimal('1'),self.now,self.end)['decision'],'review_required')
    def test_runner_rejects_budget_above_five_and_bad_expiry(self):
        config={'estimated_run_cost_usd':5,'approved_run_budget_usd':5,'expires_at_epoch':7200}
        runner.validate_live_parameters(config,0)
        for change in ({'approved_run_budget_usd':10},{'estimated_run_cost_usd':0},
                       {'estimated_run_cost_usd':6,'approved_run_budget_usd':6},
                       {'expires_at_epoch':7201},{'expires_at_epoch':0}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                runner.validate_live_parameters(dict(config,**change),0)
