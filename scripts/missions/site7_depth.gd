extends RefCounted
## Draw order of grounded actors and cover props by their ground y. z_index only
## spans -4096..4096 and projectiles draw at 3000, so bodies get 200..2999: 0.5 px
## per step over a 1400 px window that the battlefield keeps centred on the camera.
## The mission maps climb 3000+ px, more than the window, so a fixed origin would
## flatten every body above or below it into one layer.

const BASE := 200
const STEPS := 2799
const HALF_WINDOW := 700.0
static var origin_y := -HALF_WINDOW

## Whole-pixel origin, so moving the window never reorders two bodies.
static func follow(camera_y: float) -> void:
    origin_y = floorf(camera_y) - HALF_WINDOW

static func z_for(y: float) -> int:
    return BASE + clampi(int((y - origin_y) * 2.0), 0, STEPS)
