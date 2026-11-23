import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import check_yield_ready as guard

class ExportFingerprint(unittest.TestCase):
 def test_pending_review_dispatch_does_not_change_scientific_inputs(self):
  with tempfile.TemporaryDirectory() as directory:
   b=Path(directory);(b/'adjudications').mkdir();log=b/'adjudication_tasks.jsonl';log.write_text('')
   with patch.object(guard,'B',b):
    before=guard.scientific_fingerprint();log.write_text(json.dumps({'key':'completion_future_v1','started_at':'later'})+'\n')
    self.assertEqual(guard.scientific_fingerprint(),before)
    # The same entry becomes load-bearing as soon as a validated decision exists.
    (b/'adjudications/validated_completion_future_v1.json').write_text('[]')
    self.assertNotEqual(guard.scientific_fingerprint(),before)
 def test_precedence_and_evidence_changes_remain_load_bearing(self):
  with tempfile.TemporaryDirectory() as directory:
   b=Path(directory);(b/'adjudications').mkdir();e=b/'adjudications/validated_completion_existing_v1.json';e.write_text('[]');log=b/'adjudication_tasks.jsonl';log.write_text(json.dumps({'key':'completion_existing_v1','started_at':'first'})+'\n')
   with patch.object(guard,'B',b):
    first=guard.scientific_fingerprint();log.write_text(log.read_text()+json.dumps({'key':'completion_existing_v1','started_at':'changed-priority'})+'\n');second=guard.scientific_fingerprint();self.assertNotEqual(first,second)
    e.write_text('[{"decision":"changed"}]');self.assertNotEqual(second,guard.scientific_fingerprint())

if __name__=='__main__':unittest.main()
