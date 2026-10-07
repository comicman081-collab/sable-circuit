"""Upload a new, large static Site in bounded Git packs without changing its files.

Credentials arrive through stdin, are never saved, and are used per Git command.
This only initializes a previously empty Site branch. Existing content is not reset.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'web_demo'
STATE = SITE / '.sites-runtime'
STATE.mkdir(exist_ok=True)
credential = json.loads(sys.stdin.readline())
token = credential['token']
env = os.environ.copy()
env['GIT_TERMINAL_PROMPT'] = '0'
env['GIT_INDEX_FILE'] = str(STATE / 'upload.index')
auth = ['-c', 'http.extraHeader=Authorization: Bearer ' + token]

def git(*args, authenticated=False, check=True):
    command = ['git', '-c', 'user.name=SABLE CIRCUIT', '-c', 'user.email=sable-demo@local.invalid']
    if authenticated:
        command += auth
    result = subprocess.run(command + list(args), cwd=SITE, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            encoding='utf8', timeout=300)
    output = result.stdout.replace(token, '[redacted]').strip()
    if check and result.returncode:
        print(output, flush=True)
        raise SystemExit(result.returncode)
    return output

desired = git('rev-parse', 'HEAD^{tree}')
remote = git('ls-remote', credential['remote_url'], 'refs/heads/' + credential['branch'], authenticated=True)
progress_path = STATE / 'upload-progress.json'
progress = json.loads(progress_path.read_text()) if progress_path.exists() else None
if '--reconcile-deployed' in sys.argv and progress and remote and remote.split()[0] != progress['parent']:
    # A later ordinary push can supersede an old completed incremental receipt.
    # Reconcile ONLY the exact recorded live commit already in local history.
    deployed = json.loads((ROOT / 'qa/demo_web_20260920/deployment.json').read_text(encoding='utf8'))['source_commit']
    if remote.split()[0] != deployed:
        raise SystemExit('Remote does not match the recorded deployment; refusing reconciliation.')
    git('merge-base', '--is-ancestor', deployed, 'HEAD')
    progress = {'tree':git('rev-parse', deployed+'^{tree}'), 'parent':deployed,
                'uploaded':git('ls-tree','-r','--name-only',deployed).splitlines()}
    progress_path.write_text(json.dumps(progress, indent=2), encoding='utf8')
if progress and progress['tree'] != desired:
    if (not remote or remote.split()[0] != progress['parent']
            or git('rev-parse', progress['parent'] + '^{tree}') != progress['tree']):
        raise SystemExit('Previous upload incomplete or remote changed; reconcile before updating.')
    git('merge-base', '--is-ancestor', progress['parent'], 'HEAD')
    def entries(ref):
        return {line.split('\t',1)[1]:line.split('\t',1)[0] for line in git('ls-tree','-r',ref).splitlines()}
    before, after = entries(progress['parent']), entries('HEAD')
    git('read-tree', progress['parent'])
    removed = sorted(set(before)-set(after))
    if removed:
        git('update-index', '--force-remove', '--', *removed)
    progress = {'tree':desired, 'parent':progress['parent'],
                'uploaded':[name for name in after if before.get(name)==after[name]], 'removed':removed}
    progress_path.write_text(json.dumps(progress, indent=2), encoding='utf8')
if remote and (not progress or remote.split()[0] != progress['parent']):
    raise SystemExit('Remote branch has unexpected content; refusing to overwrite it.')
if not progress:
    git('read-tree', '--empty')
    progress = {'tree':desired, 'parent':None, 'uploaded':[]}
else:
    git('read-tree', progress['parent'])
    if progress.get('removed'):
        git('update-index', '--force-remove', '--', *progress['removed'])

files = git('ls-tree', '-r', '--name-only', 'HEAD').splitlines()
pending = [name for name in files if name not in progress['uploaded']]
pending.sort(key=lambda name: ((SITE / name).stat().st_size > 1024*1024, name))
batch = []
batches = []
size = 0
for name in pending:
    length = (SITE / name).stat().st_size
    if batch and size + length > 42*1024*1024:
        batches.append(batch)
        batch, size = [], 0
    batch.append(name)
    size += length
if batch:
    batches.append(batch)
for index, batch in enumerate(batches):
    git('add', '--', *batch)
    tree = git('write-tree')
    args = ['commit-tree', tree]
    if progress['parent']:
        args += ['-p', progress['parent']]
    args += ['-m', 'Stage validated SABLE web delivery assets']
    commit = git(*args)
    print('UPLOAD_BATCH', index+1, '/', len(batches), flush=True)
    print(git('push', credential['remote_url'], commit + ':refs/heads/' + credential['branch'], authenticated=True), flush=True)
    progress['parent'] = commit
    progress['uploaded'] += batch
    progress_path.write_text(json.dumps(progress, indent=2), encoding='utf8')
if git('rev-parse', progress['parent'] + '^{tree}') != desired:
    raise SystemExit('Uploaded source tree does not match the validated source.')
old = git('rev-parse', 'HEAD')
git('update-ref', 'refs/heads/codex/pre-upload-state', old)
git('update-ref', 'refs/heads/' + credential['branch'], progress['parent'], old)
print('UPLOAD_COMPLETE', progress['parent'], flush=True)
