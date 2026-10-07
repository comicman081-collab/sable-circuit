# Demo music and combat input repair — 2026-09-20

## Confirmed defects and repairs

- Short keyboard taps could be released before the next physics poll. Real browser `2` did not switch the old deployed ASTER selection. Discrete action presses now survive two process frames; movement is not buffered.
- Portraits were drawn, not selectable. Mouse and touch selection now use the normal squad control transaction, with downed-character restrictions unchanged. HUD clicks do not fire a weapon.
- Training actors could lack an explicit equipped weapon record and depend on profile fallback. Actor initialization now assigns each operator's registered default weapon; campaign loadouts can still override it. HUD weapon names use the equipped specification.
- The normal route starts in a noncombat entry room. A short `F` press could be missed, and the objective lacked an actionable indication. The HUD now exposes entry confirmation and the distance to the next combat area. No encounter, reward or movement trigger was bypassed.
- Final Web console review found the authored ASTER projectile excluded by `assets/units/*` and loaded through an OS path. The export now preserves this exact active asset while excluding retired unit trees. The projectile decodes the original bytes through FileAccess, which works in the Web pack. A packed-resource check blocks a build missing the image.

## Scoped evidence

- `combat_regression.json`: 20 passing checks using native input events, the normal mission path, actual movement physics, ammo consumption and ROOK/MICA follower firing. This is a controlled regression, not a complete human campaign playtest.
- `runtime_check.json`: 51 passing music checks. Title and intro are separate tracks; the intro does not loop, fades at the cinematic tail, and transitions on skip or completion. Mute and pause do not mute the SFX bus.
- The existing integration test also passed 27 checks with a full 60-second intro completion.
- In-app browser, native 1920x1080: short `2` selected ROOK; MICA portrait selected MICA; the selected weapon HUD changed and a shot consumed ammo. `F`, followed by ordinary rightward movement, produced three authored robots in the normal operation (`web_normal_combat.png`).
- `web_mica_control.png` and `web_normal_combat.png` precede the last projectile packaging correction. They prove the input/encounter changes, not the later pack fix. Final pack and browser checks are recorded separately.
- Final packed check: `qa/demo_web_20260920/packed_assets.log` confirms the original 61,694-byte ASTER image decodes from the exported PCK. After reloading this pack, browser training showed three robots, ROOK selected with its MAG SCATTERGUN, and no new error/warning entries. `web_final_rook_combat.png` and `final_visual_evidence.json` record that pass at native 1920x1080.
- Music was selected from the user's supplied packs using the pack descriptions, file inspection, full local decoding and level checks. Actual native AudioServer output was recorded non-silent. This does not assert subjective listening approval or an audit of every other game's historical use.

## Exclusive music allocation

Ten byte-verified originals are retained under `sound/music/originals`; runtime copies and the catalog are under `sound/music`. Only the exact selected shared-library files were removed after verification. See `source_retirement.json` for original paths and hashes. Originals are recoverable from this project; no shared folders or unrelated audio were deleted.

## Release caution

Sites version 2 was saved but intentionally not deployed after final browser QA revealed the missing projectile. Publish only the subsequent build with the packed-asset regression passing. Preserve the public site's existing audience and the prior deployment record.

The host also enforces a 256 MiB *expanded TAR* limit. The packager now checks both compressed and expanded sizes. The custom loader already hid the generated engine splash and used an embedded SVG icon; three reproducible Web-only PNG exports were removed and the remaining icon/splash references made inline. Source art, video, gameplay and music bytes were not reduced. USTAR avoids unnecessary extended timestamp records. Final expanded TAR is 268,431,360 bytes (22 files).
