# Active checkpoint — 2026-09-13 19:02 KST

This is a recovery checkpoint written while implementation continues, not a
completion report or permission to stop after giving status.

- GPT 6 Pro round8 actual reply was read in the same existing conversation.
  `gpt6pro_round8_observed_review.json` records an agent summary, not invented
  verbatim text. R8-01/02/03 capture defects were implemented and tested.
- `tests/render/site7_anchor_capture_smoke.gd` passed 52 actual Godot checks:
  missing/malformed candidate isolation, hidden/offscreen artwork, real warning
  clocks and damage at 30/60/120Hz, and actual no-warning negative subclass.
  Passing receipt: `anchor_capture_edges_1789292477_647/report.json`.
  First failed fixture run stays retained at `anchor_capture_edges_1789292389_472`.
- Normal app capture with an explicitly nonexistent candidate path succeeded:
  `anchor_native_1789292550_916/capture_report.json`; 22 native 1080p WebP images,
  candidate_input_read=false. Phase2 warning+impact and phase3 impact were viewed.
  This is controlled attack capture, not full gameplay visual approval.
- Actual additional harness bug: cycle-rejected non-E sources were skipped for
  new directions. `cycle_followup` now prioritizes failed slots and pending
  completed cycles, but preserves explicit source rejection and E pilot review.
  The first full run exposed pilot ordering regression; it was fixed, not
  excused. Full current Python run: 101 tests OK, 196.763s, in
  `r9_workflow_regression_v2.stderr.log`. Negative decoder fixture stderr remains.
- Round9 was actually submitted with 16 frozen code/evidence files plus native
  phase2-warning and phase3-impact images. `gpt6pro_round9_submission.json`.
  Reply is pending; do not claim it approved. Same conversation URL ends
  `6aa629cc-15f0-83ee-996c-b42d58eefe91`; model 6 Pro.
- SE whole cycle was rejected for upper-body/gun projection drift in frames
  3/4/5. The old kit `motion_lab_v1/qa/site7_rifle/gait/43a8fd788749c694_75694577`
  is not approved. Its actual video and evidence stay retained.
- SE/walk/3 v3 is newly source-approved only, SHA256
  `818568119a629197c56aedffb41d2bdc0d6a04871b64b80994f201ca72fe14ff`.
  Raw SHA256 `655b5b9ba82379fb7c4193c53fa68daa6f2dfdf466362c786a13c6ad96ac1844`.
  References: exact phase3 guide + native upper crop of SE1, no competing full
  leg reference. Native upper/lower light+dark panels observed two leg chains
  and improved foreshortened weapon. This is not whole-cycle approval.
  Raw/tool response/normalization/mask and prior failed copies remain retained.
- Next exact action is SE/walk/4 repair, then SE/walk/5, then fresh full SE cycle
  review at actual speed before new directions. Current packet
  `motion_lab_v1/qa/site7_rifle/handoffs/20260913_190120_654347.json`.
  The SE idle image may also need projection comparison after the cycle repairs.
- No player art/gameplay, enemy registry pointers or production deployment was
  changed in this batch. Rifle/shield/aberrant art integration remains incomplete.
  Technical regression success is not Luna generation success or complete MVP.
