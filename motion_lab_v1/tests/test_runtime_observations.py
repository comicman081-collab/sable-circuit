import copy
import unittest
from runtime_observations import template, validate, FIELDS
from character_workflow import DIRECTIONS


class RuntimeObservationTests(unittest.TestCase):
    def fixture(self):
        package={'inputSHA256':'technical-build'}
        capture={'videoSHA256':'technical-video','observations':[]}
        report=template('fixture',package,capture)
        for direction in DIRECTIONS:
            for action in ('walk','run'):
                start=len(capture['observations'])
                for i in range(3):capture['observations'].append({'segment':direction+' '+action,'elapsedMs':(start+i)*1000,'amount':1})
                report['directions'][direction][action]={'seconds':[start+.1,start+1.1],**{key:'Synthetic timestamp validation fixture only' for key in FIELDS}}
        for name in report['transitions']:
            start=len(capture['observations'])
            for i in range(3):capture['observations'].append({'segment':'E walk / '+name,'elapsedMs':(start+i)*1000,'amount':1})
            report['transitions'][name]={'seconds':[start+.1,start+1.1],'notes':'Synthetic transition timing fixture only'}
        report.update(reviewer='unit-test',decision='approved')
        return report,package,capture

    def test_complete_observation_schema_with_actual_segment_times(self):
        report,package,capture=self.fixture()
        self.assertTrue(validate(report,'fixture',package,capture,'unit-test'))

    def test_generic_notes_or_wrong_video_times_cannot_approve(self):
        report,package,capture=self.fixture()
        for mutate in [lambda r:r.update(decision='unreviewed'),lambda r:r.update(videoSHA256='other'),
                       lambda r:r['directions']['E']['walk'].update(seconds=[50,51]),
                       lambda r:r['directions']['N']['run'].update(footSliding=''),
                       lambda r:r['transitions']['resume'].update(seconds=[]),
                       lambda r:r.update(reviewer='someone-else')]:
            bad=copy.deepcopy(report);mutate(bad)
            with self.assertRaises(ValueError):validate(bad,'fixture',package,capture,'unit-test')


if __name__=='__main__':unittest.main()
