"""Technical codec fixture only; this test never approves character art."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
from PIL import Image
import character_workflow as w
import cycle_preview


class CyclePreviewTests(unittest.TestCase):
    def test_review_video_is_native_vp8_webm_and_stays_unreviewed(self):
        base = w.ROOT / 'qa/technical_tests'
        base.mkdir(parents=True, exist_ok=True)
        # Project-local fixture, removed after the test; no production writes.
        root = Path(tempfile.mkdtemp(prefix='preview_codec_', dir=base))
        self.addCleanup(shutil.rmtree, root, True)
        kit = root / 'qa/kit'
        contact = kit / 'reference/atlas/fixture/contact.png'
        atlas = kit / 'public/assets/atlas/fixture/walk.webp'
        contact.parent.mkdir(parents=True)
        atlas.parent.mkdir(parents=True)
        Image.new('RGBA', (96, 64), (120, 80, 50, 255)).save(atlas)
        Image.new('RGB', (1920, 1080)).save(contact)
        clip = {'image':'assets/atlas/fixture/walk.webp','cell':[32,32],
                'columns':3,'height':28,'root':[16,30],'frames':6}
        recipe = {'clips':{'walk':{'frames':6}},'heightMetres':1.72,
                  'locomotion':{'walkSpeed':3.,'walkStride':1.}}
        with patch.object(w, 'ROOT', root), patch.object(w, 'recipe', return_value=recipe), \
             patch('cycle_review.require_pilot'), patch('cycle_review.inputs', return_value={}), \
             patch('preview_gait.preview', return_value={'clip':clip,'contact':str(contact.relative_to(root))}):
            result = cycle_preview.prepare('fixture','E')
        movie = Path(result['video'])
        self.assertEqual(movie.suffix, '.webm')
        self.assertEqual(movie.read_bytes()[:4], b'\x1a\x45\xdf\xa3')
        cap = cv2.VideoCapture(str(movie))
        try:
            codec = int(cap.get(cv2.CAP_PROP_FOURCC))
            self.assertEqual(''.join(chr((codec >> (8*i)) & 255) for i in range(4)), 'VP80')
            self.assertEqual([int(cap.get(3)),int(cap.get(4))],[1920,1080])
            count = 0
            while cap.read()[0]:
                count += 1
            self.assertGreaterEqual(count, 63)
        finally:
            cap.release()
        packet = json.loads(Path(result['packet']).read_text(encoding='utf-8'))
        preview = json.loads(Path(result['preview']).read_text(encoding='utf-8'))
        self.assertEqual(packet['decision'], 'unreviewed')
        self.assertFalse(preview['visualApproval'])
        self.assertFalse(preview['gameRuntimeApproval'])
        self.assertFalse((root/'public').exists())


if __name__ == '__main__':
    unittest.main()
