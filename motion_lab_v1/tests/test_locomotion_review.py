import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from locomotion_review import validate_report,DIRECTIONS

class TemporalReviewTests(unittest.TestCase):
    def fixture(self):
        rows=[]
        for action in ['walk','run','walk_fire','run_fire','stationary_fire']:
            for d in DIRECTIONS:
                stationary=action=='stationary_fire';firing='fire' in action
                samples=[{'frame':0 if stationary else i%6,'frameCount':1 if stationary else 6,'hash':f'{0 if stationary else i%6:064x}','direction':d,
                    'time':i*.2,'phase':0 if stationary else (i%6+.5)/6,'position':[0 if stationary else i*.2,0],'shots':i//3 if firing else 0} for i in range(13)]
                rows.append({'name':action+'_'+d,'direction':d,'stationary':stationary,'firing':firing,'shots':4 if firing else 0,'travel':0 if stationary else 2.4,'pass':True,'frameCount':samples[0]['frameCount'],'frames':sorted({s['frame'] for s in samples}),'lowerPixelHashes':sorted({s['hash'] for s in samples}),'samples':samples})
        return {'kind':'motion-studio-locomotion-browser','character':'fixture','build':{'inputSHA256':'current'},'testScriptSHA256':'script','viewport':[1920,1080],'results':rows,'pass':True}
    def check(self,r):return validate_report(r,'fixture','current','script')
    def test_complete_technical_fixture(self):self.assertTrue(self.check(self.fixture()))
    def test_previous_failures_cannot_pass_via_a_true_label(self):
        for mutate in [lambda r:r['results'].pop(),lambda r:r['build'].update(inputSHA256='old'),lambda r:r.update(viewport=[1280,720]),lambda r:r['results'][0].update(frames=[5]),lambda r:r['results'][0].update(travel=0),lambda r:r['results'][0].update(samples=[]),lambda r:r['results'][-1].update(travel=.1)]:
            r=self.fixture();mutate(r)
            with self.assertRaises(ValueError):self.check(r)
    def test_displacement_plus_six_unique_indices_but_identical_legs_is_rejected(self):
        r=self.fixture();row=r['results'][0]
        for s in row['samples']:s['hash']='0'*64
        row['lowerPixelHashes']=['0'*64]
        with self.assertRaisesRegex(ValueError,'duplicate visible'):self.check(r)
    def test_shot_timer_must_not_change_stationary_support_feet(self):
        r=self.fixture();row=r['results'][-1];row['samples'][2]['hash']='a'*64;row['lowerPixelHashes']=['0'*64,'a'*64]
        with self.assertRaisesRegex(ValueError,'support feet'):self.check(r)
    def test_audit_permuted_indices_cannot_pass_set_coverage(self):
        r=self.fixture();row=r['results'][0];permutation=[0,3,1,4,2,5]
        for s in row['samples']:s['frame']=permutation[s['frame']]
        with self.assertRaisesRegex(ValueError,'Chronological'):self.check(r)
    def test_frozen_positions_and_times_do_not_inherit_travel_summary(self):
        for field,value in [('time',0),('phase',0),('position',[0,0])]:
            r=self.fixture()
            for s in r['results'][0]['samples']:s[field]=value
            with self.assertRaises(ValueError):self.check(r)
    def test_nonfinite_negative_and_mismatched_evidence_fails(self):
        for mutate in [lambda r:r['results'][0]['samples'][4].update(time=float('nan')),
                       lambda r:r['results'][0]['samples'][4].update(position=[float('inf'),0]),
                       lambda r:r['results'][0].update(shots=2),
                       lambda r:r['results'][0].update(direction='N'),
                       lambda r:r['results'][0]['samples'][4].update(phase=-.1)]:
            r=self.fixture();mutate(r)
            with self.assertRaises(ValueError):self.check(r)
if __name__=='__main__':unittest.main()
