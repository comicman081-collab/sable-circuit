# ASTER fire-pose candidate rejection log

## `qwen_fire_pose_se_muzzle_v1_seed251129`

- Technical generation, exact-green matte, binary mask, and local-only QA:
  **PASS**.
- Visual basis SHA-256: `1e7a117a68e77bcac7cf7a3840cc425dc0976edde5b8ddfa4e0465325d104366`.
- Blender SE muzzle-contact guide SHA-256:
  `5b4298d5c94a2a3d79bc80f2d648e88b89bb8d8722c3f07769ab185dee71f092`.
- Rejection: **POSE_GUIDE_CONFORMANCE FAIL**. The Qwen graph used the visual
  basis as image-edit latent anchor, so the output remained too close to the
  basis's passive rifle arrangement instead of realizing the independently
  authored Blender firing stance.
- Disposition: exact project-local candidate and its temporary workspace are
  removed. No runtime asset, atlas, animation frame, commit, or other unit was
  created from it.
- Correction: the next single candidate anchors Qwen image 1 to the Blender
  SE firing guide and uses ASTER_VISUAL_BASIS_V1 only as image 2 identity/style
  authority. This maintains the user's preferred visual language while making
  the requested firing pose non-negotiable.

## `qwen_fire_pose_se_muzzle_mass_anchor_v3_seed251131`

- Local Qwen Image Edit 2511 completed one 1024px candidate from the locked
  visual-basis SHA-256 `1e7a117a68e77bcac7cf7a3840cc425dc0976edde5b8ddfa4e0465325d104366`
  and the headless Blender dense SE fire-guide SHA-256
  `f1739ca676c4eb6e8bc1ceb5573ee18b0d85ee93f869f44b6bf85b3b39dd0834`.
- Local-only provenance was verified: approved Qwen diffusion, text encoder,
  and VAE were recognized; cloud inference calls were `0`; Krea/Krea2 calls
  were `0`; no UAL mesh or proxy body was rendered as final art.
- The initial SAM2 matte passed its weak structural checks but visibly removed
  major operator pixels. That is a **matte QA defect**, not an acceptable
  source frame. The reusable Qwen matte path is corrected to use an
  edge-median, green-chroma extraction for controlled Qwen green backdrops;
  the corrected regression result preserved the whole raw body before writing
  exact `#00FF00` exterior.
- Rejection: **POSE_GUIDE_CONFORMANCE FAIL**. Even when the Blender fire pose
  was image-1 latent anchor, Qwen retained the near-passive cross-body rifle
  arrangement: there is no unambiguous muzzle-contact shot, no readable
  trigger/support-arm change, and no recoil/shot event. This is not a firing
  keyframe and cannot seed the 360 fire set.
- Disposition: delete this exact project-local candidate and its temporary
  workspace after this record is written. Keep no image, mask, or runtime
  export from it. `ASTER_VISUAL_BASIS_V1` remains the user-preferred style and
  identity reference only; it is not a fire-pose authority.
- Next pipeline work: correct the high-fidelity pose-authoring stage before
  any further generation. Do not batch or start idle/move/fire expansion.

## `qwen_fire_pose_e_from_se_v5_seed251133`

- Purpose: first image-to-direction transfer test. The active SE firing key was
  supplied as visual anchor and the mesh-free Blender `E` muzzle-contact guide
  supplied direction, hand, feet, and rifle-axis authority.
- Technical QA: **PASS** — 1024 square, binary mask, exact-green exterior,
  cloud inference `0`, Krea/Krea2 calls `0`.
- Rejection: **VISUAL IDENTITY / WEAPON CONSISTENCY FAIL**. The result changes
  the narrow coil rifle into an oversized generic gun, invents a lower-body
  apparatus, increases the chibi/toy read, and does not preserve the source
  key's controlled silhouette. Technical matte success is not visual success.
- Disposition: delete all V5 candidate files and its Comfy workspace. Retain
  only this concise rejection record. Do not use iterative Qwen direction
  transfer as the production method for the eight-sector set.

## `qwen_fire_pose_se_proportion_v6_seed251134`

- Purpose: one bounded local Qwen refinement of the active SE source frame.
  The V4 firing image was the single spatial source; no cloud, Krea/Krea2, or
  external API was used.
- Technical QA: **PASS** — one 1024px PNG rendered locally using the approved
  Qwen 2511 weights on the 12GB GPU; exact-green exterior, binary mask, and
  single-component silhouette all passed. Cloud inference calls: `0`.
- Rejection: **ADULT PROPORTION / STATIC-QUALITY FAIL**. The result retains
  the oversized head, short legs, rounded boots, and doll-like body mass of
  the source instead of reaching ASTER's mature 4.8–5.2-head tactical combat
  construction. It is not an acceptable source art for Blender 360° body
  authoring even though the two-hand rifle silhouette remains readable.
- Disposition: delete the exact candidate, generated raw/green/mask files,
  and temporary Comfy workspace. Retain only this evidence entry. Do not
  iterate from the chibi V4/V6 source again.

## `qwen_fire_pose_se_from_visual_basis_v7_seed251135`

- Purpose: single-image edit from the user-selected V3 ASTER visual basis
  itself, rather than from the rejected chibi fire source. The intent was to
  retain its mature body/identity while authoring only a firing event.
- Technical QA: **PASS** — one approved local Qwen 2511 render, exact-green
  source, binary mask, cloud inference `0`, and Krea/Krea2 calls `0`.
- Rejection: **FIRE EVENT / IDENTITY CONSISTENCY FAIL**. The candidate has no
  credible shot/recoil/muzzle event, loses facial detail, turns the lower
  costume toward magenta/red, and alters boot/equipment treatment. It is a
  passive rifle pose with identity drift, not the required high-quality ASTER
  firing original.
- Disposition: delete the exact candidate and its workspace. The V3 basis
  remains a style/identity reference only; do not use it as the direct Qwen
  input for another fire-pose attempt.
