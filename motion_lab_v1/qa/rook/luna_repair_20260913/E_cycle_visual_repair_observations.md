# ROOK E Luna repair — cycle visual review evidence

Date: 2026-09-13 (Asia/Seoul)

Decision: `repair` / unapproved. This is a visual rejection record, not a technical PASS.

## Evidence reviewed

- Current source cycle was prepared with `character_workflow.py prepare-cycle --character rook --direction E`.
- Native cycle kit: `cycle_kit/e3fc6a5d99f82196_237960ef/`.
- Native review video: `cycle_kit/e3fc6a5d99f82196_237960ef/E_walk_cycle_1080p.mp4` (1920x1080; three cycles).
- Chronological keyframes: `cycle_kit/e3fc6a5d99f82196_237960ef/reference/atlas/rook/E_walk_keyframes.png`.
- Decoded samples: `video_samples_0p30s/samples.json` and the twelve native 1920x1080 PNG samples in that folder.
- Native pair panels: `E_walk_pair0_native_2128x1626.png`, `E_walk_pair1_native_1920x1080.png`, and `E_walk_pair2_native_1920x1080.png`.

## Time-specific observations

- `0.000s` (frame 0 / E0): screen-right leg is the planted support and screen-left leg trails behind.
- `1.500s` (frame 1 / E1): screen-right leg remains the planted support while screen-left is the rear swing; this is consistent with frame 0 but does not establish a complete opposing phase.
- `3.000s` (frame 3 / E3): the alleged opposite contact repeats the same screen-right planted / screen-left trailing arrangement seen at `0.000s`; the required left/right support exchange is absent.
- `3.300s` (frame 4 / E4): screen-right remains support and screen-left remains rear swing; the opposing swing role is absent.
- Pair 2 inspection shows E2 and E5 do not exchange the passing/support roles: both repeat the same screen-left support / screen-right lifted-forward arrangement.
- The 5-to-0 loop seam therefore does not close as a natural left/right gait: phase 5 does not lead into an opposite phase-0 contact with a consistent support transition.

## Pair-level findings

- Pair 0 (E0/E3): both generated ROOK figures repeat the same screen-right planted / screen-left trailing orientation. The pair does not provide opposite contacts. The panel also exposes source-framing mismatch: E0 is a much larger 1024x1536 master while E3 is a smaller 714x950 crop before runtime normalization.
- Pair 1 (E1/E4): both repeat the same rear-swing/support role. The current Luna pair attempt also retained visible guide/mannequin color leakage in the trailing leg, so it is not an intake-ready appearance source.
- Pair 2 (E2/E5): both repeat the same passing/support role; E5 does not provide the opposite forward pass required by the gait contract.
- ROOK identity, hair, dark suit/poncho, gold trim, boots, and scattergun remain recognizable in the current source cycle, but identity continuity does not compensate for the missing opposite contacts or inconsistent framing.

## Luna attempt disposition

Three native high-resolution ImageGen pair attempts were made, one per E pair, using the E guide pair followed by the ROOK identity reference. The exact tool-response envelopes, project copies, and SHA-256 values are in:

- `E_walk_pair0_tool-response.json` — failed: RGB with painted checkerboard; repeated support role.
- `E_walk_pair1_tool-response.json` — failed: RGB near-green background without alpha; repeated support role and guide color leakage.
- `E_walk_pair2_tool-response.json` — failed: RGB green background without alpha; repeated support role.

Because none of the three pair candidates supplied a visually valid opposite role, no failed pixels were imported through `intake_pair.py`; active ROOK source slots and their existing provenance were left unchanged.

## Required next repair

Repeat the E pair authoring with a generation mechanism that produces two genuinely opposite ROOK poses per pair: E0/E3 opposite contacts, E1/E4 opposite rear swings, and E2/E5 opposite forward passes. Preserve clean native alpha (or a genuinely uniform green fallback), stable full-body framing, weapon continuity, and no guide/mannequin color leakage. Re-run source review and `prepare-cycle`; only after all six current frames and the complete cycle are visually reviewed may the candidate be considered for intake/build.
