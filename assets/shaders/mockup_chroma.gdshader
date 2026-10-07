shader_type canvas_item;
// Display-only separation of the existing ROOK green master; no source mutation.
void fragment() {
    vec4 c = texture(TEXTURE, UV) * COLOR;
    float green_excess = c.g - max(c.r, c.b);
    float key = smoothstep(0.08, 0.34, green_excess);
    c.a *= 1.0 - key;
    c.g = min(c.g, max(c.r, c.b) + 0.06);
    COLOR = c;
}
