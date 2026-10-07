extends RefCounted
const NEW_IDS := ["WPN_DMR_RAIL_01", "WPN_SHOTGUN_NULL_01"]
static func dps(row: Dictionary) -> Dictionary:
    var rounds := float(row.magazine_size) / float(row.ammo_per_trigger)
    var volley := float(row.damage) * float(row.pellet_count)
    return {"burst":volley/float(row.fire_interval),"sustained":volley*rounds/(rounds*float(row.fire_interval)+float(row.reload_duration))}
static func legacy_best(operator: String) -> float:
    var best := 0.0
    for row: Dictionary in WeaponRegistry.get_all_weapons():
        if not NEW_IDS.has(row.weapon_id) and (row.compatible_operators as Array).has(operator):
            best = maxf(best,dps(row).sustained)
    return best
