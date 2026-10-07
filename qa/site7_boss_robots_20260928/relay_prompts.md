# RELAY SENTINEL ImageGen requests

All three calls used Codex built-in `image_gen.imagegen` with `transparent_background: true`. Referenced files were inside this repository. Every result was copied unchanged into the project and checked by `motion_lab_v1/source_alpha_policy.py` before another call.

## Attempt 1

References, in order:

1. `assets/enemies/stage4_forge_warden/authored_core_v1/FORGE_WARDEN.png`
2. `assets/environments/site7_v2/stage02/S2_R05/S2_R05_GAME.png`
3. `art_src/environments/site7/references/IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png`

```text
Use case: stylized-concept. Asset type: final native transparent PNG sprite for SABLE CIRCUIT boss BOSS_SITE7_RELAY_01 (RELAY SENTINEL), single production illustration, square canvas at least 1254 px on a side. Input Image 1 (FORGE_WARDEN.png) is ONLY a reference for fixed dimetric three-quarter top-down camera, premium rendering quality, and full-frame scale; DO NOT copy its tracks, round iris, arms, silhouette, colors or machinery. Input Image 2 (S2_R05_GAME.png) supplies only room material and crimson color context. Input Image 3 (IMAGE_A_ENVIRONMENT_QUALITY_REFERENCE.png) supplies only hard-surface finish quality. Draw one stationary, non-humanoid boss machine bolted to a broad square floor mount: a squat heavily armored relay-transformer sentinel, four stacked transformer coil towers of different heights around one central vertical relay mast, heavy insulated cable bundles descending into the mount, crimson status slits. Overall silhouette wide and low at base, stepped upward to an asymmetric mast. Exactly ONE clearly visible crimson relay emitter node crowning the central mast, with a small caged spark gap; the emitter is vertical and reads identically from every direction, never a directional gun barrel. Its floor-mount ground-contact center is at bottom center. Whole machine and mount fit with clear margin on all sides, readable at 230 px game height. Fixed near-orthographic 2.5D dimetric tactical camera, neutral white upper-left key, colored light only from its own lamps, thick hard-surface armor, recessed panels, bolts, cables, cast self-shadow, stylized realism. background: transparent_alpha. Deliver a genuine untouched RGBA PNG with native background alpha exactly 0 and visible subject alpha only 1..254, near-opaque interior alpha 254, absolutely NO alpha 255 anywhere. Transparent empty space around entire object; no floor, backdrop, matte, green screen, checkerboard, ground-shadow plate or glow outside the silhouette. No legs, feet, knees, wheels, tracks, arms with hands, head, face, text, numbers, logos, UI, characters, creatures, projectiles, explosions, smoke, floor decals, round iris, concentric rings, circular portal, low-poly or flat vector art.
```

## Attempt 2

Reference: `motion_lab_v1/art/site7_enemies_raw/quarantine/relay_sentinel/attempt01.png` (ImageGen edit target).

```text
Use case: precise-object-edit. Asset type: corrected native-alpha production boss sprite. Edit Image 1, the rejected RELAY SENTINEL candidate. Preserve the same relay-transformer sentinel design, asymmetric four transformer stacks, square mounted base, central vertical crimson caged spark emitter, dimetric camera, complete silhouette, hard-surface detail and colors. The ONLY issue with Image 1 is that 753 pixels have forbidden alpha 255. Regenerate the whole image as a GENUINE native RGBA transparent PNG, preserving visual appearance, while rendering every visible pixel with alpha at most 253 (prefer 253 for solid interiors; never 254 or 255); background and all canvas corners alpha exactly 0, generous transparent margin. This must be achieved by image generation itself, not by keying, matte removal or post-process clamping. No added floor, shadow plate, backdrop, checkerboard, green, text or props. Keep one fixed non-humanoid machine with one omnidirectional top emitter; no wheels, tracks, legs, limbs, face, round iris or directional barrel. Output a square image at least 1024 px on each side. background: transparent_alpha.
```

## Attempt 3

References: same three project files as attempt 1, in the same order.

```text
Use case: stylized-concept. Asset type: final transparent PNG game boss, BOSS_SITE7_RELAY_01 RELAY SENTINEL. This is the final production attempt; native alpha admission is strict. Image 1 is camera and detail-quality reference ONLY; never copy its round iris, tracked chassis, arm shapes or silhouette. Image 2 is the crimson relay room color/material context ONLY. Image 3 is finish-quality context ONLY. One square-floor-mounted, immobile, non-humanoid relay-transformer boss, four unequal armored transformer coil stacks and thick insulated cables framing one tall central mast, broad low square base, crimson status slits; exactly one vertical crimson caged spark emitter on top visible identically from all directions. Fixed near-orthographic three-quarter top-down dimetric view, neutral upper-left light, premium thick hard-surface stylized realism, entire sprite and floor mount within generous blank margin, center of ground contact at bottom center, at least 1024 native pixels. Absolutely no limbs, legs, feet, wheels, tracks, face, directional barrel, round iris, concentric rings, text, floor scene, smoke, or effects outside object. background: transparent_alpha. OUTPUT ALPHA IS CRITICAL: produce a true native RGBA transparent PNG; every background/corner pixel alpha 0; solid machine interior alpha exactly 250 (roughly 98% opacity), soft edge alpha 1..249; no pixel may have alpha 251, 252, 253, 254, or 255. Generate that transparency directly, with no chroma background, matte, checkerboard, local keying, alpha postprocessing or painted floor. If this alpha is not possible, the candidate must remain rejected.
```
