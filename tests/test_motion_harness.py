"""Negative regression tests. Analytic fixtures are NOT production art evidence."""
import copy
import importlib.util
import json
import math
import shutil
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/character_pipeline"))
import motion_harness as h
import sable_character_pipeline as pipeline

R21 = ROOT / "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_r21_r8c_frame_transition_sole_lock/runtime_descriptor.json"
R22 = ROOT / "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_r22_r4_wide_stride_sole_lock/runtime_descriptor.json"
R4_FRAME = ROOT / "art_src/characters/mica/fast_pipeline/motion/candidate_mica_c03_v9_neutral_r4_wide_step_segmented/blender_frames/N/move/03.png"


def analytic_runtime():
    raw = {"actor_id": "CHR_PROTO_03", "physics_hz": 30, "descriptor": "res://fixture/descriptor.json",
           "input_method": "Input.parse_input_event", "clock": "production_physics_delta", "cases": []}
    for key in sorted(h.expected_cases()):
        case = {"id": key, "start_position": [960,540], "samples": [], "shots": []}
        pos = [960.0,540.0]
        for index in range(63):
            cmd = h.case_command(key, index, 63, {"walk":152,"run":224})
            delta = [x * cmd["speed"] / 30 if not cmd["blocked"] else 0 for x in cmd["move"]]
            pos = [p+d for p,d in zip(pos,delta)]
            reload = cmd["kind"] == "reload" and 8 <= index <= 40
            case["samples"].append({"dt":1/30, "world_position":pos[:], "delta":delta, "requested_speed":cmd["speed"],
                "move_vector":cmd["move"], "aim_vector":cmd["aim"], "active_descriptor":raw["descriptor"],
                "runtime_active":True, "state":"move" if cmd["speed"] else "idle", "frame":index%24,
                "reloading":reload, "slide_collisions":1 if cmd["blocked"] else 0})
        if cmd["fire"]:
            indices=[32,40,48] if cmd['kind']=='start_turn_fire' else [0,12,42]
            for tick in indices:
                shot_cmd=h.case_command(key,tick,63,{'walk':152,'run':224})
                case['shots'].append({"origin":[10,10], "socket":[10,10], "direction":shot_cmd["aim"],
                    "shown_sector":shot_cmd["aim_sector"], "reloading":False,"physics_sample_index":tick})
        raw["cases"].append(case)
    return raw


class MotionHarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = ROOT / "artifacts/motion_harness_audit/technical_fixtures" / uuid.uuid4().hex
        cls.work.mkdir(parents=True)
        cls.baseline = analytic_runtime()

    def errors(self, raw):
        return h.score_runtime(raw)["errors"]

    def altered(self, case_id, modifier):
        raw = copy.deepcopy(self.baseline)
        case = next(x for x in raw["cases"] if x["id"] == case_id)
        modifier(case)
        return self.errors(raw)

    def test_analytic_positive_tests_the_harness_not_art(self):
        self.assertEqual(self.errors(self.baseline), [])

    def test_combined_gait_cannot_borrow_basic_16_channels(self):
        descriptor={'representation':{'kind':'authored_8x8','assets':[]}}
        with self.assertRaisesRegex(ValueError,'EXACT_COMBINED_GAIT_CHANNEL'):
            h.gait_channel({'mode':'walk','direction':'E'},descriptor)
        channel={'mode':'walk','move':'N','aim':'E','firing':True}
        row={**channel,'path':'fixture.png','frames':24,'fps':24}
        descriptor['representation']['assets']=[row]
        seq={'mode':'walk','direction':'E','motion_channel':channel}
        self.assertEqual(h.gait_channel(seq,descriptor)[0],('walk','N','E',True))
        seq['direction']='N'
        with self.assertRaisesRegex(ValueError,'VIEW_OR_MODE'):
            h.gait_channel(seq,descriptor)

    def test_strafe_excursion_axis_is_measured_without_swapping_anatomy(self):
        geometry={'frames':{str(i):{'world_to_body_m':[[1,0,0,0],[0,1,0,-i],[0,0,1,0],[0,0,0,1]]} for i in range(3)}}
        self.assertEqual(list(h.measured_travel_axis(geometry,[0,1,2],1.8)),[0,1,0])
        geometry['frames']['2']['world_to_body_m'][1][3]=0
        with self.assertRaisesRegex(ValueError,'ACTUAL_WORLD_ROOT_TRAVEL'):
            h.measured_travel_axis(geometry,[0,1,2],1.8)
        geometry['frames']['2']['world_to_body_m'][1][3]=-2
        geometry['frames']['2']['world_to_body_m'][2][3]=-.1
        with self.assertRaisesRegex(ValueError,'CANNOT_FOLLOW_PELVIS_BOB'):
            h.measured_travel_axis(geometry,[0,1,2],1.8)

    def test_actual_phase_and_sprite_probe_reject_detached_report(self):
        import hashlib
        path=self.work/'phase_pixels.png'
        image=Image.new('RGBA',(16,16*24),(80,90,100,255))
        image.putpixel((2,18),(255,0,0,255)); image.save(path)
        channel='walk/E/E/travel'
        rows=[{'mode':mode,'move':'E','aim':'E','firing':False,'frames':24,'fps':24,'cell_size':16,'path':h.rel(path)} for mode in ('walk','run')]
        d={'actor_id':'CHR_PROTO_03','qa_fixture_only':True,'representation':{'kind':'authored_8x8','assets':rows}}
        descriptor=self.work/'phase_descriptor.json';h.write(descriptor,d)
        sample={'dt':1/24,'world_position':[152/24,0],'locomotion_phase':1/24,'frame':1,
                'representation_channel':channel,'representation_atlas':h.rel(path),
                'visible_marker_count':1,'sprite_visible':True,'sprite_alpha':1,'sprite_centered':True,'sprite_flip':[False,False],
                'sprite_region':[0,16,16,16],'shown_frame_rgba_sha256':hashlib.sha256(image.crop((0,16,16,32)).tobytes()).hexdigest()}
        raw={'actor_id':'CHR_PROTO_03','subject_sha256':'fixture','descriptor':h.rel(descriptor),
             'representation_kind':'authored_8x8','sprite_pixel_probe':True,
             'cases':[{'id':'walk/E/travel','start_position':[0,0],'start_locomotion_phase':0,'samples':[sample],'shots':[]}]}
        h.validate_runtime_subject(raw,'fixture',descriptor)
        for field,value,error in [('locomotion_phase',0,'GAIT_PHASE_NOT_ACTUAL'),('frame',9,'SHOWN_GAIT_FRAME'),
                                  ('shown_frame_rgba_sha256','wrong','ACTUAL_SPRITE_PIXELS'),
                                  ('sprite_visible',False,'ACTUAL_SPRITE_HIDDEN')]:
            bad=copy.deepcopy(raw);bad['cases'][0]['samples'][0][field]=value
            with self.assertRaisesRegex(ValueError,error): h.validate_runtime_subject(bad,'fixture',descriptor)
        bad=copy.deepcopy(raw)
        bad['cases'][0]['shots']=[{**sample,'physics_sample_index':0,'state':'move'}]
        with self.assertRaisesRegex(ValueError,'ACTUAL_SHOT_DID_NOT_DISPLAY_REQUIRED_FIRE_CHANNEL'):
            h.validate_runtime_subject(bad,'fixture',descriptor)

    def test_bad_slow_speed_cannot_become_its_own_oracle(self):
        def mutate(c):
            pos = [960.,540.]
            for row in c["samples"]:
                row["requested_speed"] = 14
                row["delta"] = [14/30,0]
                pos[0] += 14/30
                row["world_position"] = pos[:]
        errors = self.altered("walk/E/travel", mutate)
        self.assertTrue(any("ACTUAL_SPEED_MISMATCH" in e for e in errors))
        self.assertTrue(any("INDEPENDENT_CONTRACT" in e for e in errors))

    def test_collision_presentation_deadband_is_time_based_not_position_based(self):
        for hz in (30,60,120):
            for speed in (0,.04,1.92,11.99,12):
                self.assertFalse(h.presentation_is_moving(speed/hz,1/hz))
            for speed in (12.01,138,152,224):
                self.assertTrue(h.presentation_is_moving(speed/hz,1/hz))
        with self.assertRaises(ValueError):h.presentation_is_moving(1,0)

    def test_blocked_flag_cannot_hide_slow_travel(self):
        def mutate(c):
            c["blocked"] = True
            for row in c["samples"]:
                row["delta"] = [0,0]
                row["world_position"] = [960,540]
        self.assertTrue(any("SPEED_MISMATCH" in e for e in self.altered("walk/E/travel", mutate)))

    def test_requires_fire_false_cannot_skip_shots(self):
        self.assertTrue(any("SUSTAINED_FIRE" in e for e in self.altered("walk/E/fire/W", lambda c:c.update(shots=[],requires_fire=False))))

    def test_static_legs_during_moving_fire(self):
        def mutate(c):
            for row in c["samples"]: row.update(state="fire",frame=0)
        self.assertTrue(any("STATIC_LEGS" in e for e in self.altered("walk/E/fire/E",mutate)))

    def test_wrong_muzzle(self):
        def mutate(c): c["shots"][0]["origin"] = [40,20]
        self.assertTrue(any("SPAWN_SOCKET" in e for e in self.altered("idle_fire/E",mutate)))

    def test_wrong_aim_and_wrong_descriptor(self):
        def mutate(c):
            for row in c["samples"]: row.update(aim_vector=[-1,0],active_descriptor="different.json")
        errors = self.altered("walk/E/travel",mutate)
        self.assertTrue(any("AIM_INPUT" in e for e in errors))
        self.assertTrue(any("WRONG_ACTIVE_DESCRIPTOR" in e for e in errors))

    def test_average_speed_does_not_replace_speed_switch(self):
        def mutate(c):
            pos = [960.,540.]
            for row in c["samples"]:
                row["delta"] = [188/30,0]
                pos[0] += 188/30
                row["world_position"] = pos[:]
        self.assertTrue(any("SPEED_MISMATCH" in e for e in self.altered("speed_switch/E",mutate)))

    def test_stop_is_a_real_stop(self):
        def mutate(c):
            pos = [960.,540.]
            for row in c["samples"]:
                row["delta"] = [152/30,0]
                pos[0] += 152/30
                row["world_position"] = pos[:]
        self.assertTrue(any("DURING_STOP" in e for e in self.altered("stop_resume/E",mutate)))

    def test_missing_direction_duration_and_nonfinite(self):
        raw = copy.deepcopy(self.baseline)
        raw["cases"].pop()
        self.assertIn("CASE_COVERAGE",self.errors(raw))
        raw["cases"][0]["samples"].pop()
        self.assertTrue(any("DURATION" in e for e in self.errors(raw)))
        raw["cases"][0]["samples"][0]["dt"] = math.nan
        with self.assertRaises(ValueError): self.errors(raw)

    def test_empty_build_provenance_does_not_pass(self):
        p = self.work / "empty_build.json"
        h.write(p,{"files":{}})
        self.assertEqual(len(h.build_closure_errors(p)),6)

    def test_path_escape_and_forged_receipts(self):
        with self.assertRaises(ValueError): h.inside(ROOT.parent)
        with self.assertRaises(ValueError): h.require_seal(None)
        p = self.work / "forged.json"
        h.write(p,{"gate":"PASS_ALL_REQUIRED_GATES"})
        with self.assertRaises((KeyError,ValueError)): h.require_seal(p)

    def test_review_evidence_hash_is_recomputed(self):
        p = self.work / "evidence.json"
        h.write(p,{"result":1})
        ref = {"path":h.rel(p),"sha256":h.digest(p)}
        h.write(p,{"result":2})
        with self.assertRaisesRegex(ValueError,"STALE_EVIDENCE"): h.verify_evidence_file(ref)

    def test_no_receipt_cannot_change_production_pointer(self):
        spec = pipeline.read_spec(ROOT / "tools/character_pipeline/specs/mica_c03_fast_v1.json")
        target = pipeline.spec_paths(spec)["descriptor"]
        before = h.digest(target)
        for action in (lambda:pipeline.promote_runtime(spec,None), lambda:pipeline.register_profile(spec,None),
                       lambda:pipeline.promote_motion_candidate(spec,str(self.work),None)):
            with self.assertRaises(ValueError): action()
            self.assertEqual(h.digest(target),before)

    @unittest.skipUnless(R21.exists(),"Large local candidate not present in CI")
    def test_real_r21_bad_muzzles_and_speed_are_rejected(self):
        report = h.audit(R21)
        self.assertEqual(report["gate"],"FAIL")
        self.assertTrue(any("SOCKET_IN_EMPTY_SPACE:E" in e for e in report["errors"]))
        self.assertTrue(any("ROOT_SPEED_CONTRACT" in e for e in report["errors"]))
        self.assertFalse(any("INVALID_ROOT_TRACK" in e for e in report["errors"]))

    @unittest.skipUnless(R22.exists(),"Large local candidate not present in CI")
    def test_real_r22_unit_regression_is_rejected(self):
        report = h.audit(R22)
        self.assertTrue(any("REJECTED_SOURCE" in e for e in report["errors"]))
        self.assertLess(report["metrics"]["E"]["authored_world_px_per_second"],1)

    @unittest.skipUnless(R4_FRAME.exists(),"Large local candidate not present in CI")
    def test_renamed_rejected_r4_still_rejected(self):
        target = self.work / "renamed.png"
        shutil.copy2(R4_FRAME,target)
        self.assertTrue(h.rejection_reasons([target]))

    def test_quarantine_preserves_bytes_and_inventory(self):
        folder = self.work / "old_candidate"
        folder.mkdir()
        h.write(folder / "source.json",{"retain":"all"})
        before = h.digest(folder/"source.json")
        target = h.quarantine(folder,"synthetic retention regression")
        self.assertFalse(folder.exists())
        self.assertEqual(h.digest(target/"source.json"),before)
        self.assertTrue(target.with_suffix(".inventory.json").exists())

    def gait_fixture(self):
        work = self.work / ("gait_"+uuid.uuid4().hex)
        work.mkdir()
        result = {"subject_sha256":"fixture", "method":"decoded_frames_and_evaluated_skinned_vertices",
                  "units":"metres_seconds_body_forward_left_up", "sequences":[]}
        # Deliberately tiny analytic diagrams, not character artwork or review evidence.
        images = []
        for i in range(24):
            p = work/f"analytic_{i}.png"
            Image.new("RGBA",(16,16),(i*10,60,120,255)).save(p)
            images.append(p)
        for mode in ("walk","run"):
            rows, geometry_frames = [], {}
            for i in range(49):
                row = {"time_s":i/24,"geometry_frame":i,"image":h.rel(images[i%24]),"image_sha256":h.digest(images[i%24]),"pelvis_world_z_m":1.0}
                vertices = {}
                for side, offset, y in (("left",0,0.15),("right",0.5,-0.15)):
                    phase = (i/24 + offset) % 1
                    stance = .6 if mode == "walk" else .4
                    contact = phase < stance
                    swing = (phase-stance)/(1-stance)
                    x = .6 if contact else -.6 + 1.2*swing
                    z = 0 if contact else (.12 if mode == "walk" else .24)*math.sin(math.pi*swing)
                    pos = [x,y,z]
                    row.update({side+"_contact":contact,side+"_sole_body_m":pos[:],side+"_sole_world_m":pos[:],
                                side+"_calf_width_ratio":1,side+"_ankle_reference_error_degrees":0,side+"_toe_heading_error_degrees":0})
                    vertices["0" if side == "left" else "1"] = pos[:]
                geometry_frames[str(i)] = {"time_s":i/24,"image_sha256":row["image_sha256"],"vertices_world_m":vertices,
                    "world_to_body_m":[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]}
                rows.append(row)
            geometry_path = work/f"{mode}_geometry.json"
            h.write(geometry_path,{"method":"Blender_evaluated_depsgraph_vertices","subject_sha256":"fixture",
                "exporter_sha256":h.digest(ROOT/"tools/character_pipeline/export_evaluated_motion_geometry.py"),
                "sole_vertex_ids":{"left":[0],"right":[1]},"frames":geometry_frames})
            for row in rows:
                row.update(evaluated_mesh_evidence=h.rel(geometry_path),evaluated_mesh_sha256=h.digest(geometry_path))
            for direction in h.DIRECTIONS:
                result["sequences"].append({"mode":mode,"direction":direction,"body_height_m":1.8,"frames_per_cycle":24,
                    "geometry":{"path":h.rel(geometry_path),"sha256":h.digest(geometry_path)},"frames":copy.deepcopy(rows)})
        return result

    def test_gait_oracles_reject_known_anatomy_regressions(self):
        baseline = self.gait_fixture()
        self.assertEqual(h.validate_observations(baseline,"fixture"),[])
        for field,value,expected in (("left_calf_width_ratio",1.8,"CALF_VOLUME"),
                                     ("left_ankle_reference_error_degrees",90,"ANKLE"),
                                     ("right_toe_heading_error_degrees",65,"TOE_HEADING")):
            bad = copy.deepcopy(baseline)
            bad["sequences"][0]["frames"][3][field] = value
            self.assertTrue(any(expected in e for e in h.validate_observations(bad,"fixture")))

    def test_bad_stride_lift_crossing_and_contact_slip_are_not_pass(self):
        baseline = self.gait_fixture()
        for field,value,expected in (("left_sole_body_m",[0,0,0],"STRIDE"),
                                     ("left_sole_body_m",[0,.15,.9],"LIFT"),
                                     ("left_sole_body_m",[0,-.5,0],"LANE_CROSS")):
            bad = copy.deepcopy(baseline)
            for f in bad["sequences"][0]["frames"]: f[field] = value
            errors = h.validate_observations(bad,"fixture")
            self.assertTrue(any(expected in e for e in errors))
            self.assertTrue(any("NOT_FROM_EVALUATED" in e for e in errors))
        bad = copy.deepcopy(baseline)
        for i,f in enumerate(bad["sequences"][0]["frames"]):
            f["left_sole_world_m"][0] += i*.015 # Each step below 1.5% height, cumulative stance slip above it.
        self.assertTrue(any("CONTACT_SLIP" in e for e in h.validate_observations(bad,"fixture")))

    def test_repeated_still_and_fake_cycle_are_rejected(self):
        baseline = self.gait_fixture()
        for f in baseline["sequences"][0]["frames"]:
            f["image"] = baseline["sequences"][0]["frames"][0]["image"]
            f["image_sha256"] = baseline["sequences"][0]["frames"][0]["image_sha256"]
            f["geometry_frame"] = 0
        errors = h.validate_observations(baseline,"fixture")
        self.assertTrue(any("REPEATED_STATIC_RENDER" in e for e in errors))
        self.assertTrue(any("REPEATED_OR_REORDERED" in e for e in errors))

    def test_runtime_report_cannot_borrow_another_subject(self):
        descriptor = self.work/"bound_descriptor.json"
        other = self.work/"other_descriptor.json"
        h.write(descriptor,{"actor_id":"CHR_PROTO_03"})
        h.write(other,{"actor_id":"CHR_PROTO_03"})
        raw = {"subject_sha256":"subject","actor_id":"CHR_PROTO_03","descriptor":h.rel(descriptor)}
        h.validate_runtime_subject(raw,"subject",descriptor)
        for field,value in (("subject_sha256","stale"),("actor_id","CHR_PROTO_02"),("descriptor",h.rel(other))):
            changed = {**raw,field:value}
            with self.assertRaises(ValueError): h.validate_runtime_subject(changed,"subject",descriptor)

    def test_extra_run_assets_are_in_snapshot_and_unknown_states_fail(self):
        p = self.work/"extra_state_descriptor.json"
        base = self.work/"base.png"
        run = self.work/"run.png"
        Image.new("RGBA",(16,16),(1,2,3,255)).save(base)
        Image.new("RGBA",(16,16),(2,3,4,255)).save(run)
        d = {"states":{s:{"frames":1,"fps":1} for s in ("idle","move","fire","run")},
             "directions":{di:{s+"_atlas":h.rel(run if s=="run" else base) for s in ("idle","move","fire","run")} for di in h.DIRECTIONS}}
        h.write(p,d)
        before = h.snapshot(p)
        self.assertIn(h.rel(run),before["files"])
        Image.new("RGBA",(16,16),(9,3,4,255)).save(run)
        self.assertNotEqual(before["subject_sha256"],h.snapshot(p)["subject_sha256"])
        d["states"]["uninspected_animation"] = {"frames":1,"fps":1}
        with self.assertRaises(ValueError): h.state_names(d)

    def test_policy_string_without_actual_8x8_assets_is_not_support(self):
        self.assertTrue(h.representation_errors({"aim_move_policy":"independent_upper_lower"}))
        self.assertTrue(h.representation_errors({"aim_move_policy":"authored_8x8","representation":{"schema":1,"kind":"authored_8x8","assets":[]}}))

    def test_combined_runtime_cannot_claim_walk_for_run_or_wrong_pair(self):
        raw=copy.deepcopy(self.baseline)
        raw['representation_kind']='authored_8x8'
        for case in raw['cases']:
            for index,row in enumerate(case['samples']):
                cmd=h.case_command(case['id'],index,len(case['samples']),{'walk':152,'run':224})
                row.update(locomotion_phase=(index%24)/24,
                    state='run' if cmd['mode']=='run' else ('move' if cmd['speed'] else 'idle'),
                    representation_channel='/'.join((cmd['mode'],h.DIRECTIONS[cmd['move_sector']],h.DIRECTIONS[cmd['aim_sector']],'travel')))
        self.assertEqual(self.errors(raw),[])
        case=next(c for c in raw['cases'] if c['id']=='run/E/fire/W')
        for row in case['samples']:
            row.update(state='move',representation_channel='walk/W/W/travel')
        errors=self.errors(raw)
        self.assertTrue(any('WRONG_ACTUAL_MOVE_AIM_CHANNEL' in e for e in errors))
        self.assertTrue(any('WALK_RUN_CLIP_NOT_SEPARATE' in e for e in errors))

    def test_combined_muzzle_requires_its_own_decoded_pixels(self):
        import hashlib
        path=self.work/'muzzle_base.png'; other=self.work/'muzzle_combined.png'
        Image.new('RGBA',(16,16),(40,80,120,255)).save(path)
        Image.new('RGBA',(16,16),(90,20,170,255)).save(other)
        d={'cell_size':16,'states':{s:{'frames':1} for s in ('idle','move','fire')},
           'directions':{di:{k:v for s in ('idle','move','fire') for k,v in
                ((s+'_atlas',h.rel(path)),(s+'_muzzle_xy',[[8,8]]))} for di in h.DIRECTIONS},
           'representation':{'kind':'authored_8x8','assets':[
                {'mode':'walk','move':'E','aim':'W','firing':True,'frames':1,'cell_size':16,'path':h.rel(other),'muzzle_xy':[[9,9]]}]}}
        def row(p):
            with Image.open(p) as im: digest=hashlib.sha256(im.tobytes()).hexdigest()
            return {'frame':0,'atlas_frame_rgba_sha256':digest,'visible_tip_xy':[8,8],
                    'barrel_to_shot_error_degrees':0,'evidence':{}}
        observations={'frames':[{**row(path),'direction':di,'state':s} for di in h.DIRECTIONS for s in d['states']]}
        with self.assertRaisesRegex(ValueError,'INCOMPLETE_VISIBLE_MUZZLE_REVIEW'):
            h.validate_visible_muzzles(observations,d,lambda r:None)
        observations['combined_frames']=[{**row(path),'mode':'walk','move':'E','aim':'W','firing':True}]
        with self.assertRaisesRegex(ValueError,'DIFFERENT_FRAME'):
            h.validate_visible_muzzles(observations,d,lambda r:None)
        observations['combined_frames'][0].update(row(other))
        h.validate_visible_muzzles(observations,d,lambda r:None)

    def test_pointer_copy_is_byte_exact_and_failure_leaves_old_pointer(self):
        work = self.work/("pointer_"+uuid.uuid4().hex)
        work.mkdir()
        spec = pipeline.read_spec(ROOT/"tools/character_pipeline/specs/mica_c03_fast_v1.json")
        spec["paths"] = {"work_root":h.rel(work/"work"),"runtime_root":h.rel(work/"runtime"),"descriptor":h.rel(work/"public.json")}
        candidate = work/"candidate.json"
        candidate.write_text('{ "actor_id" : "CHR_PROTO_03" }\n',encoding="utf-8")
        target = work/"public.json"
        h.write(target,{"old":"pointer"})
        approved = {"snapshot":{"descriptor":h.rel(candidate),"files":{h.rel(candidate):h.digest(candidate)}}}
        with patch.object(h,"require_seal",return_value=approved), patch.object(pipeline,"validate_runtime",return_value={"gate":"PASS_STRUCTURE_ONLY"}):
            pipeline.promote_runtime(spec,work/"mock_receipt.json")
            self.assertEqual(candidate.read_bytes(),target.read_bytes())
            h.write(target,{"old":"must_survive"})
            before = target.read_bytes()
            original_hash = pipeline.sha256
            with patch.object(pipeline,"sha256",side_effect=lambda p:"corrupted-copy" if p.suffix==".pending" else original_hash(p)):
                with self.assertRaises(ValueError): pipeline.promote_runtime(spec,work/"mock_receipt.json")
            self.assertEqual(before,target.read_bytes())
            # A candidate changed after seal validation must not validate itself.
            candidate.write_text('{"actor_id":"CHR_PROTO_03","tampered":true}',encoding='utf-8')
            with self.assertRaises(ValueError): pipeline.promote_runtime(spec,work/'mock_receipt.json')
            self.assertEqual(before,target.read_bytes())

    def test_geometry_cannot_borrow_an_extra_unapproved_blend_or_direction(self):
        import generation_harness as g
        work=self.work/('geometry_binding_'+uuid.uuid4().hex); work.mkdir()
        def put(name,value):
            p=work/name; h.write(p,value); return p
        blend=put('approved.blend',{'synthetic':'not production'})
        receipt_path=put('pose.json',{'synthetic':'not production'})
        descriptor=put('descriptor.json',{'actor_id':'QA'})
        put('MOTION_BUILD_INPUTS.json',{'roles':{'generation_receipt':[h.rel(receipt_path)]}})
        config={'generation_receipt':h.rel(receipt_path),'direction':'E','skinned_mesh':'body',
                'body_coordinate_frame':'ground','sole_vertex_ids':{'left':[1],'right':[2]},
                'subject_sha256':'fixture','frames':[]}
        config_path=put('config.json',config)
        binding={'qa_fixture_only':False,'generation_receipt':g.ref(receipt_path),'direction':'E',
                 'config':g.ref(config_path),'skinned_mesh':'body','body_coordinate_frame':'ground'}
        render_path=put('render.json',{**binding,'frames':{}})
        geometry={**binding,'blend_sha256':g.sha(blend),'config_sha256':g.sha(config_path),
                  'render_receipt':g.ref(render_path),'frames':{},'sole_vertex_ids':config['sole_vertex_ids'],
                  'subject_sha256':'fixture'}
        mesh_path=put('approved_mesh.json',{'scene':{'unit_scale':1}})
        pose_path=put('approved_pose_bundle.json',{'mesh_preflight':g.ref(mesh_path)})
        receipt={'blend':g.ref(blend),'approved_scope':['E'],'pose_bundle':g.ref(pose_path)}
        with patch.object(g,'verify_receipt',return_value=receipt), patch.object(g,'authorize_animation'):
            h.validate_geometry_generation(geometry,'E',descriptor)
            for field,value in (('blend_sha256','other-blend'),('direction','W'),
                                ('generation_receipt',g.ref(config_path)),('qa_fixture_only',True),
                                ('sole_vertex_ids',{'left':[8],'right':[9]})):
                with self.subTest(field=field), self.assertRaises(ValueError):
                    h.validate_geometry_generation({**geometry,field:value},'E',descriptor)

    @unittest.skipUnless((ROOT/"artifacts/motion_harness_audit/technical_fixtures/blender_pair_v1/geometry.json").exists(),"Blender paired-render local smoke not present")
    def test_real_paired_render_binding_rejects_changed_geometry(self):
        geometry = h.read(ROOT/"artifacts/motion_harness_audit/technical_fixtures/blender_pair_v1/geometry.json")
        h.validate_render_binding(geometry,"SYNTHETIC_QA_NOT_PRODUCTION")
        geometry["frames"]["1"]["vertices_world_m"]["0"][0] += .1
        with self.assertRaises(ValueError): h.validate_render_binding(geometry,"SYNTHETIC_QA_NOT_PRODUCTION")


if __name__ == "__main__":
    unittest.main(verbosity=2)
