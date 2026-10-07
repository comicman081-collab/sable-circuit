# Native-alpha capability probe — FAIL, do not promote

2026-09-07. The user authorized omitting green backgrounds only if clean native
separation can actually be demonstrated. Built-in ImageGen was requested once,
with the recorded exact prompt/request/permit and the existing front source.

The returned 1024×1536 PNG is **RGB**, not RGBA. Decoded alpha is 255 everywhere:
0 transparent pixels, 0 partially transparent pixels, 1,572,864 opaque pixels.
The displayed checkerboard is painted into the picture. Therefore it cannot be
used as a clean transparent source or passed off as a successful alpha probe.

Original result SHA-256:
`d62d2c9d035cbf2f19b02ef5f079c7e2122aa5730bded1a5bbbc8e28b63bdbed`.
The project copy was verified byte-for-byte before removing only its exact
managed staging file `exec-0ebc831d-9a91-42d7-98a6-8296cd5cf1ce.png`.

Official API documentation supports transparent-background requests in preview,
but this does not establish that the current built-in tool returned alpha:
https://developers.openai.com/api/docs/guides/image-generation#customize-image-output
No separate API/model fallback was invoked. Do not repeatedly regenerate this
failed mechanism. Keep the current good green source and continue motion work.

The harness/skill now accepts an explicitly requested native-alpha source, but
requires actual alpha, opaque semantic texture regions and independent edge
review. Existing green masters remain unchanged. This probe and its provenance
are quarantine-only until the final replacement disposal conditions are met.
