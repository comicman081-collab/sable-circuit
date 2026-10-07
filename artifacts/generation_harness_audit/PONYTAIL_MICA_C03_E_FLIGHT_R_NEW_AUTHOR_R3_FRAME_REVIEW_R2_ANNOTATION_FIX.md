# Ponytail FULL — MICA E/run/flight_r R3, annotation fix R2

Reviewer: `/root/ponytail_motion_audit`, independent Ponytail FULL.
Review UTC: **2026-09-07T18:17:40Z**.
Applied instructions: project `AGENTS.md`, `sable-motion-production`, generation gates and motion-production constraints.

**Verdict: PASS_SINGLE_STATIC_VISIBLE_FRAME_REVIEW_ONLY — all seven checks PASS.**

Exact subject: `23e725b3da510e1711acbc5ee4669a8c0016e64cdb7525b913f63e1550a2ea31`.
Actor/costume: `CHR_PROTO_03` / `MICA_RECON_C03`; direction/motion/phase: `E` / `run` / `flight_r`.

## Scope and independently verified change

I re-read the corrected annotation and exact audit, independently hashed all **25 bindings**, and reproduced this subject with **0 mismatches**. Compared with the preceding HOLD audit, only the `ANNOTATIONS.json` and `FRAME_MANIFEST.json` bindings changed. The annotation moves the main muzzle tip from `(1128,376)` to `(1132,376)` and clarifies that it is the last opaque outer-edge pixel. Raw art, normalized master, mask, RGBA, request, permit, sources and guide evidence remain byte-identical.

I directly re-opened the native 1254×1254 RGBA and checked the muzzle pixels against raw/master. The original-scale source, green/dark board and reference comparisons recorded in the preceding review apply to these same unchanged image bytes; they are not replaced with an uninspected new image. The unchanged boards were independently decoded as 1920×1310 in that review and display the source at scale 1.0. Container PASS is not visual or temporal approval.

The previous HOLD report remains intact at SHA-256 `78270e22ba9eb3d93d8b67df0e30a97f089b7432d73854484eaefaea114d1673`. This new report does not rewrite or approve the old subject.

## Seven required checks

| Check | Verdict | Direct evidence for this exact static frame |
| --- | --- | --- |
| `identity_and_costume` | PASS | Approved MICA face/profile and brown right-side braid; patterned navy coat, beige trim, teal lining, back devices, guards, boots and cyan-core rifle remain coherent. The beige vertical plate remains on the trailing near/right thigh; far-side equipment is partly occluded rather than duplicated as a second beige plate. No guide-model appearance or reconstructed costume cutout is visible. |
| `anatomy_and_limb_count` | PASS | One head, two coherent arms/hands, two connected legs and complete boots. No crossed shins, detached waist, segmented rectangular coat, swollen barrel calf or extra limb is visible at native scale. |
| `whole_body_direction` | PASS | Head, shoulder/ribcage, pelvis, both leg chains, boots and rifle agree on screen-right E. The narrow placket is also present in the approved true-E source; it does not establish front-facing torso yaw. No visible 90-degree waist kink was found. |
| `phase_and_stride` | PASS | Plate-free anatomical **LEFT leads screen-right**, beige-plate anatomical **RIGHT trails screen-left**. The broad uncrossed airborne stride matches the requested `flight_r` static relation and differs from the rejected R2 wrong-leading-leg output. |
| `feet_ankles_and_contact` | PASS | Both boots remain fully visible and depicted unplanted. Leading and trailing ankle pitch follows each leg's running plane rather than turning sideways 90 degrees. This is airborne-pose anatomy only: there is no independently measured ground plane or temporal landing/contact proof in this image. |
| `weapon_hands_and_visible_muzzle` | PASS | Trigger/support hands hold one coherent rifle; main barrel is distinct from the lower auxiliary cylinder. Corrected axis `(1080,376)`→`(1132,376)` lies on the main barrel and ends at its actual last opaque outer-edge pixel. Pixel x=1133 on that row is transparent/background. The prior 3–4 pixel interior-tip error is closed for this subject. |
| `matte_edges_and_subject_preservation` | PASS | Native edges retain the visible cyan lights, teal lining, hair, coat and boots without an obvious strong-green halo, closed green hole or deleted costume core. RGBA/source RGB remains byte-exact for all visible pixels; independently recomputed strong-green alpha-boundary count remains **0**. This is visual review plus pixel evidence, not a quality inference from the count alone. |

## Exact muzzle and matte evidence

- Main barrel row 376 is continuously opaque from x=1080 through **x=1132**; its last opaque x is **1132**.
- `(1131,376)` raw/master RGB `[40,19,44]`, RGBA `[40,19,44,255]`.
- `(1132,376)` raw/master RGB `[28,50,40]`, RGBA `[28,50,40,255]`: the rendered outer-edge sample, not a claim about an analytic 3D bore center.
- `(1133,376)` raw RGB `[19,199,26]`, master `[0,255,0]`, RGBA `[0,0,0,0]`; `(1134,376)` is also transparent.
- Unchanged matte: 300,230 opaque / 1,272,286 transparent pixels; 24 interior strong-green-family pixels and **0 boundary residuals**. Previous independent four-neighbor ratio-mask reconstruction matched every alpha pixel; no matte bytes changed in this revision.

## Hash binding

| Evidence | SHA-256 |
| --- | --- |
| New frame audit | `904961a6c8ed29cbe56d4ffcb719e3d0a27c6e899c55127695de801c3a501795` |
| Corrected ANNOTATIONS.json | `d4cd5c566c7cfcc16fbdb72320d95c8775d2336e1eaeeaad0cce417f2f0db0b3` |
| Corrected FRAME_MANIFEST.json | `911e01c0741e66e51535849da55423ee9ddec5b643b559f6222b07f009adc6d9` |
| ImageGen raw | `5d1dc992e662e29b5354ecae3a7cac69b5ba24da2d498f4e165a7a0fa1b7a4a8` |
| Exact-green master | `d8d88c0906ac82145fa33499ff6ce013a70f9fa7d16c137e83b0116d5af43178` |
| Edge mask | `243aa2b1a6bfe67db9ff687b3ce22d93b4835f2cc72fff8d89a202aaf887a5fe` |
| Runtime RGBA | `18570cea5cc1b4584ae8d1befd4e13fd0ad675dfbd2da9d44ac7baf405cd6503` |
| Primary R2 review, inspected separately | `94118dea11deeda792e0285a8fed56bf03697c882eb72122b847b60c04853c4f` |

Only this exact static frame is approved. No temporal sequence, contact/grounding, root speed, projectile birth, firing/recoil, other phases/directions, runtime matrix, HTML parity, production promotion or Luna readiness is approved. I modified only this new review report.
