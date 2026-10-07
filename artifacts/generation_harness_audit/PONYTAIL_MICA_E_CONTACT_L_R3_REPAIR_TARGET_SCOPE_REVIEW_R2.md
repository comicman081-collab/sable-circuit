# MICA E/contact_l R3 scope R2 — Ponytail FULL independent review

Reviewer: `/root/ponytail_motion_audit`. UTC: 2026-09-07T19:59:49Z.

Exact subject: `5064be6bed0756a9cc101d5c1b24292971540ee1e1d3832aeae6f8831c55a0dd`.

Verdict: **PASS_REPAIR_TARGET_SCOPE_ONLY**. The two ambiguities in the previous exact-scope HOLD have been addressed. This approves the target and bounded edit specification only; it does not reserve or approve an ImageGen output, the failed R1 pixels, or actual contact/motion.

## Actual verification

Read the new draft, complete prompt, subject record and primary review. Independently recomputed the canonical subject from the current implementation's fields and verified all **18 unique exact references**, with no stale/swapped reference. Reopened the native R1 RGB image; compared its limb markers and missing back devices with the unchanged approved neutral/true-E references and R12 contact guide directly inspected in the preceding reviews. Their actual hashes still match. The new expected raw output does not exist. No source, image, code, old report, permit or production pointer was changed.

Read-only pixel inspection used the current ratio-aware background mask without writing a derivative. It found R1 bounds **x=17..1004, y=220..1249**, and the visually identified trailing boot's bottom at **y=1143**: **107px above the declared y=1250**. The existing leading-sole band y=1248..1252 spans only **9 distinct x coordinates**, not the requested 50. These are diagnostic mask-dependent measurements, not a contact or matte PASS. The primary review's x=16..1005/y=1250 bounds differ by one boundary pixel. Accordingly, **1250 is approved as the predeclared edit-layout baseline**, not as an algorithm-independent ground measurement or a Blender-world clearance. It must not be recomputed from the next output.

## Six requested scope checks

| Check | Verdict | Bound evidence |
|---|---|---|
| 1. Preserve R1 anatomical laterality | PASS | Request and prompt explicitly preserve plate-free anatomical LEFT leading screen-right and beige-plate anatomical RIGHT trailing. The actual target exhibits this relation. No limb/marker exchange or image reflection is allowed. |
| 2. Fixed baseline / contact extent | PASS | The hash-bound change list and prompt specify 1024×1536, y=1250±2, nothing below y=1252, and at least 50 horizontal pixels of the **leading LEFT sole** at that band. This is a forward acceptance target, not a relabeling of the original heel's few pixels as contact. No floor/shadow is drawn into the artwork. |
| 3. Fixed body; coherent limited shin/ankle edit | PASS | Pelvis/waist, LEFT hip and upper thigh, body scale and E alignment are preservation-only. The edit rotates the boot about its anatomical ankle and permits, only if needed, a coherent connected shin/knee-to-boot adjustment below the preserved upper thigh. Stretching, detachment, whole-leg hip translation and calf inflation are expressly forbidden. This closes the previous frozen-calf/translating-ankle contradiction. |
| 4. Raised trailing RIGHT boot | PASS | Both request and prompt require its bottom to remain at least 80px above y=1250, equivalent to bottom y≤1170 in top-left image coordinates. The original trailing boot already satisfies this with 107px separation and remains preserve-only. |
| 5. Restore only two approved back devices | PASS | Exactly two dark upright cyan-lit devices are restored from approved ImageGen identity/true-E sources. They are visibly missing from R1 and present in those sources. Extra rods, wings, shoulder armor, backpack or other new appearance are forbidden. All unlisted appearance stays preserved. |
| 6. Ordered inputs / art authority / R2 exclusion | PASS | Exact order is R1 failed raw → approved neutral identity → approved true-E → exact R12 contact_l guide. Roles agree with the prompt. R2 is not an image input; it is only previous-failure provenance. The guide's person, mechanical arms, hair, clothes, bare feet, props, backpack and materials are forbidden visible content. Built-in ImageGen alone performs the visible repair. |

## Contract review-check mapping

- `exact_failed_target_hash`: **PASS** — exact R1 raw is in its own bound quarantine inventory.
- `requested_phase_laterality_already_present`: **PASS, anatomical relation only** — LEFT leads and RIGHT trails. This does not approve existing support/contact.
- `preserve_scope_is_visually_present`: **PASS, target-preservation scope only** — named retained appearance and marker relation are visible; absent back devices are explicitly change-only. “Preserve boots” refers to their approved design, not vetoing the listed boot-pose edit.
- `change_scope_is_explicit_and_minimal`: **PASS** — fixed canvas/body/baseline, bounded connected lower-leg edit and two-device restoration now have concrete limits.
- `failed_target_remains_non_promotable`: **PASS** — R1 inventory remains FAIL_NOT_PROMOTABLE, disposal false, no production pointer; a separate new raw output is required.
- `imagegen_only_visible_art_boundary`: **PASS** — no Blender/VRM pixel transfer, replacement model, local artwork repair or compositor route is authorized.

## Non-transferable limits

The new output must actually satisfy the 50px visible sole condition with a natural heel/sole arrival and preserved joint/boot anatomy. Merely drawing a flat stripe, inflating a boot, lowering the entire body, swapping markers, moving the baseline or deforming the calf cannot pass. Numerical conformance still requires native visual identity/costume, anatomy, phase/contact, weapon/muzzle and matte review. The 1250 layout line does not prove MICA's 3D sole clearance, root velocity, support slip or sequence timing. The R12 generic model remains pose-guide-only.

The prior report remains unchanged at SHA `7222b8ab5da59ae2932f11584e61703b7f278f0e9b2708b5e32f1237a7d3e372`. R1/R2 failed images stay quarantined. No image-frame, temporal sequence, eight-direction, firing, runtime, HTML, promotion, MICA completion or Luna approval is given here.

## Exact hashes

Paths are project-relative; SHA-256 was checked from actual bytes.

| Evidence | SHA-256 |
|---|---|
| `art_src/characters/mica/visible_frames/candidate_mica_c03_astra_r3_e_contact_l_r12_repair_scope_r2/DRAFT_REQUEST_REQUIRES_REPAIR_SCOPE_REVIEWS.json` | `180acfb02bca7616280a85bcb12e251eff55f1c9453c06bc8194d2462fd32699` |
| Same directory `PROMPT.txt` | `798a19767ab685c875d902070e9781c31ec24ec721db681e62042887f0ec44fc` |
| Same directory `REPAIR_TARGET_SUBJECT.json` | `744e9a857ffd4929cb96cfb438bbb77edafe43143fcba4fecda05df2950d7290` |
| `artifacts/generation_harness_audit/PRIMARY_MICA_E_CONTACT_L_R3_REPAIR_TARGET_SCOPE_REVIEW_R2.md` | `14a7cc0ab25e7fc1a3298d47e09503ab6aa2c42ef5f9dc44fd4b1e0fb4551a15` |
| Exact R1 raw at the draft's `repair_target.path` | `351443d83408de0418df2722c7cf29b80c2bc123d62ac633c2eedc7fba31d4ba` |
| R1 `QUARANTINE_MANIFEST_R2.json` | `948da7ca2e63ac32a63af73283e20c531192eec1db4b1a8cb76d18703bac6e92` |
| R2 `QUARANTINE_MANIFEST.json`, provenance only | `37d9e76a73c27ceb239868f05b213b251e4045b61bf15044bb20ba854f848a72` |
| Approved neutral `MICA_C03_S_NEUTRAL_RIG_GREEN_R1.png` | `6224f3efd1f72e97fcb95f04bd13479bbaf7c740049435705f567cd6692e8895` |
| Approved `MICA_C03_E_TRUE_PROFILE_GREEN_V1.png` | `7ece6e83561bf3c9ee720b4c5a1f75820f73ae4afce95b895fe9b38d3299f4a1` |
| `SOURCE_RECEIPT_R7.json` | `53adbb86c1216baa1923c677e978e2ccc5f8f46260e2a933c501c94f9711e017` |
| R12 `frames/contact_l.png` | `a67d1f6aed89a12846318e10c83df09b285d2a876fb6ae6fed148a33d509a815` |
| R12 `capture.json` | `75aa7582b5e1f389562ba0df75568fe11e6629fa4d31d47200fd3f7b610a92c3` |
| R12 `contact_calibration.json` | `9cab39b65b10762cdb024c81a172c7d0a99b4a4d0a52a631a362bed48a0c3207` |

Signed: `/root/ponytail_motion_audit` — Ponytail FULL; `sable-motion-production` applied.
