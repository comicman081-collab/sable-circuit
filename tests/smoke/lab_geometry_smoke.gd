extends SceneTree
const Output := preload("res://tests/support/test_output.gd")
const IntelSamples := preload("res://scripts/core/intel_samples.gd")
const MIN_FONT := 10
var checks := 0
var failures: Array[String] = []
var evidence: Array = []
func _init() -> void: call_deferred("run")
func run() -> void:
    root.size=Vector2i(1280,720)
    var flow:=GameFlow.new(); flow.persist_campaign=false; root.add_child(flow)
    var p:=flow.campaign; p.research_value=10000
    for key in IntelSamples.KEYS:p.intel_samples[key]=3
    flow.enter_base()
    var lobby:=flow.current_view as BaseLobby
    await create_timer(0.7).timeout
    check(lobby._analysis_page==0,"new lobby starts on page one")
    var reachable:Array[String]=[]
    for page in range(3):
        check(lobby._analysis_page_label.text=="%d/3"%[page+1],"page number %d"%(page+1))
        check(lobby._analysis_previous.disabled==(page==0) and lobby._analysis_next.disabled==(page==2),"only page-boundary navigation disabled")
        var buttons:=lobby._analysis_box.get_children().filter(func(n:Node)->bool:return n is Button)
        check(buttons.size()==(2 if page==2 else 3),"page has 3+3+2 analysis buttons")
        var ids:Array[String]=[]
        for button:Button in buttons:ids.append(str(button.get_meta("analysis_id")))
        if page==0:check(ids==["ANL_SECURITY_ARC_GAP","ANL_ABERRANT_JOINT_MAP","ANL_ANCHOR_SIGNAL_MODEL"],"first page keeps three original IDs and order")
        await process_frame
        geometry(lobby._m10_panel,"page%d"%(page+1))
        for id in ids:
            var button:=lobby.find_child("Analyze_"+id,true,false) as Button
            check(button!=null and not button.disabled,id+" reachable actionable actual button")
            button.pressed.emit()
            check(p.snapshot().analyzed_intel.has(id),id+" actual GameFlow analyzes and refreshes")
            check(lobby._analysis_page==page,"analysis refresh keeps selected page")
            reachable.append(id)
        if page<2:lobby._analysis_next.pressed.emit()
    check(reachable.size()==8 and p.snapshot().analyzed_intel.size()==8,"all eight analyses reachable through real flow")
    check(lobby._analysis_next.disabled,"last page next is disabled")
    geometry(lobby._m10_panel,"last_page_status")
    for operator in CampaignProgression.OPERATOR_IDS:
        var choices:Array[String]=[]
        for row:Dictionary in p.snapshot().discoveries:
            if row.operator_id==operator:choices.append(row.module_id)
        check(choices.size()==(2 if operator=="CHR_PROTO_03" else 3),operator+" owns intended 3/3/2 choices")
        for i in range(choices.size()+1):
            var button:=lobby.find_child("ModuleCycle_"+operator,true,false) as Button
            var expected:=choices[i] if i<choices.size() else ""
            var caption:="EQUIP" if i==0 else ("NEXT MOD" if i<choices.size() else "UNEQUIP")
            check(button.text==caption and button.get_meta("module_id")==expected,operator+" exact cycle request and caption")
            button.pressed.emit()
            check(p.equipped_modules[operator]==expected,operator+" actual GameFlow equips single requested slot")
            await process_frame
            geometry(lobby._m10_panel,operator+"_cycle%d"%i)
            module_listing(lobby,p,operator,expected)
        var button:=lobby.find_child("ModuleCycle_"+operator,true,false) as Button
        check(button.text=="EQUIP" and button.get_meta("module_id")==choices[0],operator+" cycle returns to first module after removal")
    for key in IntelSamples.KEYS:check(key in lobby._intel_summary_label.text,"lobby includes the full name "+key)
    check(lobby._intel_summary_label.text=="SAMPLES // "+IntelSamples.named_counts(p.intel_samples),"lobby samples line is exactly the full-name line")
    check(lobby._intel_summary_label.get_theme_font_size("font_size")==12,"lobby samples line keeps 12 px with full names")
    flow.enter_base(); lobby=flow.current_view as BaseLobby
    check(lobby._analysis_page==0,"reopened lobby resets page; page is not saved")
    check(not p.snapshot().has("analysis_page"),"page number never persisted")
    flow.deploy_mission("MIS_CH01_01")
    await process_frame
    var stage:=flow.current_view as StoryStage01
    check(stage!=null,"actual mission deployment reaches stage")
    if stage:
        stage.debug_seed_intel(2,1,1,{"AERATOR":1,"CRYO":1,"GANTRY":1,"ARCHIVE":1,"ORIGIN":1})
        var samples:=stage.debug_intel_cargo()
        for abbreviation in IntelSamples.SHORT:check(abbreviation in stage.hud.debug_intel_text(),"HUD includes "+abbreviation)
        check(stage.hud._resource_values.intel.text==str(IntelSamples.total(samples)),"HUD resource counter sums all eight keys")
        text_fit(stage.hud._intel_label,"HUD intel")
        var intel_box:Rect2=stage.hud._intel_label.get_global_rect()
        check(not intel_box.intersects(stage.hud._transmission_panel.get_global_rect()),"HUD intel box stays clear of the transmission panel")
        check(Rect2(0,0,1280,720).encloses(intel_box),"HUD intel box stays on screen")
        var summary:=stage.debug_extraction_summary()
        flow.show_results(summary)
        var results:=flow.current_view as MissionResults
        for abbreviation in IntelSamples.SHORT:
            check(abbreviation in results._body.text,"secured results include "+abbreviation)
            check(abbreviation in results._campaign_line.text,"base stock includes "+abbreviation)
        text_fit(results._body,"results body")
        text_fit(results._campaign_line,"results stock")
        check(results._campaign_line.get_global_rect().end.y<=results._epilogue.get_global_rect().position.y,"stock never overlaps debrief")
        check(results._body.get_global_rect().end.y<=results._contract_line.get_global_rect().position.y,"intel body never overlaps contract")
        var bar:=results.find_child("CommandBar",true,false) as ColorRect
        check(bar!=null,"results command bar is findable")
        if bar:
            var bar_rect:=bar.get_global_rect()
            for control in results._panel.find_children("*","Control",true,false):
                if control is Label or control is Button:check(not control.get_global_rect().intersects(bar_rect),"command bar nonoverlap "+control.name)
            var stock_bottom:=results._campaign_line.get_global_rect().position.y+results._campaign_line.get_minimum_size().y
            check(stock_bottom<=bar_rect.position.y,"two-line stock text ends above the command bar "+str(stock_bottom)+" / "+str(bar_rect.position.y))
    var out:=Output.path("res://.cache/tests/lab_geometry.json")
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out.get_base_dir()))
    var f:=FileAccess.open(out,FileAccess.WRITE); f.store_string(JSON.stringify({"checks":checks,"geometry":evidence,"failures":failures},"  ")); f.close()
    flow.queue_free(); await process_frame
    print("LAB_GEOMETRY_SMOKE: ","PASS" if failures.is_empty() else "FAIL"," (",checks," checks)")
    quit(0 if failures.is_empty() else 1)
func geometry(panel:Panel,scene:String)->void:
    var bounds:=panel.get_global_rect()
    check(Rect2(0,0,1280,720).encloses(bounds),scene+" panel inside 1280x720")
    # Entrance tweens can leave ~0.0002 px of float rounding in Control.size.
    check(panel.size.distance_to(Vector2(1224,202))<0.001,scene+" original panel size "+str(panel.size))
    var controls:Array[Control]=[]
    for node in panel.find_children("*","Control",true,false):
        if node is Label or node is Button:controls.append(node)
    var boxes:Array=[]
    for control in controls:
        check(control.is_visible_in_tree(),scene+" "+control.name+" visible")
        check(bounds.encloses(control.get_global_rect()),scene+" "+control.name+" inside panel")
        text_fit(control,scene+" "+control.name)
        boxes.append({"name":str(control.name),"rect":str(control.get_global_rect()),"text":control.text})
    for a in range(controls.size()):
        for b in range(a+1,controls.size()):
            check(not controls[a].get_global_rect().intersects(controls[b].get_global_rect()),scene+" nonoverlap "+controls[a].name+" / "+controls[b].name)
    evidence.append({"scene":scene,"boxes":boxes})
## The second line of an operator's module row names every unlocked module and brackets the equipped one.
func module_listing(lobby:BaseLobby,p,operator:String,equipped:String)->void:
    var names:Array[String]=[]; var equipped_name:=""
    for row:Dictionary in p.snapshot().discoveries:
        if row.operator_id==operator:
            names.append(str(row.module_name))
            if row.module_id==equipped:equipped_name=str(row.module_name)
    var listing:=lobby.find_child("ModuleChoices_"+operator,true,false) as Label
    check(listing!=null,operator+" lists its unlocked modules without pressing anything")
    if listing==null:return
    for module_name in names:check(module_name in listing.text,operator+" listing names "+module_name)
    check(listing.text.count("[")==(1 if equipped!="" else 0),operator+" listing marks only the equipped module")
    check(equipped=="" or ("["+equipped_name+"]") in listing.text,operator+" listing brackets "+equipped_name)
func text_fit(control:Control,label:String)->void:
    var font:Font=control.label_settings.font if control is Label and control.label_settings else control.get_theme_font("font")
    var font_size:int=control.label_settings.font_size if control is Label and control.label_settings else control.get_theme_font_size("font_size")
    var width:=-1.0
    var available:=control.size
    if control is Label and control.autowrap_mode!=TextServer.AUTOWRAP_OFF:width=available.x
    if control is Button:
        var style:=control.get_theme_stylebox("normal")
        available-=style.get_minimum_size()
    var extent:=font.get_multiline_string_size(control.text,HORIZONTAL_ALIGNMENT_LEFT,width,font_size)
    check(extent.x<=available.x+0.01 and extent.y<=available.y+0.01,label+" full text fits font geometry "+str(extent)+" / "+str(available))
    check(font_size>=MIN_FONT,label+" font size "+str(font_size)+" stays readable (>= "+str(MIN_FONT)+")")
func check(ok:bool,label:String)->void:
    checks+=1
    if not ok:failures.append(label); push_error(label)
