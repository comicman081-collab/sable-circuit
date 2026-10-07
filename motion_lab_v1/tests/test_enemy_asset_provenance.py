"""Tiny local diagnostic inputs, not generated art or visual approvals."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

LAB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB))
import prepare_enemy_asset as prep

class EnemyProvenanceTests(unittest.TestCase):
    def setUp(self):
        folder=LAB/'qa/technical_tests';folder.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='enemy_proof_',dir=folder));self.addCleanup(shutil.rmtree,self.root,True)
        p=patch.object(prep,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        self.source=self.root/'master.png';Image.new('RGBA',(16,24),(60,80,100,255)).save(self.source)
        self.response=self.root/'response.json'
        self.returned=str(self.root/'managed-original.png')
        self.proof={'tool':'image_gen.imagegen','returnedPath':self.returned,
                    'result':{'output_hint':'Generated image saved to '+self.returned},
                    'projectCopy':'master.png','projectCopySHA256':prep.sha(self.source)}
    def check(self):
        self.response.write_text(json.dumps(self.proof),encoding='utf-8')
        return prep.verify_source(self.source,self.response)
    def test_exact_retained_copy_survives_absent_managed_staging(self):
        self.check()
    def test_metadata_name_alone_does_not_prove_art(self):
        del self.proof['projectCopy']
        with self.assertRaisesRegex(ValueError,'exact project copy'):self.check()
    def test_source_tamper_rejected(self):
        self.source.write_bytes(b'changed fixture')
        with self.assertRaisesRegex(ValueError,'hash'):self.check()
    def test_other_tool_file_cannot_substitute(self):
        self.proof['result']['output_hint']='Saved another file.png'
        with self.assertRaisesRegex(ValueError,'metadata'):self.check()
    def test_returned_path_requires_exact_output_path(self):
        self.proof['result']['output_hint']=self.returned+'.other.png'
        with self.assertRaisesRegex(ValueError,'metadata'):self.check()
    def test_identifier_cannot_escape_qa(self):
        with self.assertRaisesRegex(ValueError,'asset id'):
            prep.prepare('../../runtime',self.source,self.response)

    def test_quoted_longer_path_is_not_the_returned_file(self):
        for quote in ['\"',"'",'`']:
            for suffix in [' other.png','. other.png']:
                self.proof['result']['output_hint']=f'Saved to {quote}{self.returned}{suffix}{quote}'
                with self.assertRaisesRegex(ValueError,'metadata'):self.check()

    def test_exact_path_with_spaces_remains_supported(self):
        self.proof['returnedPath']=str(self.root/'actual image with spaces.png')
        for hint in [f'Saved to "{self.proof["returnedPath"]}"',
                     f'Generated images are saved to {self.root} as {self.proof["returnedPath"]} by default.\nNext instruction.']:
            self.proof['result']['output_hint']=hint;self.check()

    def test_unclosed_quote_cannot_expose_a_path_suffix(self):
        for quote in ['"',"'",'`']:
            self.proof['result']['output_hint']=f'Saved to {quote}/staging/other {self.returned}'
            with self.assertRaisesRegex(ValueError,'metadata'):self.check()

    def test_matte_code_change_preserves_previous_preparation(self):
        # Real prepare() and real deterministic key_image, synthetic art only.
        Image.new('RGBA',(1024,1024),(60,80,100,254)).save(self.source)
        self.proof['projectCopySHA256']=prep.sha(self.source);self.check()
        matte=self.root/'build_atlas.py';matte.write_text('technical dependency version 1')
        (self.root/'source_provenance.py').write_text('technical dependency fingerprint')
        prep.prepare('fixture',self.source,self.response)
        first=next((self.root/'qa/stage1_enemies_20260913/fixture').glob('*/preparation.json'))
        first_hash=prep.sha(first)
        matte.write_text('technical dependency version 2')
        prep.prepare('fixture',self.source,self.response)
        reports=list((self.root/'qa/stage1_enemies_20260913/fixture').glob('*/preparation.json'))
        self.assertEqual(len(reports),2);self.assertEqual(prep.sha(first),first_hash)
