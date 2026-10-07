# Round 5: bounded closure of the two R4 residual cases

Actual changes, not altered old receipts:
- Removed phase-difference pixel subsampling completely. Absolute mean and bad
  pixel fraction, as well as relative comparisons, visit EVERY differing pixel.
  Thresholds12 /48 /10% unchanged. The64px boundary ghost rejects,65px interlaced
  ghost rejects, normal65px motion passes. Added all three actual FFV1 cases.
- After complete quoted spans are consumed, remaining unmatched opening quote
  sections are excluded through end-of-line. They cannot expose a candidate path
  suffix to unquoted lookup. Added all three delimiter negative cases, retained
  real space-containing path and actual output boilerplate positive cases.

Actual local results after these changes:
- All Python96 tests passed in184.265s.
- Actual rifle source-cycle VP8:107 frames passed complete difference-region
  checks in8.138s. Art has not changed to make the validator pass.
- Godot authored-machine emitter + locked telegraph388 checks and actual projectile
  owner/ordinal339 checks passed. These are not visual quality approvals.

Please only retest your R4 sampling-boundary and unclosed-quote counterexamples
and their stated positive controls. The eight attached files are current-byte
sources, not a whole-project runtime package. If those cases are blocked, state
that limited result; do not imply unseen art, whole MVP or Luna reproduction PASS.
We continue the separately tracked asset production and R1 work locally.
