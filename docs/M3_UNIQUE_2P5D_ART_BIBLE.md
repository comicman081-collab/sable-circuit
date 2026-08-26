# M3 — Unique 2.5D Art & Combat Feedback Bible

## Non-negotiable production rule

SABLE CIRCUIT may share **systems**, semantic rig names, import tooling, shader/VFX code and audio playback code. It may **not share visible or audible final content identities** across playable characters, enemy archetypes or bosses.

Forbidden duplication includes:
- final character body/face/hair/clothing/weapon art
- enemy bodies or silhouette bases with recolors/ornament swaps
- weapon art
- projectile art/signatures
- impact/hit VFX signatures
- weapon fire sounds
- impact sounds
- defeat/death sounds
- animation personality curves used as a hidden clone between identities

A reused system is allowed. A reused final asset or perceptually identical result is not.

## Playable identity matrix

### ASTER — Assault
**Read:** fast precision / forward momentum / airy technology.
- silhouette: short asymmetric jacket, comet ponytail, right-shoulder plate, long narrow rifle
- locomotion: quick two-beat step, forward lean, restrained vertical bob
- aim: rifle rides high and stable; eyes/head settle before shoulders
- recoil: short sharp impulse, immediate return to sightline
- secondary motion: ponytail delayed one beat, jacket tails snap lightly
- projectile: cyan-white needle / segmented wake / gold tip
- hit VFX: three-way prism splinter
- fire sound: tight coil-metal snap
- hit sound: ceramic tick + crystalline micro-shatter

### ROOK — Breach
**Read:** mass / close-range force / mechanical impact.
- silhouette: broad cropped mantle, heavy left gauntlet, compact blunt hair, rectangular scattergun
- locomotion: low center of gravity, heel-heavy steps, larger shoulder counter-rotation
- aim: weapon held lower with visible bracing
- recoil: full torso compression and slower recover
- secondary motion: mantle lags, gauntlet inertia visibly pulls arm
- projectile: five amber shards in widening fan
- hit VFX: pressure ring + square sparks + debris chunks
- fire sound: chamber thump + metal clack + sub punch
- hit sound: dense plate slam + gravel fragments

### MICA — Support / Recon
**Read:** controlled analysis / graceful motion / sensor technology.
- silhouette: long split tech coat, twin sensor fins, rounded side braid, compact circular-emitter carbine
- locomotion: upright glide-like cadence, softer step rhythm
- aim: sensor leads, weapon follows; less shoulder aggression
- recoil: restrained, followed by a visible sensor settle
- secondary motion: coat/fins continue after torso stops
- projectile: mint hollow pulse bead + telemetry dots
- hit VFX: hex scan bloom + rotating arcs
- fire sound: electronic pop + descending sonar chirp
- hit sound: digital tap + filtered fizz

## Enemy identity matrix

### SITE-7 Rifle Trooper
Narrow humanoid hazard silhouette. Cautious patrol, snap-to-alert, disciplined bursts. Red-white dash tracer. Small pale fork sparks. Dry suppressed crack and thin plate ping.

### SITE-7 Shield Breacher
Large slab shield is the silhouette anchor. Slow shield-first stomp, brace, hydraulic ram. Fat brass plasma slug with rectangular wake. Broad angled spark sheet. Piston bark and heavy gong/hydraulic impact.

### SITE-7 Recon Drone
Non-humanoid crescent body with three unequal sensor eyes. Constant hover orbit, asymmetrical banking and darting. Magenta dotted packets. Electric crescent arcs and pixel sparks. Servo chirp/laser zip and glass-electronic hit.

### SITE-7 Aberrant Runner
Long forelimbs, collapsed shoulder line and trailing biofilament. Uneven crouch gait, head lag, explosive lunge. Violet organic glob if ranged state is used. Membrane-tear VFX. Throat/viscous release and damp fibrous impacts.

### Signal Anchor Guardian
No reuse from normal enemies. Suspended ring chassis, offset pylons, four emitter arms and inner iris. Slow orbital motion with phase-specific choreography. Wide rift-lance projectile. Iris rupture hit VFX. Multi-layer spatial charge/crack and structural/reversed-crystal impact.

## High-resolution 2.5D production target

Production masters are authored large and downsampled in runtime:
- playable master art: target 2200–3200 px character height equivalent
- normal enemy master: 1800–2800 px equivalent
- boss master: 3000–4500 px equivalent

Each production skin is decomposed into separately riggable elements. Minimum playable decomposition:
- face/base head
- hair front / back / optional side pieces
- torso upper / pelvis
- left/right upper arm, lower arm, hands
- left/right thigh, shin, feet
- weapon body / moving magazine or action parts
- character-specific coat, ribbon, fins, mantle, cables or accessories
- shadow
- muzzle / support-hand / VFX sockets

Enemy decomposition is archetype-specific rather than forced into the playable human template. Drone and boss rigs must remain genuinely non-humanoid.

## Motion policy

Semantic rig APIs may be shared, but **motion identity must not collapse into one animation with different colors**. Each identity receives its own authored values for:
- stride length and cadence
- pelvis vertical travel
- torso counter-rotation
- head lag/lead
- arm stiffness
- recoil amplitude and recover curve
- reload timing/body involvement
- evade/charge behavior
- secondary-motion delay and damping
- hit reaction family
- defeat/death choreography

## Projectile / impact / sound policy

Every combat identity has unique profile IDs for:
- `projectile_profile`
- `hit_vfx_profile`
- `fire_sfx_profile`
- `impact_sfx_profile`

Changing only hue, pitch or EQ is insufficient. Geometry/timing/rhythm/envelope must also differ.

Material hit variation is allowed *under* an identity profile (metal/flesh/shield/weak-point), but must not erase the attacker's signature.

## CI uniqueness gate

`tools/validate_unique_art.py` rejects:
- duplicate visual, motion, projectile, hit-VFX, fire-SFX or impact-SFX IDs
- duplicate final master-asset paths
- missing identity fields
- playable/enemy collisions in these namespaces
- same signature text reused as a shortcut

When production binary/audio assets are committed, this gate will additionally compare SHA-256 hashes so byte-identical visible/audio final assets cannot be accidentally reused under different names.
