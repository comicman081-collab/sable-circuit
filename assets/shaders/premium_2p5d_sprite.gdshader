shader_type canvas_item;

uniform vec4 accent_color : source_color = vec4(0.35, 0.85, 1.0, 1.0);
uniform float top_light = 0.20;
uniform float lower_shadow = 0.26;
uniform float rim_strength = 0.08;
uniform float contrast = 1.12;
uniform float saturation = 0.96;
uniform float bounce_strength = 0.08;
uniform float sheen_strength = 0.12;
uniform float edge_ao_strength = 0.07;
uniform float ink_softening = 0.24;

void fragment() {
    vec4 vertex_modulate = COLOR;
    vec4 tex = texture(TEXTURE, UV);
    vec3 final_color = tex.rgb;

    if (tex.a > 0.001) {
        vec2 local_uv = fract(UV * vec2(4.0, 4.0));
        vec2 centered = local_uv - vec2(0.5);
        float source_luma = dot(tex.rgb, vec3(0.299, 0.587, 0.114));

        float key_plane = clamp((1.0 - local_uv.y) * 0.72 + (1.0 - local_uv.x) * 0.28, 0.0, 1.0);
        float key = smoothstep(0.12, 0.92, key_plane);
        float lower_ao = smoothstep(0.50, 1.0, local_uv.y);
        float side_edge = smoothstep(0.30, 0.50, abs(centered.x));
        float bottom_edge = smoothstep(0.72, 1.0, local_uv.y);
        float edge_ao = max(side_edge * 0.62, bottom_edge);

        final_color *= 0.92 + key * top_light;
        final_color *= 1.0 - lower_ao * lower_shadow;
        final_color *= 1.0 - edge_ao * edge_ao_strength;

        float right_bounce = smoothstep(0.58, 1.0, local_uv.x) * (1.0 - local_uv.y * 0.58);
        final_color += vec3(0.18, 0.34, 0.42) * right_bounce * bounce_strength * tex.a;
        final_color += accent_color.rgb * side_edge * rim_strength * (0.42 + 0.58 * key) * tex.a;

        float center_falloff = 1.0 - smoothstep(0.12, 0.72, length(centered * vec2(0.92, 1.08)));
        float diagonal_band = 1.0 - smoothstep(0.025, 0.20, abs(local_uv.x * 0.72 + local_uv.y * 0.42 - 0.43));
        float sheen = center_falloff * diagonal_band;
        final_color += vec3(0.54, 0.66, 0.72) * sheen * sheen_strength * tex.a;

        // Only near-black pixels are treated as line art. Lift those pixels toward
        // a material-tinted navy/charcoal so the rig does not read like a thick
        // black comic sticker at field scale. Dark cloth/armor remains untouched.
        float ink_mask = 1.0 - smoothstep(0.028, 0.085, source_luma);
        vec3 material_ink = vec3(0.018, 0.032, 0.040) + accent_color.rgb * 0.024;
        final_color = mix(final_color, max(final_color, material_ink), ink_mask * ink_softening);

        float luma = dot(final_color, vec3(0.299, 0.587, 0.114));
        final_color = mix(vec3(luma), final_color, saturation);
        final_color = (final_color - vec3(0.5)) * contrast + vec3(0.5);
    }

    COLOR = vec4(clamp(final_color, vec3(0.0), vec3(1.28)), tex.a) * vertex_modulate;
}
