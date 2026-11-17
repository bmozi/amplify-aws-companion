"""Run Terraform with refreshable short-lived AWS credentials."""

raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')

import subprocess,sys
from aws_session import session_environment
with session_environment() as env:
 raise SystemExit(subprocess.run(['terraform',*sys.argv[1:]],env=env).returncode)
