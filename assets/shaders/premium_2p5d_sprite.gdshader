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

void fragment() {
    vec4 vertex_modulate = COLOR;
    vec4 tex = texture(TEXTURE, UV);
    vec3 final_color = tex.rgb;

    if (tex.a > 0.001) {
        // Every rig uses a 4x4 equal-cell sheet. Work in tile-local coordinates
        // so each articulated part receives the same pseudo-3D light model.
        vec2 local_uv = fract(UV * vec2(4.0, 4.0));
        vec2 centered = local_uv - vec2(0.5);

        // Broad key from upper-left. This is intentionally smooth: the authored
        // SVG materials remain visible while the field sprite gains volume.
        float key_plane = clamp((1.0 - local_uv.y) * 0.72 + (1.0 - local_uv.x) * 0.28, 0.0, 1.0);
        float key = smoothstep(0.12, 0.92, key_plane);

        // Contact/AO darkens lower surfaces and the far silhouette edges.
        float lower_ao = smoothstep(0.50, 1.0, local_uv.y);
        float side_edge = smoothstep(0.30, 0.50, abs(centered.x));
        float bottom_edge = smoothstep(0.72, 1.0, local_uv.y);
        float edge_ao = max(side_edge * 0.62, bottom_edge);

        final_color *= 0.92 + key * top_light;
        final_color *= 1.0 - lower_ao * lower_shadow;
        final_color *= 1.0 - edge_ao * edge_ao_strength;

        // Cool reflected light from screen-right and a restrained identity rim.
        float right_bounce = smoothstep(0.58, 1.0, local_uv.x) * (1.0 - local_uv.y * 0.58);
        final_color += vec3(0.18, 0.34, 0.42) * right_bounce * bounce_strength * tex.a;
        final_color += accent_color.rgb * side_edge * rim_strength * (0.42 + 0.58 * key) * tex.a;

        // A soft material sheen gives armor/hair/gun pieces a painted 2.5D read
        // without introducing a plastic white hotspot.
        float center_falloff = 1.0 - smoothstep(0.12, 0.72, length(centered * vec2(0.92, 1.08)));
        float diagonal_band = 1.0 - smoothstep(0.025, 0.20, abs(local_uv.x * 0.72 + local_uv.y * 0.42 - 0.43));
        float sheen = center_falloff * diagonal_band;
        final_color += vec3(0.54, 0.66, 0.72) * sheen * sheen_strength * tex.a;

        // Final grade: slightly lower chroma and higher local contrast than M5/M6
        // so the actors read as materials in the dark facility instead of flat icons.
        float luma = dot(final_color, vec3(0.299, 0.587, 0.114));
        final_color = mix(vec3(luma), final_color, saturation);
        final_color = (final_color - vec3(0.5)) * contrast + vec3(0.5);
    }

    COLOR = vec4(clamp(final_color, vec3(0.0), vec3(1.28)), tex.a) * vertex_modulate;
}
