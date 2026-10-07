# Retained technical-fixture failure

The paired exporter and root/camera binding completed, but the runner's expected
world-space vector assertion failed. The fixture assigned a world-space (x,y,z)
vector directly to PoseBone.location, which is bone-local; this bone's Y follows
world Z. The observed displacement was (1.45,-0.58,0), not (1.45,-0.5,0.08).
R2 explicitly converts the requested world offset into rest-bone local axes.
This failure is a synthetic fixture-authoring bug, not character approval.
Files are retained; no production asset is referenced or changed.
