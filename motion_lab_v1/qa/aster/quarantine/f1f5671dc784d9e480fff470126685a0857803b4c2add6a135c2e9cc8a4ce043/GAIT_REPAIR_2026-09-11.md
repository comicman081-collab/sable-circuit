# ASTER gait repair — in progress, NOT a reviewed delivery

## Reproduced in the existing browser package

Input SHA: `73c47e327c5f37eedba6e599387b6765f8f1aa09d54f66b071d3ec4ddaceb913`.
At phases `[0, .17, .34, .51, .68, .85]`, the actual browser renderer returned
`[5, 5, 5, 5, 5, 5]` for both non-firing WALK and RUN. `fullBodyFrame` routed
walk/run through the fire-recovery branch. Position/shot tests did not catch it.

Moving fire selected `coherent/move` (old `move_360_ual_v6`) instead of the
modern profile. Its generator fits and deforms 2D leg pixels from a static
authority while preserving the upper body. This is the rejected leg-waving
path, not the accepted MICA authored-frame route. The recipe's six walk images
also lacked passing/opposite-leg phases; distinct hashes were not proof.

## Implementation underway

- Fix actual walk/run selector; add renderer tests with and without firing.
- Clear shot event history on reset, expose actual action/frame count in debug.
- Modern compiled profiles explicitly choose `authored_frames`; stale legacy
  bundles cannot override those clips. Shared MICA recoil leaves support feet
  unchanged and shares its transform with the actual muzzle.
- Add a 40-case live temporal matrix and validate decoded lower-body pixels,
  not just actor travel. Full runtime PASS requires both this and input QA.
- Approved runtime review/delivery now needs a bound motion video, not only a
  still screenshot. Numerical tests do not grant anatomy/visual approval.
- Add native pair intake and original-scale light/dark gait previews; preserve
  previous sources and original tool metadata. No leg resynthesis in scripts.

## Source generation observations

Six-figure E pilot established leg-role progression but cells were too small
for the existing 656px atlas. Not promoted. SE six-figure request repeated EAST
camera; S repeated the same leg in both halves. These are failed candidates.
The approach changed to native two-figure opposite-pose pairs, one guide per
pair. E's 6 native separated frames (about 965–1001px tall, no upscaling) now
show cyan-left versus pouch-right contact/passing/swing roles distinctly.
The E native panels and chronological contact sheet are under
`qa/aster/gait/7befe3013142a0ba`.

S walk pair attempts showed rifle foreshortening drifting toward SE. A new
direct-front aimed idle master is being used as the strict upper-body/camera
reference for the next attempt. Do not package the earlier S attempts as S.

## Remaining before completion

Finish/inspect all 8 direction walk + planted aimed idle sources, exact source
reviews, compile/package, actual held-mouse/input and temporal browser checks,
native runtime video and visual review. Preserve movement speeds; running may
reuse the walk cycle at faster distance cadence as MICA does, but must not be
described as a separately authored sprint. No real Luna reproduction performed.
The existing opened standalone HTML has NOT yet been replaced in this repair.
