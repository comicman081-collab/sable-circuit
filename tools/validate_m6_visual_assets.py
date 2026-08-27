#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
ROOM_MANIFEST = ROOT / "data/visual/site7_room_art.json"
PLAYABLE = ROOT / "data/art_profiles/playable_profiles.json"
errors = []
visible_assets = []

try:
    room_data = json.loads(ROOM_MANIFEST.read_text(encoding="utf-8"))
except Exception as exc:
    room_data = {}
    errors.append(f"cannot parse room art manifest: {exc}")
rooms = room_data.get("rooms", [])
if room_data.get("schema_version") != 1:
    errors.append("room art manifest schema_version must be 1")
if not isinstance(rooms, list) or len(rooms) != 8:
    errors.append("room art manifest must contain exactly 8 authored room assets")
room_ids = set(); asset_ids = set()
for row in rooms if isinstance(rooms, list) else []:
    room_id = str(row.get("room_id", "")); asset_id = str(row.get("asset_id", "")); rel = str(row.get("asset", ""))
    if not room_id or room_id in room_ids: errors.append(f"duplicate/missing room_id: {room_id!r}")
    if not asset_id or asset_id in asset_ids: errors.append(f"duplicate/missing asset_id: {asset_id!r}")
    room_ids.add(room_id); asset_ids.add(asset_id)
    if not rel: errors.append(f"{room_id}: missing room art asset")
    else: visible_assets.append((f"room:{room_id}", rel))

try:
    playable_data = json.loads(PLAYABLE.read_text(encoding="utf-8"))
except Exception as exc:
    playable_data = {}
    errors.append(f"cannot parse playable profiles: {exc}")
profiles = playable_data.get("profiles", [])
if not isinstance(profiles, list) or len(profiles) != 3:
    errors.append("playable profiles must contain exactly 3 operators")
for profile in profiles if isinstance(profiles, list) else []:
    ident = str(profile.get("actor_id", "?"))
    weapon = str(profile.get("weapon_hud_asset", ""))
    actions = profile.get("hud_action_icon_assets", [])
    if not weapon:
        errors.append(f"{ident}: missing weapon_hud_asset")
    else:
        visible_assets.append((f"weapon:{ident}", weapon))
    if not isinstance(actions, list) or len(actions) != 3:
        errors.append(f"{ident}: hud_action_icon_assets must contain exactly 3 unique assets")
    else:
        for index, rel in enumerate(actions):
            visible_assets.append((f"action:{ident}:{index}", str(rel)))

paths = {}
hashes = {}
for owner, rel in visible_assets:
    if not rel:
        errors.append(f"{owner}: empty asset path")
        continue
    if rel in paths:
        errors.append(f"visible M6 asset path reused by {paths[rel]} and {owner}: {rel}")
    else:
        paths[rel] = owner
    path = ROOT / rel
    if not path.is_file():
        errors.append(f"{owner}: missing asset file: {rel}")
        continue
    if path.suffix.lower() != ".svg":
        errors.append(f"{owner}: M6 authored visible asset must be SVG: {rel}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest in hashes:
        errors.append(f"byte-identical M6 visible asset reused by {hashes[digest]} and {owner}: sha256={digest}")
    else:
        hashes[digest] = owner

if len(visible_assets) != 20:
    errors.append(f"expected 20 M6 authored visible assets (8 rooms + 3 weapons + 9 action icons), got {len(visible_assets)}")

if errors:
    print("M6_VISUAL_ASSET_VALIDATION: FAIL")
    for error in errors:
        print(" -", error)
    sys.exit(1)

print("M6_VISUAL_ASSET_VALIDATION: PASS")
print("validated 20 unique authored M6 SVG assets with unique paths and SHA-256")
