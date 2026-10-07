import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

import sys
LAB = Path(__file__).resolve().parents[1]
# Package imports need the repository root; the modules' own flat imports need LAB.
sys.path[:0] = [str(LAB.parent), str(LAB)]

from motion_lab_v1 import source_provenance as provenance
from motion_lab_v1 import intake_web_alpha as intake


def bind(root, path):
    return {'path': path.relative_to(root).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


class WebAlphaIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'motion_lab_v1'
        self.root.mkdir()
        self.qa = self.root / 'qa' / 'site7_rifle'
        self.qa.mkdir(parents=True)
        self.returned = self.qa / 'web_alpha_return.png'
        image = Image.new('RGBA', (1024, 1536), (0, 0, 0, 0))
        image.paste((50, 60, 70, 254), (260, 120, 760, 1420))
        image.save(self.returned)
        self.bridge = self.qa / 'bridge.json'
        self.bridge.write_text(json.dumps({
            'kind': 'sable-web-alpha-bridge', 'schema': 1,
            'status': 'WEB_ALPHA_BRIDGE_ONLY', 'directIntakeAllowed': False,
            'source': {'path': 'qa/site7_rifle/source_green.png', 'sha256': 'retained'},
        }), encoding='utf-8')
        self.response = self.qa / 'web-response.json'
        bridge_binding = bind(self.root, self.bridge)
        self.response.write_text(json.dumps({
            'tool': 'chatgpt.web.alpha_conversion',
            'returnedPath': str(self.returned.resolve()),
            'projectCopy': self.returned.relative_to(self.root).as_posix(),
            'projectCopySHA256': hashlib.sha256(self.returned.read_bytes()).hexdigest(),
            'bridgeManifest': bridge_binding,
            'result': {'returnedPath': str(self.returned.resolve()), 'conversationUrl': 'https://chatgpt.com/c/example'},
        }), encoding='utf-8')

    def test_web_response_master_is_native_project_copy(self):
        master = provenance.response_master(self.root, self.response)
        self.assertEqual(master, self.returned)

    def test_web_response_rejects_external_return_path(self):
        proof = json.loads(self.response.read_text(encoding='utf-8'))
        proof['returnedPath'] = str((self.root.parent / 'outside.png').resolve())
        self.response.write_text(json.dumps(proof), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'differs from project copy'):
            provenance.response_master(self.root, self.response)

    def test_intake_response_requires_exact_project_copy(self):
        with patch.object(intake, 'ROOT', self.root):
            with self.assertRaisesRegex(ValueError, 'project copy/hash'):
                proof = json.loads(self.response.read_text(encoding='utf-8'))
                proof['projectCopySHA256'] = 'stale'
                self.response.write_text(json.dumps(proof), encoding='utf-8')
                intake._validate_web_response(self.response, self.bridge, self.returned)


if __name__ == '__main__':
    unittest.main()
