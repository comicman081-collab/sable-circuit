# Primary visual review — MICA C03 E/run/flight_l R1

- Reviewer: Codex Astra primary visual review
- Reviewed: 2026-09-08T01:03:00+09:00
- Raw SHA-256: `548872ee7d748d738ca6deb0bebe0bb5f3b42e948d91c9bf78cb8535fed9d692`
- Verdict: **FAIL_NOT_PROMOTABLE**

The candidate has a broad, coherent E-running silhouette, but it repeats the
anatomical laterality failure. In the approved front source, the beige vertical
thigh-pouch plate identifies the anatomical right leg. In this generated frame
that marker is on the rear/trailing leg (approximately x530–552, y699–762),
while `flight_l` requires the anatomical right leg to lead.

| Contract check | Verdict | Basis |
| --- | --- | --- |
| identity_and_costume | HOLD | Overall MICA identity is strong, but the immutable right-thigh marker is assigned to the wrong moving leg. |
| anatomy_and_limb_count | PASS | Limb count and visible joint continuity are coherent. |
| whole_body_direction | PASS | Head, torso, pelvis, legs and weapon form a coherent screen-right silhouette without a 90-degree waist twist. |
| phase_and_stride | FAIL | Wide airborne stride exists, but the anatomical right leg is trailing instead of leading. |
| feet_ankles_and_contact | HOLD | Both feet appear airborne and not sideways, but the named anatomical phase is wrong. |
| weapon_hands_and_visible_muzzle | PASS | Two hands grip the rifle and the main rightmost muzzle is visible. |
| matte_edges_and_subject_preservation | HOLD | The raw background is nonuniform. The first broad diff>=8 RGBA derivation removed valid teal/cyan details and is rejected. The corrected G>=20/diff>=32 diagnostic preserves teal/cyan and removes obvious dark chroma fringe, but this failed-laterality frame cannot receive a production receipt. |

The next permitted mechanism is a fresh built-in ImageGen
`repair_failed_frame` request bound to this exact quarantined raw image and its
failure manifest. The target repair is localized: keep the otherwise coherent
pose and MICA design, but transfer the beige vertical thigh plate to the actual
forward anatomical-right leg and restore the rear anatomical-left leg's dark
equipment. The failed frame itself may not be renamed or reclassified.
