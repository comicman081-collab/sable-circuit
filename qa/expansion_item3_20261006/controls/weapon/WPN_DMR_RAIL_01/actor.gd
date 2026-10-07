extends "res://scripts/actors/operator_actor.gd"
func _spawn_projectile(dir:Vector2)->void:
    var projectile:=Projectile.new(); get_tree().root.add_child(projectile); projectile.setup(_get_projectile_spawn_origin(),dir,self,accent_color.lightened(0.35),_weapon_art_profile())
    projectile_spawned.emit(projectile)
    if not weapon_spec.is_empty():
        projectile.damage=clampf(float(weapon_spec.get("damage",projectile.damage)),0.1,200.0); projectile.speed=clampf(float(weapon_spec.get("projectile_speed",projectile.speed)),100.0,2400.0); projectile.lifetime=clampf(float(weapon_spec.get("projectile_lifetime",projectile.lifetime)),0.1,4.0)
    var skill_multiplier:=1.25 if _overclock_left>0.0 else (1.18 if _scatter_cycle_left>0.0 else 1.0); projectile.damage*=campaign_damage_multiplier*skill_multiplier*run_primary_damage_multiplier
    if equipped_weapon_id == "WPN_DMR_RAIL_01": projectile.damage = 0.0
