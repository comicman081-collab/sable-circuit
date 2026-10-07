# ROOK E green fallback attempt 02 — visual review

Date: 2026-09-13 (Asia/Seoul)

Decision: `repair` / `FAIL_NOT_PROMOTABLE`. No source slot was imported or replaced.

## Actual outputs

Each E pair received exactly one built-in ImageGen attempt at native 1536x1024, using the corresponding UAL guide for pose/camera only and `art/rook/identity_reference.png` for ROOK appearance and scattergun authority. The requested backdrop was `background: flat_uniform_green`.

- Pair 0 E0/E3 raw: `E_walk_pair0_luna_raw.png`, SHA-256 `91ac57827c484d70891c9786d324e01dd3abdc8676f16c5f135f0d3e0e80d6e5`.
- Pair 1 E1/E4 raw: `E_walk_pair1_luna_raw.png`, SHA-256 `f10c343f160629aa20fd7a0e81cdd021b3a1e595b7f7c9c9ccd98ef0b95d5a88`.
- Pair 2 E2/E5 raw: `E_walk_pair2_luna_raw.png`, SHA-256 `d784cb68d71d5e115032572042ddb4a408f53351f7be28bc2288931e6020694c`.
- Exact returned paths, tool envelopes, prompts/roles, and all derived hashes are recorded in `green_attempt_02_manifest.json` and the three `E_walk_pair*_tool-response.json` files.

## Background and keying inspection

All three results are RGB, not native alpha. Their canvas-edge colors vary (`edgeUniqueColors`: pair0 159, pair1 132, pair2 147), so the raw results are not literally flat-uniform green. The project normalizer nevertheless passed all three as deterministic near-green matte normalization with subject pixels byte-exact:

- Pair 0 edge-connected coverage `0.6850897471110026`; normalized output and binary mask are preserved in this folder.
- Pair 1 edge-connected coverage `0.6966431935628256`; normalized output and binary mask are preserved in this folder.
- Pair 2 edge-connected coverage `0.686553955078125`; normalized output and binary mask are preserved in this folder.

The normalized images were inspected at original scale. Normalization changed only connected near-green backdrop pixels; it did not redraw or alter the leg poses.

## Visible gait findings

- Pair 0: both figures show the same screen-right planted / screen-left trailing contact arrangement. The requested opposite E0 contact versus E3 contact is not visible.
- Pair 1: both figures show the same rear-swing/support arrangement. The requested E1 right rear-swing versus E4 left rear-swing exchange is not visible.
- Pair 2: both figures show the same passing/support arrangement. The requested E2 right passing-forward versus E5 left passing-forward exchange is not visible.
- ROOK identity and scattergun continuity are recognizable, but the repeated lower-body roles make the pair unusable for the six-phase gait. The generated figures also need comparison against the neighboring source framing before any future intake.

## Disposition

This attempt remains quarantine/evidence-only. `intake_derived_frame.py` was not run: these are two-figure pair masters, all three failed the visual opposite-role gate, and importing a pair as one frame would be invalid. No `intake_pair.py`, source review approval, prepare-cycle replacement, build, activation, or deployment was performed. Stop further generation in this batch.

Next repair: use a mechanism that visibly produces opposite support/rear-swing/passing legs in each pair, with stable full-body framing and a true flat #00FF00 master (or a valid deterministic normalization), then repeat the pair-specific visual review before any intake.
