# Blender 5.2.1 LTS Portable — Validated

## Fixed executable

- Version: `5.2.1 LTS` (`9e2066aef7ef`, built 2026-08-25)
- Portable archive: `tools/blender/blender-5.2.1-windows-x64.zip`
- SHA-256: `0e631dad7d0cad6d5d18abdd2e2550f6c0213215334eda00ddbd3d22b96ecb2c`
- Executable: `tools/blender/5.2.1/blender.exe`
- Installation record: `tools/blender/5.2.1/INSTALLATION.json`
- No external Blender installation is a SABLE pipeline dependency.

## Validation run

The fixed executable completed this headless command on 2026-08-29:

```powershell
tools/blender/5.2.1/blender.exe --background --python \
  art_src/pilot_v2/blender/validate_blender_5_ual.py -- --project-root <repo>
```

It reported `5.2.1 LTS`, exposed `bpy.ops.import_scene.gltf`, imported each
approved UAL GLB, and ran Python successfully. Both sources yielded one
armature with the standard pelvis/spine/head/limb hierarchy and 43 actions.
The validation explicitly records `visual_mesh_promoted: false` for both.

## Blender 5 compatibility rule

The V2 scripts use the Blender 5 Eevee enum `BLENDER_EEVEE`, not the old
`BLENDER_EEVEE_NEXT` spelling. Batch render and pose-guide jobs must call the
fixed 5.2.1 executable above so their result is reproducible.
