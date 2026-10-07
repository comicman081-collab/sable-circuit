"""Synthetic review fixtures only. They are never production art approvals."""
import copy
import json
import sys
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import character_workflow as w
import cycle_review as cycle
import gait_contract as contract
import intake_frame
import build_atlas
PALETTE=[(90,120,130),(170,90,110),(100,160,190),(170,140,70),(80,100,190),(180,80,180)]


class CycleGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import cv2
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        cls.video_fixture=Path(tempfile.mkdtemp(prefix='cycle_video_',dir=base))/'synthetic_1080p.mp4'
        cls.addClassCleanup(shutil.rmtree,cls.video_fixture.parent,True)
        encoded=[]
        for i,color in enumerate(PALETTE):
            source=cls.video_fixture.with_name(f'phase_{i}.png');Image.new('RGB',(64,96),color).save(source)
            frame,_=build_atlas.register(source,{},'E',{})
            panel=Image.new('RGB',(1920,1080),(16,30,39))
            panel.paste(Image.fromarray(frame),(30,170),Image.fromarray(frame[:,:,3]))
            encoded.append(cv2.cvtColor(np.array(panel),cv2.COLOR_RGB2BGR))
        writer=cv2.VideoWriter(str(cls.video_fixture),cv2.VideoWriter_fourcc(*'mp4v'),30,(1920,1080))
        if not writer.isOpened():raise RuntimeError('Local cycle video encoder unavailable')
        try:
            for i in range(108):
                writer.write(encoded[contract.frame_at(i/30*1.35/1.6,contract.starts({}))])
        finally:writer.release()

    def setUp(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='cycle_',dir=base));self.addCleanup(shutil.rmtree,self.root,True)
        for module in (w,intake_frame,build_atlas):
            p=patch.object(module,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        reference=self.root/'art/fixture/identity.png';reference.parent.mkdir(parents=True);reference.write_bytes(b'identity fixture')
        c={'id':'fixture','name':'Fixture','source':'art/fixture','workflowVersion':1,
           'identityReference':'art/fixture/identity.png','referenceSHA256':w.sha(reference),
           'heightMetres':1.72,'clips':{'walk':{'frames':6},'idle':{'frames':1}},'locomotion':{'walkSpeed':1.35,'walkStride':1.6}}
        w.write(self.root/'characters/fixture.json',c)
        reviews=[]
        for i,(slot,path) in enumerate(w.slots(c)):
            info=PngInfo();info.add_text('technical_slot',slot)
            Image.new('RGB',(64,96),PALETTE[int(slot.split('/')[-1])]).save(path,pnginfo=info)
            master=path.with_name(f'original_fixture_{i}.png');master.write_bytes(path.read_bytes())
            returned=str(self.root/f'fake_returned_{i}.png')
            proof=self.root/f'qa/tool-fixture-{i}.json';w.write(proof,{'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Synthetic test; not a real invocation: '+returned},'projectCopy':str(master.relative_to(self.root)),'projectCopySHA256':w.sha(master)})
            receipt=path.with_suffix('.source.json')
            w.write(receipt,{'generator':'Codex built-in ImageGen','sha256':w.sha(path),'destination':str(path.relative_to(self.root)),'toolResponse':w.binding(proof),'sourceMaster':w.binding(master)})
            reviews.append({'slot':slot,'decision':'approved','sourceSHA256':w.sha(path),'sourceReceiptSHA256':w.sha(receipt),'referenceSHA256':c['referenceSHA256'],'evidence':w.binding(path)})
        w.write(self.root/'qa/fixture/source_reviews.json',reviews)
        self.expected=cycle.inputs('fixture','E')
        self.out=self.root/'qa/cycle';self.out.mkdir(parents=True)
        self.clip={'cell':[768,768],'height':656,'columns':3,'frames':6,'root':[384,716],'phaseStarts':contract.starts(c['clips']['walk']),'muzzles':[],'sources':[]}
        atlas=Image.new('RGBA',(2304,1536))
        for i,row in enumerate(self.expected['sources']):
            pixels,note=build_atlas.register(w.local(row['path']),c,'E',{})
            atlas.paste(Image.fromarray(pixels),(i%3*768,i//3*768))
            self.clip['muzzles'].append(note['muzzle']);self.clip['sources'].append(note)
        atlas_path=self.out/'atlas.png';atlas.save(atlas_path)
        contact=self.out/'contact.png';Image.new('RGB',(2304,1536)).save(contact)
        movie=self.out/'video.mp4';shutil.copy2(self.video_fixture,movie)
        self.preview=self.out/'preview.json'
        w.write(self.preview,{'cycleInputs':self.expected,'clip':self.clip,'atlas':w.binding(atlas_path),
                'contact':w.binding(contact),'video':w.binding(movie),'nativeVideo':[1920,1080],
                'cycles':3,'durationSeconds':3.6})
        soles=[([500,716],[220,690]),([390,716],[290,640]),([290,716],[450,650]),
               ([220,690],[500,716]),([290,640],[390,716]),([450,650],[290,716])]
        frames=[]
        for p,(left,right) in zip(contract.PHASES,soles):
            pts={}
            for side,sole,hx in [('left',left,375),('right',right,405)]:
                pts[side+'Hip']=[hx,360];pts[side+'Knee']=[(hx+sole[0])/2,(360+sole[1])/2];pts[side+'Sole']=sole
            frames.append({'index':p['index'],'phase':p['name'],'support':p['support'],'landmarks':pts})
        self.packet={'kind':'sable-cycle-observation','character':'fixture','direction':'E','action':'walk',
                     'inputs':self.expected,'preview':w.binding(self.preview),'decision':'approved','reviewer':'UNIT FIXTURE NOT ART REVIEW',
                     'legMarkers':{'left':'left technical marker','right':'right technical marker'},'frames':frames,
                     'observations':{name:{'decision':'pass','seconds':[.1,1.1], 'notes':'Synthetic geometry unit test only'} for name in cycle.OBSERVATIONS}}
        self.packet_path=self.out/'observations.json';w.write(self.packet_path,self.packet)

    def test_explicit_complete_technical_packet_is_accepted(self):
        self.assertTrue(cycle.validate_packet(self.packet,self.expected))

    def test_same_leading_leg_at_opposite_contact_is_rejected(self):
        p=copy.deepcopy(self.packet);p['frames'][3]['landmarks']=copy.deepcopy(p['frames'][0]['landmarks'])
        with self.assertRaisesRegex(ValueError,'Opposite contacts'):cycle.validate_packet(p,self.expected)

    def test_repeated_swing_and_passing_chain_is_rejected(self):
        for a,b in ((1,4),(2,5)):
            p=copy.deepcopy(self.packet)
            p['frames'][b]['landmarks']=copy.deepcopy(p['frames'][a]['landmarks'])
            with self.assertRaisesRegex(ValueError,'swing/passing'):
                cycle.validate_packet(p,self.expected)

    def test_rebound_video_hash_does_not_prove_the_correct_atlas_pixels(self):
        path=self.out/'atlas.png'
        Image.new('RGBA',(2304,1536),(220,30,80,255)).save(path)
        preview=w.read(self.preview);preview['atlas']=w.binding(path);w.write(self.preview,preview)
        self.packet['preview']=w.binding(self.preview)
        with self.assertRaisesRegex(ValueError,'video.*pixels'):
            cycle.validate_packet(self.packet,self.expected)

    def test_declared_video_dimensions_cannot_hide_undecodable_bytes(self):
        movie=self.out/'video.mp4';movie.write_bytes(b'not an actual video')
        preview=w.read(self.preview);preview['video']=w.binding(movie);w.write(self.preview,preview)
        self.packet['preview']=w.binding(self.preview)
        with self.assertRaisesRegex(ValueError,'actually decode'):cycle.validate_packet(self.packet,self.expected)

    def test_blank_approvals_wrong_phase_and_missing_video_binding_fail(self):
        for mutate in [lambda p:p.update(decision='unreviewed'),lambda p:p['frames'][1].update(phase='right_passing'),
                       lambda p:p['frames'][3].update(support='left'),lambda p:p['frames'][0]['landmarks'].update(leftSole=None),
                       lambda p:p['observations']['footSliding'].update(seconds=[]),lambda p:p['observations']['loopSeam'].update(notes=''),
                       lambda p:p.update(preview={'path':'missing.json','sha256':'0'*64})]:
            p=copy.deepcopy(self.packet);mutate(p)
            with self.assertRaises(ValueError):cycle.validate_packet(p,self.expected)

    def test_background_landmarks_are_rejected(self):
        atlas=np.zeros((1536,2304,4),dtype=np.uint8)
        with self.assertRaisesRegex(ValueError,'visible subject'):cycle.validate_landmarks(self.packet,self.clip,atlas)

    def test_changed_source_recipe_and_review_packet_invalidate_gate(self):
        cycle.record('fixture','E','walk','approved',str(self.packet_path))
        self.assertEqual(cycle.current('fixture','E')['state'],'approved')
        p=copy.deepcopy(self.packet);p['observations']['footSliding']['notes']='edited after approval'
        w.write(self.packet_path,p)
        self.assertNotEqual(cycle.current('fixture','E')['state'],'approved')
        w.write(self.packet_path,self.packet)
        Image.new('RGB',(64,96),(30,50,90)).save(self.root/'art/fixture/E_walk_3_master.png')
        self.assertNotEqual(cycle.current('fixture','E')['state'],'approved')

    def test_rejected_pixels_cannot_be_reapproved_by_notes(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Actual fixture rejection',reviewer='unit fixture',rejection_scope='source-art',failed_slots=['E/walk/3'])
        with self.assertRaisesRegex(ValueError,'source bytes are unchanged'):
            cycle.record('fixture','E','walk','approved',str(self.packet_path))
        self.assertEqual(w.read(self.root/'dist/fixture.delivery.json')['status'],'HOLD_VISUAL_REPAIR')

    def test_renaming_rejected_sources_does_not_clear_rejection(self):
        cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic rejection fixture',reviewer='unit fixture',rejection_scope='source-art',failed_slots=['E/walk/3'])
        for i in range(6):
            path=self.root/f'art/fixture/E_walk_{i}_master.png'
            shutil.copy2(path,path.with_name(f'E_walk_{i}_override.png'))
        self.assertEqual(cycle.current('fixture','E')['state'],'repair')

    def test_other_slot_or_metadata_cannot_resolve_failed_slot(self):
        row=cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic E4 failed',reviewer='unit fixture',rejection_scope='source-art',failed_slots=['E/walk/4'])
        Image.new('RGB',(64,96),(70,80,90)).save(self.root/'art/fixture/E_walk_0_master.png')
        self.assertTrue(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))
        path=self.root/'art/fixture/E_walk_4_master.png'
        info=PngInfo();info.add_text('new_note','same rejected pixels')
        Image.new('RGB',(64,96),PALETTE[4]).save(path,pnginfo=info)
        self.assertTrue(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))

    def test_preview_repair_does_not_force_source_replacement(self):
        path=self.out/'preview-settings.json';w.write(path,{'testFixture':'old'})
        row=cycle.record('fixture','E','walk','repair',evidence=str(self.out/'contact.png'),notes='Synthetic preview fault',reviewer='unit fixture',rejection_scope='preview',required_change=[str(path)])
        before=cycle.source_content(cycle.inputs('fixture','E'))
        self.assertTrue(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))
        w.write(path,{'testFixture':'fixed'})
        self.assertFalse(cycle.rejection_unresolved(row,cycle.inputs('fixture','E')))
        self.assertEqual(before,cycle.source_content(cycle.inputs('fixture','E')))

    def test_rebound_source_metadata_cannot_use_old_atlas(self):
        path=self.root/'art/fixture/E_walk_0_master.png'
        Image.new('RGB',(64,96),(200,80,90)).save(path)
        expected=cycle.inputs('fixture','E')
        with self.assertRaisesRegex(ValueError,'atlas pixels'):
            cycle.validate_source_atlas(json.dumps(expected,sort_keys=True),json.dumps(self.clip,sort_keys=True),str(self.out/'atlas.png'),w.sha(self.out/'atlas.png'))

    def test_preview_timing_cannot_override_recipe(self):
        config=w.recipe('fixture');config['clips']['walk']['phaseStarts']=[0,.2,.33,.5,.7,.83]
        w.write(self.root/'characters/fixture.json',config)
        with self.assertRaisesRegex(ValueError,'phase schedule'):
            cycle.validate_source_atlas(json.dumps(cycle.inputs('fixture','E'),sort_keys=True),json.dumps(self.clip,sort_keys=True),str(self.out/'atlas.png'),w.sha(self.out/'atlas.png'))

    def test_frozen_panel_with_small_distinct_cells_is_rejected(self):
        import cv2
        atlas=Image.new('RGBA',(2304,1536));frames=[]
        for i in range(6):
            cell=np.full((768,768,4),(70,90,100,255),dtype=np.uint8)
            cell[300:332,100+i*70:132+i*70,:3]=255
            frames.append(cell);atlas.paste(Image.fromarray(cell),(i%3*768,i//3*768))
        path=self.out/'small_changes.png';atlas.save(path)
        movie=self.out/'frozen.mkv'
        writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'FFV1'),30,(1920,1080))
        self.assertTrue(writer.isOpened())
        page=np.full((1080,1920,3),(16,30,39),np.uint8);page[170:938,30:798]=frames[0][:,:,:3]
        encoded=cv2.cvtColor(page,cv2.COLOR_RGB2BGR)
        try:
            for _ in range(108):writer.write(encoded)
        finally:writer.release()
        with self.assertRaisesRegex(ValueError,'distinguish|phase-region'):
            cycle.validate_video_pixels(str(movie),w.sha(movie),str(path),w.sha(path),json.dumps(self.clip,sort_keys=True),1.35,1.6)

    def test_superposed_phase_ghosts_cannot_pass_as_authored_frames(self):
        import cv2
        atlas=Image.new('RGBA',(2304,1536));frames=[]
        for i in range(6):
            cell=np.full((768,768,4),(70,90,100,255),dtype=np.uint8)
            cell[300:332,100+i*70:132+i*70,:3]=255
            frames.append(cell[:,:,:3]);atlas.paste(Image.fromarray(cell),(i%3*768,i//3*768))
        path=self.out/'phase_ghost_atlas.png';atlas.save(path)
        base=np.rint(np.mean(frames,axis=0)).astype(np.uint8)
        for ghost in (False,True):
            movie=self.out/('ghosts.mkv' if ghost else 'correct_small_motion.mkv')
            writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'FFV1'),30,(1920,1080))
            self.assertTrue(writer.isOpened())
            try:
                for tick in range(108):
                    index=contract.frame_at(tick/30*1.35/1.6,contract.starts(self.clip))
                    cell=base.copy() if ghost else frames[index]
                    if ghost:cell[300:332,100+index*70:132+index*70]+=4
                    page=np.full((1080,1920,3),(16,30,39),np.uint8);page[170:938,30:798]=cell
                    writer.write(cv2.cvtColor(page,cv2.COLOR_RGB2BGR))
            finally:writer.release()
            args=(str(movie),w.sha(movie),str(path),w.sha(path),json.dumps(self.clip,sort_keys=True),1.35,1.6)
            if ghost:
                with self.assertRaisesRegex(ValueError,'phase-region'):cycle.validate_video_pixels(*args)
            else:self.assertEqual(cycle.validate_video_pixels(*args),108)

    def test_missing_pilot_blocks_non_e_intake_before_any_source_copy(self):
        source=self.root/'qa/not-read.png';source.write_bytes(b'invalid image proves guard runs first')
        before=(self.root/'art/fixture/SE_walk_0_master.png').read_bytes()
        with self.assertRaisesRegex(ValueError,'E full-cycle review'):
            intake_frame.intake('fixture','SE','walk',0,source)
        self.assertEqual((self.root/'art/fixture/SE_walk_0_master.png').read_bytes(),before)

    def test_interlaced_ghost_is_rejected_on_both_sides_of_old_sampling_limit(self):
        import cv2
        for height in [64,65]:
            atlas=Image.new('RGBA',(2304,1536));frames=[]
            for i in range(6):
                cell=np.full((768,768,4),(70,90,100,255),dtype=np.uint8)
                cell[300:300+height,100+i*70:132+i*70,:3]=255
                frames.append(cell[:,:,:3]);atlas.paste(Image.fromarray(cell),(i%3*768,i//3*768))
            path=self.out/f'interlaced_{height}.png';atlas.save(path)
            base=np.rint(np.mean(frames,axis=0)).astype(np.uint8)
            for ghost in ([True] if height==64 else [False,True]):
                movie=self.out/f'interlaced_{height}_{ghost}.mkv'
                writer=cv2.VideoWriter(str(movie),cv2.VideoWriter_fourcc(*'FFV1'),30,(1920,1080))
                self.assertTrue(writer.isOpened())
                try:
                    for tick in range(108):
                        index=contract.frame_at(tick/30*1.35/1.6,contract.starts(self.clip))
                        cell=base.copy() if ghost else frames[index]
                        if ghost:
                            cell[300:300+height,100+index*70:132+index*70]+=4
                            cell[:,::2]=frames[index][:,::2]
                        page=np.full((1080,1920,3),(16,30,39),np.uint8);page[170:938,30:798]=cell
                        writer.write(cv2.cvtColor(page,cv2.COLOR_RGB2BGR))
                finally:writer.release()
                args=(str(movie),w.sha(movie),str(path),w.sha(path),json.dumps(self.clip,sort_keys=True),1.35,1.6)
                if ghost:
                    with self.assertRaisesRegex(ValueError,'phase-region'):cycle.validate_video_pixels(*args)
                else:self.assertEqual(cycle.validate_video_pixels(*args),108)


if __name__=='__main__':unittest.main()
