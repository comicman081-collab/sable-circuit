shader_type canvas_item;
render_mode blend_add, unshaded;

uniform vec4 primary_color : source_color = vec4(0.35, 0.88, 1.0, 1.0);
uniform vec4 secondary_color : source_color = vec4(0.95, 0.40, 0.72, 1.0);
uniform float progress : hint_range(0.0, 1.0) = 0.0;
uniform float energy : hint_range(0.0, 2.0) = 1.0;
uniform float seed = 0.0;
uniform float style : hint_range(0.0, 4.0) = 0.0;

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345 + seed);
    return fract(p.x * p.y);
}

float value_noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p) {
    float n = value_noise(p) * 0.64;
    n += value_noise(p * 2.07 + 7.13) * 0.25;
    n += value_noise(p * 4.11 - 3.71) * 0.11;
    return n;
}

void fragment() {
    vec2 p = UV - vec2(0.5);
    float life = clamp(progress, 0.0, 1.0);
    float outward = 0.04 + life * (0.10 + style * 0.012);
    p.x += outward;

    vec2 anisotropy = vec2(0.74 - style * 0.035, 1.12 + style * 0.045);
    float radius = length(p * anisotropy);
    float radial = 1.0 - smoothstep(0.10 + life * 0.025, 0.50, radius);
    float noisy_edge = fbm(p * (8.0 + style * 1.25) + vec2(life * 2.7, seed * 0.013));
    float body = smoothstep(0.25, 0.73, radial * 0.82 + noisy_edge * 0.48 - life * 0.18);

    float directional_lobe = 1.0 - smoothstep(0.04, 0.32 + life * 0.18, length(vec2(p.x * 0.66, p.y * 1.72)));
    float core = 1.0 - smoothstep(0.012, 0.115 + life * 0.035, length(p * vec2(0.72, 1.42)));
    float flash = (1.0 - smoothstep(0.0, 0.22, life)) * core;
    float plume = body * (1.0 - smoothstep(0.46, 1.0, life));
    float afterglow = directional_lobe * (1.0 - smoothstep(0.62, 1.0, life));

    vec3 hot = mix(primary_color.rgb, vec3(1.0), 0.72);
    vec3 body_color = mix(secondary_color.rgb, primary_color.rgb, clamp(radial + noisy_edge * 0.24, 0.0, 1.0));
    vec3 rgb = body_color * plume * 0.70 + primary_color.rgb * afterglow * 0.48 + hot * flash * 1.65;
    float alpha = (plume * 0.44 + afterglow * 0.30 + flash * 0.88) * energy;
    alpha *= texture(TEXTURE, UV).a;
    COLOR = vec4(rgb * energy, clamp(alpha, 0.0, 1.0));
}
