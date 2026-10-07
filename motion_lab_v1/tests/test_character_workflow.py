"""Deterministic technical fixtures only; no generated game art or API calls."""
import copy,hashlib,json,math,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
LAB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB))
import character_workflow as workflow
import package_standalone as packager
import new_character
import build_character
import cycle_review
from PIL import Image

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value),encoding='utf-8')

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='workflow_',dir=base));self.addCleanup(shutil.rmtree,self.root,True)
        assert self.root.resolve().is_relative_to(base.resolve())
        # Preserve tiny test fixtures as evidence; never recursively clean user assets.
        self.patches=[patch.object(module,'ROOT',self.root) for module in [workflow,packager,new_character,build_character]]
        for p in self.patches:p.start();self.addCleanup(p.stop)
        self.art=self.root/'art/fixture';self.art.mkdir(parents=True)
        self.reference=self.art/'identity_reference.png';self.reference.write_bytes(b'technical-identity-fixture')
        self.config=json.loads((LAB/'characters/mica.json').read_text(encoding='utf-8-sig'))
        self.config.update(id='fixture',name='TECHNICAL FIXTURE',source='art/fixture',workflowVersion=1,identityReference='art/fixture/identity_reference.png',referenceSHA256=digest(self.reference),clips={'walk':{'frames':6},'idle':{'frames':1}},annotations={})
        save(self.root/'characters/fixture.json',self.config)
    def populate_sources(self):
        reviews=[]
        for index,(slot,path) in enumerate(workflow.slots(self.config)):
            Image.new('RGBA',(16,24),(30+index,80,150,255)).save(path)
            master=self.art/f'technical_master_{index}.png';master.write_bytes(path.read_bytes())
            returned=str((self.root/f'fake_returned_{index}.png').resolve())
            proof=self.art/f'proof_{index}.json';save(proof,{'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Technical fixture, not a real tool invocation: '+returned},'projectCopy':str(master.relative_to(self.root)),'projectCopySHA256':digest(master)})
            receipt=path.with_suffix('.source.json')
            save(receipt,{'generator':'Codex built-in ImageGen','sha256':digest(path),'destination':str(path.relative_to(self.root)),'toolResponse':workflow.binding(proof),'sourceMaster':workflow.binding(master)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':digest(path),'sourceReceiptSHA256':digest(receipt),'referenceSHA256':self.config['referenceSHA256'],'evidence':workflow.binding(path)})
        save(self.root/'qa/fixture/source_reviews.json',reviews)
        return list(workflow.slots(self.config))
    def browser_report(self):
        test_script=self.root/'public/qa/combat-checks.js';test_script.parent.mkdir(parents=True,exist_ok=True);test_script.write_text('fixture')
        rows=[{'name':f'{mode}_{d}','direction':d,'spriteDirection':d,'pass':True,'heldMouse':True,'shotCount':2,'observedShots':2,'travel':.2,'maxFacingErrorDegrees':0,'convergedShots':2,'maxCursorError':0} for mode in ['mouse','keyboard'] for d in workflow.DIRECTIONS]
        rows.append(dict(rows[0],name='repeat_preserves_mouse'))
        rapid=[dict(name=f'{mode}_{d}',pass_=True,heldMouse=True,locomotionUnchanged=True,oldProjectileVelocityUnchanged=True,immediateErrorDegrees=0,firstFrameErrorDegrees=0,shotErrorDegrees=0,immediateMs=.1,firstFrameMs=16,shotWaitSeconds=.1,eligibleBudgetSeconds=.1,shotCount=1) for mode in ['stationary','moving'] for d in workflow.DIRECTIONS]
        for r in rapid:
            r['pass']=r.pop('pass_');r['travel']=.2 if r['name'].startswith('moving_') else 0
            r.update(initialCooldownSeconds=.1-1/120,initialReloadSeconds=0,initialAmmo=1)
            sector=workflow.DIRECTIONS.index(r['name'].split('_',1)[1])
            r['inputSamples']=[dict(sector=s,offsetMs=.01*i,actorTime=0,actorPosition=[0,0],requestedTarget=[4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)],muzzle=[0,0,self.config['weapon']['height']],target=[4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4)],aim=s*math.pi/4) for i,s in enumerate([(sector+4)%8,(sector+2)%8,sector])]
            r['locomotionBefore']=[0,0,0,0,0,1,.1-1/120,-10,0]
            r['locomotionAfterInput']=r['locomotionBefore'].copy()
            r['oldProjectileSamples']=[dict(index=0,before=[10,0],after=[10,0])]
        return {'kind':'motion-studio-combat-browser','character':'fixture','build':{'inputSHA256':'current'},'testScriptSHA256':digest(test_script),'pass':True,'results':rows,'rapidAim':rapid,'externalResources':[],'viewport':[1920,1080]}
    def test_missing_source_returns_concrete_pilot(self):
        report=workflow.source_status('fixture')
        self.assertFalse(report['ready']);self.assertEqual(report['next']['slot'],'E/idle/0')
    def test_static_walk_cannot_replace_the_required_motion(self):
        self.config['clips']['walk']['frames']=1;save(self.root/'characters/fixture.json',self.config)
        with self.assertRaises(ValueError):workflow.source_status('fixture')
    def test_scaffold_requests_exact_character_slots_without_generation(self):
        save(self.root/'characters/mica.json',self.config)
        for name,run,count in [('newwalk',False,56),('newrun',True,104)]:
            new_character.scaffold(name,name.upper(),self.reference,run)
            recipe=json.loads((self.root/'characters'/f'{name}.json').read_text())
            requests=json.loads((self.root/'art'/name/'requests.json').read_text())
            self.assertEqual(recipe['id'],name);self.assertEqual(recipe['annotations'],{})
            self.assertEqual(recipe['referenceSHA256'],digest(self.reference));self.assertEqual(len(requests),count)
            self.assertTrue(all(r['state']=='NEEDS_IMAGEGEN' and r['destination'].startswith('art/'+name+'/') for r in requests))
            self.assertTrue(all(r['sourceArtPolicy']['alphaRange']==[0,255] and r['sourceArtPolicy']['greenFallbackAllowed'] is False for r in requests))
            self.assertEqual(recipe['clips']['walk']['phaseStarts'],[0,.2,.33,.5,.7,.83])
    def test_exact_reviewed_inputs_are_ready(self):
        self.populate_sources();self.assertTrue(workflow.source_status('fixture')['ready'])
    def test_delayed_shot_cannot_enlarge_its_own_budget(self):
        report=self.browser_report()
        report['rapidAim'][0].update(shotWaitSeconds=99,eligibleBudgetSeconds=100)
        path=self.root/'qa/browser.json';save(path,report)
        with self.assertRaisesRegex(ValueError,'Self-declared eligibility'):
            workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_summary_booleans_cannot_replace_actual_aim_samples(self):
        for key,value in [('inputSamples',[]),('locomotionAfterInput',[0]*9),
                          ('oldProjectileSamples',[dict(index=0,before=[10,0],after=[0,10])])]:
            report=self.browser_report();report['rapidAim'][0][key]=value
            path=self.root/'qa/browser.json';save(path,report)
            with self.assertRaises(ValueError):
                workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_reversal_labels_cannot_replace_changed_targets(self):
        report=self.browser_report()
        for sample in report['rapidAim'][0]['inputSamples']:
            sample.update(target=[4,0],aim=0)
        path=self.root/'qa/browser.json';save(path,report)
        with self.assertRaisesRegex(ValueError,'requested target'):
            workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_reload_budget_must_match_sampled_actor(self):
        report=self.browser_report();reload=self.config['weapon']['reloadSeconds']
        report['rapidAim'][0].update(initialReloadSeconds=reload,eligibleBudgetSeconds=reload+1/120,shotWaitSeconds=reload)
        path=self.root/'qa/browser.json';save(path,report)
        with self.assertRaisesRegex(ValueError,'sampled actor'):
            workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_live_muzzle_includes_validated_weapon_height(self):
        report=self.browser_report();path=self.root/'qa/browser.json';save(path,report)
        workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
        for muzzle in [[0,0],[0,0,float('nan')],[0,0,self.config['weapon']['height']+1]]:
            bad=copy.deepcopy(report);bad['rapidAim'][0]['inputSamples'][0]['muzzle']=muzzle;save(path,bad)
            with self.assertRaisesRegex(ValueError,'weapon height'):
                workflow.check_browser('fixture','qa/browser.json',{'inputSHA256':'current'})
    def test_source_rejection_cannot_be_cleared_with_new_notes(self):
        self.populate_sources()
        path=dict(workflow.slots(self.config))['E/walk/0']
        evidence=path.relative_to(self.root).as_posix()
        workflow.review_source('fixture','E/walk/0','repair',evidence,'Observed incorrect support leg','technical fixture reviewer')
        with self.assertRaisesRegex(ValueError,'Rejected source bytes'):
            workflow.review_source('fixture','E/walk/0','approved',evidence,'Changed notes, not the art','technical fixture reviewer')
    def test_missing_provenance_cannot_receive_approval(self):
        self.populate_sources()
        path=dict(workflow.slots(self.config))['E/walk/0']
        # Corrupt the tiny owned fixture receipt, leaving its pixel bytes alone.
        save(path.with_suffix('.source.json'),{})
        with self.assertRaisesRegex(ValueError,'provenance/readiness'):
            workflow.review_source('fixture','E/walk/0','approved',path.relative_to(self.root).as_posix(),'Actual fixture test','technical fixture reviewer')
    def test_receipt_only_change_invalidates_source_approval(self):
        self.populate_sources()
        target=dict(workflow.slots(self.config))['E/walk/0']
        receipt=target.with_suffix('.source.json');row=workflow.read(receipt)
        row['provenanceNote']='Changed evidence context';save(receipt,row)
        state=next(r for r in workflow.source_status('fixture')['slots'] if r['slot']=='E/walk/0')
        self.assertEqual(state['state'],'source_alpha_repair')
    def test_missing_master_cannot_downgrade_to_original(self):
        self.populate_sources()
        target=dict(workflow.slots(self.config))['E/walk/0']
        receipt=target.with_suffix('.source.json');row=workflow.read(receipt)
        row.pop('sourceMaster');save(receipt,row)
        state=next(r for r in workflow.source_status('fixture')['slots'] if r['slot']=='E/walk/0')
        self.assertEqual(state['state'],'stale_provenance')
    def test_reencoded_rejected_pixels_remain_rejected(self):
        from PIL.PngImagePlugin import PngInfo
        self.populate_sources()
        target=dict(workflow.slots(self.config))['E/walk/0']
        workflow.review_source('fixture','E/walk/0','repair',str(target),'Observed a wrong support foot in synthetic fixture','unit-test')
        before=digest(target)
        image=Image.open(target).copy();info=PngInfo();info.add_text('different-metadata','same actual pixels')
        image.save(target,pnginfo=info)
        self.assertNotEqual(before,digest(target))
        with self.assertRaisesRegex(ValueError,'Rejected source bytes'):
            workflow.review_source('fixture','E/walk/0','approved',str(target),'No pixels changed; this approval must fail','unit-test')
    def test_complete_sources_do_not_bypass_whole_cycle_gate(self):
        self.populate_sources();state=workflow.workflow_status('fixture')
        self.assertTrue(state['sourcesReady']);self.assertFalse(state['ready'])
        self.assertEqual(state['next']['kind'],'cycle-review')
        self.assertEqual(state['next']['direction'],'E')
        with self.assertRaisesRegex(ValueError,'Whole-cycle'):
            build_character.compile_character(self.root/'characters/fixture.json')
    def test_alternate_recipe_cannot_bypass_active_build_gate(self):
        self.populate_sources()
        alternative=copy.deepcopy(self.config);alternative.pop('workflowVersion')
        path=self.root/'qa/alternate.json';save(path,alternative)
        with self.assertRaisesRegex(ValueError,'canonical reviewed'):
            build_character.compile_character(path)
    def test_replacing_source_invalidates_previous_review(self):
        slots=self.populate_sources();slots[0][1].write_bytes(b'changed source')
        report=workflow.source_status('fixture');self.assertFalse(report['ready']);self.assertEqual(report['slots'][0]['state'],'stale_provenance')
    def test_pilot_source_review_precedes_cycle_approval(self):
        self.populate_sources()
        path=self.root/'qa/fixture/source_reviews.json'
        save(path,[r for r in workflow.read(path) if r['slot']!='E/walk/5'])
        state=workflow.workflow_status('fixture')
        self.assertFalse(state['ready'])
        self.assertEqual(state['next']['slot'],'E/walk/5')
    def test_reference_change_invalidates_readiness(self):
        self.populate_sources();self.reference.write_bytes(b'changed identity')
        self.assertFalse(workflow.source_status('fixture')['ready'])
    def test_duplicate_source_cannot_pass_as_a_distinct_phase(self):
        slots=self.populate_sources();slots[1][1].write_bytes(slots[0][1].read_bytes())
        report=workflow.source_status('fixture');self.assertFalse(report['ready']);self.assertIn('same source',report['errors'][0])
    def test_rejected_source_is_retained_and_blocks_build(self):
        slots=self.populate_sources();slot,path=slots[0]
        workflow.review_source('fixture',slot,'repair',str(path),'Fixture rejection, not a real visual review','unit-test')
        self.assertFalse(workflow.source_status('fixture')['ready'])
        self.assertTrue((self.root/'qa/fixture/quarantine'/digest(path)/path.name).exists());self.assertTrue(path.exists())
    def test_changed_tool_response_invalidates_provenance(self):
        self.populate_sources();save(self.art/'proof_0.json',{'changed':True})
        self.assertFalse(workflow.source_status('fixture')['ready'])
    def test_path_escape_and_identity_mismatch_fail(self):
        for value in ['../other','foo/bar','C:\\outside']:
            with self.assertRaises(ValueError):workflow.ident(value)
        self.config['source']='../outside';save(self.root/'characters/fixture.json',self.config)
        with self.assertRaises(ValueError):workflow.recipe('fixture')
    def test_browser_receipt_checks_rows_not_only_pass_label(self):
        report=self.browser_report();path=self.root/'qa/browser.json';save(path,report)
        workflow.check_browser('fixture',str(path),{'inputSHA256':'current'})
        for mutate in [lambda r:r['results'].pop(),lambda r:r['results'][0].update(spriteDirection='W'),lambda r:r['results'][0].update(heldMouse=False),lambda r:r['results'][0].update(observedShots=0),lambda r:r['results'][0].update(convergedShots=0),lambda r:r['results'][0].update(maxCursorError=1),lambda r:r['results'][0].update(maxFacingErrorDegrees=150),lambda r:r['build'].update(inputSHA256='old'),lambda r:r.update(viewport=[1280,720]),lambda r:r.update(externalResources=['https://example.invalid/image.png'])]:
            broken=copy.deepcopy(report);mutate(broken);save(path,broken)
            with self.assertRaises(ValueError):workflow.check_browser('fixture',str(path),{'inputSHA256':'current'})
    def test_bundle_changes_cannot_reuse_a_previous_receipt(self):
        path=self.root/'dist/FIXTURE_Motion_Studio.html';path.parent.mkdir();path.write_text('<html>fixture</html>')
        inputs={'runtime':'abc'};report={'character':'fixture','path':path.relative_to(self.root).as_posix(),'inputs':inputs,'inputSHA256':hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest(),'sha256':digest(path),'bytes':path.stat().st_size}
        save(self.root/'dist/fixture.package.json',report)
        with patch.object(packager,'bundle_inputs',return_value=inputs):
            workflow.check_package('fixture');path.write_text('changed')
            with self.assertRaises(ValueError):workflow.check_package('fixture')
    def test_rapid_aim_gate_rejects_eventual_pass_stale_input_and_homing(self):
        report=self.browser_report();path=self.root/'qa/rapid.json'
        for mutate in [lambda r:r.pop('rapidAim'),lambda r:r['rapidAim'].pop(),lambda r:r['rapidAim'][0].update(immediateErrorDegrees=180),lambda r:r['rapidAim'][0].update(firstFrameErrorDegrees=12),lambda r:r['rapidAim'][0].update(shotWaitSeconds=.5),lambda r:r['rapidAim'][0].update(immediateMs=float('nan')),lambda r:r['rapidAim'][0].update(oldProjectileVelocityUnchanged=False),lambda r:r['rapidAim'][0].update(locomotionUnchanged=False)]:
            broken=copy.deepcopy(report);mutate(broken);save(path,broken)
            with self.assertRaises(ValueError):workflow.check_browser('fixture',str(path),{'inputSHA256':'current'})
    def test_new_recipe_never_overwrites_an_existing_art_folder(self):
        (self.root/'characters/fixture.json').unlink() # owned technical fixture only
        with self.assertRaises(FileExistsError):new_character.scaffold('fixture','Fixture',self.reference)
        self.assertTrue(self.reference.exists())
    def test_incomplete_direction_set_cannot_be_packaged(self):
        save(self.root/'public/assets/atlas/fixture/profile.json',{'id':'fixture','views':{'E':{}},'missingDirections':[]})
        with self.assertRaises(ValueError):packager.bundle_inputs('fixture')
    def test_standalone_package_rejects_the_retired_limb_mesh_runtime(self):
        valid='class AtlasRenderer{}; window.__MOTION_BUILD__={};'
        packager.require_whole_body_runtime(valid)
        for retired in ('class CharacterRenderer{}','function deformPoint(){}'):
            with self.assertRaisesRegex(ValueError,'retired'):
                packager.require_whole_body_runtime(valid+retired)
        with self.assertRaisesRegex(ValueError,'missing'):
            packager.require_whole_body_runtime('window.__MOTION_BUILD__={};')
    def fake_build(self,config,direction,action,paths,annotations,output_root=None):
        out=output_root/'public/assets/atlas/fixture';out.mkdir(parents=True,exist_ok=True)
        path=out/f'{direction}_{action}.webp';Image.new('RGBA',(80,120),(30,80,150,255)).save(path,lossless=True)
        return {'image':f'assets/atlas/fixture/{path.name}','cell':[80,120],'frames':1,'columns':1,'height':100,'root':[40,115],'muzzles':[[60,40]],'sources':[{'source':paths[0].relative_to(self.root).as_posix()}]}
    def test_single_frame_imports_produce_their_own_portrait(self):
        self.populate_sources()
        with patch.object(build_character,'build',side_effect=self.fake_build),patch.object(cycle_review,'require_build'):
            build_character.compile_character(self.root/'characters/fixture.json')
        portrait=self.root/'public/assets/atlas/fixture/portrait.png';self.assertTrue(portrait.exists())
        self.assertEqual(Image.open(portrait).getpixel((20,20)),(30,80,150,255))
    def test_failed_and_partial_builds_preserve_the_existing_character(self):
        self.populate_sources();marker=self.root/'public/assets/atlas/fixture/existing.txt';marker.parent.mkdir(parents=True);marker.write_text('keep')
        calls=0
        def fail_late(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==4:raise ValueError('injected late source failure')
            return self.fake_build(*args,**kwargs)
        with patch.object(build_character,'build',side_effect=fail_late),patch.object(cycle_review,'require_build'):
            with self.assertRaises(ValueError):build_character.compile_character(self.root/'characters/fixture.json')
        self.assertEqual(marker.read_text(),'keep')
        with patch.object(build_character,'build',side_effect=self.fake_build):
            build_character.compile_character(self.root/'characters/fixture.json',partial=True)
        self.assertEqual(marker.read_text(),'keep')

if __name__=='__main__':unittest.main()
