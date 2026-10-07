extends Node2D
class_name EnemyOverheadUI

var actor: EnemyActor
var _phase := 0.0

func _ready() -> void:
    actor = get_parent() as EnemyActor
    z_as_relative = false
    z_index = 3200
    queue_redraw()

func _process(delta: float) -> void:
    _phase += delta
    queue_redraw()

func bar_y_local() -> float:
    if actor == null: return -12.0
    if is_instance_valid(actor.biped_sprite):
        var bounds: Rect2=actor.biped_sprite.visual_rect_world()
        var top:=INF
        for corner in [bounds.position,bounds.position+Vector2(bounds.size.x,0),bounds.end,bounds.position+Vector2(0,bounds.size.y)]:
            top=minf(top,to_local(corner).y)
        return top-12.0
    if is_instance_valid(actor.machine_sprite):
        # Damage bounds deliberately omit antennas/pylons. A health bar must
        # clear the whole visible machine, not sit inside that inset hit box.
        # The machine's own bounds (the whole picture unless its spec names them),
        # so a machine drawn small in a large canvas keeps its bar close.
        var machine: Node2D=actor.machine_sprite
        var art: Rect2=machine.visible_rect
        var top:=INF
        for corner in [art.position,art.position+Vector2(art.size.x,0),art.end,art.position+Vector2(0,art.size.y)]:
            top=minf(top,to_local(machine.sprite.to_global(corner)).y)
        return top-12.0
    return actor.get_combat_hit_rect().position.y-actor.global_position.y-12.0

func _draw() -> void:
    if actor == null:
        return
    var ratio := clampf(actor.health/maxf(1.0,actor.max_health),0.0,1.0)
    var boss := "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id
    var width := 118.0 if boss else 48.0
    var y := bar_y_local()
    var accent := _accent()
    var guard := actor.get_node_or_null("BossPhaseTransitionGuard")
    var guarded: bool = boss and guard!=null and guard.debug_guard_active()
    if guarded: accent=Color("8ce1f4")

    # Backplate + thin luminous outline.
    draw_rect(Rect2(-width*0.5-3.0,y-3.0,width+6.0,10.0),Color(0.015,0.022,0.028,0.88),true)
    draw_rect(Rect2(-width*0.5-3.0,y-3.0,width+6.0,10.0),Color(accent.r,accent.g,accent.b,0.24),false,1.0)
    draw_rect(Rect2(-width*0.5,y,width,4.0),Color("182329"),true)

    # Segmented health fill.
    var segments := 12 if boss else 6
    var segment_w := (width-float(segments-1)*2.0)/float(segments)
    for i in range(segments):
        var threshold := float(i)/float(segments)
        var filled := ratio > threshold
        var x := -width*0.5 + float(i)*(segment_w+2.0)
        draw_rect(Rect2(x,y,segment_w,4.0),Color(accent,0.95 if filled else 0.12),true)

    # Elite SHIELDED barrier: its own bar just above health, so the chevron and name move up.
    var affix := actor.get_node_or_null("EliteAffix") as EliteAffix
    var lift := 0.0
    if affix != null and affix.barrier_max > 0.0:
        lift = 7.0
        draw_rect(Rect2(-width*0.5-3.0,y-10.0,width+6.0,7.0),Color(0.015,0.022,0.028,0.88),true)
        draw_rect(Rect2(-width*0.5,y-8.0,width,3.0),Color(affix.color,0.16),true)
        draw_rect(Rect2(-width*0.5,y-8.0,width*affix.barrier_share(),3.0),Color(affix.color,0.95),true)

    # Small threat chevron. Boss gets a phase-reactive double marker.
    var pulse := 0.72 + sin(_phase*4.0)*0.16
    var marker_y := y-10.0-lift
    var pts := PackedVector2Array([Vector2(-6,marker_y),Vector2(6,marker_y),Vector2(0,marker_y+6)])
    draw_colored_polygon(pts,Color(accent.r,accent.g,accent.b,pulse))

    # Elite variant name above the chevron.
    if affix != null:
        var font := ThemeDB.fallback_font
        var title := affix.title()
        var text_w := font.get_string_size(title,HORIZONTAL_ALIGNMENT_LEFT,-1,10).x
        draw_rect(Rect2(-text_w*0.5-4.0,marker_y-15.0,text_w+8.0,13.0),Color(0.015,0.022,0.028,0.82),true)
        draw_string(font,Vector2(-text_w*0.5,marker_y-5.0),title,HORIZONTAL_ALIGNMENT_LEFT,-1,10,affix.color)
    if boss:
        if guarded:
            draw_rect(Rect2(-width*0.5-4,y-4,width+8,12),Color("a5e8fa"),false,1.5)
            draw_string(ThemeDB.fallback_font,Vector2(-width*0.5,y+19),"CORE SHIELDED",HORIZONTAL_ALIGNMENT_LEFT,-1,10,accent)
        var phase := 1 if ratio>0.66 else (2 if ratio>0.33 else 3)
        if phase>=2:
            draw_arc(Vector2.ZERO,94.0+phase*5.0,-PI*0.82,-PI*0.18,28,Color(accent.r,accent.g,accent.b,0.18+phase*0.06),2.0+phase)
    elif actor.enemy_id in ["ENM_SITE7_BULWARK_01","ENM_SITE7_RAM_01","ENM_SITE7_MORTAR_01"]:
        var label := {"ENM_SITE7_BULWARK_01":"FRONT ARMOR", "ENM_SITE7_RAM_01":"RAM", "ENM_SITE7_MORTAR_01":"MORTAR"}
        draw_string(ThemeDB.fallback_font,Vector2(-width*0.5,y+17),label[actor.enemy_id],HORIZONTAL_ALIGNMENT_LEFT,-1,9,accent)

func _accent() -> Color:
    if actor == null: return Color("f05b68")
    if "BULWARK" in actor.enemy_id: return Color("e5b860")
    if "RAM_01" in actor.enemy_id: return Color("ef9251")
    if "MORTAR" in actor.enemy_id: return Color("c097fa")
    if "RIFLE" in actor.enemy_id: return Color("ef6470")
    if "SHIELD" in actor.enemy_id: return Color("e5a94d")
    if "DRONE" in actor.enemy_id: return Color("e45a91")
    if "ABERRANT" in actor.enemy_id: return Color("bd61da")
    if "BOSS" in actor.enemy_id or "ANCHOR" in actor.enemy_id:
        if actor.enemy_id == "BOSS_SITE7_ANCHOR_01":
            var anchor_ratio := actor.health/maxf(1.0,actor.max_health)
            return Color("f0529d") if anchor_ratio<=0.33 else Color("9179ff")
        var palette: Array = actor.art_profile.get("palette", [])
        if palette.size() > 1:
            return Color(str(palette[1]))
        var ratio := actor.health/maxf(1.0,actor.max_health)
        return Color("f0529d") if ratio<=0.33 else Color("9179ff")
    return Color("f05b68")
