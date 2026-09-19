#!/usr/bin/env python3
"""Install a local, opt-in LaunchAgent; never includes credentials in files."""
import datetime
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

from sync import REMOTE, validate

repo = Path(__file__).resolve().parent.parent
validate(repo)
origin = subprocess.check_output(['git', '-C', str(repo), 'remote', 'get-url', 'origin'], text=True).strip()
if origin != REMOTE:
    sys.exit('Unexpected repository origin; not installing.')
if sys.platform != 'darwin':
    sys.exit('This installer requires macOS.')
gh = shutil.which('gh')
if not gh:
    sys.exit('Install GitHub CLI first: brew install gh')
login = subprocess.check_output([gh, 'api', 'user', '--jq', '.login'], text=True).strip()
if login != 'RoberGao-hub':
    sys.exit('Log in as RoberGao-hub before enabling maintainer synchronization.')
subprocess.run([gh, 'auth', 'setup-git', '--hostname', 'github.com'], check=True)
for field, value in [('user.name', login), ('user.email', '325624277+RoberGao-hub@users.noreply.github.com')]:
    if subprocess.run(['git', '-C', str(repo), 'config', '--get', field], capture_output=True).returncode:
        subprocess.run(['git', '-C', str(repo), 'config', '--local', field, value], check=True)
app = Path.home() / 'Library/Application Support/AI Narrative Sync'
app.mkdir(parents=True, exist_ok=True)
label = 'org.robergao.ai-narrative-sync'
plist = Path.home() / 'Library/LaunchAgents' / (label + '.plist')
plist.parent.mkdir(parents=True, exist_ok=True)
domain = 'gui/' + str(os.getuid())
subprocess.run(['launchctl', 'bootout', domain + '/' + label], capture_output=True)
shutil.copy2(repo / 'tools/sync.py', app / 'sync.py')
skill = Path.home() / '.codex/skills/ai-narrative-analysis'
skill.parent.mkdir(parents=True, exist_ok=True)
if skill.is_symlink() and skill.resolve() == repo:
    pass
else:
    if skill.exists() or skill.is_symlink():
        backup = app / ('skill-backup-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        skill.rename(backup)
        print('Existing skill backed up:', backup)
    skill.symlink_to(repo, target_is_directory=True)
config = {
    'Label': label,
    'ProgramArguments': [sys.executable, str(app / 'sync.py'), '--repo', str(repo), '--state', str(app)],
    'WorkingDirectory': str(repo), 'RunAtLoad': True, 'StartInterval': 30,
    'EnvironmentVariables': {'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
                             'GIT_TERMINAL_PROMPT': '0'},
    'StandardOutPath': str(app / 'sync.log'), 'StandardErrorPath': str(app / 'errors.log'),
    'ProcessType': 'Background',
}
with plist.open('wb') as f:
    plistlib.dump(config, f)
subprocess.run(['launchctl', 'bootstrap', domain, str(plist)], check=True)
print('Installed 30-second sync. Edits settle for 30 seconds before committing.')
print('Status:', app / 'status.txt')
print('Stop:', 'launchctl bootout ' + domain + '/' + label)
