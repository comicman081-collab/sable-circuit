# Optional local VRoid / VRM / Kimodo motion assistance

The user authorized these tools on 2026-09-19 **when they improve the result**.
Keep the current Studio source slots, ImageGen appearance authority, reviewed
players, enemy body-plan limits, gameplay speeds and 1.8x player scale.

The user's later 2026-09-19 instruction cancelled ALL humanoid enemies. Do not
continue this pilot to finish the rifle. Retain it as historical motion research;
future authorized playable-character work may reuse its measured lessons.

## Implemented local pilot, not an approved new production pipeline

`motion_lab_v1/pilots/kimodo_vrm_20260919/` contains a real offline Kimodo run:

- `model_license_manifest.json`: exact installed model/encoder/adapter hashes,
  local license evidence and scope. Only SOMA-RP-v1.1 was used; do not select
  the research-only SMPL-X model. Read every new component's license before use.
- `pilot.py` / `run_owned.py`: one bounded 120-frame, 30Hz candidate. Explicit
  local snapshots, project caches, no network encoder or model download,
  read-only installed inputs. The Python write guard is defense in depth, not
  an OS sandbox. Do not edit installed Kimodo or its weights to make this work.
- `execution.json`, `candidate_raw.npz`, `candidate_raw.bvh`: the actual
  generated motion, not a canned example. Source poses and game registries were
  not changed. Keep this candidate; use a new scoped run directory for new work.
- `motion_review.json` / native 1080p review video: measured geometry. The raw
  pilot alternates stride peaks every 1.1 seconds per leg, but puts the left
  hand behind the right hand. It does **not** satisfy the rifle's right-trigger,
  left-forward-support grip. Do not infer barrel direction from its hand segment.
- `vrm_bone_mapping.json`: 21 mapped SOMA/Seed-san humanoid bones. This is
  mapping only; VRoid was not launched and no skin retarget was completed.
  Seed-san is a licensed rig reference, never SABLE character appearance.

## Apply only the parts demonstrated to help

Use Kimodo for a missing continuous body-motion or path/pose candidate, not to
regenerate an already accepted sprite gait. A generic VRoid avatar does not
automatically become a high-resolution SABLE character. Keep all appearances,
faces, equipment and material detail under the existing source-art authority.

Before admitting a new guide, validate its fixed REST-sole floor, actual
evaluated skin/foot contact, alternating support, cadence and loop seam.
Kimodo toe-joint heights and its own contact flags are proxies, not independent
boot-sole evidence. Never correct the floor per frame to hide a failed retarget.
Bind the right trigger hand, left forward support hand, shoulder stock and
weapon axis to the intended grip; a stable but reversed grip is still a failure.
Raw root constraints are guidance, not proof of exact path/heading compliance.

For VRM retargets, convert Y-up/XZ metre motion to the target's coordinate/rest
frames, map semantic humanoid bones, preserve target bone lengths and evaluate
the skinned soles. A bone-name mapping alone is not retargeting approval.
For comparison, UAL `motion_tracks.json` holds 60 resampled phases over each
action's original frame range: do not interpret its rows as 60 source frames or
compare in-place UAL foot speed to translating Kimodo without a valid root track.

When GPU memory is occupied, leave other processes alone. The tested pilot
encodes the prompt on CPU, releases the large encoder, then runs Kimodo on CPU.
Check free RAM, bound the child, and route TEMP/TMP/HF/Torch caches before launch.
No source swap, model download, paid service, global settings change or extra
generation batch follows automatically from tool availability.

Only a reviewed pose may assist a new source request. Native-alpha source,
whole-cycle, movement/fire and actual-app checks still apply independently.
Do not call this a successful Luna reproduction: this pilot was not a Luna run.
