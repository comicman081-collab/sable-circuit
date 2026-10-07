extends RefCounted

## One key/order authority for storage, field cargo and all three UI surfaces.
const KEYS := ["SECURITY", "ABERRANT", "ANCHOR", "AERATOR", "CRYO", "GANTRY", "ARCHIVE", "ORIGIN"]
const SHORT := ["SEC", "ABR", "ANC", "AER", "CRY", "GAN", "ARC", "ORG"]

static func empty() -> Dictionary:
    return sanitize({})

static func sanitize(value: Variant) -> Dictionary:
    var out: Dictionary = {}
    for key in KEYS:
        out[key] = maxi(0, int(value.get(key, 0))) if value is Dictionary else 0
    return out

static func total(samples: Dictionary) -> int:
    var count := 0
    for key in KEYS: count += maxi(0, int(samples.get(key, 0)))
    return count

static func counts(samples: Dictionary, separator: String = "   ", skip_new_zeros: bool = false) -> String:
    var parts: PackedStringArray = []
    for i in range(KEYS.size()):
        var count := maxi(0, int(samples.get(KEYS[i], 0)))
        if skip_new_zeros and i >= 3 and count == 0: continue
        parts.append("%s %02d" % [SHORT[i], count])
    return separator.join(parts)

## New boss checks precede the legacy generic BOSS branch. Missions 1-5 keep ANCHOR.
static func enemy_key(enemy_id: String) -> String:
    var id := enemy_id.to_upper()
    if "BOSS" in id: return "ANCHOR"
    if id == "BOSS_SITE7_AERATOR_01": return "AERATOR"
    elif id == "BOSS_SITE7_CRYO_01": return "CRYO"
    elif id == "BOSS_SITE7_GANTRY_01": return "GANTRY"
    elif id == "BOSS_SITE7_ARCHIVE_01": return "ARCHIVE"
    elif id == "BOSS_SITE7_ORIGIN_01": return "ORIGIN"
    elif "BOSS" in id or "ANCHOR" in id: return "ANCHOR"
    elif "ABERRANT" in id or "RAM_01" in id: return "ABERRANT"
    elif "RIFLE" in id or "SHIELD" in id or "DRONE" in id or "BULWARK" in id or "MORTAR" in id: return "SECURITY"
    return ""
