# SITE-7 Map Kit V2 — stage 0 HOLD

2026-09-27. Built-in ImageGen, one image per request. S1_R02 used its three allowed attempts. S1_C01 and S1_C06 were not attempted. Production v1 pointers and files remain unchanged. No source was promoted to MASTER/GAME. No exposure, white balance, crop, resize or pixel repair was applied.

The native tool outputs were 1672×941 RGB. Review captures are actual native 1920×1080 Godot frames, with the candidate drawn at one source pixel per screen pixel. They do not claim a 1080p-authored master or a joined v2 map.

## S1_R02 attempt 01 — FAIL_NOT_PROMOTABLE

- RAW: `art_src/environments/site7_v2/_quarantine/S1_R02/attempt01/S1_R02_RAW_NATIVE.png`
- SHA-256: `1dc5e656362777e7d015562c96e5c5d4f6984ce1c624cff328f7b618f3f18031`
- Native: 1672×941 RGB
- MASTER / GAME: not created
- Rejection: Mean floor luma 0.254 exceeds 0.24. Floor reaches inside the mandatory 8 percent canvas inset. Door aprons are incomplete.
- References: [{"path": "art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png", "sha256": "435c3b2c8965808d7a2f1480b699e8b74bdd98c4763c3da85b440c8ab3f438de"}, {"path": "qa/map_gait_20260925/MIS_CH01_01_start.png", "sha256": "68b3cab67ce68b08409982bd2c043029db2d44bc8e2d35085accd6239085c02b"}, {"path": "assets/environments/site7/decon_corridor/02_DECON_CORRIDOR_CONTINUITY.png", "sha256": "5799a43bb237c709003db6943f89adbe343f56dbb03638e32fcf6db7726d2600"}]

Final prompt (verbatim):

```text
Use case: stylized-concept. Generate ONE new opaque RGB PNG environment plate S1_R02 for the SITE-7 map kit v2, native 1920 x 1080 or larger landscape (16:9). This is an empty room background for a game, not a screenshot.
REFERENCE ROLES: Image 1 is material-detail/finish quality only. Image 2 shows relative actor, crate and railing scale only; DO NOT include its characters, objects, UI or text. Image 3 is the old decontamination room, for decon machinery identity only; discard its floor colours, lighting, camera and lack of doorways.
Premium 2.5D tactical sci-fi game environment plate for SABLE CIRCUIT, underground research facility SITE-7.
CAMERA: fixed near-orthographic three-quarter top-down dimetric view. Floor panel seams and wall bases run at exactly a 2:1 slope (26.6 degrees from horizontal) in both diagonal directions. No perspective convergence, no fisheye, no tilted horizon.
SCALE: for a 1920x1080 canvas, an imaginary standing adult is 129.6 pixels tall. Square floor panels about one adult-height wide; waist-high railings 71 pixels tall; door frames about 207 pixels tall. Do not draw people or scale rulers.
FLOOR: one clean, open, flat SITE-7 standard deck of dark gunmetal steel plates with fine seams and light wear, bounded by a wall base or a low raised lip. The floor is uncluttered: no text, no markings with letters or numbers, no objects in the open floor.
LIGHT: even neutral-white overhead industrial light (about 6000K) across the entire walkable floor. No hot spots, no pitch-black patches, no vignette, no darkened corners, no fog or haze over the floor. The floor stays neutral grey steel and is never tinted by room colour. Target rendered sRGB floor colour near RGB(51,52,53), mean luminance 0.20 with restrained surface variation, no reflections of cyan lamps on the deck. This is a uniformly mid-dark matte steel deck, not a blue floor.
COLOUR IDENTITY: only on walls, machinery, fixtures and small practical lamps along the perimeter; their light spill on the floor is subtle and never reaches within one adult-height of a doorway.
OUTSIDE: everything beyond the architecture is flat near-black void (#07090D) with no gradient.
EXCLUDE: characters, creatures, robots, weapons, UI, HUD, text, signage, numbers, logos, projectiles, explosions, smoke over the floor, translucent or doubled geometry, black borders or frames.
STYLE: premium stylized realism with hard-surface wall thickness, recessed panels, structural supports and cast contact shadows. Not low-poly, not flat vector, not generic neon cyberpunk, not blurry concept art.
ROOM PLATE. The walkable floor is a broad dimetric diamond whose sides face NW (upper-left), NE (upper-right), SE (lower-right) and SW (lower-left). Back walls rise only along the NW and NE sides; the SW and SE sides end in a low lip or railing with no wall so nothing hides the floor. Keep the floor at least 8% away from every image border; the floor occupies at least 25% of the canvas. For a 1920x1080 canvas a broad diamond approximately left(190,610), back(960,225), right(1730,610), front(960,995) establishes the 2:1 axes. Keep actual walkable steel clearly visible, including each doorway.
DOORS: Exactly TWO open doorways: NE (upper-right back wall) and SW (lower-left foreground railing). Centre them opposite one another across the room along the lower-left to upper-right direction. Each doorway is an unobstructed opening approximately 300 pixels wide, not a closed door: a heavy steel frame at NE and a clean gap in the low lip/railing at SW. No door leaf, no shutter, no doorway on NW or SE. The same standard deck and neutral-white overhead light continue through every doorway for about 195 pixels on both sides of the threshold, with no steps, no cyan spill, no dark threshold. The exterior doorway apron remains inside the canvas.
ROOM TYPE: combat room, broad open arena — walkable floor at least 1000 x 560 runtime pixels. Centre completely clear of machinery or fixed cover.
IDENTITY: decontamination hall, cold decon arches and spray manifolds on the walls, wet-steel wall panels. Accent colour cold cyan, on walls and fixtures only.
Output the finished single illustration only, no diagram, annotation or composite.

```

## S1_R02 attempt 02 — FAIL_NOT_PROMOTABLE

- RAW: `art_src/environments/site7_v2/_quarantine/S1_R02/attempt02/S1_R02_RAW_NATIVE.png`
- SHA-256: `a34711671b8994585e0bd490360e45965e17807499ac41aea26613c2ab2e3838`
- Native: 1672×941 RGB
- MASTER / GAME: not created
- Rejection: Main-floor audit passes only. SW exterior apron fades into black instead of continuing as solid lit steel. Door openings remain much narrower than the approximately 300 px target.
- References: []

Final prompt (verbatim):

```text
Use case: stylized-concept. Generate ONE new opaque RGB PNG environment plate S1_R02 for the SITE-7 map kit v2, EXACT native 2048 x 1152 pixels landscape, render directly at that resolution, never resize a smaller result. This is an empty room background for a game, not a screenshot.
Premium 2.5D tactical sci-fi game environment plate for SABLE CIRCUIT, underground research facility SITE-7.
CAMERA: fixed near-orthographic three-quarter top-down dimetric view. Floor panel seams and wall bases run at exactly a 2:1 slope (26.6 degrees from horizontal) in both diagonal directions. No perspective convergence, no fisheye, no tilted horizon.
SCALE: for this 2048x1152 canvas, an imaginary standing adult is 129.6 pixels tall. Square floor panels about one adult-height wide; waist-high railings 71 pixels tall; door frames about 207 pixels tall. Do not draw people or scale rulers.
FLOOR: one clean, open, flat SITE-7 standard deck of dark gunmetal steel plates with fine seams and light wear, bounded by a wall base or a low raised lip. The floor is uncluttered: no text, no markings with letters or numbers, no objects in the open floor.
LIGHT: even neutral-white overhead industrial light (about 6000K) across the entire walkable floor. No hot spots, no pitch-black patches, no vignette, no darkened corners, no fog or haze over the floor. The floor stays neutral grey steel and is never tinted by room colour. Target rendered sRGB floor colour near RGB(51,52,53), mean luminance 0.20 with restrained surface variation, no reflections of cyan lamps on the deck. This is a uniformly mid-dark matte steel deck, not a blue floor.
COLOUR IDENTITY: only on walls, machinery, fixtures and small practical lamps along the perimeter; their light spill on the floor is subtle and never reaches within one adult-height of a doorway.
OUTSIDE: everything beyond the architecture is flat near-black void (#07090D) with no gradient.
EXCLUDE: characters, creatures, robots, weapons, UI, HUD, text, signage, numbers, logos, projectiles, explosions, smoke over the floor, translucent or doubled geometry, black borders or frames.
STYLE: premium stylized realism with hard-surface wall thickness, recessed panels, structural supports and cast contact shadows. Not low-poly, not flat vector, not generic neon cyberpunk, not blurry concept art.
ROOM PLATE. The walkable floor is a broad dimetric diamond whose sides face NW (upper-left), NE (upper-right), SE (lower-right) and SW (lower-left). Back walls rise only along the NW and NE sides; the SW and SE sides end in a low lip or railing with no wall so nothing hides the floor. Keep the floor at least 8% away from every image border; the floor occupies at least 25% of the canvas. Composition: leave clear breathing space all around. A broad dimetric floor diamond has corners approximately left(200,620), back(1024,208), right(1848,620), front(1024,1032). These establish exact 2:1 axes. Do not zoom in or crop any portion of the floor. Floor stays within 8% image margins; walls may rise above the floor. Keep actual walkable steel clearly visible, including each doorway.
DOORS: Exactly TWO open doorways: NE (upper-right back wall) and SW (lower-left foreground railing). Centre them opposite one another across the room along the lower-left to upper-right direction. Each doorway is an unobstructed opening approximately 300 pixels wide, not a closed door: a heavy steel frame at NE and a clean gap in the low lip/railing at SW. No door leaf, no shutter, no doorway on NW or SE. The same standard deck and neutral-white overhead light continue through every doorway for about 195 pixels on both sides of the threshold, with no steps, no cyan spill, no dark threshold. The exterior doorway apron remains inside the canvas.
ROOM TYPE: combat room, broad open arena — walkable floor at least 1000 x 560 runtime pixels. Centre completely clear of machinery or fixed cover.
IDENTITY: decontamination hall, cold decon arches and spray manifolds on the walls, wet-steel wall panels. Accent colour cold cyan, on walls and fixtures only.
Output the finished single illustration only, no diagram, annotation or composite.
CRITICAL COMPOSITION CORRECTION: Show the whole isolated room from far enough away to see a continuous near-black void margin, especially left, right and bottom. No part of the walkable floor may touch the image edge. 8% margins are mandatory. The foreground SW opening and its short apron must be visible. The NW wall contains decon spray hardware, NOT extra doors. TWO doorways total, SW and NE. Floor should be flat neutral dark charcoal #333435, NOT shiny silver. Final file must be truly 2048x1152, at least native 1920x1080; do not match any previous small reference canvas.

```

## S1_R02 attempt 03 — FAIL_NOT_PROMOTABLE

- RAW: `art_src/environments/site7_v2/_quarantine/S1_R02/attempt03/S1_R02_RAW_NATIVE.png`
- SHA-256: `a1be9d8c154495695e9cd13743834732d4bd3190821bba2895653061b14dfc76`
- Native: 1672×941 RGB
- MASTER / GAME: not created
- Rejection: Mean floor luma 0.267 exceeds 0.24. SW clear width approximately 166 px (manual trace uncertainty about 15 px) versus approximately 300 px required at scale 1.0. Native output is 1672x941 despite requesting 2048x1152; no enlargement was applied.
- References: [{"path": "art_src/environments/site7_v2/_quarantine/S1_R02/attempt02/S1_R02_RAW_NATIVE.png", "sha256": "a34711671b8994585e0bd490360e45965e17807499ac41aea26613c2ab2e3838"}]

Final prompt (verbatim):

```text
Edit the attached S1_R02 candidate into the final SITE-7 decontamination room plate. ONE opaque RGB PNG, render natively at 2048x1152 (minimum native 1920x1080); do not upscale a smaller raster.
Keep the broad dimetric room, near-orthographic camera, 2:1 floor axes, low SW/SE railings, NW/NE back walls, clean open neutral charcoal steel floor, cyan wall fixtures only, two doors on SW and NE, no text, no actors, no obstacles in the floor. Keep its even floor brightness (approximately sRGB 0.20-0.23, neutral gray). Preserve detailed premium hard-surface materials.
Correct ONLY the doorway geometry and doorway apron defects, with enough framing space to include them:
1. BOTH opposite doorway openings must be WIDE: 300 runtime pixels clear across (at scale 1.0; standing adult is 129.6 pixels tall). This is roughly twice the opening width in the reference. Widen the SW railing gap and the NE heavy frame. Doorways have no leaf and no shutter. No other doorways.
2. Through EACH doorway extend an actual solid painted steel deck for a full 195 runtime pixels OUTSIDE the threshold, and the same 195px INSIDE. Each apron is the same full 300px width as the opening, following the lower-left to upper-right floor axis. A connected, flat rectangular steel platform, not light shining over black void.
3. The SW apron in the reference wrongly dissolves into black. Remove that fade ENTIRELY. Both outside aprons must retain the SAME uniform neutral gray steel panel detail and brightness all the way to a crisp geometric outer edge. No vignette, gradient, bloom, dark threshold or dark far tip. No step or stair. Outer apron ends are open with no rail or wall across them.
4. Keep the floor AND both whole aprons at least 8% inside the canvas on every side. Pull the camera framing back if needed while maintaining full room floor minimum 1000 x 560 pixels and floor coverage at least 25% of image. Do not crop or stretch architecture.
5. Outside the architecture: absolutely uniform near-black #07090D. Room colour stays only on fixtures and walls. No light cones or spray mist over the walkable floor.
Output only the final finished illustration.

```

## Stop condition

The requested production document section 6 requires HOLD when one plate misses sections 2.1–2.4 after three ImageGen calls. Door geometry and final floor luminance still fail. No fourth call or connector generation was made.

Evidence: `qa/site7_map_kit_v2_20260927/README_KO.md`.
