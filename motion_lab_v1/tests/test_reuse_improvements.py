"""Local technical fixtures only. No game art, providers, or model runs."""
import copy
import contextlib
import io
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import compact_atlas as atlas
import improvement_harness as harness
import character_handoff as handoff
import character_workflow as workflow

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')

def fixture_root(test, prefix):
    parent = LAB / 'qa/technical_tests'
    parent.mkdir(parents=True, exist_ok=True)
    # Only the fresh folder created here is removed after the test.
    root = Path(tempfile.mkdtemp(prefix=prefix, dir=parent))
    test.addCleanup(shutil.rmtree, root, True)
    return root

class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.root = fixture_root(self, 'lossless_')
        self.desc_path = self.root / 'descriptor.json'
        self.output = self.root / 'motion_lab_v1/qa/candidate'
        desc = {'cell_size': 4, 'display_scale': .5, 'display_offset': [0, -4],
                'states': {'idle': {'frames': 1, 'fps': 1}, 'move': {'frames': 4, 'fps': 24},
                           'fire': {'frames': 2, 'fps': 12}}, 'directions': {}}
        for direction in atlas.DIRECTIONS:
            row = {'muzzle_xy': [3, 1]}
            for state, spec in desc['states'].items():
                path = self.root / direction / (state + '.png')
                path.parent.mkdir(parents=True, exist_ok=True)
                image = Image.new('RGBA', (4, 4 * spec['frames']))
                for index in range(spec['frames']):
                    # Two visually transparent but byte-distinct cells catch
                    # accidental hidden-RGB normalization and false deduplication.
                    cell = Image.new('RGBA', (4, 4), (20 + 20 * (index % 2), 80, 120, 0))
                    image.paste(cell, (0, index * 4))
                image.save(path)
                row[state + '_atlas'] = path.relative_to(self.root).as_posix()
            desc['directions'][direction] = row
        save(self.desc_path, desc)

    def build(self):
        result = atlas.pack(self.root, self.desc_path, self.output)
        return Path(result['manifest'])

    def test_preserves_all_slots_and_hidden_rgba(self):
        path = self.build()
        result = atlas.verify(self.root, path)
        self.assertEqual(result['rgba_exact_timing_cells'], 56)
        self.assertTrue(result['timing_unchanged'])
        self.assertFalse(result['production_approved'])
        manifest = atlas.read(path)
        self.assertEqual(manifest['directions']['E']['unique_cells'], 2)
        frames = manifest['directions']['E']['states']['move']
        self.assertEqual(len(frames), 4)
        self.assertAlmostEqual(sum(f['duration_seconds'] for f in frames), 4 / 24)
        self.assertEqual(frames[0]['x'], frames[2]['x'])

    def test_changed_duration_or_order_or_offset_fails(self):
        path = self.build()
        original = atlas.read(path)
        for mutate in (
            lambda m: m['directions']['E']['states']['move'][0].update(duration_seconds=.5),
            lambda m: m['directions']['E']['states']['move'][0].update(duration_seconds=math.nan),
            lambda m: m['directions']['E']['states']['move'][0].update(source_frame=1),
            lambda m: m['directions']['E']['states']['move'][0].update(x=999),
            lambda m: m['directions']['E']['states']['move'].pop(),
            lambda m: m.update(display_offset=[0, 0]),
        ):
            broken = copy.deepcopy(original)
            mutate(broken)
            save(path, broken)
            with self.assertRaises(ValueError):
                atlas.verify(self.root, path)

    def test_resealed_pixel_corruption_still_fails_against_original(self):
        path = self.build()
        manifest = atlas.read(path)
        page = self.root / manifest['directions']['E']['texture']
        image = atlas.rgba(page)
        image.putpixel((0, 0), (1, 2, 3, 0))
        image.save(page)
        manifest['directions']['E']['sha256'] = atlas.sha(page)
        save(path, manifest)
        with self.assertRaisesRegex(ValueError, 'RGBA differs'):
            atlas.verify(self.root, path)

    def test_source_change_is_not_accepted_from_old_checks(self):
        path = self.build()
        source = self.root / 'E/move.png'
        Image.new('RGBA', (4, 16), (200, 0, 0, 255)).save(source)
        with self.assertRaisesRegex(ValueError, 'Original texture changed'):
            atlas.verify(self.root, path)

    def test_rgb_without_real_alpha_is_not_silently_converted(self):
        source = self.root / 'E/idle.png'
        Image.new('RGB', (4, 4), (0, 255, 0)).save(source)
        with self.assertRaisesRegex(ValueError, 'actual RGBA'):
            self.build()

    def test_no_overwrite_or_output_escape(self):
        path = self.build()
        before = atlas.sha(path)
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(atlas.sha(path), before)
        with self.assertRaises(ValueError):
            atlas.pack(self.root, self.desc_path, self.root / 'production')
        self.assertFalse((self.root / 'production').exists())

class PerformanceTests(unittest.TestCase):
    def rows(self):
        row = {'p95_ms': 6.424, 'p99_ms': 19.714, 'squad_count': 3, 'end_hostiles': 3}
        return [dict(row) for _ in range(3)]

    def test_r3_relative_failure_cannot_be_rounded_to_pass(self):
        baseline, candidate = self.rows(), self.rows()
        for row in candidate:
            row['p95_ms'] = 7.106
        result = harness.evaluate_performance(baseline, candidate)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(result['absolute_budget_met'])
        self.assertFalse(result['relative_budget_met'])

    def test_valid_within_budget_data_can_pass(self):
        self.assertEqual(harness.evaluate_performance(self.rows(), self.rows())['status'], 'PASS')

    def test_missing_repeat_invalid_number_and_population_fail(self):
        for mutate in (lambda r: r.pop(), lambda r: r[0].update(p95_ms=float('nan')),
                       lambda r: r[0].update(p99_ms=float('inf')), lambda r: r[0].update(p95_ms=True),
                       lambda r: r[0].update(end_hostiles=2), lambda r: r[0].update(p99_ms=1)):
            candidate = self.rows()
            mutate(candidate)
            with self.assertRaises(ValueError):
                harness.evaluate_performance(self.rows(), candidate)

    def test_empty_and_stale_input_binding_fails(self):
        root = fixture_root(self, 'binding_')
        path = root / 'file.txt'
        path.write_text('fixture', encoding='utf-8')
        values = {'file.txt': atlas.sha(path)}
        harness.check_bindings(root, values)
        path.write_text('changed', encoding='utf-8')
        for value in ({}, values, {'../outside': 'invalid'}):
            with self.assertRaises(ValueError):
                harness.check_bindings(root, value)

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.project = fixture_root(self, 'handoff_')
        self.lab = self.project / 'motion_lab_v1'
        self.lab.mkdir()
        self.patch = patch.object(workflow, 'ROOT', self.lab)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        for name in handoff.CORE + ('AGENTS.md',):
            path = self.lab / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('technical file fixture only', encoding='utf-8')
        for name in handoff.REFERENCES:
            path = self.project / '.agents/skills/sable-character-studio' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('technical instruction fixture only', encoding='utf-8')
        reference = self.lab / 'art/fixture/identity_reference.png'
        reference.parent.mkdir(parents=True)
        reference.write_bytes(b'not image generation: identity hash fixture')
        self.config = {'id': 'fixture', 'name': 'Technical fixture', 'source': 'art/fixture',
                       'heightMetres': 1.72, 'locomotion': {'walkSpeed': 1.35, 'walkStride': 1.6},
                       'workflowVersion': 1, 'identityReference': 'art/fixture/identity_reference.png',
                       'referenceSHA256': atlas.sha(reference), 'clips': {'walk': {'frames': 6}, 'idle': {'frames': 1}}}
        save(self.lab / 'characters/fixture.json', self.config)
        self.packet_path = self.lab / 'qa/handoff.json'

    def packet(self):
        packet = handoff.make('fixture')
        save(self.packet_path, packet)
        return packet

    def test_packet_has_real_next_slot_not_generation_success(self):
        packet = self.packet()
        self.assertEqual(packet['status'], 'READY_TO_RESUME')
        self.assertEqual(packet['nextSource']['slot'], 'E/idle/0')
        self.assertFalse(packet['lunaGenerationTested'])
        self.assertFalse(packet['reviewedDelivery'])
        self.assertEqual(handoff.verify(str(self.packet_path))['status'], 'CURRENT_HANDOFF')

    def test_code_change_invalidates_packet(self):
        self.packet()
        (self.lab / 'public/atlas-renderer.js').write_text('changed fixture', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_new_missing_source_invalidates_packet(self):
        self.packet()
        (self.lab / 'art/fixture/E_walk_0_master.png').write_bytes(b'new test bytes')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_aim_latency_instruction_change_invalidates_packet(self):
        self.packet()
        path=self.project / '.agents/skills/sable-character-studio/references/aim-response.md'
        path.write_text('Changed aim latency constraint fixture',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_runtime_texture_change_invalidates_packet(self):
        texture = self.lab / 'public/assets/atlas/fixture/E_walk.webp'
        texture.parent.mkdir(parents=True)
        texture.write_bytes(b'non-art texture fixture')
        save(texture.parent / 'profile.json', {'id': 'fixture', 'animation': {'presentation': 'authored_frames'},
             'views': {'E': {'walk': {'image': 'assets/atlas/fixture/E_walk.webp', 'sources': []}}}})
        self.packet()
        texture.write_bytes(b'changed texture fixture')
        with self.assertRaisesRegex(ValueError, 'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_changed_claim_or_instruction_is_rejected(self):
        original = self.packet()
        for update in ({'reviewedDelivery': True}, {'lunaGenerationTested': True}, {'nextAction': 'DEPLOY_NOW'},
                       {'sourceArtPolicy': {'greenFallbackAllowed': True}}):
            packet = copy.deepcopy(original)
            packet.update(update)
            save(self.packet_path, packet)
            with self.assertRaisesRegex(ValueError, 'instructions or conclusions'):
                handoff.verify(str(self.packet_path))

    def test_known_repair_precedes_missing_pilot_slot(self):
        source = self.lab / 'art/fixture/E_walk_0_master.png'
        Image.new('RGBA',(16,24),(90,110,130,255)).save(source)
        master=source.with_name('technical_original.png');master.write_bytes(source.read_bytes())
        proof = self.lab / 'qa/proof.json'
        returned=str(self.lab/'technical_returned.png')
        save(proof, {'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Synthetic test, not a real invocation: '+returned},'projectCopy':str(master.relative_to(self.lab)),'projectCopySHA256':atlas.sha(master)})
        save(source.with_suffix('.source.json'), {'testFixture': True, 'generator': 'Codex built-in ImageGen',
             'sha256': atlas.sha(source), 'toolResponse': workflow.binding(proof),'sourceMaster':workflow.binding(master),'destination':str(source.relative_to(self.lab))})
        workflow.review_source('fixture', 'E/walk/0', 'repair', str(source),
                               'Technical negative fixture, not actual art review', 'unit-test')
        packet = self.packet()
        self.assertEqual(packet['nextAction'], 'REPAIR_REPORTED_SOURCE')
        self.assertEqual(packet['nextSource']['slot'], 'E/walk/0')

    def test_runtime_rejection_is_the_next_action_not_a_rebuild(self):
        save(self.lab/'qa/fixture/runtime_reviews.json',[{'decision':'repair','notes':'Synthetic rejected gait fixture'}])
        packet=self.packet()
        self.assertEqual(packet['nextAction'],'REPAIR_RUNTIME_VISUAL')
        self.assertTrue(packet['sourceStatus']['runtimeRepairRequired'])
        self.assertFalse(packet['sourceStatus']['ready'])

    def pending_cycle_fixture(self, state='repair'):
        rows=[{'slot':f'SE/walk/{i}','path':f'art/fixture/SE_walk_{i}_master.png',
               'state':'approved','sha256':f'old-{i}'} for i in range(6)]
        missing={'slot':'S/walk/0','path':'art/fixture/S_walk_0_master.png','state':'missing'}
        source={'character':'fixture','mode':'source-authoring','ready':False,'next':missing,
                'requiredFrames':56,'approvedFrames':6,'errors':[],'slots':rows+[missing]}
        cycle={'direction':'SE','action':'walk','state':state}
        cycles={'required':True,'ready':False,'cycles':[{'direction':'E','action':'walk','state':'approved'},cycle]}
        rejection={'direction':'SE','action':'walk','decision':'repair','rejectionScope':'source-art',
                   'failedSlots':['SE/walk/3','SE/walk/4'],'inputs':{'sources':rows[:6]},'notes':'Synthetic cycle-only rejection'}
        return source,cycles,rejection

    def test_non_e_cycle_repair_precedes_unrelated_missing_direction(self):
        source,cycles,rejection=self.pending_cycle_fixture()
        with patch.object(workflow,'source_status',return_value=source), \
             patch('cycle_review.status',return_value=cycles),patch('cycle_review.ledger',return_value=[rejection]):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REPAIR_REPORTED_CYCLE_SOURCE')
            self.assertEqual(packet['nextSource']['slot'],'SE/walk/3')
            self.assertIn('--direction SE',packet['commands']['prepareCycleReview'])
            self.assertFalse(packet['reviewedDelivery'])

    def test_complete_non_e_cycle_review_precedes_new_direction(self):
        source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
        with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
            self.assertEqual(packet['nextSource']['direction'],'SE')

    def test_unreviewed_pilot_precedes_complete_non_e_cycle(self):
        source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
        pilot={'slot':'E/walk/5','path':'art/fixture/E_walk_5_master.png','state':'needs_review'}
        source['slots'].append(pilot);source['next']=pilot
        with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
            packet=self.packet()
            self.assertEqual(packet['nextSource']['slot'],'E/walk/5')
            self.assertNotEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')

    def test_e_cycle_recheck_precedes_non_e_cycle_repair(self):
        for state in ['needs_cycle_review','stale_cycle_review']:
            with self.subTest(state=state):
                source,cycles,rejection=self.pending_cycle_fixture()
                source['slots'] += [{'slot':slot,'path':'art/fixture/'+slot.replace('/','_')+'_master.png',
                                     'state':'approved'} for slot in workflow.PILOT]
                cycles['cycles'][0]['state']=state
                with patch.object(workflow,'source_status',return_value=source), \
                     patch('cycle_review.status',return_value=cycles),patch('cycle_review.ledger',return_value=[rejection]):
                    packet=self.packet()
                    self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
                    self.assertEqual(packet['nextSource']['direction'],'E')
                    self.assertEqual(packet['nextSource']['action'],'walk')

    def test_cycle_action_reaches_actual_prepare_cli(self):
        import shlex
        self.config['clips']['run']={'frames':6}
        save(self.lab/'characters/fixture.json',self.config)
        for action in ['walk','run']:
            with self.subTest(action=action):
                source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
                for row in source['slots'][:6]:row['slot']=row['slot'].replace('/walk/','/'+action+'/')
                cycles['cycles'][1]['action']=action
                with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
                    packet=self.packet()
                    self.assertEqual(packet['nextSource']['action'],action)
                    # Execute the real argument parser/branch. Only artifact generation is stubbed.
                    with patch.object(sys,'argv',shlex.split(packet['commands']['prepareCycleReview'])), \
                         patch('cycle_preview.prepare',return_value={'technicalFixture':True}) as prepare, \
                         contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(workflow.main(),0)
                        prepare.assert_called_once_with('fixture','SE',action)
                    self.assertEqual(packet['commands']['prepareCycleReview'],packet['nextSource']['command'])

    def test_e_repair_scope_keeps_its_own_next_action(self):
        for scope in ['source-art','timing']:
            with self.subTest(scope=scope):
                source,cycles,se_rejection=self.pending_cycle_fixture()
                pilot_rows=[{'slot':slot,'path':'art/fixture/'+slot.replace('/','_')+'_master.png',
                             'state':'approved','sha256':'old-'+slot} for slot in workflow.PILOT]
                source['slots']+=pilot_rows;cycles['cycles'][0]['state']='repair'
                e_rejection={'direction':'E','action':'walk','decision':'repair','rejectionScope':scope,
                             'failedSlots':['E/walk/3'],'inputs':{'sources':pilot_rows},'notes':'Synthetic E rejection'}
                with patch.object(workflow,'source_status',return_value=source), \
                     patch('cycle_review.status',return_value=cycles), \
                     patch('cycle_review.ledger',return_value=[e_rejection,se_rejection]):
                    packet=self.packet()
                    self.assertEqual(packet['nextSource']['direction'],'E')
                    if scope=='source-art':
                        self.assertEqual(packet['nextAction'],'REPAIR_REPORTED_CYCLE_SOURCE')
                        self.assertEqual(packet['nextSource']['slot'],'E/walk/3')
                    else:
                        self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
                        self.assertNotIn('slot',packet['nextSource'])

    def test_source_slot_action_and_idle_walk_mapping_reach_cli(self):
        import shlex
        self.config['clips']['run']={'frames':6};save(self.lab/'characters/fixture.json',self.config)
        for action in ['walk','run','idle']:
            with self.subTest(action=action):
                source,cycles,_=self.pending_cycle_fixture('approved')
                row={'slot':f'SE/{action}/0','path':f'art/fixture/SE_{action}_0_master.png','state':'needs_review'}
                source['next']=row;source['slots']=[row]
                with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
                    packet=self.packet();expected='walk' if action=='idle' else action
                    self.assertTrue(packet['commands']['previewAffectedCycle'].endswith('--action '+expected))
                    with patch.object(sys,'argv',shlex.split(packet['commands']['prepareCycleReview'])), \
                         patch('cycle_preview.prepare',return_value={'technicalFixture':True}) as prepare, \
                         contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(workflow.main(),0)
                        prepare.assert_called_once_with('fixture','SE',expected)

    def test_non_art_cycle_rejection_does_not_request_new_source(self):
        source,cycles,rejection=self.pending_cycle_fixture()
        rejection['rejectionScope']='timing'
        with patch.object(workflow,'source_status',return_value=source), \
             patch('cycle_review.status',return_value=cycles),patch('cycle_review.ledger',return_value=[rejection]):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REVIEW_WHOLE_CYCLE')
            self.assertNotIn('slot',packet['nextSource'])
            self.assertEqual(packet['nextSource']['rejectionScope'],'timing')

    def test_direct_source_repair_still_precedes_cycle_review(self):
        source,cycles,_=self.pending_cycle_fixture('needs_cycle_review')
        source['slots'][-1]['state']='repair'
        with patch.object(workflow,'source_status',return_value=source),patch('cycle_review.status',return_value=cycles):
            packet=self.packet()
            self.assertEqual(packet['nextAction'],'REPAIR_REPORTED_SOURCE')
            self.assertEqual(packet['nextSource']['slot'],'S/walk/0')

    def test_pose_guide_and_request_change_invalidate_handoff(self):
        guide=self.lab/'reference/guide.png';guide.parent.mkdir(parents=True);guide.write_bytes(b'technical pose guide fixture')
        save(self.lab/'art/fixture/requests.json',[{'poseGuide':'reference/guide.png'}])
        self.packet();guide.write_bytes(b'changed guide fixture')
        with self.assertRaisesRegex(ValueError,'Stale handoff'):
            handoff.verify(str(self.packet_path))

    def test_handoff_rejects_foreign_generation_reference(self):
        foreign=self.project.parent/'foreign-character.png'
        foreign.write_bytes(b'other project image fixture')
        self.addCleanup(lambda: foreign.unlink(missing_ok=True))
        save(self.lab/'art/fixture/requests.json',[{'reference':str(foreign)}])
        with self.assertRaisesRegex(ValueError,'PROJECT_REFERENCE_REQUIRED'):
            handoff.make('fixture')

    def test_handoff_rejects_other_sable_identity_reference(self):
        other=self.lab/'art/fixture/other-character.png'
        other.write_bytes(b'another sable character fixture')
        self.addCleanup(lambda: other.unlink(missing_ok=True))
        save(self.lab/'art/fixture/requests.json',[{'reference':str(other)}])
        with self.assertRaisesRegex(ValueError,'differs from recipe identity'):
            handoff.make('fixture')

if __name__ == '__main__':
    unittest.main()
