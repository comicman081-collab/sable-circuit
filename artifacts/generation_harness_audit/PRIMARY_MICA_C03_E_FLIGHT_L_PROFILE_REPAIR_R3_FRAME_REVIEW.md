# Primary visual review — MICA E/run/flight_l profile repair R3

- Reviewer: Codex Astra primary visual review
- Reviewed UTC: 2026-09-07T16:52:30Z
- Exact frame subject: `d2c7a34c8f6e72168ee988647200bb75ef17457d1f8d92d8ad6d73d26dc07e20`
- Exact raw SHA-256: `274d14d3e1fc45718b099447d087404063cdbea09eb3d3f4b1fccdb5857ff82c`
- Exact runtime RGBA SHA-256: `647fb840cb287a4705cd8f2c44563b6333cf8e813f0c91241923b7fa58a1516e`
- Verdict: **HOLD_NOT_PROMOTABLE for this one static frame.**

## Seven exact checks

- `identity_and_costume`: PASS. The face, right-side brown braid, navy patterned long coat, beige piping, teal lining, fitted tactical pants, pouches, protective boots, cyan devices, backpack equipment and long rifle remain recognizably consistent with the approved MICA source. The asymmetric beige vertical right-thigh marker is intact.
- `anatomy_and_limb_count`: PASS. One head, two coherent arms/hands, two distinct legs and two coherent boots are present. No extra limb, merged leg, detached waist, ballooned calf or detached rectangular coat panel is visible.
- `whole_body_direction`: **HOLD**. Face, knees, shin/boot axes, rifle and muzzle read screen-right and the previous 90-degree waist kink is absent, but the visible chest front panel/zipper and pelvis still retain a three-quarter presentation. That does not satisfy the request's stricter ribcage-and-pelvis E profile condition.
- `phase_and_stride`: PASS. The beige-plate anatomical-right leg leads screen-right; the plate-free anatomical-left leg trails screen-left. Both feet are airborne and the horizontal separation is broad enough to read as sprint flight rather than shuffle, march or tap dance.
- `feet_ankles_and_contact`: PASS for the isolated airborne silhouette. Each boot follows its shin with believable pitch; no 90-degree ankle yaw, crossed legs, swollen calves or false planted support is visible. Preceding toe-off and later landing still require temporal sequence evidence.
- `weapon_hands_and_visible_muzzle`: PASS for the static frame. Both hands maintain a coherent grip; the weapon is continuous and one main barrel tip is visibly measurable at screen-right. No projectile or muzzle flash is present in this locomotion frame.
- `matte_edges_and_subject_preservation`: PASS for this derivative pair. The connected-chroma algorithm reproduces the RGBA exactly, retains visible RGB byte-for-byte, leaves all four borders transparent, and independently measurable strong-green residuals at the alpha boundary are zero. The original-scale dark review shows preserved cyan/teal equipment and no visible green halo or large subject deletion.

## Evidence limits

The technical audit has zero errors and reports `HOLD_VISIBLE_FRAME_REVIEW`; the 1920×1310 review images pass the container/decode floor without upscaling the 1254×1254 source. Because `whole_body_direction` remains HOLD, no seven-check review bundle or frame receipt may be sealed. This report does not approve another direction or phase, temporal contact, recoil/projectile alignment, an atlas, 30/60/120Hz runtime, HTML input parity, a complete 8×8 sequence, promotion or Luna readiness.
