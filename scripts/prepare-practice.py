"""Copy application source to an isolated local practice folder; creates no AWS resources."""
from pathlib import Path
import shutil
base = Path(__file__).resolve().parents[1]
target = base / 'practice/advanced'
if target.exists():
    raise SystemExit('Practice directory already exists; preserve your work or choose a fresh copy manually.')
shutil.copytree(base / 'app', target, ignore=shutil.ignore_patterns('node_modules', '.amplify', 'dist', 'amplify_outputs.json', '.env*'))
print(f'Copied source to {target}. No cloud deployment was performed.')
