# Tripo-to-SABLE motion repair: independent cause and architecture review

Status: **RECOMMENDED_GEOMETRY_REPAIR_WITH_PRODUCTION_HOLD**. Read-only review;
no Blender launch, production script execution, asset generation, target-rig
edit or promotion. The parent separately owns target-body intake and repair.

The appropriate next geometric change is retargeting the supplied Run onto a
separately licensed target whose genuine neutral REST soles define one level
floor. The Tripo standing pack remains an immutable reference input. Its native
standing action deliberately reproduces the supplied bind pose, including its
unequal sole heights; it is not a calibrated neutral locomotion rig. Applying a
single vertical offset cannot remove the 32.3887 mm difference between its two
REST sole bottoms. Frame-dependent root lowering or redefining the floor from
action minima would hide the defect and violate the existing contact gate.
The target's actual licence, skin and REST sole evidence still require checking;
this review does not infer those properties from its filename or a prior PASS.

The source's moving trajectory belongs to Hip, not Root. Across the unchanged
1.25-second action, Hip moves 4.91955 m horizontally and Root does not move.
The existing bridge's linear planar subtraction is a documented coordinate
transform only. It is neither a ground correction nor a complete root-motion
decomposition. Passing the stationary source Root to an actor controller would
lose the locomotion trajectory; applying both Hip translation and actor travel
would apply movement twice. Preserve raw world transforms and timestamps, record
the selected candidate actor trajectory separately, and use anatomical motion
relative to that trajectory for the target body. Keep vertical pelvis motion,
lateral sway and source timing visible in the audit.

The full action is not supported as one exact cycle. A read-only comparison of
eight leg joints relative to Hip gives its best nontrivial repeated offset at
24 of the 48 sample intervals, or 0.625 seconds. RMS coordinate difference is
17.36 mm across 25 overlapping pose pairs. Full-action endpoint difference is
55.15 mm by the same metric. This suggests roughly two similar strides in the
1.25-second clip; it does not prove an exact cycle boundary. The sampled source
also has several local sole-height minima per side. Do not rename the whole
clip as one cycle, average two dissimilar strides into a receipt, or replace the
real terminal sample with a copied first pose to satisfy the single-cycle
classifier. Locate homologous same-side events in the native action, preserve
their source times, inspect all intervening phases, and explicitly author any
required periodic transition in a new motion-only derivative. Evaluate genuine
repeated playback plus the seam and its velocities.

Recommended bounded implementation:

1. Keep the source Run and standing pack unchanged. Copy the chosen licensed
   neutral target into project-local working output. Before evaluating motion,
   establish world-up and forward axes, both thigh–calf–foot chains, real limb
   lengths, render-enabled Armature binding and actual sole surface IDs. The
   target's neutral REST geometry fixes the floor once.
2. Transfer anatomical leg/pelvis motion using source and target rest frames
   and limb lengths. Bone names are lookup keys, not proof that local axes or
   roll agree. Use the source's Hip trajectory explicitly and retain source
   frame/time information. Do not copy the source's heel-dependent ankle
   height, unequal neutral-foot offsets or spear pose into the target.
3. Add actual target-space foot/ankle constraints for authored support windows.
   Solve both foot placement/orientation and the thigh–calf chain with a stable
   knee pole; allow anatomically justified pelvis loading and unloading. A foot
   constraint must account for the sole-to-ankle transform and foot roll, not
   merely put the ankle bone at ground height. Lock stance against the intended
   world trajectory and blend constraint influence through lift-off/landing;
   do not hold a foot at a drifting actor-relative point. Preserve clear flight
   and distinct contact/down/passing states.
4. Audit evaluated target mesh vertices, not the IK targets, as ground truth.
   Include the actual heel/toe/sole surface needed throughout foot roll; the
   source pack's bottommost 2 mm REST subset is a diagnostic subset, not proof
   of an adequate target sole mask. Target support soles must meet the unchanged
   4 mm visual threshold and down poses must have the required 15 mm pelvis
   drop from same-side contact. Check knee bend, foot yaw, penetration, stance
   slip, leg reach, distinct support/flight and genuine cycle closure.
5. Keep independently specified SABLE actor speeds and reviewed display scale.
   Do not infer a new pixels-per-metre scale solely to make the Tripo mean speed
   equal the contract. If target proportions and stride require an explicit
   cadence/trajectory change, record it as a separate reviewed derivative;
   raw source time remains unchanged.

This is a real rig/motion correction, not a visual reconstruction. The generic
body, Tripo mesh and all local renders remain pose/contact evidence only. They
cannot supply MICA's final face, hair, coat, boots, weapon, atlas or HTML layer.

MICA's `SOURCE_RECEIPT_R7.json` has all 15 bound files intact. The two approved
E `flight_l` and `flight_r` frame receipts have all 26 and 25 bound files intact,
respectively. They each approve one visible frame. Their existing native rifle
grip and ImageGen appearance are worth retaining. They do not approve a new
Tripo cycle, timing, contact pose or independent move/aim matrix. The production
source-preserving adapter registry currently contains zero entries.

Once the target geometry is calibrated, the shortest complete visible-art route
is to use the exact existing approved artwork where it fits the reviewed phase,
then obtain the missing E contact/down/passing artwork through the current
one-frame ImageGen gates. Each changed pose and the resulting temporal sequence
need their own exact reviews. Existing one-frame receipts remain intact; bind
their reuse in a newly reviewed sequence rather than rewriting their old guide
hashes. If the chosen route instead deforms approved pixels, implement and review
the actual source-preserving adapter first. Projecting an illustration onto a
new visible generic body or rotating calf cutouts is not that implementation.

Firing must be solved separately from the Tripo spear-arm animation. Retain the
leg/pelvis gait and use target spine/chest aim plus hand constraints referenced
to the approved rifle grip. Match both hands and the shoulder interface through
the entire gait; do not freeze the full actor while firing. The final visible
barrel tip must be measured independently in the actual approved output and
bound to the same muzzle transform used for projectile spawning. Keep recoil,
reload and aim transitions on the same reviewed actor/runtime clock.

Begin with movement=aim E and its actual native gait/shot test. Eight rotations
of a forward Run do not produce strafe/backward motion or 8×8 independent firing.
For the wider matrix, use genuinely appropriate licensed lateral/backward
locomotion or explicitly authored target motion, combined with reviewed upper
aim poses and appearance continuity. The existing 30/60/120 Hz runtime, turns,
stop/resume, speed switching, reload, bounds/collision and live HTML parity
requirements remain unchanged. No contact, gait, appearance or runtime PASS is
issued by this architecture review.
