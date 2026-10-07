# ASTER Directional Key-Pose Rejection Log

## Retention policy — updated 2026-08-30

Rejected and retired visual routes are purged from the project. This file keeps
only concise gate outcomes. The active production lineage may retain its
current work-in-progress candidate and exactly one immediate previous candidate
until a verified replacement exists; that exception is recorded by the active
lineage's retention manifest, not by this rejection log. `C:\AI_MODELS` and
`C:\AI_ENVS` remain immutable read-only sources.

## `fire_upper_16_sse_static_proof_v1` — REJECTED / PURGED

- Date: 2026-08-30
- Intent: Construct the missing SSE native midpoint from the approved SE and S
  directional parents while preserving the rifle/hands/forearms as one rigid
  assembly.
- Technical result: two deterministic project-local proof iterations rendered;
  no server, cloud model, Qwen, Krea2, Godot, or runtime promotion was used.
- Visual result: FAIL.
- Rejection reason: the broad geometric corridor was not a semantic assembly
  mask. It copied large triangular fragments of ASTER's face, arms, and hair,
  causing duplicated anatomy, cuts, and an invalid weapon/body topology.
- Disposition: both proof iterations, reviews, manifests, and the two
  route-specific scripts were deleted immediately. No failed image remains in
  the active lineage or its current/previous retention slots.
- Required correction: validate tightly separated semantic rifle, trigger-hand,
  trigger-forearm, support-hand, and support-forearm masks before constructing
  another midpoint. Mask QA must fail closed before any full-frame candidate is
  authored.

## `fire_upper_16_sse_auto_semantic_masks_v1` — REJECTED / PURGED

- Date: 2026-08-30
- Intent: Recover tightly separated SE rifle, trigger-arm/hand, and
  support-arm/hand regions with automatic CLIPSeg/SAM2 segmentation before
  attempting another deterministic SSE midpoint.
- Technical result: the automatic masks were generated and checked entirely in
  project-local staging; no candidate was promoted to runtime.
- Visual result: FAIL.
- Rejection reason: the inferred rifle mask absorbed trigger-arm and shoulder
  anatomy, producing an invalid rigid weapon cluster rather than separated
  semantic parts.
- Disposition: all 34 attempt files totaling 7,459,629 bytes were permanently
  deleted. The rejected route occupies no current/previous retention slot.
- Replacement status: the project-local manual three-part SE mask lineage at
  `art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_sse_semantic_masks_v1/manual_fallback_v1/`
  has only the limited gate `PASS_THREE_SE_SOURCE_MASK_CHECKS_ONLY_HOLD` and
  records `contract_complete=false`. It is not runtime eligible and promotion
  remains prohibited until the full semantic-mask contract and visual gates
  pass.

## `imagegen_aim_fire_360_mvp_v2` — REJECTED / PURGED

- Date: 2026-08-29
- Intent: Correct the v1 vertical UV inversion and preserve the separate
  Blender-only muzzle-event timing over all eight directions.
- Technical result: PASS. 48 upright raw frames rendered in headless Blender
  5.2.1; the aim masters remained clean.
- Visual result: FAIL.
- Rejection reason: the procedural vector-star muzzle shape is visibly flatter
  and cheaper than the authored ASTER art.  It is not an acceptable final VFX
  layer even though it is correctly absent from non-fire keys.
- Disposition: source, renders, masks, reviews, manifests, and route logs were
  deleted on 2026-08-30 after the later v3 lineage became the active route.
- Required correction: use a separated image-authored flash without changing
  clean aim masters.

## `imagegen_aim_fire_360_mvp_v1` — REJECTED / SUPERSEDED

- Date: 2026-08-29
- Intent: First eight-direction source-art Fire motion render using clean
  ImageGen aim masters, Blender 5.2.1 headless rendering, and UAL1
  `Pistol_Shoot` timing only.  The muzzle flash was implemented as a separate
  Blender emission object and keyed on only `muzzle_contact`/`recoil_peak`.
- Technical result: PASS. 48 raw renders were created with no UAL mesh,
  Krea2, or cloud runtime inference.
- Visual result: FAIL.
- Rejection reason: the initial image-plane UV mapping inverted every ASTER
  render vertically.  It cannot be used for contact review, runtime export,
  or motion QA.
- Disposition: source, renders, masks, reviews, manifests, and route logs were
  deleted on 2026-08-30. This gate record is the only retained evidence.
- Required correction: flip the V coordinates in the headless Blender
  source-plane builder and render a new versioned MVP.

## `fire_E_2p5d_mapping_candidate_v1` — REJECTED / SUPERSEDED

- Date: 2026-08-29
- Intent: First direct source-art-to-Blender `Pistol_Shoot` construction proof.
  It used the user-approved 2048 ASTER master and green/mask source plates;
  Blender 5.2.1 was run headlessly and UAL1 supplied timing only.
- Technical result: PASS. Six 2048 raw frames, six exact-green source pairs,
  and six matching masks were produced. Cloud/Krea2 calls were zero and no UAL
  mesh was rendered.
- Visual result: FAIL.
- Rejection reasons:
  - The v1 "rifle" / "arm" plate masks were broad construction polygons, not
    semantic isolated shapes. Moving them copied unrelated body fragments.
  - That produced doubled/fragmented rifles, broken interior cutouts, and an
    unreadable muzzle event. It cannot represent an ASTER fire key or be used
    for a runtime atlas.
- Disposition: superseded by the later image-authored route. Source plates,
  masks, raw renders, review evidence, `.blend`, QA sidecars, and job logs were
  deleted on 2026-08-30; this record remains.
- Required correction: build a tightly masked single upper-weapon assembly
  from the locked source, remove only that assembly from a derived underlay,
  and move the assembly coherently before any small masked seam repair.

## `idle_E_ready_v1_seed251144` — REJECTED

- Date: 2026-08-29
- Intent: First 8-direction pipeline candidate. Local Qwen Image Edit 2511 used the approved ASTER Static Master as identity authority and a Blender 5.2.1 headless pose guide as the E-direction spatial authority.
- Technical result: PASS. The candidate, binary mask, and deterministic `#00FF00` exterior were produced locally; cloud and Krea2 calls were zero.
- Visual result: FAIL.
- Rejection reasons:
  - The candidate stayed close to the front-quarter Static Master framing instead of obeying the headless Blender E-direction pose guide; it does not establish a credible E-direction turnaround pose.
  - The rifle and its distinctive end component remain part of the approved Static Master authority. The rejection is not a claim that this approved equipment design is invalid; the problem is that the two-reference edit did not supply controlled directional rotation.
  - It is therefore not suitable as an E-direction idle key pose and must not seed the other directions or animation frames.
- Disposition: Candidate and private Comfy workspace deleted after QA. Only this concise rejection record remains.
- Required correction before another attempt: separate the image-identity authority from the camera-direction authority. The next method must make the headless Blender turntable render the dominant spatial reference while locking the approved Static Master costume and rifle design as a non-regenerated identity overlay.

## `idle_E_ready_fullmass_v2_seed251145` — REJECTED

- Date: 2026-08-29
- Intent: Replace the earlier stick-pose guide with a Blender 5.2.1 headless full-mass guide built from UAL1 `Idle_Loop` frame 0. The Blender scene had no UAL mesh, mannequin, or final character body; its smooth forms only described the E-direction camera, body volume, two-hand rifle grips, and feet.
- Technical result: PASS. Local Qwen Image Edit 2511 produced one candidate, one binary mask, and exact `#00FF00` exterior; cloud and Krea2 calls were zero.
- Visual result: FAIL.
- Rejection reasons:
  - The generated output preserved the approved Static Master's front-quarter camera almost verbatim instead of rotating to the full-mass guide's E-direction spatial construction.
  - Identity preservation is not directional construction. Repeating the static view cannot supply the required independent E-direction body, ponytail, asymmetric gear, rifle, hands, and feet.
  - The Qwen two-reference directional-authoring method has therefore failed twice with different guide densities. It is retired rather than used for a third random trial or for batch generation.
- Disposition: Candidate, private Comfy workspace, guide image, guide `.blend`, and their method-specific scripts deleted after this record. The retained 360 UAL/Blender motion driver remains valid timing/pose evidence only; it is not a final art source.
- Required replacement: author direction masters as deliberate SABLE source art first, then map those masters onto the existing Blender-guided 2.5D motion rig. Qwen may remain limited to controlled repairs inside an already-authored direction master; it may not be asked to invent the direction turntable from the static master.

## `fire_SE_muzzle_contact_v1_seed251150` — REJECTED

- Date: 2026-08-29
- Intent: One ASTER SE firing key-art candidate after the user-approved 2048 Static Master. The local Qwen 2511 graph used the UAL1-derived Blender 5.2.1 full-mass fire-contact guide as the latent pose anchor and the SHA-locked Static Master as identity authority.
- Technical result: PASS. All approved local Qwen weights were recognized and loaded; the raw PNG was written after 399.963 seconds. Cloud and Krea2 calls were zero.
- Visual result: FAIL.
- Rejection reasons:
  - The result retained the passive cross-body rifle carry instead of the required stock-braced firing stance.
  - It did not establish a readable muzzle-contact event, forward firing axis, or active recoil/muzzle-light action.
  - It therefore cannot be the first key of ASTER's Fire state, regardless of its retained identity and material quality.
- Disposition: Raw candidate, copied inputs, private Comfy workspace, and the now-proven ineffective direct-Qwen fire-pose scripts are deleted. The Blender fire contact guide remains as valid non-final motion evidence.
- Required replacement: construct the fire key directly in the 2.5D source-art rig from the locked ASTER master, then use Qwen only for small, masked repair work after the authored firing silhouette, stock position, trigger hand, support hand, and muzzle point already exist.

## `qwen_fire_pose_se_muzzle_guideonly_v4_seed251132` — SUPERSEDED / PURGED

- Date: 2026-08-30 cleanup.
- Historical result: technical PASS at 1024×1024, but no user visual approval
  and no Static Master or runtime eligibility.
- Superseded by: the approved 2048 Static Master and later native 1254
  directional aim-master package.
- Disposition: candidate, masks, inputs, previews, provenance, and route
  workspace permanently deleted. This concise record is the only retained
  route evidence.
