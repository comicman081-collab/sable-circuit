# ASTER UAL V5 locomotion and moving-fire integration

## Status

- Failure baseline `5dbae66`: **VISUAL FAIL / technical QA PASS / production HOLD**. This verdict is unchanged.
- This slice: ASTER-only locomotion, moving-fire composition, and authored muzzle/projectile socket repair.
- Technical runtime gate: **PASS**.
- V5 leg-amplitude visual gate: **FAIL**. Runtime frame/cursor progression passed,
  but user review found the deformation too subtle to read as moving legs at
  gameplay scale. Technical progression is not accepted as visual motion.
- Socket/timing local gate: **PASS** for same-tick sector, immediate flash,
  continuous off-axis aim, and shot-snapshot continuity.
- External ChatGPT visual review: **BLOCKED ON V6 LEG REBUILD**. No commit is
  permitted before the replacement capture and that review.
- Production expansion: **HOLD**.

## Authorities

- Character visual authority remains the existing user-approved ASTER raster identity and costume.
- Motion authority is the installed Quaternius UAL1 FREE Standard `Jog_Fwd_Loop` only.
- Blender 5.2.1 Portable was used headlessly to extract normalized joint curves and timing. No Blender UI control was used.
- No UAL mesh, Universal Base Character, mannequin, base-character pack, paid asset, Krea/Krea2, Photoshop, or cloud generation is present in the runtime output.

The deterministic curve export is:

```text
art_src/pilot_v2/blender/extract_aster_ual1_locomotion_v5.py
art_src/pilot_v2/aster_v2/animation_360/ual_locomotion_v5/ASTER_UAL1_LOCOMOTION_CURVES_V5.json
```

The curve JSON contains 24 samples over the UAL1 loop, 15 normalized joints,
left/right contact windows, root-motion evidence, and idle timing metadata. Its
SHA-256 is:

```text
DBE613C68B9AB40E9667D5772C416DE5EF6A8C36F28AD5AC502F4D2F8163278B
```

Two independent headless exports produced the same hash.

## Runtime assets

### Move V5

```text
assets/units/operators/aster/move_360_ual_v5/{D}/ASTER_MOVE_{D}_360_UAL_V5_ATLAS.webp
```

- Directions: `E, SE, S, SW, W, NW, N, NE`
- Frames: 24 per direction
- Cell: 384 x 384
- Atlas: 384 x 9216 lossless RGBA WebP
- Playback: 24 fps
- Adjacent-frame alpha crossfade: disabled

Top-level manifest:

```text
art_src/pilot_v2/aster_v2/animation_360/move_360_ual_v5/ASTER_MOVE_360_UAL_V5_MANIFEST.json
SHA-256 38f4442df676181c5621cb7883255b435e978ece78de79bd60be3a25bafa5afb
```

The visible ASTER raster is retained; UAL joint curves drive restrained,
direction-projected lower-body motion. The UAL preview mesh is never rendered
or exported.

### Clean Idle V5

```text
assets/units/operators/aster/idle_360_clean_v5/{D}/ASTER_IDLE_{D}_CLEAN_V5_ATLAS.webp
```

- Frames: 4 per direction at 4 fps
- Atlas: 384 x 1536 lossless RGBA WebP
- Manifest SHA-256: `aae7db949870b6362127b2c7ce9bf3c6bab8ace84d483ad2fc8ee69c1930dda8`

The prior idle export contained opaque white/green/purple bands and a detached
black/green foot ring. The clean family was rebuilt from the immutable
exact-green sources and masks. Final numeric QA found zero strong-green chroma
pixels, zero exterior black pixels, and zero full-width band rows. The old
family remains only as the immediate previous comparison and is no longer the
runtime authority.

### Moving-fire composite V5

```text
assets/units/operators/aster/composite_fire_v5/
  move_lower/{D}/ASTER_MOVE_{D}_LOWER_V5_ATLAS.webp   # 384 x 9216
  idle_lower/{D}/ASTER_IDLE_{D}_LOWER_V5_ATLAS.webp   # 384 x 1536
  fire_upper/{D}/ASTER_FIRE_{D}_UPPER_V5_ATLAS.webp   # 384 x 2304
```

Manifest SHA-256:

```text
685a3c2ebd5003a51b4125163327496e7a07b7cd9b6bf6fb3ac0166e9c2901d4
```

During a moving shot the 24-frame Move lower layer continues advancing while
only the six-frame Fire upper layer is applied. During a stationary shot the
clean Idle lower layer remains active under the same Fire upper sequence. The
complementary masks preserve the rifle/forearm corridor and connected ponytail
with a feathered seam. Sixteen representative composites passed zero black
blob and zero seam-hole checks. Muzzle flash remains a separate runtime VFX;
it is not baked into character frames.

The locomotion cursor is no longer advanced at one fixed rate for every ground
speed. Runtime cadence is scaled from actual velocity against ASTER's walk
speed: half-speed analog movement runs the UAL phase at approximately `0.5x`,
walk at `1.0x`, and faster movement increases the phase proportionally within
a bounded range. Tests also cover moving right while aiming forward, sideways,
and backward; every relative-aim case continues advancing the lower-body phase.

UAL1 and UAL2 Free Standard contain no dedicated tactical strafe/backpedal
cycle. This slice therefore fixes the frozen-leg/skating defect and speed-
cadence mismatch using the approved `Jog_Fwd_Loop` authority; it does not claim
a separately authored strafe/backpedal visual family. Cross-direction lower/
upper raster splicing was explicitly rejected because it creates visible waist
holes and mismatched anatomy. A future dedicated strafe family remains a
polish item rather than being disguised through invalid compositing.

## Socket repair

The visible muzzle flash and projectile birth now query the same direction-
specific authored socket exposed by `AsterV4LocomotionPreview`:

```text
get_authored_muzzle_local_position()
get_authored_muzzle_global_position()
```

`OperatorActor` uses that global position whenever the V5 preview is active,
and preserves the procedural muzzle as a fail-safe when the feature is disabled
or the complete asset set fails atomic promotion.

Aim may change in the same physics tick as fire. `_try_fire()` now synchronizes
`facing_sector` from the authoritative `aim_world` before emitting the fire
event or spawning projectiles. This removes the one-frame stale-sector socket
error that could disconnect the flash and projectile on rapid direction changes.

Muzzle timing is independent from the six-frame body animation. The
`primary_fired` event immediately snapshots shot sector, authored local socket,
and continuous `aim_world` direction, then starts a `0.06 s` runtime-only burst.
The body fire sequence begins on its authored contact frame (`2`) instead of
delaying the flash by two 12 fps pre-fire frames. This is essential because
ASTER's `0.105 s` fire interval is shorter than the old `0.1667 s` delay. The
snapshot also prevents a rapid post-shot aim change from teleporting the live
flash to another weapon pose.

The character raster remains an authored eight-sector asset, but projectile
and muzzle-flash rotation preserve continuous gameplay aim. Off-axis and sector-
boundary tests at eight additional angles verify that flash and projectile are
born at the same authored socket, retain the exact unquantized trajectory, and
do not alter gameplay direction.

## Runtime integration

The production `OperatorActor.tscn` already owns the preview node and the
feature flag remains enabled in `project.godot`. The integration changes only
presentation state and projectile visual origin. Movement speed, fire cadence,
damage, projectile speed/lifetime, collision, targeting, save, progression,
and combat rules are unchanged.

The hit/hurt VFX ownership contract is also unchanged: projectile contact
continues to own `CombatFeedback.spawn_hit(...)`; projectiles never call
`spawn_hurt(...)`.

## QA evidence

Headless runtime smoke:

```powershell
& 'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe' `
  --headless --path . `
  --script res://tests/smoke/aster_v4_locomotion_preview_smoke.gd
```

Result: `ASTER_UAL_V5_LOCOMOTION_PREVIEW_SMOKE: PASS`.

The smoke covers all eight directions and verifies:

- coherent 8 x 24 V5 atomic promotion;
- no adjacent-frame blend sprite;
- clean V5 idle selection;
- lower-body cursor advances throughout a moving shot;
- Fire upper overlay and Move lower layer are both active;
- rapid same-tick aim change and fire resolves the new sector;
- projectile birth equals the visible authored muzzle socket within 0.05 px;
- muzzle flash is visible on the exact shot tick and owns one independent burst
  per rapid-fire event;
- eight off-axis/sector-boundary shots preserve continuous aim and a stable
  shot-time socket snapshot;
- half-speed and full-speed locomotion produce materially different UAL phase
  advance, and relative aim never freezes the legs;
- gameplay movement speed, fire cadence, and collision invariants remain unchanged.

Non-headless production-scene capture:

```powershell
& 'D:\AI 종합 폴더\Godot\4.7.1-standard\Godot_v4.7.1-stable_win64_console.exe' `
  --path . --display-driver windows `
  --rendering-method gl_compatibility --rendering-driver opengl3 `
  --script res://tests/render/aster_ual_v5_moving_fire_capture.gd
```

Result: PASS on Godot 4.7.1 / OpenGL3 / RTX 4070 SUPER.

Evidence:

```text
artifacts/aster_ual_v5_moving_fire_capture/ASTER_UAL_V5_8_DIRECTION_MOVING_FIRE_CONTACT.png
artifacts/aster_ual_v5_moving_fire_capture/ASTER_UAL_V5_8_DIRECTION_SOCKET_BIRTH_CONTACT.png
artifacts/aster_ual_v5_moving_fire_capture/ASTER_UAL_V5_MOVING_FIRE_TEMPORAL_CONTACT.png
artifacts/aster_ual_v5_moving_fire_capture/ASTER_UAL_V5_MOVING_FIRE_EVIDENCE.json
```

All eight same-tick direction changes reported `0.0000 px` projectile/socket
birth error. Every direction selected `move_lower + fire_upper`, and every
lower-body frame advanced during the firing window. Representative progression
was E `2 -> 6 -> 10` and NW `18 -> 22 -> 2` across the loop boundary.

## Interactive review

```text
art_src/pilot_v2/aster_v2/interactive_preview/ASTER_360_INTERACTIVE_AIM_REVIEW.html
```

The review page now consumes the same V5 assets as Godot: clean Idle V5,
24-frame Move V5, and the lower/upper moving-fire composition. Click/touch
selects the nearest eight-way character/socket sector while the pointer itself
remains a continuous aim angle. Flash and projectile are created immediately at
click time from the same `MUZZLE_OFFSETS` snapshot; neither waits for animation
pre-roll. The upper body starts directly on contact frame `2`, can retrigger at
ASTER's `105 ms` cadence, and leaves existing muzzle/projectile bursts alive
independently while the Move lower cursor continues. The 40 V5 atlases plus VFX
references, dimensions, manifest hashes, JavaScript syntax, cadence simulation,
and local HTTP load all pass. HTML SHA-256:

```text
1de397aec88040b3024671cc26ac23fdf9ab8c8f94523b3666bf72e5a8f21771
```

Final external visual review and user review still control promotion. Technical
success alone does not authorize ASTER Pilot PASS or production expansion.
