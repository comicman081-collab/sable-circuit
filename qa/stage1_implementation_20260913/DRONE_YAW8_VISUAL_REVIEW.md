# Drone facing repair — observed local MVP review

Reviewer: current main implementation agent, 2026-09-13. This is not a user
approval, independent Ponytail review, GPT art approval or Luna reproduction.

Exact candidate: `motion_lab_v1/qa/stage1_enemies_20260913/drone_yaw8/a2a58793089e24f3/candidate_spec.json`
SHA256: `f3cc4fb74925e0a84fb1c475911af0c4e3e0ac4467cfb4d092b0ed41dfe880a8`.

Observed all eight original illustrations, the original-scale emitter panels
over light/dark mattes, and all eight actual-emission frames in the native
1920x1080 game scene under `facing_native_1789285783_092/`.

- E/W show the front toward the target at the corresponding side, with the
  magenta firing orb under the forward sensor cluster. Sideward shots start
  at that orb, not at the floor root or rear thruster.
- SE/S/SW expose the frontal sensors toward the lower-half target. S is a
  frontal view; diagonal views retain the asymmetric sensor arrangement.
- NW/N/NE expose rear hull/vents while the nose faces the upper-half target.
  Rear views partially occlude the forward orb behind the hull. The projectile
  begins at its authored projected location; this is a flat sprite, not 3D
  projectile occlusion or a rotating turret.
- No green or painted checkerboard is visible in the reviewed drone runtime
  edges. The rejected four-thruster N v1 and mirrored-sensor SW v1 are not used.
- The sprite is a rigid floating machine. Bounded bank/bob is appropriate;
  this review makes no biped/quadruped gait claim. No bitmap mirror or screen
  rotation manufactures the eight views.
- These are controlled facing cases, with other combat actors hidden/frozen.
  The southern target overlaps the HUD/canvas edge. They are not a complete
  playthrough or a player-character anatomy review.

Decision: accept this exact eight-view drone appearance for the local Stage 1
MVP connection, contingent on the app registry/integration and current-code
regressions passing. This does not approve remaining humanoid enemy motion,
the boss, deployment, all Stage 1 art, or earlier rejected assets.

The 1080p validator report only establishes capture resolution/decoding.
GPT reviews 6/7 concern code defects, not these visual observations.
