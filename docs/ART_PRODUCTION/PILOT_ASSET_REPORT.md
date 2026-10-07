# SABLE CIRCUIT Pilot Asset Report — V2 Static-Master Hold

## Fixed baseline and scope

`5dbae66` remains the controlling failure baseline: ASTER visual **FAIL**,
pipeline technical QA **PASS**, production expansion **HOLD**. This V2 phase
changes the construction method, not that verdict. ASTER alone is in scope;
ROOK, MICA, every enemy, boss, animation expansion, and gameplay logic remain
untouched.

## Visual authority and construction decision

- Image A reviewed: **YES**, as a render/readability authority only.
- Existing ASTER authority: `data/art_profiles/playable_profiles.json` and
  `assets/characters/playable/aster/aster_master.svg`.
- New final-body route: high-resolution SABLE-owned 2.5D sprite authoring,
  controlled by an identity/render/pose authority pack.
- Retired final-body route: visible low-poly, voxel, clay, manual-mass, or
  generic 3D proxy rendering. These can only be diagnostic pose guides.

The authority pack lives at
`art_src/pilot_v2/aster_v2/static_master/ASTER_STATIC_MASTER_AUTHORITY/`.
It keeps character identity, Image A finish, and positional/depth data from
overruling one another. Source authoring cutouts require uniform `#00FF00`;
runtime exports will remain RGBA.

## Blender and UAL audit

`tools/blender/5.2.1/blender.exe` is a validated Blender 5.2.1 LTS Portable
installation. It imports both existing free Standard UAL GLBs in headless
mode. UAL1 provides the selected ASTER references: `Idle_Loop`, `Walk_Loop`,
`Jog_Fwd_Loop`, `Pistol_Aim_Neutral`, `Pistol_Shoot`, `Pistol_Reload`, and
`Hit_Chest`. UAL visual meshes are not promoted.

- UAL1 Standard used: **motion-source validation only**
- UAL2 Standard used: **motion-source validation only**
- Universal Base Characters used: **NO**
- Paid/Pro/Source assets used: **NO**
- Krea-2 used: **NO**

## Actual work and evidence

1. Installed and checksum-recorded the fixed Blender version; retained the
   existing Blender 4.5 installation unchanged.
2. Validated Blender Python, glTF import, UAL armature hierarchy, and action
   inventory.
3. Authored a locked quarter-view ASTER pose/depth guide. It has 2048px RGBA
   and exact-green source versions plus measurable rifle/grip/head/pelvis/foot
   anchors. It is expressly not a combat body.
4. Authored `AUTHORITY_LOCK.json` with hashes and property-scoped authority
   rules.
5. Installed the three licensed official Qwen 2511 local weights in an isolated
   ComfyUI root; verified header/hash/model recognition and an actual local
   technical edit with zero Krea/cloud calls.
6. Ran a bounded ASTER static-edit diagnostic; it did not meet the static
   visual gate. The graph route was closed without a parameter sweep.
7. Purged all rejected low-poly/body experiments, failed image outputs, copied
   inputs, and route-specific scripts. No rejected visual asset remains in
   `assets/`, an atlas, a scene, or a runtime actor.

## Gate result

The Qwen installation and technical image edit are both **PASS**, but the
three-authority Qwen graph failed the ASTER visual test in every permitted
bounded configuration. No unapproved substitution was made. Consequently no
high-quality ASTER static master exists, no animation frames were authored,
no contact sheet can be honestly supplied, and runtime integration is correctly
withheld.

| Unit | Static visual gate | Expansion state |
| --- | --- | --- |
| ASTER | **FAIL** — no approved static master | HOLD |
| Rifle Trooper | NOT STARTED | blocked by ASTER |
| Shield Breacher | NOT STARTED | blocked by ASTER |
| Recon Drone | NOT STARTED | blocked by ASTER |

`SABLE_COMBAT_ASSET_PILOT_GATE: FAIL`

The next allowed operation is a different, approved static-master authoring
route against the lock package. Do not re-open the failed Qwen graph through
prompt, seed, denoise, or reference-slot sweeps. Only a genuine static visual
pass unlocks ASTER Idle/Move/Fire keys and Godot integration.
