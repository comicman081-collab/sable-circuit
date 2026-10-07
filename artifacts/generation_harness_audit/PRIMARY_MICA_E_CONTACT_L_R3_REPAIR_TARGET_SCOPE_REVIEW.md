# Primary repair-target scope review — MICA E run contact_l R3

Verdict: `PASS_REPAIR_TARGET_SCOPE_ONLY`

Exact subject: `3cbcc9d7456314f730b0a9fb9b2b4949f58e0799636abe9e6f6fefbed2243d51`

The exact quarantined R1 ImageGen image is eligible only as a narrow ImageGen
edit target. It already contains the requested contact_l anatomical relation:
the plate-free anatomical left leg leads screen-right and the beige-plate right
leg trails. The R2 image is not an edit target because that relation is reversed.

Approved change scope is exactly two localized areas:

1. Adjust only the leading anatomical left ankle/boot placement so the sole
   reads as planted contact against the independently calibrated R12 guide. The
   trailing right boot remains raised and the existing leg laterality is not
   swapped.
2. Restore exactly the approved pair of dark vertical cyan-lit back devices
   missing from R1, using the approved MICA identity/true-E art as authority.

Every other R1 region is immutable: face, braid, proportions, strict E torso
and pelvis, coat, colors, rifle, hands, muzzle, plate-free-left/beige-right
markers, broad stride, scale and green background. Blender/VRM visible pixels
are forbidden; the guide communicates pose geometry only.

Checks

- exact_failed_target_hash: PASS
- requested_phase_laterality_already_present: PASS
- preserve_scope_is_visually_present: PASS
- change_scope_is_explicit_and_minimal: PASS
- failed_target_remains_non_promotable: PASS
- imagegen_only_visible_art_boundary: PASS

This scope review does not approve a generated edit, visible frame, sequence,
motion, firing, runtime, HTML or promotion.
