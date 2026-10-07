import math
import sys
import unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import tripo_cycle_fit as fitting
import motion_harness as h


class TripoCycleTimingTests(unittest.TestCase):
    def test_two_observed_strides_fit_one_continuous_period(self):
        phases=np.linspace(0,2,49)
        curve=fitting.fit(phases,[[math.sin(2*math.pi*p),.03*math.cos(4*math.pi*p)] for p in phases])
        for phase in (0,.12,.53,.98,1,1.53):
            np.testing.assert_allclose(fitting.evaluate(curve,phase),[math.sin(2*math.pi*phase),.03*math.cos(4*math.pi*phase)],atol=1e-12)
        self.assertEqual(fitting.evaluate(curve,0),fitting.evaluate(curve,1))

    def test_nonuniform_contact_window_is_not_uniform_frame_clock(self):
        row={'frames':8,'phase_starts':[0,.125,.1875,19/48,22/48,28/48,29/48,41/48]}
        self.assertEqual(h.phase_frame(row,.38),2)
        self.assertEqual(h.phase_frame(row,19/48),3)
        self.assertEqual(h.phase_frame(row,1.38),2)
        self.assertEqual(h.phase_frame(row,.999),7)

    def test_invalid_phase_data_cannot_retime_one_firing_channel(self):
        for values in ([0,.5,.5],[.1,.3,.7],[0,.5,1],[0,float('nan'),.8],[0,.5]):
            with self.assertRaises(ValueError):h.phase_starts({'frames':3,'phase_starts':values})


if __name__=='__main__':unittest.main()
