# GLOBAL 1080P VISUAL EVIDENCE CONTRACT

Authority: user project-wide condition, 2026-08-30 (Asia/Seoul).

## Contract

All SABLE CIRCUIT art-pipeline review outputs are authored or captured at a
native minimum frame of 1920×1080.  This includes contact sheets, HTML review
canvases and browser captures, Godot runtime screenshots, comparison frames,
and review videos.

Low-resolution art enlarged into a 1920×1080 container is not evidence of
high-resolution quality.  Every visual manifest or QA record must distinguish:

- source/master resolution;
- runtime atlas cell and atlas resolution;
- review canvas/capture resolution;
- whether any scaling occurred and, if so, its purpose.

Runtime sprite resolution remains governed by actual gameplay readability,
memory, and frame-time requirements.  A runtime-sized sprite must therefore be
shown at its actual in-game scale in a native 1080p combat capture, while an
original-scale panel or crop verifies fine anatomy, hands, rifle continuity,
materials, costume continuity, and alpha/chroma edges.

## Gate

A new review artifact fails this contract when any of the following is true:

- the review frame is below 1920×1080;
- a low-resolution render is merely enlarged and presented as quality proof;
- native/source/runtime resolutions are omitted from its evidence;
- only a thumbnail exists for a visual-quality decision;
- the 1080p frame does not show the asset at actual game scale when runtime
  readability is being claimed.

Existing sub-1080p evidence remains historical only.  It must be regenerated at
1080p before being used for the current promotion decision.

## Automated gate

Run `tools/art_pipeline/validate_visual_evidence_1080p.py` against every current
review image, video, and interactive HTML before a visual gate is submitted.
The validator checks native container dimensions and decodability.  Its PASS is
not an art-quality PASS and cannot prove that a low-resolution source was not
upscaled; the producing manifest must still record source, runtime, review, and
scaling resolutions.

An HTML file alone is static configuration evidence and is labeled
`PASS_STATIC_CONFIG_ONLY`; it does not prove that Chromium rendered the page at
that size.  For an interactive review gate, run the validator with
`--require-dynamic-capture` and include at least one actual native 1920×1080
browser capture or review video.  Sub-1080 captures remain historical FAIL/HOLD
even when their behavioral observations are still useful.
