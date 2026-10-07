"""Video-player HTML is static configuration, never proof of a runtime capture."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

LAB=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('evidence1080',LAB.parent/'tools/art_pipeline/validate_visual_evidence_1080p.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)


class HtmlEvidenceTests(unittest.TestCase):
    def test_video_page_is_config_only_and_small_or_missing_surface_fails(self):
        base=LAB/'qa/technical_tests';base.mkdir(parents=True,exist_ok=True)
        page=Path(tempfile.mkdtemp(prefix='html_evidence_',dir=base))/'fixture.html'
        self.addCleanup(shutil.rmtree,page.parent,True)
        for markup,accepted in [('<video width="1920" height="1080"></video>',True),
                                ('<video width="1280" height="720"></video>',False),
                                ('<p>No configured review surface</p>',False),
                                ('<canvas width="1920" height="1080"></canvas>',True)]:
            page.write_text(markup,encoding='utf-8')
            result=gate.inspect_html(page)
            self.assertEqual(result['native_1080p_container'],accepted)
            self.assertFalse(result['dynamic_runtime_evidence'])
            self.assertEqual(result['evidence_class'],'static_config_only')


if __name__=='__main__':unittest.main()
