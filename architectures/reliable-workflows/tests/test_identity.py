import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('runner',Path(__file__).resolve().parents[1]/'run.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

class IdentityTests(unittest.TestCase):
    account='123456789012'
    def test_expected_assumed_role(self):
        runner.require_deployment_role({'Account':self.account,'Arn':f'arn:aws:sts::{self.account}:assumed-role/lab-deployer/session'},self.account)
    def test_root_and_user_rejected(self):
        for resource in ['root','user/lab']:
            with self.assertRaises(ValueError):
                runner.require_deployment_role({'Account':self.account,'Arn':f'arn:aws:iam::{self.account}:{resource}'},self.account)
    def test_wrong_account_or_missing_identity_rejected(self):
        for identity in [{},{'Account':'000000000000','Arn':f'arn:aws:sts::{self.account}:assumed-role/lab/session'},{'Account':self.account}]:
            with self.assertRaises(ValueError):runner.require_deployment_role(identity,self.account)
    def test_forged_or_malformed_arn_rejected(self):
        for arn in [f'arn:aws:sts::000000000000:assumed-role/lab/session',f'arn:aws:sts::{self.account}:assumed-role/lab/',f'arn:aws:sts::{self.account}:assumed-role/lab/session/extra']:
            with self.assertRaises(ValueError):runner.require_deployment_role({'Account':self.account,'Arn':arn},self.account)
