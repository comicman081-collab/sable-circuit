import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import character_workflow as workflow

class DeliveryInvalidationTests(unittest.TestCase):
    def test_rejection_preserves_prior_receipt_and_removes_current_approval(self):
        parent=workflow.ROOT/'qa/technical_tests';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as folder:
            root=Path(folder);(root/'dist').mkdir()
            path=root/'dist/fixture.delivery.json'
            original=b'{"status":"REVIEWED_DELIVERY","character":"fixture"}'
            path.write_bytes(original)
            with patch.object(workflow,'ROOT',root):workflow.invalidate_delivery('fixture','Observed frozen gait')
            self.assertEqual(json.loads(path.read_text())['status'],'HOLD_VISUAL_REPAIR')
            saved=list((root/'qa/fixture/delivery_history').glob('*.json'))
            self.assertEqual(len(saved),1);self.assertEqual(saved[0].read_bytes(),original)

if __name__=='__main__':unittest.main()
