shader_type canvas_item;
render_mode unshaded;

// Object-space material treatment: stable across time, preserves source alpha.
uniform float wear = 0.7;
uniform float heat = 0.0;
uniform float damage = 0.0;
float hash21(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}
float noise2(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i+vec2(1,0)), f.x),
               mix(hash21(i+vec2(0,1)), hash21(i+vec2(1,1)), f.x), f.y);
}
void fragment() {
    vec4 original = texture(TEXTURE, UV);
    vec3 c = original.rgb;
    float hi = max(c.r, max(c.g, c.b));
    float lo = min(c.r, min(c.g, c.b));
    // Saturated luminous optics stay readable; dirt belongs to the chassis.
    float optic = smoothstep(0.15, 0.46, hi-lo) * smoothstep(0.32,0.8,hi);
    float metal = 1.0-optic;
    float broad = noise2(UV*vec2(18.0,21.0));
    float grain = noise2(UV*vec2(175.0,190.0));
    float streak = noise2(UV*vec2(95.0,5.0));
    float dirt = smoothstep(0.4,0.8,broad) * (0.65+0.35*streak);
    float dust = smoothstep(0.45,0.94,UV.y) * smoothstep(0.3,0.85,broad);
    float luma = dot(c,vec3(0.2126,0.7152,0.0722));
    float neighbor = dot(texture(TEXTURE,UV+TEXTURE_PIXEL_SIZE*2.0).rgb,vec3(0.2126,0.7152,0.0722));
    float edge = smoothstep(0.025,0.15,abs(luma-neighbor));
    float chips = smoothstep(0.69,0.84,grain)*edge;
    vec3 aged = c * (1.0 - dirt*(0.28+damage*0.1));
    aged = mix(aged, vec3(0.24,0.17,0.115)*max(luma,0.18)*2.0, dirt*0.26);
    aged = mix(aged,vec3(0.34,0.30,0.24),dust*0.23);
    aged = mix(aged,vec3(0.48,0.47,0.43),chips*0.36);
    c = mix(c,aged,metal*wear);
    c += original.rgb*optic*heat*0.16;
    COLOR *= vec4(c,original.a);
}
