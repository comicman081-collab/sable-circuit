# ASTER — technical fixes complete, visual delivery HOLD

Checkpoint 2026-09-11 14:30 KST. NOT a completed natural-gait delivery.
No real Luna reproduction or deployment. Use the current Motion Studio skill.
Final local preview server: owned PID 8176 on loopback 14821, hidden window,
logs qa/aster_preview_14821.out.log and .err.log. The earlier 14821 process had
already stopped; HTTP 200 and current build bytes were rechecked after restart.
Temporary QA server 14822 was stopped. Viewport override restored. App opening
of the original preview was queued, not claimed as an observed final UI render.
Latest unit results: 27 Node + 23 Python PASS. All 34 current source review
containers pass 1080p decoding/dimensions; these do not override visual HOLD.

## Reproduced failure
User video: C:/Users/AAA/Videos/화면 녹화/화면 녹화 중 2026-09-11 140504.mp4
(native 642x374, 25.267s; diagnostic samples qa/aster/user_video_140504).
At 6.0–6.9s the floor moves but the legs stay fixed; 1.0–2.2s shows old fire
leg deformation. Around 7s the entire pose switches on fire. This is not latency.
The user video is NOT native 1080p quality evidence.

Old build input SHA: 73c47e327c5f37eedba6e599387b6765f8f1aa09d54f66b071d3ec4ddaceb913.
fullBodyFrame returned [5,5,5,5,5,5] for walk/run at phases
[0,.17,.34,.51,.68,.85]: only "move" selected locomotion.
Moving fire also overrode modern clips with the old coherent/move_360_ual_v6
raster-leg warp. Position/shot-only tests missed the visible failure.

## Current development HTML
dist/ASTER_Motion_Studio.html and public/standalone/aster.html now contain the
shared authored MICA route. No legacy fire bundle. Movement and firing use the
same distance phase; stationary fire uses planted idle feet with upper recoil.
Input/aim/speeds and other characters are unchanged.
Prior files remain under qa/package_history/aster and qa/build_previous.
HTML SHA: 724afdc1a93063cf7c7b24461aa4cf8ed79564b44da6d474e8189711d62906ae
Input SHA: 1115270a9f3564e3fffc813058971a1592df9a33515336c1fb5412c940f61ac0

Actual native 1920x1080 browser: 17 held-mouse input + 40 temporal cases PASS.
Reports: qa/aster_combat_v8_browser.json, qa/aster_locomotion_v8_browser.json.
Chords are synthetic DOM physical codes with actual held mouse and live
Actor/WebGL, not physical Windows IME testing. Numeric PASS is not visual PASS.

Native capture: qa/aster_motion_v8_bound.webm with sibling JSON binding actual
video/build/script hashes, real elapsed samples and full cycles/transitions.
Sequentially decoded 1,138 frames, 1920x1080, effective 29.919 fps.
qa/aster/runtime_v8/native_capture_validation.json passes container/decoding
ONLY. Earlier same-build chronological samples are under qa/aster/runtime_v8:
e_walk, SE_walk, S_walk, SW_walk, W_walk, NW_walk, N_walk, NE_walk, E_run,
stationary, transitions.

## Visual HOLD — do not deliver as finished natural gait
Feet now alternate and stationary fire no longer waves the legs, but:
- E/walk/1 and E/walk/4 turn the torso toward camera and shorten the rifle
  compared with the other E sources. Source approvals revoked after runtime.
- NW/walk/2 becomes visibly narrower than adjacent poses. Approval revoked.
- Six discrete authored poses still step visibly. Running reuses walk at faster
  distance cadence as MICA does, NOT separately authored sprint.
- MICA E contact sheet was actually compared: its upper-body continuity is the
  standard, not authority to copy its character art.

53/56 current source slots remain approved. status must return E/walk/1 next.
Current development atlas contains those three HOLD frames; it is a candidate,
not promotion. dist/aster.delivery.json is invalidated to HOLD and the prior
receipt preserved under qa/aster/delivery_history.

Last attempts were rejected and NOT imported:
aster_E_pair1_v8_camera_r2 fixes camera but repeats contact-like extended legs;
aster_NW_walk2_v8_proportion_r6 repeats rear heel lift instead of forward passing.
Both exact sources/prompts/tool metadata are retained under
qa/aster/quarantine/gait_v8_rejections. Do not accept attractive isolated images
without a correct phase. Do not continue identical failed prompts blindly.

## Reusable hardening
Renderer regressions cover walk/run/move, fire-phase parity, fixed idle feet,
real Actor at 30/60/120Hz, and legacy bundle exclusion.
40-case temporal QA hashes actual selected lower-body pixels, not file hashes.
Native pair intake/preview preserves source/tool proofs and failed halves.
Delivery requires current input/locomotion reports plus actual video and
capture metadata bound to the exact package and capture script.
A source/runtime rejection invalidates current delivery without deleting history.
Current character skill records actual source failures and verification steps.
None of this claims zero future art failures or an unperformed Luna run.

Next: repair ONLY three rejected sources while keeping opposite-leg roles,
inspect native panels and full chronological cycles, rebuild/package and repeat
57 browser cases + bound native capture. Do not call deliver while visual HOLD
remains. Do not restore the rejected old leg-warp bundle as a shortcut.
