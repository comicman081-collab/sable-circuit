# Failed first construction: Blender library list alias

FAIL_NOT_PROMOTABLE. No mesh, pose image or animation was rendered. The owned
Blender child exited with code 2 and the runner wrote BUILD_FAILURE, never
JOB_COMPLETE. All original licensed/source inputs remain unchanged.

The library loader mutates its assigned objects list from names to objects.
`selected.objects = wanted` aliased the expected list; after loading,
`o.name == wanted[0]` compared a string against an Object and raised
StopIteration. The checked source objects existed; this was adapter API usage,
not an art failure and not a reason to regenerate source art.

Fix: pass `list(wanted)` to Blender and retain the independent expected names.
The exact old builder is preserved in `build_mica_anatomical_candidate_R1_snapshot.py`.
The failed folder moved intact from `art_src/characters/mica/rigged_v2/model_r01`
to this quarantine directory. No failed asset or log was deleted. The original
build attempt and runner/builder claims remain consumed; do not reuse them.
Review the changed builder/new output plan before any further attempt.
