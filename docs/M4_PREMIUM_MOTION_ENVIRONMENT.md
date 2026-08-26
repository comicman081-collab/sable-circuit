# M4 — Premium Directional Motion, Reactions, Boss Phases & Site-7 Environment

## Scope
M4 raises the M3 high-resolution identity assets into a more expressive 2.5D presentation without changing combat authority or enabling deployment.

## 1. Eight-sector character presentation
- Facing sectors are 0..7: E, SE, S, SW, W, NW, N, NE.
- Direction changes depth ordering, rear/front shading, head/torso perspective and weapon/arm z-order.
- Rear sectors hide facial micro overlays; front/side sectors show them.
- ASTER, ROOK and MICA keep separate perspective/motion coefficients.

## 2. Facial and secondary motion
- A vector facial micro rig provides identity-specific eyes, brows, blink behavior, aim-following pupil offset and hit response.
- Hair/accessory motion is spring-damper driven from acceleration and aim angular velocity, not a shared sine wobble.
- ASTER uses quicker, sharper trailing motion; ROOK uses heavier, damped mantle motion; MICA uses softer long-delay coat/sensor motion.

## 3. Enemy hit and death identity
- Rifle: shoulder/body kick and metal fragment tumble.
- Shield: shield-first recoil and heavy slab/armor collapse.
- Drone: banking hit reaction and spiral electronic breakup.
- Aberrant: elastic torso/skull/tail reaction and organic contraction/tear breakup.
- Signal Anchor Guardian: iris/arm recoil followed by ring/pylon collapse.

Death presentation is a detached runtime sequence so gameplay defeat authority remains exactly-once while visible destruction can continue after the authoritative enemy node is removed.

## 4. Boss phases
Signal Anchor Guardian uses health thresholds:
- Phase 1: >66% — base orbital behavior.
- Phase 2: 34–66% — widened ring/pylon presentation plus additional angled lance pattern.
- Phase 3: <=33% — accelerated iris/arm instability, shorter attack pressure and five-way lance pattern.

## 5. Stage 01 environment identity
The eight authored rooms have distinct animated environment signatures:
1. Outer Gate — gate ribs + amber access terminal.
2. Decon Corridor — cyan strips + drifting decon mist.
3. Archive Annex — physical shelves + scanning hologram.
4. Containment Junction — red alarm glow + barricades.
5. Core C — violet iris rings + energy columns responding to boss presence.
6. Emergency Lift — moving green lift rails.
7. Emergency Stores — amber crate cluster.
8. Signal Lab — live teal waveform + scanner arcs.

## Non-reuse rule
M3's no-reuse contract remains mandatory. M4 motion/reaction/environment signatures may share code infrastructure, but identity-specific presentation parameters and authored room signatures may not collapse into a single reused visible result.

## Validation
M4 CI must retain M1/M2/M3 regression gates and additionally verify:
- premium operator presentation and facial rig,
- all eight facing sectors,
- front/rear face behavior,
- enemy premium presentation,
- detached identity death sequence,
- boss Phase 3 threshold,
- exactly eight distinct Stage 01 room signatures.

Public deployment remains disabled.
