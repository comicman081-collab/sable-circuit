# Ponytail FULL — r3 limited actual retarget/replay review

Verdict: **PASS for this limited retarget/replay check only**.
MICA identity, calibrated gait/contact, shooting and runtime remain HOLD.

The reviewer directly read r3 retarget/capture/video manifests, native validation,
current probe/capture code and the original UAL animation time accessor. Forty-five
file references (code, inputs/scenes, 33 PNGs and video) matched their SHA values.
The reviewer visually inspected PNG 000 and 016; did not play the MP4, and used
its exact hash plus existing native decoding results for the video-container check.

- Source, baked and captured cycle duration: approximately 1.333333 seconds.
- Initial 25 samples versus baked replay: maximum corresponding sole-vertex
  difference 0.0m.
- Reloaded capture versus bake: nine common times (frames 0,4,...,32), 108 sole
  vertices at each, maximum position/time difference 0.0m / 0.0s. The other
  capture samples do not have a one-to-one prior sample; no such claim is made.
- Captured forward sole-centroid excursion: left 0.693624m, right 0.693257m.
  F0/F16 exchanges left/right forward position; F0/F32 seam difference is 0.0m.
- Diagnostic capture guards the camera world matrix per frame and completed
  without detected transform drift. It does not independently guard projection
  or ortho_scale, so this is not the full production camera-lock gate.
- Video: 32 unique frames repeated three times, 24fps, four seconds. Not three
  independently simulated cycles and not ground-referenced actor movement.

Review was read-only; no render, edits or Luna execution were performed.
This document is not a source/pose/motion production receipt.
