# Primary repair-target scope review — MICA E/run/flight_r R3

- Reviewer: Codex Astra primary visual review
- Review UTC: 2026-09-07T17:47:00Z
- Exact repair-target subject: `092c0066efb87ffe0bc9768096947e7935c0325de1286493e8538c6fd9bd0880`
- Verdict: `PASS_REPAIR_TARGET_SCOPE_ONLY`

## Direct inspection

The exact quarantined R2 raw target `2c2cca4b...` remains recognizably MICA, contains one full body, a coherent two-hand rifle hold, a visible right-pointing main muzzle, broad uncrossed airborne stride, intact boots and asymmetric thigh markers. It is still `FAIL_NOT_PROMOTABLE`: the beige-plate anatomical RIGHT leg leads although `flight_r` requires the plate-free anatomical LEFT leg to lead; the torso/pelvis is not strict E; and its old runtime derivative retained a dark-green halo.

The request keeps those existing usable properties and restricts visible ImageGen changes to exactly two defects: anatomical lead/trail correction without moving the beige marker to the wrong leg, and whole-body strict E alignment. The post-generation ratio-aware connected matte is a separate derivative step, not a request to repaint MICA. The failed target is the first ordered ImageGen input, followed by the approved true-E direction reference and approved neutral identity/costume source.

## Required checks

| Check | Verdict | Evidence |
| --- | --- | --- |
| `exact_failed_target_hash` | PASS | Target path/hash exactly matches an inventory member of the R2 quarantine manifest `8eb42d67...`. |
| `requested_phase_laterality_already_present` | PASS | The target contains both distinct anatomical marker-bearing legs and a broad airborne stride, so the correction is a bounded lead/trail repair rather than a new unreviewed body design. |
| `preserve_scope_is_visually_present` | PASS | Identity, costume, palette, weapon, hands, muzzle, limb count, boot axes, coat silhouette, scale and margins are visible in the exact target. |
| `change_scope_is_explicit_and_minimal` | PASS | Only leg laterality for `flight_r` and torso/pelvis E alignment are permitted visible-art changes. |
| `failed_target_remains_non_promotable` | PASS | The request and quarantine manifest retain R2 as FAIL; no pointer or promotion claim is made. |
| `imagegen_only_visible_art_boundary` | PASS | Visible art is assigned only to built-in ImageGen. Blender/UAL F14 remains a licensed lower-body motion guide and is not an appearance input. |

This is request-scope approval only. It does not approve an output frame, matte, temporal motion, runtime, firing, sequence, HTML, promotion, or Luna readiness.

