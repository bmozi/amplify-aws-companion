"""Cloud-free rejection and execution-boundary checks for the Amplify helpers."""
import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from aws_session import require_deployment_role, deployment_profile, session_environment

class DeploymentIdentityTests(unittest.TestCase):
 def setUp(self):
  self.settings=patch.dict(os.environ,{'AWS_LAB_DEPLOY_PROFILE':'approved-profile','AWS_LAB_DEPLOY_ROLE':'lab-deployer'})
  self.settings.start();self.addCleanup(self.settings.stop)
 def test_exact_role(self):
  require_deployment_role({'Account':'111111111111','Arn':'arn:aws:sts::111111111111:assumed-role/lab-deployer/run'})
 def test_reject_other_principals(self):
  for arn in ['arn:aws:iam::111111111111:root','arn:aws:iam::111111111111:user/operator','arn:aws:sts::111111111111:assumed-role/admin/run','arn:aws:sts::000000000000:assumed-role/lab-deployer/run','arn:aws:sts::111111111111:assumed-role/lab-deployer/']:
   with self.subTest(arn=arn),self.assertRaises(RuntimeError):
    require_deployment_role({'Account':'111111111111','Arn':arn})
 def test_no_profile_fallback(self):
  with patch.dict(os.environ,{'AWS_LAB_DEPLOY_PROFILE':''}),self.assertRaises(RuntimeError):deployment_profile()
 def test_missing_identity(self):
  with self.assertRaises(RuntimeError):require_deployment_role({})
 def test_reject_before_environment_yield(self):
  with patch('aws_session.subprocess.check_output',return_value='{"Account":"111111111111","Arn":"arn:aws:iam::111111111111:root"}') as call:
   with self.assertRaises(RuntimeError):
    with session_environment():self.fail('Rejected principal reached deployment environment')
   self.assertIn('approved-profile',call.call_args.args[0])
 def test_role_environment_and_cleanup(self):
  with patch('aws_session.subprocess.check_output',return_value='{"Account":"111111111111","Arn":"arn:aws:sts::111111111111:assumed-role/lab-deployer/run"}'),patch.dict(os.environ,{'AWS_ACCESS_KEY_ID':'synthetic','AWS_SECRET_ACCESS_KEY':'synthetic','AWS_SESSION_TOKEN':'synthetic'}):
   with session_environment() as env:
    config=Path(env['AWS_CONFIG_FILE'])
    self.assertTrue(config.exists())
    self.assertEqual(env['AWS_PROFILE'],'amplify-session')
    self.assertEqual(env['AWS_LAB_DEPLOY_PROFILE'],'approved-profile')
    self.assertNotIn('AWS_ACCESS_KEY_ID',env)
    self.assertNotIn('AWS_SECRET_ACCESS_KEY',env)
    self.assertNotIn('AWS_SESSION_TOKEN',env)
    self.assertNotIn('synthetic',config.read_text())
   self.assertFalse(config.exists())
 def test_frontend_rejects_before_packaging_or_upload(self):
  with patch('subprocess.check_output',return_value='{"Account":"111111111111","Arn":"arn:aws:iam::111111111111:root"}') as call,patch('urllib.request.urlopen') as upload:
   with self.assertRaises(RuntimeError):runpy.run_path(str(Path(__file__).resolve().parents[1]/'deploy-frontend.py'))
   self.assertEqual(call.call_count,1);upload.assert_not_called()

if __name__=='__main__':unittest.main()
