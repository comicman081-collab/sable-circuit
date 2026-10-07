# SABLE CIRCUIT Asset Retirement Policy

## Immediate removal rule

When an art candidate, animation route, or supporting code path is marked
**REJECTED** or **RETIRED**, remove it in the same change. Do not keep it as
SSD-consuming evidence.

Remove its source and generated images, masks, raw outputs, atlases, contact
sheets, blend files, QA sidecars, temporary logs, and route-specific scripts.
Keep only a concise gate outcome in the active production documentation and the
commit history needed to explain the decision.

## Project-local image rule

Every authored or generated image asset must live below the SABLE CIRCUIT
project root. An external tool's output directory is ingestion staging only:
copy the selected file into its project lineage, verify its SHA-256, then delete
the external original and all rejected siblings. Do not use Codex, application,
or system temporary folders as an asset archive.

An active lineage may retain only:

1. its current work-in-progress candidate; and
2. exactly one immediate previous candidate.

After a replacement is verified, purge anything older in the same change. A
route marked `REJECTED` or `RETIRED` loses this exception and is purged in full.

## Scope guard

This rule does not remove an active authority package, approved tool runtime,
license inventory, or reusable neutral utility. Those items remain only until
they themselves are explicitly retired.

## Current ASTER state — 2026-08-30 cleanup

The direct-SSE route, Qwen Fire16 route, imagegen aim/fire v1-v2 routes,
2.5D E-fire mapping candidate, and orphaned UAL v6 temporary outputs are
retired and purged. Their route-specific scripts and external generated-image
duplicates were removed with them.

The obsolete Qwen move interpolation workspace, stale PID/log files, and the
superseded Qwen Fire Pose V4 package are also purged. The move workspace had
three junctions to `C:\AI_animation\H3\outputs`; only the project-local junction
objects were removed and the external targets were verified unchanged.

Projectile V6 is the current candidate and V5 is its sole immediate previous
candidate. Projectile V1-V3, their Comfy workspaces, and their route-specific
scripts are retired and purged.

The Codex staging directory
`C:\Users\AAA\.codex\generated_images\01a04819-7f38-7182-bb9a-fc313b7f4b65`
was removed in full after a 31-file SHA-256 audit: 30 files had byte-identical
project-local copies and the remaining file was an unselected three-effect VFX
sheet. No asset authority remains in that external directory.

The remaining failed Qwen Move V2 package, stale `artifacts/qwen_runs` logs,
one root temporary costume-drift contact, and eight unreferenced Fire16 root
prototype images were also permanently purged. None was referenced by the
current V6/V5/V4 locomotion fallback chain or an active Fire16 manifest.

The rejected broad-mask 2.5D source-plate v1 route, its idle-E mapping proof,
and all four route-specific builders were purged. The East locomotion lineage
was reduced to authoring v3 plus its immediate previous v2, and runtime v4 plus
its immediate previous v3; authoring v1 and runtime v2 were removed.

Two project-local iterations of `fire_upper_16_sse_static_proof_v1` were
visually rejected because broad corridor extraction copied triangular face,
arm, and hair fragments into the moving weapon assembly. Its staging images,
reviews, manifests, and route scripts were deleted immediately, so the failed
proof consumes no current/previous retention slot.

The automatic CLIPSeg/SAM2 semantic-mask attempts were also visually rejected:
the inferred rifle region absorbed trigger-arm and shoulder anatomy, so it was
not a valid rigid weapon assembly. All 34 project-local attempt files totaling
7,459,629 bytes were permanently purged. This failed route consumes no
current/previous retention slot.

The counted cleanup ledger through this audit is 738 files totaling
426,239,118 bytes (406.49 MiB), plus empty project directories and junction
objects. The junction targets outside the project were verified unchanged.

The current manual three-part SE semantic-mask lineage is project-local at
`art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_sse_semantic_masks_v1/manual_fallback_v1/`.
Its narrow gate is `PASS_THREE_SE_SOURCE_MASK_CHECKS_ONLY_HOLD`, with
`contract_complete=false`. It is now the sole immediate previous
mask-authoring candidate and the locked authority for the rifle and two
forearm/hand masks. It is not runtime eligible.

The current complete SE source-mask candidate is the immutable 21-file package
at
`art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_sse_semantic_masks_v1/manual_full_contract_v1/accepted_v1/`.
It contains all 17 native 1254×1254 binary roles plus QA, manifest, 1920×1440
review, and 1080p evidence. Its narrow result is
`PASS_FULL_SE_SOURCE_MASK_CONTRACT_ONLY_HOLD`; `contract_complete=true`
applies only to the source-mask contract. Runtime promotion, body-composite
approval, and visual PASS remain false.

Independent validation is retained as exactly the current
`manual_full_contract_v1/independent_validation_v2/` and its immediate
previous `independent_validation_v1/`. V2 independently passed all 17 roles
with zero hard-mask overlap, zero partition miss, zero exact-green invasion,
an exact 0-pixel seam-derivation XOR, 94.4888% RIFLE ownership in the locked
weapon receiver region, and 85.0423% BODY_CORE ownership in the distinct
under-receiver non-weapon flap/strap ROI. V1 is the immediate previous failed
validation record: it exposed an incorrectly placed weapon ROI and an
inappropriate raster-thickness threshold; it was not used to alter accepted
mask pixels. No older independent-validation candidate exists.
The V2 validator script and output hashes are fixed in
`docs/ART_PRODUCTION/ASTER_FIRE16_SE_FULL_MASK_INDEPENDENT_V2_PROVENANCE.json`.

`upper_identity_staging/` and `lower_costume_staging/` are not rejected
duplicates: their manifests and exact hashes are locked inputs of
`accepted_v1`, and the accepted manifest explicitly retains them as current
authoring provenance. They must remain until a later accepted package embeds
or replaces that lineage without dangling paths. Failed predecessor staging
from those builders was purged before acceptance.

This full-mask batch wrote no image asset outside the repository and launched
no Godot, ComfyUI, model, server, or network generation process. The required
review in the existing project ChatGPT web conversation completed on
2026-08-30 with
`FIRE16_SSE_17ROLE_REVIEW: PASS_FULL_SE_SOURCE_MASK_CONTRACT_ONLY_HOLD` and
`NEXT_STAGE: PASS_TO_DETERMINISTIC_BODY_COMPOSITE`. The exact scoped decision
and submitted evidence hashes are recorded in
`docs/ART_PRODUCTION/ASTER_FIRE16_SE_FULL_MASK_WEB_REVIEW_V2.json`.

That web gate permits beginning the deterministic body-composite phase but
does not supply missing pixels or approve a finished candidate. Moving the
locked rigid cluster exposes 46,016 `TARGET_REVEAL` pixels for which the
accepted source masks contain no hidden-body color. The retained segmented
SSE body and rifle plates remain
`HOLD_COSTUME_CONTINUITY_REPAIR_REQUIRED`, `runtime_eligible=false`, and
`visual_approval=false`; they must not be used as approved reveal donors.
Until a project-local builder establishes and independently validates an
approved reveal-donor or deterministic SE+S-to-SSE correspondence rule, the
implementation gate is
`HOLD_APPROVED_REVEAL_DONOR_AND_PIXEL_CORRESPONDENCE_NOT_ESTABLISHED`.
Completed-character visual PASS and runtime promotion remain false.

The derived rigid-cluster structural check is project-local at
`art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_sse_rigid_cluster_preview_v1/`.
It applies one shared similarity transform to the rifle, trigger
forearm/hand, and support forearm/hand and passes only
`PASS_STRUCTURAL_GEOMETRY_ONLY_HOLD`. The package is immutable, contains no
body composite, and makes no runtime or visual-PASS claim; a revision must use
a new versioned directory rather than overwrite v1.

The active Fire16 SSE lineage is project-local at
`art_src/pilot_v2/aster_v2/animation_360/fire_upper_16_segmented_sources_v1/`.
It contains two files in the current segmented source set and one immediate
previous composite. Its gate remains `HOLD_COSTUME_CONTINUITY_REPAIR_REQUIRED`;
none of these files is runtime eligible or visually approved.
