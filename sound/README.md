# SABLE CIRCUIT exclusive soundtrack

The user assigned these ten tracks from the shared sound library on 2026-09-20.
Do not put them back into a shared pool or reuse them for another game.

- `music/originals/`: byte-identical masters, including original file names.
- `music/runtime/`: the nine scene-music payloads; only these are exported.
- `music/quarantine/`: a prior, replaced intro cue retained outside the runtime.
- `music/catalog.json`: scene keys and conservative per-track playback gain.
- `music/allocation.json`: original shared paths, SHA-256, roles and retirement state.
- `music/*SOURCE_README.md`: original pack provenance statements.

No other game's project files were imported. The allocation is forward-looking;
it is not a claim that historical usage in every other project was audited.

Title, base/briefing, five operations, bosses and results have scene music.
Operations 6-10 (all playable) own no track yet:
`DemoMusic.stage_key` reuses the stage cues in order (6 -> stage1 ... 10 ->
stage5) until `stage6`-`stage10` are added to `music/catalog.json`.
The intro plays the original audio already embedded in its six source video
clips, not a separately selected library song. The earlier Break the Barricade
runtime copy is preserved in quarantine after the complete video-audio
replacement was validated. Title music still uses Steel Horizon. Music
crossfades separately from SFX.
Use the title MUSIC button or M to mute/unmute music without muting effects.
Browsers may require a click or key press before any audio can begin.
