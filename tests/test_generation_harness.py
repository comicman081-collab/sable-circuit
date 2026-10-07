"""Technical counterexamples only. No generated test image is character artwork.

Synthetic review receipts exercise code, never authorize production: every
request is explicitly qa_fixture_only, and production packaging rejects it.
"""
import copy
import json
import os
import runpy
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageDraw
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
import collect_generation_mesh_preflight as mesh


class GenerationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=ROOT/'artifacts/generation_harness_audit/unit_fixtures'/uuid.uuid4().hex
        cls.root.mkdir(parents=True)

    def setUp(self):
        self.work=self.root/self._testMethodName; self.work.mkdir()

    def put(self,name,data):
        p=self.work/name; g.write(p,data); return p

    def test_final_job_rejects_other_identity_and_previous_pose(self):
        pose=self.put('pose.json',{'synthetic':'not approval'})
        previous=self.put('previous.json',{'synthetic':'not approval'})
        descriptor=self.put('descriptor.json',{'actor_id':'QA','costume_id':'C'})
        build_path=self.put('MOTION_BUILD_INPUTS.json',{'actor_id':'QA','costume_id':'C',
            'roles':{'generation_receipt':[g.ref(pose)['path']]}})
        job={'actor_id':'QA','costume_id':'C','pose_receipt':g.ref(pose)}
        g.validate_job_motion_chain(job,descriptor)
        with self.assertRaisesRegex(ValueError,'JOB_MOTION_IDENTITY_MISMATCH'):
            g.validate_job_motion_chain({**job,'actor_id':'OTHER'},descriptor)
        with self.assertRaisesRegex(ValueError,'JOB_CURRENT_POSE_NOT_IN_FINAL_GENERATION_CHAIN'):
            g.validate_job_motion_chain({**job,'pose_receipt':g.ref(previous)},descriptor)

    def source(self,direction='S',mutate=None):
        image=self.work/'synthetic_source.png'
        im=Image.new('RGB',(1024,1536),(0,255,0))
        ImageDraw.Draw(im).rectangle((300,130,720,1399),fill=(70,45,100)); im.save(image)
        mask=self.work/'semantic_mask.png'
        m=Image.new('L',im.size); ImageDraw.Draw(m).rectangle((330,160,690,1360),fill=255); m.save(mask)
        prompt=self.work/'synthetic_prompt.txt'; prompt.write_text('QA geometric fixture, not artwork.',encoding='utf-8')
        request={'schema':1,'actor_id':'CHR_GENERATION_QA','costume_id':'QA_NOT_PRODUCTION',
            'qa_fixture_only':True,'generator':'built_in_ImageGen','max_unreviewed_outputs':1,
            'output_root':'art_src/characters/_technical_generation_requests/'+self.work.name+'_'+self.root.name,
            'references':[{**g.ref(image),'role':'identity_authority'}],
            'implementation':[g.ref(ROOT/'tools/character_pipeline/build_mica_skinned_pilot.py')],
            'prompt':g.ref(prompt),'background':'uniform_chroma_green',
            'views':[{'id':direction,'projection':'orthographic','body_facing':direction,
                      'pose':'neutral_rig','minimum_canvas':[1024,1536],'regions':['body']} ]}
        request_path=self.put('request.json',request)
        permit=self.put('permit.json',{'verdict':'RESERVED_SINGLE_SOURCE_ATTEMPT','request':g.ref(request_path)})
        points={'head_top':[510,130],'ground':[510,1400],'hip_left':[480,700],'hip_right':[540,700],
            'shoulder_left':[480,350],'shoulder_right':[540,350],'heel_left':[460,1380],
            'heel_right':[480,1380],'toe_left':[510,1380],'toe_right':[530,1380],'waist':[510,740]}
        if direction=='W':
            points.update(toe_left=[410,1380],toe_right=[430,1380])
        ann={'image_sha256':g.sha(image),'body_facing':direction,'metres_per_pixel':1.78/1270,'points':points}
        annotation=self.put('annotation.json',ann)
        source={'actor_id':request['actor_id'],'costume_id':request['costume_id'],'source_author':'built_in_ImageGen',
                'request':g.ref(request_path),'attempt_permit':g.ref(permit),
                'views':[{'id':direction,'image':g.ref(image),'annotations':g.ref(annotation),
                          'native_size':[1024,1536],'panel':[0,0,1024,1536]}],
                'regions':[{'id':'body','view':direction,'mask':g.ref(mask),'exclusions':[],
                            'purpose':'volumetric_texture','allowed_mesh_parts':['body']} ]}
        if mutate: mutate(source,request,ann)
        return self.put('source.json',source)

    def reviews(self,subject,kind):
        evidence=self.work/(kind+'_SYNTHETIC_REVIEW_NOT_CHARACTER_APPROVAL.txt')
        evidence.write_text('Synthetic unit-test reviewer. No character was assessed.',encoding='utf-8')
        return [{'role':role,'reviewer':'SYNTHETIC UNIT TEST ONLY','reviewed_utc':'2026-09-07T00:00:00Z',
                 'subject_sha256':subject,'verdict':'PASS','checks':{k:'PASS' for k in g.read(g.CONTRACT)[kind+'_review_checks']},
                 'reply_evidence':g.ref(evidence)} for role in ('visual','Ponytail FULL')]

    def approved_source(self):
        source=self.source(); audit=g.audit_source(source)
        self.assertEqual(audit['errors'],[])
        bundle=self.put('source_reviews.json',{'source_manifest':g.ref(source),
                    'reviews':self.reviews(audit['subject_sha256'],'source')})
        return self.put('source_receipt.json',g.seal_source(bundle))

    def mesh_record(self,source_path=None):
        source=g.read(source_path) if source_path else None
        blend=self.work/'synthetic.blend'; blend.write_bytes(b'NOT_A_BLENDER_FILE_UNIT_TEST_ONLY')
        ids={'left':[0,1,2],'right':[3,4,5]}
        ob={'name':'body','role':'body','hidden':False,'vertices':6,'armature':'rig','unweighted_vertices':0,
            'invalid_bone_weights':0,'bad_weight_sums':0,'boundary_edges':0,'nonmanifold_edges':0,
            'degenerate_faces':0,'dimensions':[.5,.3,1.78],'outward_normal_errors':0,'material_errors':[],
            'source_images':[],'polygon_count':8,'modifier_types':['ARMATURE'],'vertex_groups':2,
            'vertices_in_faces':list(range(6))}
        data={'schema':1,'method':'actual_Blender_scene_skin_topology_uv','collector':g.ref(mesh.__file__),
            'blend':g.ref(blend),'scene':{'view':'S','frame':1,'unit_scale':1,'render':[1920,1920,100],'camera':{'name':'camera'}},
            'contract':{'body_height_m':1.78,'required_parts':{'body':'body'},'sole_mesh':'body','sole_vertex_ids':ids,
                'attachments':[{'id':'waist'}],'body_coordinate_frame':'ground',
                'body_axes_world':{'forward':[1,0,0],'left':[0,1,0],'up':[0,0,1]},'ground_origin_world_m':[0,0,0]},
            'body_frame_matrix':[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],
            'objects':[ob],'attachments':[{'id':'waist','distance_m':0.001}],
            'sole_samples':{side:[{'id':i,'world_m':[i*.01,0,0],'weights':{'foot_'+side:1}} for i in values] for side,values in ids.items()},
            'charts':{},'triangles':[],'errors':[]}
        if source:
            data['charts']={'body_chart':{'mask':source['regions'][0]['mask'],'image':source['views'][0]['image'],
                'allowed_mesh_parts':['body'],'purpose':'volumetric_texture'}}
            data['triangles']=[{'part':'body','chart_ids':['body_chart']*3,'uv':[[.45,.5],[.47,.5],[.45,.52]]}]
        return data

    def source_surface_record(self):
        """A source-surface fixture, intentionally unlike generic body parts."""
        green=self.work/'source_green.png'; Image.new('RGB',(32,32),(0,255,0)).save(green)
        rgba=self.work/'source_rgba.png'; Image.new('RGBA',(32,32),(50,40,90,255)).save(rgba)
        blend=self.work/'source_surface.blend'; blend.write_bytes(b'UNIT_TEST_SOURCE_SURFACE')
        receipt=self.put('existing_source_receipt.json',{'fixture':'source intake only'})
        neutral=self.put('neutral.json',{'rig_name':'SourceRig','mesh_name':'SourceSurface',
            'visible_front_vertex_count':3,'fixed_native_neutral_sole_floor_m':0.0,
            'blend':g.ref(blend),'source_rgba':g.ref(rgba)})
        native=self.put('native_binding.json',{'inputs':{'report':g.ref(neutral),'blend':g.ref(blend)}})
        skin=self.put('source_skin_snapshot.json',{'fixture':'source skin snapshot'})
        bindings={'l':{'vertices':[[0,1,2]]*3,'barycentric':[[1,0,0],[0,1,0],[0,0,1]],
                       'pixels':[[2,2],[3,2],[4,2]]},
                  'r':{'vertices':[[0,1,2]]*3,'barycentric':[[1,0,0],[0,1,0],[0,0,1]],
                       'pixels':[[5,2],[6,2],[7,2]]}}
        evidence=self.put('source_sole_evidence.json',{'visible_sole_bindings':bindings})
        contract={'schema':1,'kind':mesh.SOURCE_SURFACE_KIND,
            'source':{'source_receipt':g.ref(receipt),'source_green':g.ref(green),'source_rgba':g.ref(rgba),
                      'neutral':g.ref(neutral),'native_binding':g.ref(native),
                      'sole_binding_evidence':g.ref(evidence),
                      'source_skin_snapshot':g.ref(skin),
                      'surface_sampler':g.ref(ROOT/'tools/character_pipeline/source_surface_sampling.py')},
            'surface':{'mesh':'SourceSurface','rig':'SourceRig','visible_front_vertex_count':3,
                       'fixed_native_neutral_sole_floor_m':0.0,'source_image_sha256':g.sha(green),
                       'visible_surface_authority':mesh.SOURCE_SURFACE_AUTHORITY},
            'construction':{'build_receipt':g.ref(receipt),'build_attempt':g.ref(native)}}
        positions=[[0,0,0],[.1,0,0],[0,.1,0]]
        samples={side:{'sample_count':3,'min_world_z_m':0.,'max_world_z_m':0.,
                       'positions_world_m':positions} for side in ('l','r')}
        snapshot={'source_skin_snapshot':g.ref(skin),'front_triangle_count':4,'snapshot_triangle_count':4,
                  'front_uv_and_topology_match':True,'front_weights_match':True,'front_positions_match':True}
        uv_checks={side:{'sample_count':3,'original_opaque_pixel_binding':True} for side in ('l','r')}
        ob={'name':'SourceSurface','role':'source_preserving_surface','hidden':False,
            'vertices':6,'polygon_count':8,'front_material_faces':4,'closure_faces':4,
            'front_vertices':3,'front_vertex_min':0,'front_vertex_max':2,
            'source_images':[str(rgba.resolve())],'material_errors':[],
            'source_image_sha256':g.sha(green),'visible_surface_authority':mesh.SOURCE_SURFACE_AUTHORITY,
            'modifier_types':['ARMATURE'],'armature':'SourceRig','armature_modifier_count':1,
            'unweighted_vertices':0,'invalid_bone_weights':0,'bad_weight_sums':0,'vertex_groups':4,
            'boundary_edges':0,'nonmanifold_edges':0,'degenerate_faces':0}
        return {'schema':1,'method':mesh.SOURCE_SURFACE_METHOD,'collector':g.ref(mesh.__file__),
                'blend':g.ref(blend),'scene':{'name':'Scene','frame':1,'unit_scale':1,'view':'E',
                'render':[1920,1920,100],'camera':{'name':'Camera','render':[1920,1920,100],
                'film_transparent':True,'type':'ORTHO'}},'contract':contract,'charts':{},'triangles':[],
                'objects':[ob],'source_sole_samples':samples,
                'source_snapshot':snapshot,'source_sole_uv_checks':uv_checks,
                'source_sole_binding_evidence':g.ref(evidence),'errors':[]}

    def approved_pose(self):
        receipt=self.approved_source(); s=g.read(receipt)
        raw=self.mesh_record(g.resolve(s['source_manifest']))
        raw_path=self.put('mesh.json',raw)
        image=self.work/'pose.png'; im=Image.new('RGBA',(1920,1920)); ImageDraw.Draw(im).rectangle((700,200,1200,1700),fill=(70,45,100,255)); im.save(image)
        render=self.put('render.json',{'method':'same_process_native_pose_and_mesh_preflight',
            'image':g.ref(image),'blend':raw['blend'],'view':'S','scene_sha256':g.canonical(raw['scene']),
            'mesh_preflight':g.ref(raw_path)})
        bundle=self.put('pose_bundle.json',{'source_receipt':g.ref(receipt),'mesh_preflight':g.ref(raw_path),
            'views':[{'id':'S','image':g.ref(image),'render_receipt':g.ref(render)}]})
        audit=g.audit_pose_bundle(bundle); self.assertEqual(audit['errors'],[])
        review=self.put('pose_reviews.json',{'pose_bundle':g.ref(bundle),
            'reviews':self.reviews(audit['subject_sha256'],'pose')})
        return self.put('pose_receipt.json',g.seal_pose(review))

    def test_source_technical_clean_is_hold(self):
        result=g.audit_source(self.source()); self.assertEqual(result['errors'],[])
        self.assertEqual(result['verdict'],'HOLD_SOURCE_VISUAL_REVIEW')

    def build_plan_fixture(self):
        source=self.approved_source(); authority=g.source_authority(source)
        source_image=authority['sources'][0]['views'][0]['image']
        builder=self.work/'builder.py';builder.write_text('# synthetic builder, never executed',encoding='utf-8')
        runner=self.work/'runner.py';runner.write_text('# synthetic runner, never executed',encoding='utf-8')
        scope=self.work/'scope.md';scope.write_text('SYNTHETIC QA, not an actual asset approval.',encoding='utf-8')
        license_path=self.work/'license.txt';license_path.write_text('SYNTHETIC LICENSE TEST, no production model.',encoding='utf-8')
        asset=self.work/'rig.blend';asset.write_bytes(b'NOT A BLEND FILE')
        plan=self.put('build_plan.json',{'schema':1,'stage':'build_plan','actor_id':authority['actor_id'],
            'costume_id':authority['costume_id'],'source_receipt':g.ref(source),'source_images':[source_image],
            'builder':g.ref(builder),'runner':g.ref(runner),'scope':g.ref(scope),
            'dependencies':[g.ref(mesh.__file__)],'readonly_inputs':[{'asset':g.ref(asset),'license':g.ref(license_path),'readonly':True}],
            'output_root':str(self.work/'actual_output'),'direction':'S',
            'limits':{'max_native_poses':1,'max_motion_frames':0,'threads':2,'timeout_seconds':120}})
        audit=g.audit_build_plan(plan);self.assertEqual(audit['errors'],[])
        evidence=self.work/'synthetic_build_review.txt';evidence.write_text('SYNTHETIC QA REVIEW ONLY.',encoding='utf-8')
        reviews=[{'role':role,'reviewer':role+'_unit_fixture','reviewed_utc':'2026-09-07T00:00:00Z',
            'subject_sha256':audit['subject_sha256'],'verdict':'PASS',
            'checks':{k:'PASS' for k in g.read(g.CONTRACT)['build_review_checks']},'reply_evidence':g.ref(evidence)}
            for role in g.read(g.CONTRACT)['build_review_roles']]
        bundle=self.put('build_reviews.json',{'build_plan':g.ref(plan),'reviews':reviews})
        receipt=self.put('build_receipt.json',g.seal_build_plan(bundle))
        return plan,receipt

    def test_retired_recipe_is_blocked_even_with_old_receipt_and_diagnostic_label(self):
        retired=ROOT/'tools/character_pipeline/build_mica_anatomical_candidate.py'
        with self.assertRaisesRegex(ValueError,'RETIRED_ART_REAUTHORING'):
            g.authorize_build(None,self.work,[],retired,diagnostic=True)
        result=g.next_action(ROOT/'art_src/characters/mica/rigged_v2/job_r12.json')
        self.assertEqual(result['allowed_next_action'],'REPAIR_MOTION_ADAPTER_WITHOUT_REAUTHORING_ART')
        self.assertFalse(result['production_ready'])

    def test_renamed_retired_content_cannot_get_new_build_approval(self):
        plan,_=self.build_plan_fixture();data=g.read(plan)
        original=ROOT/'artifacts/quarantine/generation_diagnostics/art_authority_retired_scripts_r1/build_mica_anatomical_candidate.py'
        renamed=self.work/'claimed_motion_only.py';renamed.write_bytes(original.read_bytes())
        data['builder']=g.ref(renamed)
        audit=g.audit_build_plan(self.put('renamed_plan.json',data))
        self.assertTrue(any('RETIRED_ART_REAUTHORING' in e for e in audit['errors']))

    def test_declarations_do_not_approve_an_unimplemented_motion_adapter(self):
        from art_authority import production_errors
        plan,_=self.build_plan_fixture();data=g.read(plan)
        data['output_root']='art_src/characters/mica/UNCREATED_BOUNDARY_TEST'
        data['art_authority']='imagegen_visuals_blender_motion_only'
        data['local_operations']=['rigging','ual_retarget']
        authority=g.source_authority(g.resolve(data['source_receipt']))
        errors=production_errors(data,authority)
        self.assertIn('SOURCE_PRESERVING_MOTION_ADAPTER_NOT_IMPLEMENTED_OR_REVIEWED',errors)
        data['local_operations'].append('face_reconstruction')
        self.assertIn('LOCAL_VISUAL_REAUTHORING_OR_UNSPECIFIED_OPERATION',production_errors(data,authority))

    def test_build_plan_preserves_source_and_requires_actual_review(self):
        plan,receipt=self.build_plan_fixture();data=g.read(plan)
        before=g.sha(g.resolve(data['source_receipt']))
        self.assertEqual(g.verify_build_plan(receipt),data)
        self.assertEqual(before,g.sha(g.resolve(data['source_receipt'])))
        empty=self.put('no_build_review.json',{'build_plan':g.ref(plan),'reviews':[]})
        with self.assertRaisesRegex(ValueError,'INDEPENDENT_REVIEW'):g.seal_build_plan(empty)

    def test_build_plan_mutated_adapter_or_license_invalidates(self):
        plan,receipt=self.build_plan_fixture();data=g.read(plan)
        g.resolve(data['readonly_inputs'][0]['license']).write_text('CHANGED LICENSE',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'STALE'):g.verify_build_plan(receipt)
        
    def test_build_plan_rejects_bad_scope_and_truthy_integer(self):
        plan,_=self.build_plan_fixture();data=g.read(plan)
        for key,value,token in [('direction','E','DIRECTION_NOT_IN_SOURCE'),
                ('output_root','art_src/characters/synthetic_escape','FIXTURE_CANNOT_ESCAPE')]:
            result=g.audit_build_plan(self.put(key+'.json',{**data,key:value}))
            self.assertTrue(any(token in e for e in result['errors']),result)
        data['limits']['max_native_poses']=True
        self.assertIn('BUILD_PLAN_ONE_BOUNDED_FIRST_POSE_ONLY',g.audit_build_plan(self.put('truthy.json',data))['errors'])

    def test_build_claims_are_exclusive_and_child_requires_runner(self):
        plan,receipt=self.build_plan_fixture();data=g.read(plan)
        attempt=g.resolve(g.reserve_build_attempt(receipt))
        with self.assertRaises((ValueError,FileNotFoundError)):
            g.claim_build_execution(attempt,receipt,g.resolve(data['builder']),'S')
        for role in ('runner','builder'):
            claim=g.claim_build_execution(attempt,receipt,g.resolve(data[role]),'S')
            self.assertEqual(claim,g.verify_build_claim(attempt,receipt,role))
            with self.assertRaisesRegex(ValueError,'RETAIN_EXISTING'):
                g.claim_build_execution(attempt,receipt,g.resolve(data[role]),'S')
        with self.assertRaisesRegex(ValueError,'RETAIN_EXISTING'):g.reserve_build_attempt(receipt)

    def test_build_execution_rejects_missing_attempt_wrong_image_direction_and_entrypoint(self):
        plan,receipt=self.build_plan_fixture();data=g.read(plan)
        attempt=g.resolve(g.reserve_build_attempt(receipt))
        args=[g.resolve(data['source_receipt']),data['output_root'],[g.resolve(r) for r in data['source_images']],g.resolve(data['runner'])]
        with self.assertRaisesRegex(ValueError,'BUILD_ATTEMPT_REQUIRED'):
            g.authorize_build(*args,build_receipt=receipt,direction='S')
        with self.assertRaisesRegex(ValueError,'DIRECTION_MISMATCH'):
            g.authorize_build(*args,build_receipt=receipt,build_attempt=attempt,direction='E')
        for index,value,token in [(1,str(self.work/'other'),'DESTINATION'),(2,[self.work/'synthetic_prompt.txt'],'UNAPPROVED_IMAGE'),(3,__file__,'ENTRYPOINT')]:
            wrong=args.copy();wrong[index]=value
            with self.assertRaisesRegex(ValueError,token):
                g.authorize_build(*wrong,build_receipt=receipt,build_attempt=attempt,direction='S')
        g.authorize_build(*args,build_receipt=receipt,build_attempt=attempt,direction='S')

    def test_actual_construction_cannot_be_omitted_by_moving_fixture_bundle(self):
        receipt=self.approved_pose();bundle=g.read(g.resolve(g.read(receipt)['pose_bundle']))
        outside=ROOT/'artifacts/generation_harness_audit'/('escaped_fixture_'+uuid.uuid4().hex+'.json')
        g.write(outside,bundle)
        self.assertIn('ACTUAL_BUILD_CONSTRUCTION_REQUIRED',g.audit_pose_bundle(outside)['errors'])

    def test_next_with_preexisting_mesh_cannot_skip_build_plan(self):
        source=self.approved_source();src=g.resolve(g.read(source)['source_manifest'])
        raw=self.put('preexisting_mesh.json',self.mesh_record(src))
        job=self.job(src);job.update(source_receipt=g.ref(source),mesh_preflight=g.ref(raw))
        result=g.next_action(self.put('job.json',job))
        self.assertEqual(result['allowed_next_action'],'AUTHOR_EXACT_BUILD_PLAN_WITHOUT_IMAGE_GENERATION')

    def bound_build_pose_fixture(self):
        plan,receipt=self.build_plan_fixture();data=g.read(plan)
        attempt=g.resolve(g.reserve_build_attempt(receipt))
        for role in ('runner','builder'):g.claim_build_execution(attempt,receipt,g.resolve(data[role]),'S')
        out=g.local(data['output_root']);out.mkdir()
        source=g.read(g.resolve(data['source_receipt']))
        raw=self.mesh_record(g.resolve(source['source_manifest']))
        blend=out/'body.blend';blend.write_bytes(b'NOT_A_BLEND_UNIT_FIXTURE')
        raw['blend']=g.ref(blend)
        raw['contract']['construction']={'build_receipt':g.ref(receipt),'build_attempt':g.ref(attempt)}
        raw_path=out/'mesh.json';g.write(raw_path,raw)
        image=out/'pose.png';im=Image.new('RGBA',(1920,1920));ImageDraw.Draw(im).rectangle((700,200,1200,1700),fill=(70,45,100,255));im.save(image)
        render=out/'render.json';g.write(render,{'method':'same_process_native_pose_and_mesh_preflight',
            'image':g.ref(image),'blend':raw['blend'],'view':'S','scene_sha256':g.canonical(raw['scene']),
            'mesh_preflight':g.ref(raw_path)})
        construction=out/'construction.json';g.write(construction,{'build_receipt':g.ref(receipt),
            'build_attempt':g.ref(attempt),'blend':g.ref(blend),'readonly_inputs_after':data['readonly_inputs'],
            'execution_claims':{r:g.verify_build_claim(attempt,receipt,r) for r in ('runner','builder')}})
        bundle=out/'bundle.json';g.write(bundle,{'source_receipt':data['source_receipt'],
            'construction':g.ref(construction),'mesh_preflight':g.ref(raw_path),
            'views':[{'id':'S','image':g.ref(image),'render_receipt':g.ref(render)}]})
        self.assertEqual(g.audit_pose_bundle(bundle)['errors'],[])
        return bundle,plan,receipt

    def test_actual_construction_output_scope_and_claims_are_bound(self):
        bundle,_,_=self.bound_build_pose_fixture();data=g.read(bundle)
        construction=g.read(g.resolve(data['construction']))
        moved=self.put('outside_construction.json',construction)
        data['construction']=g.ref(moved)
        self.assertIn('FIRST_POSE_OUTSIDE_APPROVED_BUILD_OUTPUT',
            g.audit_pose_bundle(self.put('outside_bundle.json',data))['errors'])
        construction['execution_claims']={}
        moved=self.put('missing_claims.json',construction);data['construction']=g.ref(moved)
        self.assertIn('BUILD_EXECUTION_CLAIMS_REQUIRED',
            g.audit_pose_bundle(self.put('missing_claim_bundle.json',data))['errors'])

    def test_actual_material_input_scope_is_bound_even_without_extra_chart(self):
        bundle,_,_=self.bound_build_pose_fixture();data=g.read(bundle)
        raw=g.read(g.resolve(data['mesh_preflight']))
        extra=self.work/'unapproved_texture.png';Image.new('RGB',(16,16),(22,30,44)).save(extra)
        raw['objects'][0]['source_images']=[str(extra)]
        moved=self.put('extra_material.json',raw);data['mesh_preflight']=g.ref(moved)
        errors=g.audit_pose_bundle(self.put('extra_material_bundle.json',data))['errors']
        self.assertIn('FIRST_POSE_OUTSIDE_APPROVED_BUILD_SOURCE_IMAGES',errors)

    def test_retired_entrypoints_never_start_any_child(self):
        # Retired entrypoints must fail before parser, filesystem or Blender.
        for name in ('run_mica_anatomical_candidate.py', 'build_mica_anatomical_candidate.py',
                     'run_mica_skinned_pilot.py', 'build_mica_skinned_pilot.py'):
            script=ROOT/'tools/character_pipeline'/name
            with patch.object(sys,'argv',[name,'--diagnostic-only']),patch('subprocess.run') as child:
                with self.assertRaisesRegex(RuntimeError,'RETIRED_ART_REAUTHORING_ROUTE'):
                    runpy.run_path(str(script),run_name='__main__')
                child.assert_not_called()
        self.assertFalse((self.work/'actual_output').exists())

    def test_native_alpha_not_opaque_checkerboard(self):
        import numpy as np
        image=np.zeros((32,32,4),dtype=np.uint8)
        image[8:24,8:24]=[90,75,100,255]
        result=g.audit_native_alpha(image)
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['verdict'],'HOLD_ALPHA_VISUAL_REVIEW')
        image[...,3]=255
        self.assertIn('REAL_ZERO_AND_OPAQUE_ALPHA_REQUIRED',g.audit_native_alpha(image)['errors'])

    def test_native_alpha_rejects_empty_clipped_and_globally_translucent(self):
        import numpy as np
        image=np.zeros((32,32,4),dtype=np.uint8)
        self.assertIn('MISSING_OPAQUE_SUBJECT',g.audit_native_alpha(image)['errors'])
        image[8:24,8:24]=[90,75,100,128]
        self.assertIn('REAL_ZERO_AND_OPAQUE_ALPHA_REQUIRED',g.audit_native_alpha(image)['errors'])
        image[0:24,8:24]=[90,75,100,255]
        self.assertIn('ALPHA_BACKGROUND_NOT_CLEAR_AT_BORDER',g.audit_native_alpha(image)['errors'])

    def test_transparent_request_is_explicitly_supported(self):
        src=g.read(self.source()); request=g.read(g.resolve(src['request']))
        request['background']='transparent_alpha'
        self.assertEqual(g.audit_request(self.put('alpha_request.json',request))['errors'],[])
        request['background']='checkerboard'
        self.assertIn('EXPLICIT_CHROMA_OR_NATIVE_ALPHA_BACKGROUND_REQUIRED',
                      g.audit_request(self.put('bad_background.json',request))['errors'])

    def test_native_alpha_failure_requires_independent_green_fallback_review(self):
        src=g.read(self.source()); request=g.read(g.resolve(src['request']))
        failed=self.put('native_alpha_failure.json',{
            'schema':1,'stage':'failed_source_attempt','verdict':'FAIL',
            'actor_id':request['actor_id'],'costume_id':request['costume_id'],
            'category':'native_alpha_response','errors':['NO_GENUINE_TRANSPARENT_PIXELS']})
        request.update(background='transparent_alpha',previous_attempt=g.ref(failed))
        errors=g.audit_request(self.put('alpha_retry.json',request))['errors']
        self.assertIn('NATIVE_ALPHA_FAILURE_REQUIRES_CHROMA_FALLBACK',errors)
        self.assertIn('NATIVE_ALPHA_FAILURE_REQUIRES_INDEPENDENT_CAUSE_REVIEW',errors)
        review=self.put('independent_review.json',{
            'schema':1,'stage':'independent_failure_cause_review','reviewer':'synthetic reviewer',
            'failure_attempt':g.ref(failed),'verdict':'PASS_CHROMA_GREEN_FALLBACK',
            'checks':{'failure_reproduced':'PASS','transparent_alpha_retry_prohibited':'PASS',
                      'uniform_chroma_green_changed_mechanism':'PASS'}})
        request.update(background='uniform_chroma_green',previous_failure_review=g.ref(review))
        self.assertEqual(g.audit_request(self.put('green_fallback.json',request))['errors'],[])

    def test_matte_normalization_binds_raw_master_mask_and_exact_normalizer(self):
        source=self.source(); data=g.read(source); request=g.read(g.resolve(data['request']))
        raw=self.work/'raw.png'; Image.new('RGB',(1024,1536),(12,240,9)).save(raw)
        master=g.resolve(data['views'][0]['image'])
        mask=self.work/'matte_mask.png'; Image.new('L',(1024,1536),0).save(mask)
        qa=self.put('normalization_qa.json',{
            'input':g.ref(raw)['path'],'input_sha256':g.sha(raw),
            'output':data['views'][0]['image']['path'],'output_sha256':data['views'][0]['image']['sha256'],
            'mask':g.ref(mask)['path'],'mask_sha256':g.sha(mask),
            'subject_pixels_byte_exact':True})
        data['matte_normalization']={'raw_image':g.ref(raw),'normalized_master':g.ref(master),
            'background_mask':g.ref(mask),'normalization_qa':g.ref(qa),
            'normalizer':g.ref(ROOT/'tools/character_pipeline/normalize_imagegen_chroma.py')}
        self.assertEqual(g.audit_source(self.put('normalized_source.json',data))['errors'],[])
        bad=copy.deepcopy(data); bad['matte_normalization']['normalizer']=g.ref(ROOT/'tools/character_pipeline/derive_chroma_runtime_rgba.py')
        errors=g.audit_source(self.put('bad_normalizer_source.json',bad))['errors']
        self.assertIn('UNSUPPORTED_MATTE_NORMALIZER',errors)

    def test_native_alpha_uv_rejects_hole_without_rejecting_green_material(self):
        import numpy as np
        img=Image.new('RGBA',(32,32),(0,220,0,255))
        img.putpixel((0,0),(0,0,0,0)); image_path=self.work/'native_alpha.png';img.save(image_path)
        mask_path=self.work/'opaque_mask.png';Image.new('L',(32,32),255).save(mask_path)
        chart={'mask':g.ref(mask_path),'image':g.ref(image_path),'allowed_mesh_parts':['body']}
        triangles=[{'part':'body','chart_ids':['body']*3,'uv':[[.4,.4],[.6,.4],[.4,.6]]}]
        self.assertEqual(g.check_uv_triangles(triangles,{'body':chart}),[])
        img.putpixel((15,16),(0,220,0,0));hole=self.work/'hole.png';img.save(hole)
        chart['image']=g.ref(hole)
        self.assertIn('UV_INTERIOR_SAMPLES_CHROMA_OR_FOREIGN_REGION',g.check_uv_triangles(triangles,{'body':chart}))

    def test_unreviewed_source_cannot_seal(self):
        p=self.put('reviews.json',{'source_manifest':g.ref(self.source()),'reviews':[]})
        with self.assertRaisesRegex(ValueError,'INDEPENDENT_REVIEW'): g.seal_source(p)

    def test_request_no_local_generator(self):
        src=g.read(self.source()); request=g.read(g.resolve(src['request'])); request['generator']='ComfyUI'
        self.assertIn('BUILT_IN_IMAGEGEN_REQUEST_REQUIRED',g.audit_request(self.put('local_request.json',request))['errors'])

    def test_repeated_request_is_not_a_new_permit(self):
        source=g.read(self.source()); path=g.resolve(source['request'])
        g.reserve_request(path)
        copied=self.put('renamed_request.json',g.read(path))
        with self.assertRaisesRegex(ValueError,'RETAIN_EXISTING'): g.reserve_request(copied)

    def test_missing_permit_blocks_source(self):
        src=g.read(self.source()); src['attempt_permit']=g.ref(self.put('wrong_permit.json',{}))
        self.assertIn('SOURCE_HAS_NO_MATCHING_PRE_GENERATION_PERMIT',g.audit_source(self.put('bad_source.json',src))['errors'])

    def test_native_source_below_floor(self):
        source=self.source(); src=g.read(source)
        low=self.work/'low.png'; Image.new('RGB',(1024,900),(50,30,80)).save(low)
        src['views'][0].update(image=g.ref(low),native_size=[1024,900],panel=[0,0,1024,900])
        ann=g.read(g.resolve(src['views'][0]['annotations'])); ann['image_sha256']=g.sha(low)
        ann['points']={k:[v[0],v[1]*.5] for k,v in ann['points'].items()}
        src['views'][0]['annotations']=g.ref(self.put('low_annotation.json',ann))
        errors=g.audit_source(self.put('low_source.json',src))['errors']
        self.assertIn('S:SOURCE_NATIVE_RESOLUTION',errors)
        self.assertIn('S:INSUFFICIENT_NATIVE_SUBJECT_DETAIL',errors)

    def test_profile_front_hips_and_wrong_boot_axis(self):
        src=g.read(self.source('E')); ann=g.read(g.resolve(src['views'][0]['annotations']))
        ann['points'].update(hip_left=[300,700],hip_right=[700,700],toe_left=[430,1380])
        src['views'][0]['annotations']=g.ref(self.put('wrong_direction.json',ann))
        errors=g.audit_source(self.put('wrong_source.json',src))['errors']
        self.assertIn('E:FRONT_FACING_HIP_IN_PROFILE',errors); self.assertIn('E:BOOT_NOT_FACING_PROFILE:left',errors)

    def test_green_and_foreign_part_in_mask(self):
        src=g.read(self.source()); mask=self.work/'all_mask.png'; Image.new('L',(1024,1536),255).save(mask)
        src['regions'][0].update(mask=g.ref(mask),exclusions=[g.ref(mask)])
        errors=g.audit_source(self.put('foreign.json',src))['errors']
        self.assertIn('body:MASK_INCLUDES_CHROMA',errors); self.assertIn('body:FOREIGN_PART_IN_TEXTURE_REGION',errors)

    def test_upper_mask_cannot_include_legs(self):
        src=g.read(self.source()); src['regions'][0]['purpose']='unwarped_upper'
        errors=g.audit_source(self.put('upper.json',src))['errors']
        self.assertIn('body:UPPER_MASK_INCLUDES_LOWER_BODY',errors)

    def test_actual_consumed_image_not_approved(self):
        receipt=self.approved_source()
        other=self.work/'other.png'; Image.new('RGB',(32,32)).save(other)
        with self.assertRaisesRegex(ValueError,'UNREVIEWED_SOURCE_ART'):
            g.authorize_build(receipt,self.work/'out',[other],__file__)

    def test_changed_source_or_generator_invalidates_receipt(self):
        receipt=self.approved_source(); g.verify_receipt(receipt)
        p=self.work/'synthetic_prompt.txt'; p.write_text('Changed prompt.',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'STALE'): g.verify_receipt(receipt)

    def test_two_reviewed_sources_compose_without_bypassing_review(self):
        receipt=self.approved_source()
        source_set=self.put('set.json',{'stage':'source_set','receipts':[g.ref(receipt)]})
        self.assertEqual(g.source_authority(source_set)['actor_id'],'CHR_GENERATION_QA')
        fake=self.put('fake_receipt.json',{'stage':'source','verdict':'HOLD'})
        source_set=self.put('bad_set.json',{'stage':'source_set','receipts':[g.ref(fake)]})
        with self.assertRaises(ValueError): g.source_authority(source_set)

    def test_shared_runner_blocks_before_starting_blender(self):
        args=['runner','--out',str(self.work/'out')]
        with patch.object(sys,'argv',args),patch('subprocess.run') as process:
            with self.assertRaisesRegex(RuntimeError,'RETIRED_ART_REAUTHORING_ROUTE'):
                runpy.run_path(str(ROOT/'tools/character_pipeline/run_mica_skinned_pilot.py'),run_name='__main__')
            process.assert_not_called()
        self.assertFalse((self.work/'out').exists())

    def test_diagnostic_output_cannot_enter_art_sources(self):
        with self.assertRaisesRegex(ValueError,'QUARANTINE_ONLY'):
            g.authorize_build(None,'art_src/characters/test_escape',[],__file__,True)

    def test_new_or_edited_character_builder_cannot_use_diagnostic_bypass(self):
        generator=self.work/'newly_named_builder.py'
        generator.write_text('# unknown character reconstruction',encoding='utf-8')
        out=ROOT/'artifacts/quarantine/generation_diagnostics/UNCREATED_SCOPE_TEST'
        with self.assertRaisesRegex(ValueError,'NO_DIAGNOSTIC_BYPASS'):
            g.authorize_build(None,out,[],generator,True)
        with self.assertRaisesRegex(ValueError,'FLAG_MUST_BE_BOOLEAN'):
            g.authorize_build(None,out,[],generator,'false')
        self.assertFalse(out.exists())

    def uv_case(self):
        image=self.work/'texture.png'; mask=self.work/'region.png'
        Image.new('RGB',(64,64),(80,40,100)).save(image); Image.new('L',(64,64),255).save(mask)
        return image,mask,[{'part':'coat','chart_ids':['coat']*3,'uv':[[.2,.2],[.8,.2],[.5,.8]]}]

    def uv_errors(self,image,mask,triangles):
        return g.check_uv_triangles(triangles,{'coat':{'mask':g.ref(mask),'image':g.ref(image),'allowed_mesh_parts':['coat']}})

    def test_uv_triangle_interior_catches_foreign_hand_mask(self):
        image,mask,tri=self.uv_case(); self.assertEqual(self.uv_errors(image,mask,tri),[])
        m=Image.open(mask).copy(); ImageDraw.Draw(m).rectangle((31,25,32,45),fill=0); m.save(mask)
        self.assertIn('UV_INTERIOR_SAMPLES_CHROMA_OR_FOREIGN_REGION',self.uv_errors(image,mask,tri))

    def test_uv_filter_footprint_catches_boundary(self):
        image,mask,tri=self.uv_case(); tri[0]['uv'][0]=[0.01,0.01]
        self.assertTrue(self.uv_errors(image,mask,tri))

    def test_uv_different_charts_cannot_share_face(self):
        image,mask,tri=self.uv_case(); tri[0]['chart_ids'][1]='other'
        self.assertIn('UV_FACE_CROSSES_CHART_OR_UNASSIGNED',self.uv_errors(image,mask,tri))

    def test_uv_point_cannot_pretend_to_be_source_coverage(self):
        image,mask,tri=self.uv_case(); tri[0]['uv']=[[.5,.5]]*3
        self.assertIn('DEGENERATE_UV_TRIANGLE',self.uv_errors(image,mask,tri))

    def test_mesh_skin_topology_and_attachments(self):
        data=self.mesh_record(self.source()); self.assertEqual(mesh.validate_collected(data)['errors'],[])
        data['objects'][0].update(hidden=True,unweighted_vertices=1,boundary_edges=4,dimensions=[.3,0,1.78])
        data['attachments'][0]['distance_m']=.2
        errors=mesh.validate_collected(data)['errors']
        for token in ('INVALID_OR_INVISIBLE_REAL_SKIN','OPEN_OR_NONMANIFOLD_ANATOMY','ANATOMICAL_PLANE_NOT_VOLUME','DISCONNECTED_ATTACHMENT'):
            self.assertTrue(any(token in e for e in errors),token)

    def test_source_surface_preflight_has_its_own_truthful_contract(self):
        data=self.source_surface_record()
        self.assertEqual(mesh.validate_collected(data)['errors'],[])
        data['contract']['required_parts']={'body':'body'}
        self.assertIn('GENERIC_ANATOMICAL_PART_SCHEMA_FORBIDDEN_FOR_SOURCE_SURFACE',
            mesh.validate_collected(data)['errors'])

    def test_camera_plane_source_surface_requires_exact_motion_evidence(self):
        data=self.source_surface_record()
        skin=self.put('camera_source_skin.json',{'bone_order':[{'name':'root'},{'name':'calf_r'}]})
        raw=self.work/'raw_tripo_pose_matrices.npy'
        np.save(raw,np.tile(np.eye(4,dtype=float),(97,2,1,1)),allow_pickle=False)
        source=data['contract']['source']
        source['source_skin_snapshot']=g.ref(skin)
        data['source_snapshot']['source_skin_snapshot']=g.ref(skin)
        witness=self.put('calf_width_witness.json',{
            'kind':'MICA_E_camera_plane_calf_width_witness',
            'source_rgba':source['source_rgba'],
            'source_skin':source['source_skin_snapshot'],
            'cross_sections':[{}, {}, {}],
            'minimum_retained_width_ratio':.90,
        })
        source['camera_plane_calf_witness']=g.ref(witness)
        source['raw_tripo_pose_matrices']=g.ref(raw)
        data['contract']['kind']=mesh.SOURCE_SURFACE_CAMERA_PLANE_KIND
        self.assertEqual(mesh.validate_collected(data)['errors'],[])
        source.pop('camera_plane_calf_witness')
        self.assertIn('EXACT_SOURCE_SURFACE_BINDING_SCHEMA_REQUIRED',
            mesh.validate_collected(data)['errors'])

    def test_camera_plane_kind_stays_in_source_surface_trust_boundary(self):
        self.assertTrue(mesh.is_source_preserving_surface_kind(mesh.SOURCE_SURFACE_KIND))
        self.assertTrue(mesh.is_source_preserving_surface_kind(mesh.SOURCE_SURFACE_CAMERA_PLANE_KIND))
        self.assertFalse(mesh.is_source_preserving_surface_kind('unreviewed_surface_kind'))

    def test_source_surface_rejects_nonreviewed_texture_or_open_surface(self):
        data=self.source_surface_record()
        data['objects'][0]['source_images']=[str((self.work/'foreign.png').resolve())]
        data['objects'][0]['boundary_edges']=1
        errors=mesh.validate_collected(data)['errors']
        self.assertIn('ACTUAL_SOURCE_SURFACE_OR_SKIN_MISMATCH',errors)

    def test_actual_sole_vertices_not_controller_points(self):
        data=self.mesh_record(self.source()); data['sole_samples']['left'][0]['id']=999
        errors=mesh.validate_collected(data)['errors']
        self.assertIn('ACTUAL_SOLE_VERTEX_COVERAGE:left',errors)
        self.assertIn('SOLE_SAMPLE_NOT_ON_REAL_WEIGHTED_SURFACE:left',errors)

    def test_body_frame_axis_and_ground_locked(self):
        data=self.mesh_record(self.source()); data['body_frame_matrix'][2][3]=.4
        self.assertIn('BODY_FRAME_AXES_OR_GROUND_ORIGIN_MISMATCH',mesh.validate_collected(data)['errors'])

    def test_pixel_clean_pose_is_still_hold(self):
        image=self.work/'pose.png'; im=Image.new('RGBA',(1920,1080)); ImageDraw.Draw(im).rectangle((300,100,900,1000),fill=(80,40,100,255)); im.save(image)
        self.assertEqual(g.audit_pose(image)['verdict'],'HOLD_FIRST_POSE_VISUAL_REVIEW')

    def test_pose_green_and_clipping_rejected(self):
        image=self.work/'pose.png'; Image.new('RGBA',(1920,1080),(0,255,0,255)).save(image)
        self.assertEqual(set(g.audit_pose(image)['errors']),{'OPAQUE_SOURCE_GREEN_ON_CHARACTER','FIRST_POSE_CLIPPED'})

    def test_first_pose_receipt_cannot_expand_scope(self):
        receipt=self.approved_pose(); g.verify_receipt(receipt,'first_pose')
        data=g.read(receipt); data['approved_scope']=['S','E']
        with self.assertRaisesRegex(ValueError,'FORGED_FIRST_POSE'):
            g.verify_receipt(self.put('forged.json',data),'first_pose')

    def test_animation_cannot_change_direction_body_frame_or_camera(self):
        receipt=self.approved_pose(); r=g.read(receipt)
        c={'generation_receipt':str(receipt),'direction':'S','skinned_mesh':'body','sole_vertex_ids':{'left':[0,1,2],'right':[3,4,5]},'body_coordinate_frame':'ground','native_size':1920}
        with self.assertRaisesRegex(ValueError,'SYNTHETIC_GENERATION_FIXTURE_NOT_PRODUCTION'):
            g.authorize_animation(c,g.resolve(r['blend']),r['scene_sha256'])
        # Exercise the downstream contract separately; the mock is confined to
        # this unit test and never creates a production receipt.
        with patch.object(g,'assert_production_source_receipt',return_value={}):
            g.authorize_animation(c,g.resolve(r['blend']),r['scene_sha256'])
            for key,value,error in [('direction','E','REQUESTED_DIRECTION'),('body_coordinate_frame','other','BODY_FRAME'),('native_size',2048,'RESOLUTION')]:
                other={**c,key:value}
                with self.assertRaisesRegex(ValueError,error): g.authorize_animation(other,g.resolve(r['blend']))
            with self.assertRaisesRegex(ValueError,'LIVE_CAMERA'):
                g.authorize_animation(c,g.resolve(r['blend']),'changed')

    def test_animation_fixture_receipt_cannot_be_downgraded_by_omitting_flag(self):
        receipt=self.approved_pose(); r=g.read(receipt)
        config={'generation_receipt':str(receipt),'direction':'S','skinned_mesh':'body',
                'sole_vertex_ids':{'left':[0,1,2],'right':[3,4,5]},
                'body_coordinate_frame':'ground','native_size':1920}
        self.assertNotIn('qa_fixture_only',config)
        with self.assertRaisesRegex(ValueError,'SYNTHETIC_GENERATION_FIXTURE_NOT_PRODUCTION'):
            g.authorize_animation(config,g.resolve(r['blend']))

    def test_truthy_non_boolean_fixture_flag_is_rejected(self):
        for value in ('false',1,[],None):
            with self.assertRaisesRegex(ValueError,'MUST_BE_BOOLEAN'):
                g.authorize_animation({'qa_fixture_only':value},self.work/'not_needed.blend')

    def test_fixture_all_outputs_remain_isolated(self):
        root=ROOT/'artifacts/motion_harness_audit/technical_fixtures'
        c={'qa_fixture_only':True,'subject_sha256':'SYNTHETIC_QA_NOT_PRODUCTION',
            'output':str(root/'geometry.json'),'render_receipt':str(root/'render.json'),
            'frames':[{'image':str(root/'cell.png'),'master_image':'art_src/characters/escape.png'}]}
        with self.assertRaisesRegex(ValueError,'ESCAPE'): g.authorize_animation(c,root/'fixture.blend')
        c['frames'][0]['master_image']=str(root/'native.png'); c['render_receipt']='assets/escape.json'
        with self.assertRaisesRegex(ValueError,'ESCAPE'): g.authorize_animation(c,root/'fixture.blend')

    def test_later_camera_keyframe_is_not_authorized(self):
        camera={'name':'E','matrix':[[1,0,0],[0,1,0],[0,0,1]],'ortho_scale':2.65}
        g.assert_camera_lock(camera,copy.deepcopy(camera))
        moved=copy.deepcopy(camera); moved['ortho_scale']=3
        with self.assertRaisesRegex(ValueError,'CAMERA_CHANGED'): g.assert_camera_lock(camera,moved)

    def test_generation_approval_required_before_packaging(self):
        with self.assertRaisesRegex(ValueError,'EIGHT_REVIEWED'): g.motion_build_bindings([], 'CHR_PROTO_03','MICA')

    def test_partial_output_never_gets_completion(self):
        self.put('rig_manifest.json',{})
        with self.assertRaises((ValueError,KeyError,FileNotFoundError)): g.completion_record(self.work,'E')
        self.assertFalse((self.work/'JOB_COMPLETE.json').exists())

    def test_atomic_evidence_never_overwrites(self):
        p=self.put('immutable.json',{'first':1}); before=g.sha(p)
        with self.assertRaises(ValueError): g.write(p,{'second':2})
        self.assertEqual(before,g.sha(p)); self.assertEqual(list(self.work.glob('*.pending')),[])

    def test_project_boundary(self):
        for target in (ROOT,ROOT.parent):
            with self.assertRaisesRegex(ValueError,'PROJECT_LOCAL'): g.local(target)

    def job(self,source_path):
        source=g.read(source_path)
        return {'schema':1,'actor_id':source['actor_id'],'costume_id':source['costume_id'],
            'request':source['request'],'permit':source['attempt_permit'],'source_manifest':g.ref(source_path)}

    def test_next_action_requires_review_not_animation(self):
        job=self.put('job.json',self.job(self.source()))
        result=g.next_action(job)
        self.assertEqual(result['allowed_next_action'],'REQUEST_INDEPENDENT_SOURCE_REVIEWS')
        self.assertFalse(result['allow_batch_generation']); self.assertFalse(result['production_ready'])

    def test_next_action_cannot_borrow_permit_or_character(self):
        job=self.job(self.source()); job['actor_id']='CHR_PROTO_03'
        result=g.next_action(self.put('job.json',job))
        self.assertEqual(result['allowed_next_action'],'REPAIR_BINDINGS_WITHOUT_GENERATION')
        self.assertIn('JOB_REQUEST_IDENTITY_MISMATCH',result['errors'])

    def test_next_action_exposes_bad_source_before_generation(self):
        source=self.source(); data=g.read(source); data['views'][0]['native_size']=[100,100]
        bad=self.put('bad.json',data); result=g.next_action(self.put('job.json',self.job(bad)))
        self.assertEqual(result['allowed_next_action'],'QUARANTINE_AND_REPAIR_SOURCE')
        self.assertIn('S:SOURCE_NATIVE_RESOLUTION',result['errors'])


if __name__=='__main__':
    unittest.main(verbosity=2)
