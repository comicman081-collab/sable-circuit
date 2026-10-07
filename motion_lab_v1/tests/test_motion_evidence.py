import copy,unittest
from motion_evidence import validate_capture

class MotionCaptureTests(unittest.TestCase):
    def fixture(self):
        rows=[]
        for d in ['E','SE','S','SW','W','NW','N','NE']:
            for action in ['walk','run']:
                for i in range(13):rows.append({'segment':d+' '+action,'frame':i%6,'amount':1,'elapsedMs':len(rows)*40})
        for t in ['adjacent turn + fire','opposite turn','speed up','speed down + stop fire','stop + planted fire','resume']:
            rows.append({'segment':'E walk / '+t,'frame':0,'amount':1,'elapsedMs':len(rows)*40})
        return {'kind':'motion-studio-native-capture','build':{'inputSHA256':'build'},'videoSHA256':'video','captureScriptSHA256':'script','native':[1920,1080],'pixelUpscaling':False,'observations':rows}
    def test_complete_capture_fixture(self):self.assertTrue(validate_capture(self.fixture(),'build','video','script'))
    def test_old_video_still_and_missing_cycles_are_rejected(self):
        for mutate in [lambda r:r['build'].update(inputSHA256='old'),lambda r:r.update(videoSHA256='other'),lambda r:r.update(captureScriptSHA256='old'),lambda r:r.update(pixelUpscaling=True),lambda r:r.update(observations=[]),lambda r:r['observations'].pop(),lambda r:r['observations'][2].update(frame=0)]:
            r=self.fixture();mutate(r)
            with self.assertRaises(ValueError):validate_capture(r,'build','video','script')
    def test_reordered_phases_and_nonmonotonic_timestamps_fail(self):
        for mutate in [lambda r:r['observations'][1].update(frame=3),
                       lambda r:r['observations'][1].update(elapsedMs=0),
                       lambda r:r['observations'][1].update(elapsedMs=float('nan'))]:
            r=self.fixture();mutate(r)
            with self.assertRaises(ValueError):validate_capture(r,'build','video','script')

if __name__=='__main__':unittest.main()
