"""Claude review helper (N-1 re-check): did Codex's 89d30934 keep the old reference planner verbatim and delete no check?

usage: ref_fidelity_check.py [old rev] [new rev]     (run from the project root; default 4f86d3af 89d30934)
1. the old ref_clear_ground / ref_plan of the old revision, with the names ref_old_ put in front, equal the new revision's
   ref_old_clear_ground / ref_old_plan character for character;
2. every check line of the old revision is still in the new one (C-05: nothing deleted, nothing weakened);
3. which production symbols the NEW reference planner reads (it must not call the planner it checks).
"""
import re
import subprocess
import sys

OLD = sys.argv[1] if len(sys.argv) > 1 else '4f86d3af'
NEW = sys.argv[2] if len(sys.argv) > 2 else '89d30934'
PATH = 'tests/smoke/combat_query_fastpath_smoke.gd'


def show(rev):
    return subprocess.run(['git', 'show', '%s:%s' % (rev, PATH)], capture_output=True, check=True).stdout.decode('utf-8').replace('\r\n', '\n')


def grab(text, start_pat, end_pat):
    s = text.index(start_pat)
    return text[s:text.index(end_pat, s + len(start_pat))]


old, new = show(OLD), show(NEW)
old_block = grab(old, 'static func ref_clear_ground(', '\n\n') + '\n\n' + old[old.index('## The planner before the graph cache'):]
new_a = grab(new, 'static func ref_old_clear_ground(', '\n\n')
new_b = new[new.index('## The planner before the graph cache'):new.index('# --- reference planner with N-1 rules')]
renamed_old = old_block.replace('ref_clear_ground', 'ref_old_clear_ground').replace('ref_plan', 'ref_old_plan').strip()
renamed_new = (new_a + '\n\n' + new_b).strip()
print('1. old reference bodies (renamed) equal the new ref_old_* bodies:', renamed_old == renamed_new)


def checks(text):
    return [ln.strip() for ln in text.splitlines() if '_same(' in ln or '_check(' in ln or 'failures.append' in ln]


oc, nc = checks(old), checks(new)
missing = [ln for ln in oc if ln not in nc]
added = [ln for ln in nc if ln not in oc]
print('2. check lines: %d in %s, %d in %s; missing now: %d; new: %d' % (len(oc), OLD, len(nc), NEW, len(missing), len(added)))
for ln in missing:
    print('   MISSING:', ln)
for ln in added:
    print('   +', ln[:160])
block = new[new.index('# --- reference planner with N-1 rules'):]
print('3. production symbols read by the new reference planner:', sorted(set(re.findall(r'\bNAV\.[A-Za-z_]+', block))))
print('   production planner entry points it calls (must be empty):', sorted(set(re.findall(r'NAV\.(?:_[a-z_]+|direction|ground_obstacles)', block))))
