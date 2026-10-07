"""Reject self-declared subject preservation using actual synthetic pixels."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image

LAB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB))
import character_workflow as w
import intake_derived_frame as derived

class DerivedIntegrityTests(unittest.TestCase):
    def setUp(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='derived_integrity_',dir=base));self.addCleanup(shutil.rmtree,self.root,True)
        for module in (w,derived):
            p=patch.object(module,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        self.master=self.root/'raw.png';self.output=self.root/'normalized.png'
        self.mask=self.root/'mask.png';self.report=self.root/'report.json';self.response=self.root/'response.json'
        self.rgb=np.full((1024,1024,3),(10,240,10),np.uint8)
        self.rgb[200:800,300:700]=(70,80,90)
        Image.fromarray(self.rgb).save(self.master)
        self.bg=derived._actual_background(self.rgb)
        self.normal=self.rgb.copy();self.normal[self.bg]=(0,255,0)
        Image.fromarray(self.normal).save(self.output)
        Image.fromarray(np.where(self.bg,0,255).astype(np.uint8)).save(self.mask)
        returned=str((self.root/'technical_returned.png').resolve())
        w.write(self.response,{'tool':'image_gen.imagegen','returnedPath':returned,'result':{'output_hint':'Technical fixture: '+returned},
                              'projectCopy':'raw.png','projectCopySHA256':w.sha(self.master)})
    def check(self):
        w.write(self.report,{'operation':'edge-connected green matte normalization only; no source-art redraw',
                            'input_sha256':w.sha(self.master),'output_sha256':w.sha(self.output),
                            'mask_sha256':w.sha(self.mask),'subject_pixels_byte_exact':True,'alpha_ready':True})
        return derived._verify_derivative(self.output,self.master,self.response,self.report,self.mask)
    def test_real_byte_preserving_normalization(self):self.check()
    def test_rehashed_redrawn_subject_is_rejected(self):
        self.normal[500,500]=(255,0,0);Image.fromarray(self.normal).save(self.output)
        with self.assertRaisesRegex(ValueError,'protected subject'):self.check()
    def test_mask_cannot_reclassify_subject_as_background(self):
        self.bg[500,500]=True;self.normal[500,500]=(0,255,0)
        Image.fromarray(self.normal).save(self.output)
        Image.fromarray(np.where(self.bg,0,255).astype(np.uint8)).save(self.mask)
        with self.assertRaisesRegex(ValueError,'edge-connected'):self.check()
    def test_subject_cannot_be_removed_by_all_background_mask(self):
        Image.new('RGB',(1024,1024),(0,255,0)).save(self.output)
        Image.new('L',(1024,1024),0).save(self.mask)
        with self.assertRaisesRegex(ValueError,'protected subject'):self.check()
