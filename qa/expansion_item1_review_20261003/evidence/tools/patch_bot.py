"""Apply the same fail-fast stall detector to the scratch copies of the full-operation bot (never the repository)."""
import sys, io
from pathlib import Path
root = Path('.cache/claude_scratch')
OLD = "            active.debug_drive(nav.direction(active,goal,1.0/60.0) if offset.length() > 50.0 else Vector2.ZERO, Vector2.RIGHT)\n"
NEW = ("            var nav_dir := nav.direction(active,goal,1.0/60.0) if offset.length() > 50.0 else Vector2.ZERO\n"
       "            if offset.length() > 50.0 and nav_dir.length_squared() < 0.0001:\n"
       "                zero_nav_ticks += 1\n"
       "                if zero_nav_ticks == 300:\n"
       "                    print(\"NAV_ZERO_STALL tick=%d step=%d pos=%s goal=%s\" % [frame, stage.current_step, active.global_position, goal])\n"
       "                    break\n"
       "            else:\n"
       "                zero_nav_ticks = 0\n"
       "            active.debug_drive(nav_dir,Vector2.RIGHT)\n")
DECL_OLD = "var returned_from_branch := [false, false]\n"
DECL_NEW = DECL_OLD + "var zero_nav_ticks := 0\n"
for proj in ('proj_base', 'proj_after'):
    p = root / proj / 'tests' / 'smoke' / 'site7_full_operation_smoke.gd'
    t = p.read_bytes().decode('utf-8')
    if 'zero_nav_ticks' in t: print(proj, 'already patched'); continue
    assert OLD in t and DECL_OLD in t, proj
    t = t.replace(OLD, NEW, 1).replace(DECL_OLD, DECL_NEW, 1)
    p.write_bytes(t.encode('utf-8'))
    print(proj, 'patched')
