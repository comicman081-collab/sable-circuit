# Quaternius Free Standard Asset Policy

SABLE CIRCUIT may use the Quaternius assets listed in `assets/external/manifest.json` only under the rules below.

## Allowed

- Quaternius **Standard (Free)** downloads only.
- Assets whose upstream license is **CC0 1.0 Universal** and whose upstream page explicitly permits personal, educational, and commercial use.
- Immutable public mirrors may be used only as deterministic transport when the official itch.io download requires an interactive download step. The Quaternius official page remains the license authority.
- Shared animation/retargeting infrastructure may use these assets as source/reference material.

## Forbidden

- `Pro`, `Source`, paid member-reward, or other paid-tier files.
- Paid `.blend` source kits.
- Any asset whose commercial-use permission is unclear.
- Replacing ASTER / ROOK / MICA or enemy final visible identities with a shared Quaternius base character. SABLE's unique-art rules remain authoritative.

## Approved upstream packs

### Universal Base Characters — Standard (Free)

- Author: Quaternius
- Upstream: https://quaternius.com/packs/universalbasecharacters.html
- Itch: https://quaternius.itch.io/universal-base-characters
- Upstream license: CC0 1.0 Universal
- Upstream states the Standard character models are free for personal, educational, and commercial projects.
- SABLE initially fetches only a female humanoid base pair (`female.gltf` + its referenced `.bin`) for rig/retarget validation. It is not final SABLE character art.

### Universal Animation Library — Standard (Free)

- Author: Quaternius
- Upstream: https://quaternius.com/packs/universalanimationlibrary.html
- Itch: https://quaternius.itch.io/universal-animation-library
- Upstream license: CC0 1.0 Universal
- 120+ humanoid animations. The free Standard pack includes engine-ready exports; paid Pro/Source files are excluded.

### Universal Animation Library 2 — Standard (Free)

- Author: Quaternius
- Upstream: https://quaternius.com/packs/universalanimationlibrary2.html
- Itch: https://quaternius.itch.io/universal-animation-library-2
- Upstream license: CC0 1.0 Universal
- 130+ complementary humanoid animations. The free Standard pack is allowed; paid Source files are excluded.

## Mirror policy

Each mirrored binary is pinned to an immutable Git commit and verified using its Git blob SHA-1 (`sha1("blob <size>\\0" + bytes)`). The downloader also verifies the declared file size. Where a SHA-256 is independently known, it may be recorded in addition to the Git blob hash.

Mirror provenance does not replace upstream license authority. If a mirror changes, disappears, or conflicts with the official pack/license, fetching must fail rather than silently substitute another file.

## Runtime policy

Quaternius files are **not fetched by default**. Run:

```bash
python tools/fetch_external_assets.py --group quaternius
```

or fetch a single stable asset ID with `--id`.

This keeps the normal M5 font/CI fetch small and prevents a new external animation dependency from becoming authoritative before retarget/runtime validation passes.
