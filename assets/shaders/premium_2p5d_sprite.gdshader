shader_type canvas_item;

uniform vec4 accent_color : source_color = vec4(0.35, 0.85, 1.0, 1.0);
uniform float top_light = 0.22;
uniform float lower_shadow = 0.20;
uniform float rim_strength = 0.12;
uniform float contrast = 1.08;
uniform float saturation = 1.04;

void fragment() {
    vec4 vertex_modulate = COLOR;
    vec4 tex = texture(TEXTURE, UV);
    vec3 final_color = tex.rgb;

    if (tex.a > 0.001) {
        // Rig sheets are 4x4 equal cells. Reconstruct tile-local UV so every
        // articulated part receives the same lighting response.
        vec2 local_uv = fract(UV * vec2(4.0, 4.0));
        float upper = smoothstep(0.92, 0.08, local_uv.y);
        float lower = smoothstep(0.48, 1.0, local_uv.y);
        float edge = smoothstep(0.22, 0.50, abs(local_uv.x - 0.5));

        final_color *= 1.0 + upper * top_light;
        final_color *= 1.0 - lower * lower_shadow;
        final_color += accent_color.rgb * edge * rim_strength * tex.a;

        float luma = dot(final_color, vec3(0.299, 0.587, 0.114));
        final_color = mix(vec3(luma), final_color, saturation);
        final_color = (final_color - vec3(0.5)) * contrast + vec3(0.5);

        float spec = smoothstep(0.34, 0.0, distance(local_uv, vec2(0.31, 0.23)));
        final_color += vec3(0.72, 0.88, 1.0) * spec * 0.10 * tex.a;
    }

    COLOR = vec4(clamp(final_color, vec3(0.0), vec3(1.35)), tex.a) * vertex_modulate;
}
