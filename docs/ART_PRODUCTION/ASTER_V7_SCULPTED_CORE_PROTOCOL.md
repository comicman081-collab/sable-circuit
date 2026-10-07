# ASTER Body Construction Gate Protocol

## Decision

The rejected v2-v5 construction method assembled visible character parts from
rounded primitives and boxes.  v6 and v7 then fused overlapping forms with a
voxel remesh, which averaged away the jaw, hand, foot, limb, and torso planes.
They are rejected source experiments.  A first V8 implementation also failed
the Stage-1 mass gate: its head, grip wedges, and lower-body joins still read
as a mannequin and its render backdrop was not a valid flat source matte. The
V8 code/output were discarded. Any later human-authored continuation must use
the following construction premise, rather than another procedural variant:

`camera lock → separated anatomical poly masses → mass gate → manual join/retopo → rifle/hand lock → boot shells → jacket/armour shells → face/hair → animation bake`

No asset beyond the repository, Blender's built-in modelling tools, and the
already-approved UAL motion source is permitted.  UAL is never visual
geometry.  v7 introduces no runtime or gameplay change.

## Immutable ASTER identity

- Adult, slender precision-rifle operator; 4.8–5.2 head combat proportion.
- Silver comet ponytail; deep-navy asymmetric short jacket; selective cyan and
  gold accent; narrow coil precision rifle.
- Right hand is the rifle primary grip; left hand is the support grip.
- Fixed quarter combat camera: orthographic, approximately 45-degree yaw and
  50–55-degree downward pitch.  No mirror-facing export.

## Stage 1 — separated manual clay masses only

This stage contains no coat, armour, hair, rifle, material finish, or runtime
asset.  It begins from separate original cube/low-poly masses and must not use
voxel remesh, implicit surfaces, a downloaded base, or a mannequin.  Head,
ribcage, waist, pelvis, upper arm, forearm, hand wedge, thigh, calf, and foot
wedge are individually inspected from the fixed combat camera.  The mass
assembly must make these forms explicit before any join or overlay is
permitted:

| Region | Required sculpt read |
| --- | --- |
| Torso | Separate ribcage, waist narrowing, and pelvis masses |
| Shoulder/arm | Deltoid-to-upper-arm transition, elbow break, forearm taper |
| Leg | Thigh planes, knee plane, shin front, ankle break |
| Foot base | Instep and heel separation; never a rectangular foot block |
| Head | Cranium, cheek/brow, and jaw plane; never a ball head |
| Hand base | Palm and thumb/finger volumes that can later wrap a grip |

### Mass gate

The untextured core is rejected immediately if any condition holds:

- torso reads as one cylinder;
- limbs read as capsules/tubes;
- head is oversized or spherical;
- hands read as balls;
- feet read as blocks;
- the camera-facing silhouette reads as a chibi or mannequin.

Passing this gate only allows manual joins and a retopo cage; it is not
approval to export or connect the body to Godot.

## Stage 2 — retopo and rifle-hand lock

After the manual-mass approval, bridge/join only the approved adjacent masses
and make a quad-dominant deformation cage preserving the
ribcage-to-waist-to-pelvis flow and clean loops at shoulder, elbow, wrist,
hip, knee, and ankle.  A limited remesh is allowed only to repair a specific
join after its planes are captured in the retopo; it is never a source-body
generator.  Freeze the narrow coil rifle before sculpting hands.
The right primary and left support grips receive permanent target nodes; palms,
thumbs, and fingers must visibly wrap their respective grip.  If this contact
does not read in the locked combat camera, stop before boots or garments.

## Stage 3 — wearable shells, then identity layers

Boots are separate wearable shells with cuff, upper shaft, ankle pinch,
instep, toe box, sole/heel, and shin panel.  The jacket has collar/neck
transition, asymmetric shoulder attachment, waist overlap, hem thickness, and
an actually asymmetric silhouette.  Only then add the scalp cap, face planes,
side locks, ponytail root, and three to five tapered ponytail clumps.

## Promotion gates

1. `CORE_GATE`: continuous adult clay body passes the locked-camera review.
2. `GRIP_GATE`: two hands visibly grip the final rifle; no ball hands or
   detached wrist connection.
3. `SHELL_GATE`: boots/jacket/armour read as worn, attached structures.
4. `IDENTITY_GATE`: silver ponytail, asymmetric navy jacket, and narrow coil
   rifle read at native combat scale.
5. `ANIMATION_GATE`: only then create rig, UAL-derived motion, bake, and
   runtime visual proxy.

Failure at any gate stops the pipeline at that stage.  No rejected output can
be promoted as a temporary runtime body.

## Rejected V8 implementation evidence

- The headless Blender output contained only SABLE-authored procedural clay
  masses, with no downloaded character mesh, UAL visual mesh, mannequin,
  voxel remesh, or runtime export.
- It still failed `CORE_GATE`: oversized faceless head, round grip wedges,
  abrupt limb/torso transitions, and an overall mannequin rather than an
  adult tactical operator. Its green plane was also a floor under the locked
  camera rather than a uniform source exterior.
- The exact output folder and its construction script are deleted. This
  failure does not authorize a low-poly cleanup pass. It proves procedural
  mesh assembly is not the next production route for the required visual bar.
