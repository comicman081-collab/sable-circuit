# SABLE character fast pipeline

This is the shortest production-safe path for adding another playable
character after ASTER.

The first pass is intentionally eight-direction full-body playback. It avoids
copying ASTER's character-specific 16-way upper/lower split, while retaining
directional movement, firing, visible muzzle ownership, exact-alpha runtime
assets, and a later upgrade path to independent 16-way aim.

## One-time preparation

1. Copy `character_spec.template.json` to a character-specific JSON file and
   replace every placeholder and path.
2. Run:

   `python tools/character_pipeline/sable_character_pipeline.py init --spec <spec.json>`

3. Give the generated `IMAGEGEN_HANDOFF.md` to Codex built-in ImageGen. The
   generated source master and eight direction masters must remain under the
   character work root. No local image generator may author or repair them.
4. After `COSTUME_CONTINUITY_PASS`, use Blender+UAL to export the three exact
   green vertical atlases for every direction as defined by
   `BLENDER_UAL_HANDOFF.json`.

## Motion candidate promotion and runtime build

The Blender+UAL candidate must contain `SOURCE_PROVENANCE.json` with a native
1024px-or-larger ImageGen authority source (never an upscaled smaller image), and:

`<DIR>/<idle|move|fire>_green.png`

for `E, SE, S, SW, W, NW, N, NE`.

When a spec defines `gait_completion_gate`, a candidate is not promotable
until every direction uses the requested single ImageGen gait revision and it
contains the named Ponytail FULL acceptance JSON.  That JSON must mark every
direction PASS and link native 1920×1080-or-larger gait review evidence.  A
partial direction repair, a fallback revision, frame-count-only QA, or a
synthesized atlas video is never a visual completion gate.

Run:

`python tools/character_pipeline/sable_character_pipeline.py promote-motion --spec <spec.json> --candidate <candidate-dir>`

`python tools/character_pipeline/sable_character_pipeline.py all --spec <spec.json>`

The pipeline atomically builds RGBA atlases, keeps current plus one previous
package, proposes per-direction muzzle sockets, creates a native 1920×1080
contact sheet, writes the Godot descriptor, and performs structural QA.
Automatic muzzle sockets are proposals until visually reviewed.

After review and required UI assets are present:

`python tools/character_pipeline/sable_character_pipeline.py register --spec <spec.json>`

The shared `FastCharacterRuntime` activates automatically from the resulting
`authored_runtime_descriptor` profile field. ASTER remains on its higher-
fidelity bespoke runtime.
