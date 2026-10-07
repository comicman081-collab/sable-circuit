extends Node2D
## What the SITE-7 level hangs over, drawn behind the plates wherever their flat
## outer void is see-through (site7_mood.gd void masks) instead of a black card.
## Code-drawn atmosphere, no painted art. Every mission has a dark depth colour;
## two banks of fog that drift and move slower than the camera (parallax); the
## plates' lamp light scattered into the haze under each floor; and dust drifting
## up through it. Below that its STYLES entry: a shaft of broken girders along the
## level's own dimetric axes with work lights; black flood water with ripples and
## drip rings; the shaft with strobing lights and rising steam; molten seams
## behind black girders with embers; or the sea with swell, rain and rig beacons.
## One quad over the world bounds; the camera centre is the only per-frame input.
## Settings: the mission's "abyss" row in data/visual/site7_mood.json.

const MAX_GLOWS := 16
const MAX_CONTACTS := 15
const STYLES := ["shaft", "flood", "pressure", "forge", "offshore", "spore", "cryo", "dawn", "vault", "null"]
const SHADER := """shader_type canvas_item;
uniform vec2 camera_center;
uniform vec3 base_color = vec3(0.018, 0.024, 0.034);
uniform vec3 fog_color = vec3(0.07, 0.085, 0.11);
uniform float fog_strength = 1.0;
uniform float haze_strength = 0.16;
uniform int glow_count = 0;
uniform vec4 glow[16];
uniform vec4 glow_color[16];
uniform float far_light_density = 0.08;
uniform float dust_strength = 0.5;
uniform vec3 dust_color = vec3(0.8, 0.85, 0.9);
uniform vec3 work_color = vec3(1.0, 0.7, 0.42);
uniform int octaves = 4;
uniform int style = 0;
uniform vec3 style_color = vec3(0.3, 0.5, 0.6);
uniform float style_strength = 1.0;
uniform sampler2D contact_atlas : filter_linear, repeat_disable;
uniform int contact_count = 0;
uniform vec4 contact_rect[15];
uniform vec4 contact_uv[15];
uniform float contact_strength = 0.0;
varying vec2 world_pos;
void vertex() { world_pos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy; }
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}
float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < 5; i++) {
        if (i >= octaves) { break; }
        value += amplitude * noise(p);
        p = p * 2.07 + vec2(13.1, 7.7);
        amplitude *= 0.5;
    }
    return value;
}
// Girders `width` px wide along the two dimetric axes (2:1), `spacing` px apart,
// broken into runs; x: how much of a girder covers the point, y: work lights on it.
vec2 girders(vec2 p, float spacing, float width, float seed) {
    vec2 axes = vec2(p.x * 0.5 + p.y, p.x * 0.5 - p.y) / spacing + seed;
    vec2 line_id = floor(axes + 0.5);
    vec2 across = abs(axes - line_id) * spacing / 1.118;
    vec2 along = axes.yx * spacing / 1.118;
    float beam = 0.0;
    float lights = 0.0;
    for (int k = 0; k < 2; k++) {
        float run = noise(vec2(line_id[k] * 7.31 + seed * 13.0, along[k] / 900.0));
        if (run < 0.48) { continue; }
        float fade = smoothstep(0.48, 0.6, run);
        beam = max(beam, fade * (1.0 - smoothstep(width * 0.35, width * 0.5 + 2.0, across[k])));
        float slot = floor(along[k] / 170.0);
        float pick = hash(vec2(line_id[k], slot) + seed);
        if (pick < 0.3) {
            float gap = (fract(along[k] / 170.0) - 0.5) * 170.0;
            float d2 = gap * gap + across[k] * across[k];
            float flicker = pick < 0.03 ? step(0.35, fract(sin(TIME * 7.0 + pick * 90.0) * 43.1)) : 1.0;
            lights += fade * flicker * (exp(-d2 / 5.0) + 0.22 * exp(-d2 / 90.0));
        }
    }
    return vec2(beam, lights);
}
// A floor far below, seen along the level's dimetric view (twice as wide as tall).
vec2 flat_floor(vec2 p, float scale) { return p * vec2(1.0, 2.0) / scale; }
// Cracked crust: x = distance from the nearest crack (cell edge), y = the cell's
// own random value. Cell centres drift slowly.
vec2 crust(vec2 p) {
    vec2 cell = floor(p);
    vec2 f = fract(p);
    float d1 = 8.0;
    float d2 = 8.0;
    float id = 0.0;
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 g = vec2(float(x), float(y));
            vec2 o = 0.5 + 0.38 * sin(TIME * 0.04 + 6.2831853 * vec2(hash(cell + g), hash(cell + g + 19.19)));
            vec2 r = g + o - f;
            float d = dot(r, r);
            if (d < d1) { d2 = d1; d1 = d; id = hash(cell + g + 3.3); }
            else if (d < d2) { d2 = d; }
        }
    }
    return vec2(sqrt(d2) - sqrt(d1), id);
}
void fragment() {
    // A layer at depth k moves k of the camera's motion less: far fog, mid fog,
    // distant structure and near dust each keep their own parallax.
    vec2 deep = world_pos - camera_center * 0.8;
    vec2 far = world_pos - camera_center * 0.65;
    vec2 mid = world_pos - camera_center * 0.4;
    vec2 near = world_pos - camera_center * 0.15;
    float fog_far = fbm(far * vec2(0.0011, 0.0022) + vec2(TIME * 0.004, 0.0));
    float fog_mid = fbm(mid * vec2(0.0019, 0.0038) + vec2(-TIME * 0.007, TIME * 0.002));
    float density = smoothstep(0.3, 0.8, fog_far) * 0.55 + smoothstep(0.35, 0.85, fog_mid) * 0.45;
    vec3 color = base_color + fog_color * density * fog_strength;
    vec3 haze = vec3(0.0);
    for (int i = 0; i < 16; i++) {
        if (i >= glow_count) { break; }
        vec2 d = (world_pos - glow[i].xy) * vec2(1.0, 1.7);
        haze += glow_color[i].rgb * glow[i].w * exp(-dot(d, d) / (glow[i].z * glow[i].z));
    }
    color += haze * haze_strength * (0.45 + 0.9 * density);
    vec3 catch_light = fog_color * 0.8 + haze * haze_strength * 3.0;
    vec3 work = work_color * 0.5 + fog_color * 2.0;
    float rise = 16.0;
    float mote_glow = 0.0;
    if (style == 0 || style == 2) {
        // SHAFT / PRESSURE: two depths of broken girders with work lights; the
        // pressure deck's lights strobe and steam columns rise through the haze.
        vec2 low = girders(deep, 520.0, 12.0, 0.0);
        vec2 high = girders(far, 760.0, 22.0, 0.37);
        color += catch_light * (low.x * 0.25 + high.x * 0.45) * (0.35 + density);
        float strobe = 1.0;
        if (style == 2) {
            strobe = 0.25 + 0.75 * step(0.55, fract(TIME * 0.7 + floor(far.x / 760.0) * 0.37));
            float column = floor(far.x / 340.0);
            float offset = far.x - (column + 0.5) * 340.0 + (hash(vec2(column, 3.1)) - 0.5) * 160.0;
            float width = 36.0 + 30.0 * noise(vec2(column, far.y / 300.0));
            float steam = exp(-offset * offset / (width * width)) * step(0.45, hash(vec2(column, 9.7)));
            steam *= smoothstep(0.3, 0.7, fbm(vec2(far.x / 60.0, far.y / 260.0 + TIME * 0.3)));
            color += (vec3(0.16) + style_color * 0.4 + catch_light) * steam * style_strength;
        }
        color += work * far_light_density * 4.0 * strobe * (low.y * 0.45 + high.y * 0.8);
    } else if (style == 1) {
        // FLOODED: black water far below; ripples catch the rooms' light and
        // drips spread rings. Only the tops of the deeper girders stand clear.
        float dash = smoothstep(0.6, 0.85, noise(vec2(deep.x / 48.0 + TIME * 0.25, deep.y / 4.5)));
        dash *= smoothstep(0.35, 0.7, noise(vec2(deep.x / 260.0 - TIME * 0.05, deep.y / 60.0)));
        float lit_water = dot(haze * haze_strength, vec3(0.299, 0.587, 0.114)) * 12.0 + 0.15;
        color = color * 0.8 + (haze * haze_strength * 5.0 + style_color * 0.5) * dash * lit_water * style_strength;
        vec2 cell = floor(deep / 260.0);
        vec2 local = (deep - (cell + 0.5) * 260.0) * vec2(1.0, 2.0);
        float phase = fract(TIME * 0.22 + hash(cell));
        float ring = exp(-pow(length(local) - phase * 120.0, 2.0) / 30.0) * (1.0 - phase) * (1.0 - phase) * step(hash(cell + 7.1), 0.3);
        color += (catch_light + style_color * 0.5) * ring * style_strength * 0.35;
        vec2 high = girders(far, 760.0, 22.0, 0.37);
        color += catch_light * high.x * 0.35 * (0.35 + density);
        color += work * far_light_density * 3.0 * high.y;
    } else if (style == 3) {
        // FORGE: molten seams glowing through a dark crust far below, girders
        // standing black against them, embers rising fast.
        vec2 cracks = crust(flat_floor(deep, 95.0));
        float active = smoothstep(0.3, 0.75, fbm(flat_floor(deep, 700.0) + vec2(TIME * 0.008, 0.0)));
        float heat = 0.5 + 0.5 * sin(TIME * 0.9 + cracks.y * 40.0);
        float width = 0.03 + 0.05 * cracks.y;
        float segment = smoothstep(0.45, 0.75, noise(flat_floor(deep, 40.0) + cracks.y * 7.0));
        float core = exp(-cracks.x * cracks.x / (width * width * 0.4)) * segment;
        float halo = exp(-cracks.x * cracks.x / (width * width * 6.0)) * (0.08 + 0.92 * segment);
        float pool = smoothstep(0.9, 0.97, cracks.y) * smoothstep(0.04, 0.3, cracks.x) * 0.45;
        vec3 molten = mix(style_color, vec3(1.0, 0.8, 0.42), core * 0.5);
        vec3 under = molten * (core * 0.6 + halo * 0.18 + pool) * active * (0.35 + 0.65 * heat) + style_color * 0.08 * active;
        color += under * style_strength * (1.0 - 0.55 * density);
        vec2 high = girders(far, 760.0, 22.0, 0.37);
        color *= 1.0 - 0.7 * high.x;
        color += work * far_light_density * 3.0 * high.y;
        rise = 46.0;
        mote_glow = 1.0;
    } else if (style == 4) {
        // OFFSHORE: the sea far below; slow swell with pale crests, rain slanting
        // down across the view and a few rig legs with beacons.
        // One swell direction, bent by noise, so crests run as long broken lines.
        // (Two crossed swells peaked in a grid and drew closed rings, like eyes.)
        vec2 s = deep * vec2(1.0, 2.0);
        float swell = 0.5 + 0.5 * sin(dot(s, vec2(0.018, 0.006)) + TIME * 0.6 + noise(s / 380.0) * 6.0);
        float crest = pow(swell, 10.0) * smoothstep(0.35, 0.75, noise(s / 520.0 + vec2(TIME * 0.02, 0.0)));
        float foam = crest * smoothstep(0.45, 0.8, noise(vec2(s.x / 60.0 + TIME * 0.2, s.y / 14.0)));
        color = color * (0.78 + 0.14 * swell) + (style_color * 0.6 + catch_light) * (crest * 0.2 + foam * 0.6) * style_strength * (0.5 + density);
        vec2 high = girders(far, 900.0, 26.0, 0.61);
        color += catch_light * high.x * 0.3;
        float blink = step(0.8, fract(TIME * 0.5 + floor(far.x / 900.0) * 0.29));
        color += work * far_light_density * 5.0 * high.y * blink;
        vec2 r = near - vec2(TIME * 90.0, TIME * 700.0);
        vec2 rain_cell = floor(r / vec2(19.0, 90.0));
        vec2 rain_local = r - (rain_cell + 0.5) * vec2(19.0, 90.0) - vec2((hash(rain_cell) - 0.5) * 12.0, 0.0);
        float streak = exp(-pow(rain_local.x - rain_local.y * 0.13, 2.0) / 0.6) * smoothstep(40.0, 0.0, abs(rain_local.y)) * step(hash(rain_cell + 1.7), 0.3);
        color += vec3(0.6, 0.72, 0.8) * streak * dust_strength * 0.3;
    } else if (style == 6) {
        // CRYO: low frost fog sinks into the shaft. Sparse ice facets catch
        // cold light below the deck while remote pink emergency lamps blink.
        vec2 ice_p = flat_floor(deep, 570.0) + vec2(TIME * 0.006, -TIME * 0.018);
        float cold_bank = fbm(ice_p);
        float descending_fog = smoothstep(0.34, 0.77, cold_bank) * (0.45 + 0.55 * density);
        color += style_color * descending_fog * style_strength * 0.17;
        vec2 crystal_cell = floor(flat_floor(far, 135.0));
        vec2 crystal_local = fract(flat_floor(far, 135.0)) - 0.5;
        float pick = step(0.81, hash(crystal_cell + 6.3));
        float facet = exp(-abs(crystal_local.x + crystal_local.y) * 37.0)
                    * exp(-abs(crystal_local.x - crystal_local.y) * 37.0);
        color += (style_color + catch_light * 0.4) * pick * facet * style_strength * 0.13;
        vec2 beacon_cell = floor(flat_floor(deep, 760.0));
        vec2 beacon_local = fract(flat_floor(deep, 760.0)) - 0.5;
        float blink = step(0.72, fract(TIME * 0.34 + hash(beacon_cell) * 0.47));
        float beacon = step(0.86, hash(beacon_cell + 17.0))
                       * exp(-dot(beacon_local * vec2(1.0, 2.0), beacon_local * vec2(1.0, 2.0)) * 170.0);
        color += vec3(1.0, 0.26, 0.59) * beacon * blink * far_light_density * style_strength * 1.3;
        rise = -11.0;
        mote_glow = 0.22;
    } else if (style == 7) {
        // DAWN: pale gold cloud sea below the surface service deck. Broad
        // banks drift in parallax and morning wisps descend, without a horizon.
        vec2 cloud_p = flat_floor(deep, 1050.0) + vec2(TIME * 0.008, -TIME * 0.005);
        float bank = smoothstep(0.28, 0.76, fbm(cloud_p));
        float rim = smoothstep(0.43, 0.67, fbm(cloud_p + vec2(0.6, -0.2)));
        color += (style_color * (0.16 + 0.25 * rim) + vec3(0.16, 0.18, 0.23))
                 * bank * style_strength;
        float wisp = smoothstep(0.46, 0.8, fbm(flat_floor(mid, 420.0) + vec2(-TIME * 0.012, -TIME * 0.025)));
        color += (style_color * 0.12 + catch_light * 0.18) * wisp * style_strength;
        rise = -6.0;
        mote_glow = 0.0;
    } else if (style == 8) {
        // VAULT: sparse golden filaments rise slowly through deep indigo fog.
        // The same world quad supplies the atmosphere below every plate.
        vec2 filaments = far + vec2(0.0, TIME * 14.0);
        float column = floor(filaments.x / 240.0);
        float offset = (hash(vec2(column, 19.4)) - 0.5) * 130.0;
        float bend = sin(filaments.y / 410.0 + column * 2.7) * 9.0;
        float across = filaments.x - (column + 0.5) * 240.0 - offset - bend;
        float segment = smoothstep(0.39, 0.78, noise(vec2(column * 3.7, filaments.y / 470.0)));
        float core = exp(-across * across / 2.8);
        float halo = exp(-across * across / 130.0) * 0.10;
        float pick = step(0.35, hash(vec2(column, 8.2)));
        color += style_color * (core * 0.24 + halo) * segment * pick
                 * style_strength * (0.45 + 0.55 * density);
        float bank = smoothstep(0.32, 0.79, fbm(flat_floor(deep, 840.0)
                     + vec2(-TIME * 0.005, TIME * 0.008)));
        color += fog_color * bank * style_strength * 0.25;
        rise = 9.0;
        mote_glow = 0.3;
    } else if (style == 9) {
        // NULL: a white dimetric grid and red nodes drift out of register in
        // a cold slate shaft (never black: the void is lit by its own fog,
        // grid and nodes). Only this world quad receives the pattern; the
        // plates and actors draw over it.
        vec2 grid_p = deep + vec2(TIME * 1.8, -TIME * 0.9);
        vec2 axes = vec2(grid_p.x * 0.5 + grid_p.y,
                         grid_p.x * 0.5 - grid_p.y) / 360.0;
        vec2 cell = floor(axes + 0.5);
        vec2 across = abs(axes - cell) * 360.0 / 1.118;
        float nearest = min(across.x, across.y);
        float white_line = exp(-nearest * nearest / 2.4);
        float white_halo = exp(-nearest * nearest / 60.0);
        color += style_color * (white_line * 0.2 + white_halo * 0.045)
                 * style_strength;
        vec2 node_p = far + vec2(-TIME * 1.4, TIME * 0.7);
        vec2 node_axes = vec2(node_p.x * 0.5 + node_p.y,
                             node_p.x * 0.5 - node_p.y) / 360.0;
        vec2 node_cell = floor(node_axes + 0.5);
        vec2 node_local = (node_axes - node_cell) * 360.0 / 1.118;
        float node_pick = step(0.50, hash(node_cell + 27.3));
        float node_d2 = dot(node_local, node_local);
        float red_node = exp(-node_d2 / 20.0) + 0.18 * exp(-node_d2 / 320.0);
        color += vec3(1.0, 0.055, 0.04) * node_pick * red_node
                 * style_strength * 0.8;
        rise = 0.0;
        mote_glow = 0.0;
    } else {
        // SPORE: a low, slowly drifting green mist under the greenhouse deck.
        // Sparse motes rise through it; the architecture stays on the plates.
        vec2 floor_p = flat_floor(deep, 650.0);
        float bank = fbm(floor_p + vec2(TIME * 0.012, -TIME * 0.004));
        float low = smoothstep(0.38, 0.76, bank) * (0.55 + 0.45 * density);
        color += style_color * low * style_strength * 0.14;
        vec2 wisps = flat_floor(far, 130.0) + vec2(-TIME * 0.016, TIME * 0.006);
        float streak = smoothstep(0.58, 0.83, noise(wisps));
        color += (style_color * 0.55 + catch_light * 0.2) * streak * low * style_strength * 0.08;
        rise = 8.0;
        mote_glow = 0.35;
    }
    // Dust or embers drifting up, seen where the haze is lit (embers glow by themselves).
    vec2 drift = near + vec2(0.0, TIME * rise);
    vec2 mote_cell = drift / 46.0;
    vec2 mote_id = floor(mote_cell);
    if (hash(mote_id + 2.3) < 0.14) {
        vec2 mote = (vec2(hash(mote_id + 4.4), hash(mote_id + 8.8)) * 0.8 + 0.1 - fract(mote_cell)) * 46.0;
        mote.x += sin(TIME * 0.7 + hash(mote_id) * 20.0) * 4.0;
        float lit = max(mote_glow * (0.5 + 0.5 * sin(TIME * 3.0 + hash(mote_id) * 30.0)), 0.25 + 6.0 * dot(haze, vec3(0.299, 0.587, 0.114)));
        color += dust_color * dust_strength * 0.12 * lit * exp(-dot(mote, mote) / 1.6);
    }
    if (style == 7 && contact_strength > 0.0) {
        // The same world quad shades only the dawn haze beside the plates.
        // A distance field follows their original silhouettes, without
        // eroding wall alpha or applying a grade to actors or props.
        float contact = 0.0;
        for (int i = 0; i < 15; i++) {
            if (i >= contact_count) { break; }
            vec2 q = (world_pos - contact_rect[i].xy) / contact_rect[i].zw;
            if (q.x >= 0.0 && q.y >= 0.0 && q.x <= 1.0 && q.y <= 1.0) {
                contact = max(contact, texture(contact_atlas, contact_uv[i].xy + q * contact_uv[i].zw).r);
            }
        }
        color = mix(color, base_color, contact * contact_strength);
    }
    COLOR = vec4(color, 1.0);
}
"""

var _rect := Rect2()

func _ready() -> void:
    # Behind every plate of the art layer (z -100): plates, shadows and actors
    # all draw over it.
    z_index = -20
    set_process(false)

## `rect`: world area to cover. `settings`: the mission's abyss row (colours are
## [r, g, b] 0-1). `glows`: {position, radius, color: Vector3, strength} per
## plate, its lamp light in the haze under its floor.
func setup(rect: Rect2, settings: Dictionary, glows: Array[Dictionary], contacts: Array[Dictionary] = []) -> void:
    _rect = rect
    var shader := Shader.new()
    shader.code = SHADER
    var shader_material := ShaderMaterial.new()
    shader_material.shader = shader
    for pair in [["base", "base_color"], ["fog", "fog_color"], ["dust", "dust_color"], ["work_lights", "work_color"], ["style_color", "style_color"]]:
        var value: Variant = settings.get(pair[0], null)
        if value is Array and (value as Array).size() >= 3:
            shader_material.set_shader_parameter(pair[1], Vector3(float(value[0]), float(value[1]), float(value[2])))
    shader_material.set_shader_parameter("style", maxi(0, STYLES.find(str(settings.get("style", "shaft")))))
    for key in ["fog_strength", "haze_strength", "far_light_density", "dust_strength", "style_strength"]:
        if settings.has(key): shader_material.set_shader_parameter(key, float(settings[key]))
    if str(settings.get("style", "")) == "dawn":
        shader_material.set_shader_parameter("contact_strength", clampf(float(settings.get("contact_shadow_strength", 0.0)), 0.0, 1.0))
        _set_contacts(shader_material, contacts.slice(0, MAX_CONTACTS))
    # Web builds have no threads and a weaker GPU budget: half the fog detail.
    shader_material.set_shader_parameter("octaves", 2 if OS.has_feature("web") else 4)
    var positions := PackedVector4Array()
    var colors := PackedVector4Array()
    for glow in glows.slice(0, MAX_GLOWS):
        positions.append(Vector4(glow.position.x, glow.position.y + float(glow.radius) * 0.15, float(glow.radius), float(glow.get("strength", 1.0))))
        colors.append(Vector4(glow.color.x, glow.color.y, glow.color.z, 1.0))
    shader_material.set_shader_parameter("glow_count", positions.size())
    positions.resize(MAX_GLOWS)
    colors.resize(MAX_GLOWS)
    shader_material.set_shader_parameter("glow", positions)
    shader_material.set_shader_parameter("glow_color", colors)
    material = shader_material
    set_meta("glows", mini(glows.size(), MAX_GLOWS))
    _follow_camera()
    set_process(true)
    queue_redraw()

## One scalar atlas, built once. Per frame only the camera-centre uniform moves.
func _set_contacts(shader_material: ShaderMaterial, contacts: Array[Dictionary]) -> void:
    set_meta("contact_shadows", contacts.size())
    if contacts.is_empty(): return
    var cell := Vector2i.ZERO
    for contact in contacts:
        var image: Image = contact.image
        cell.x = maxi(cell.x, image.get_width() + 2)
        cell.y = maxi(cell.y, image.get_height() + 2)
    var columns := mini(4, contacts.size())
    var rows := ceili(float(contacts.size()) / float(columns))
    var atlas_size := Vector2i(cell.x * columns, cell.y * rows)
    var atlas := Image.create(atlas_size.x, atlas_size.y, false, Image.FORMAT_L8)
    atlas.fill(Color.BLACK)
    var rects := PackedVector4Array()
    var uvs := PackedVector4Array()
    for index in contacts.size():
        var image: Image = contacts[index].image
        var rect: Rect2 = contacts[index].rect
        var slot := Vector2i((index % columns) * cell.x + 1, floori(float(index) / float(columns)) * cell.y + 1)
        atlas.blit_rect(image, Rect2i(Vector2i.ZERO, image.get_size()), slot)
        rects.append(Vector4(rect.position.x, rect.position.y, rect.size.x, rect.size.y))
        uvs.append(Vector4(float(slot.x) / atlas_size.x, float(slot.y) / atlas_size.y, float(image.get_width()) / atlas_size.x, float(image.get_height()) / atlas_size.y))
    shader_material.set_shader_parameter("contact_atlas", ImageTexture.create_from_image(atlas))
    shader_material.set_shader_parameter("contact_count", contacts.size())
    rects.resize(MAX_CONTACTS)
    uvs.resize(MAX_CONTACTS)
    shader_material.set_shader_parameter("contact_rect", rects)
    shader_material.set_shader_parameter("contact_uv", uvs)
    set_meta("contact_atlas_size", atlas_size)

func _process(_delta: float) -> void:
    _follow_camera()

func _follow_camera() -> void:
    var camera := get_viewport().get_camera_2d() if is_inside_tree() else null
    if camera and material:
        (material as ShaderMaterial).set_shader_parameter("camera_center", camera.get_screen_center_position())

func _draw() -> void:
    if _rect.has_area(): draw_rect(Rect2(to_local(_rect.position), _rect.size), Color.WHITE)
