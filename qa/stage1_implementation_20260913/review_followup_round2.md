# GPT 6 Pro review round 2 — implemented subset, not final approval

Round 1 was read in the same user-requested chat. Its original observed text is
retained at motion_lab_v1/qa/stage1_enemies_20260913/cycle_capture/gpt6pro_review_round1.json.

Please review ONLY the actual changed subset below, focusing on new regressions
or insufficient fixes. Do not repeat the whole original report or treat this as
a request for final art/MVP approval. No image/video or Luna validation is claimed.

Implemented and tested:
- prepare_enemy_asset validates project copy path/hash and actual returned path
  in tool output; rejects path-like ids before outputs; code-hash candidate paths
  preserve prior processing versions. This is consistency, not signed attestation.
- Derived normalization now decodes original+output, verifies native RGB size,
  subject existence and exact subject pixels, and recomputes edge-connected mask.
  Four synthetic corruption tests passed.
- Source review refuses unchanged rejected bytes and invalid provenance status.
  intake_frame no longer silently returns a stale source receipt.
- Actual video character-panel pixels are compared to the chronological atlas
  with VP8 tolerance; 1/4 and 2/5 annotated chain repetitions are rejected.
  11 cycle tests passed. This does not yet recompile source->atlas independently.
- Rapid aim rows now retain reversal samples, actor before/after, old velocities,
  initial ammo/reload/cooldown; eligibility is recalculated against the recipe.
  24 workflow tests passed. Live browser recapture is pending.
- NPC roles use explicit current ids; unknown roles stop, not ranged fallback.
- Lunge draw and damage use the same frozen swept capsule, including speed boosts.
  World warnings use top-level identity transform and local shape tests.
  217 actual Godot geometry assertions passed under transformed parents.
- Old duplicate boss volley owner disabled; normal 6-room/10-kill mission was
  rerun to extraction; all three operators survived (4/106/88 HP at boss exit).
- Nonwalking machine source preview: rigid-body hover vs anchored body, emission
  from observed image orb/iris, no old SVG death fragments. 178 Godot checks passed.
  Raster candidates are still isolated and NOT registry-promoted.
- Updated the existing skill narrowly from the actual failures; no new framework.

Still open / intentionally not claimed fixed:
- Complete common response->captured master->derivation->slot provenance validation
  and receipt binding at every current source/delivery consumer.
- Pixel-content rejection hashes, reason-scoped rejection and required affected-slot
  changes; current unchanged-file rejection alone is not a metadata-reencode defense.
- Source->atlas independent recompilation, observation time-category coverage,
  browser 1x/no-seek playback evidence and observed anatomical labels.
- Atomic renderer load / missing modern-presentation fallback and importer two-half
  transaction + delivery invalidation.
- Four-limb motion contract and final enemy cycles, live QA, Stage 1 raster promotion.

Do not recommend changing accepted ASTER/MICA/ROOK appearance, gait or weapon cadence.
Please identify any definite bugs in the changes and give the smallest targeted test.
