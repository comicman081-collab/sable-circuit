# Delivery review — not production art approval

Six successful original Flow video outputs are retained unmodified under `source_720p`. Six silent 1920x1080 derivatives and the ordered 60-second assembly are under `delivery_1080p`. Each source contains 240 video frames at 24fps (10 seconds); the original audio track slightly extends the MP4 container to 10.005 seconds. Exports omit audio entirely, so each is exactly 10 seconds and the assembly is exactly 60 seconds / 1440 frames.

The output is Lanczos-upscaled from 1280x720, as explicitly requested by the user. It is NOT native-1080p generation or reconstructed high-frequency detail. `container_validation.json` verifies only dimensions and decoding. Its generic `native_1080p_container` field must not be interpreted as a native source-quality approval. Every output frame was decoded, hashes were recorded, and absence of audio streams was checked.

## Visual sample observations

Reviewed extracted 1s, 5s, and 9s samples from all six actual clips. These are sample observations, not a claim that every frame passed anatomical, costume or gait review. The trio and the amber gate → cyan corridor → archive → red junction → violet core → mint lift narrative are recognizable. This is an editorial sequence of six generated shots, not one uninterrupted matched take.

Unresolved generated discrepancies retained transparently:

- A provider sparkle watermark is visible in the returned frames. It was not removed.
- ASTER's shoulder fabric is inconsistent: exposed/strapped shoulder details appear in corridor/archive samples; the lift introduces a padded shoulder detail. These are not approved changes to her game costume.
- MICA's weapon changes in the archive, with the mint scanner rendered as a floating/panel graphic rather than consistently attached to her authored carbine.
- Near the end of the red junction, MICA gains ROOK-like mantle detail over her long coat. Character attributes are not perfectly isolated across the generated sequence.
- Some shots contain letterboxing, and shot boundaries are hard cuts with narrative/light continuity rather than exact pose matches. The provider does not follow every requested camera beat.

No extra generation or paid upscaling was used to repair these issues because the user capped successful outputs at six and authorized only the one failed-part retry. This is a delivered cinematic review draft, not approved production art and not a new source for character generation. No app texture, character profile, harness approval, or live deployment pointer was modified.

## Budget evidence

Flow UI displayed 15 credits for a 10-second 720p x1 generation. Six outputs succeeded. The first part-3 submission failed with a provider possible-celebrity notice and an explicit no-charge message. Only that failed part was retried once after the user's explicit approval, and it succeeded. Seven attempts / six successful outputs / expected 90 billed credits; the account billing ledger was not independently audited.

Exact prompt components are retained in `FLOW_PROMPTS.md`; reference sources and hashes are in `references.json`; output hashes and frame counts are in `delivery_manifest.json`.
