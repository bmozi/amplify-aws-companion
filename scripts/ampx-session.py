"""Run ampx in a named practice workspace with the existing refreshable account guard."""

raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')

import argparse
from pathlib import Path
import subprocess
from aws_session import session_environment
parser = argparse.ArgumentParser()
parser.add_argument('--app-dir', required=True)
parser.add_argument('command', nargs=argparse.REMAINDER)
args = parser.parse_args()
workspace = Path(args.app_dir).resolve()
base = Path(__file__).resolve().parents[1]
if workspace == base / 'app' or not (workspace / 'amplify/backend.ts').is_file():
    parser.error('Select a practice app containing amplify/backend.ts, not the live app directory.')
if not args.command or args.command[0] != 'sandbox':
    parser.error('This teaching helper accepts sandbox commands only.')
if not (workspace / 'node_modules/.bin/ampx').exists():
    parser.error('Install the practice app dependencies with npm ci first.')
with session_environment() as env:
    raise SystemExit(subprocess.run([str(workspace / 'node_modules/.bin/ampx'), *args.command], cwd=workspace, env=env).returncode)
