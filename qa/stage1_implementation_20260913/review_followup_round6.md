# Narrow SITE-7 NPC facing / reusable skill review

Round5's two named residual counterexamples are closed in the tested scope. Do not
restart that closure audit. The actual reply is retained separately. Continue with
the user-requested concrete NPC-facing correction below while local art work runs.

The user supplied a real game capture: a drone on the right faced down-right while
shooting left toward the squad. Root cause: one front-three-quarter image was used
for all AI aim directions. A spherical omni emitter did NOT solve body facing.
The current candidate now contains eight individually generated1536x1024 yaw
masters and per-view muzzle/root points. A first rear image with four thrusters
and a southwest image with reversed sensor order were rejected/repaired, retained.
The actual game recapture now shows the drone facing left and its left-side magenta
orb toward the squad. This does not prove every angle is artistically perfect.

Code changes: complete8-view intake before publication; no mirrored or2D-rotated
single-image fallback; select visual yaw and its own actual emitter ray together;
initial frame follows actor aim; no new visual target resolution during announced
WINDUP/BURST/LUNGE; recovery can retarget. Candidate yaw evaluation commits only the
selected texture, not8texture changes per tick. The anchored boss remains stationary.
Legacy mock weapons were rotating to world aim THEN being horizontally flipped;
weapon/arm pixels now remain unflipped. Humanoid mock bodies are still temporary.

Actual local Godot4.7.1 tests: enemy_facing_smoke240checks PASS, machine_source_smoke
388checks PASS. They exercise30/60/120Hz,8directions, real emitted object ids, locked
warning/body state, opposite movement/target changes, rejected missing/duplicate
views, actual mock gun transforms and transformed hit bounds. Native real-game
captures are1920x1080. Tests are not visual approval and images are not attached here.
No player source, gait, size, weapon interval or remote deployment changed. New art
is currently QA-candidate only, not an automatically approved app registry update.

Review the actual attached changed code/skill for concrete bugs in target-facing,
one-shot/telegraph ownership and false eight-view acceptance. Provide minimal
reproduction + narrowly scoped fix for confirmed defects; distinguish unverifiable
painted direction/art issues. Do not claim to run Godot or inspect unseen images.
This is not permission to author new art, run Luna, or approve the whole MVP.
