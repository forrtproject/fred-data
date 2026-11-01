import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from concurrency_limits import live_count,slot_ceiling,review_launch_paused,recorded_quota_failure

class ConcurrencyLimits(unittest.TestCase):
 def test_service_hold_pauses_only_the_named_review_service(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'hold.json';self.assertFalse(review_launch_paused(p))
   d={'active':True,'provider':'antigravity','model':'gemini-4-argon-high','reason':'quota_exhausted'}
   p.write_text(json.dumps(d));self.assertTrue(review_launch_paused(p))
   p.write_text(json.dumps({**d,'active':False}));self.assertFalse(review_launch_paused(p))
   p.write_text(json.dumps({**d,'provider':'other'}))
   with self.assertRaises(AssertionError):review_launch_paused(p)
 def test_quota_failure_never_counts_as_a_validated_review(self):
  d={'status':'completed','failure_disposition_recorded':True,'output_failure_code':'quota_exhausted','output_contract':'failed','summary':'Usage Limit Reached'}
  self.assertTrue(recorded_quota_failure(d,False))
  self.assertFalse(recorded_quota_failure(d,True))
  for change in [{'status':'running'},{'failure_disposition_recorded':False},{'output_failure_code':'other'},{'output_contract':'done'},{'summary':'Review complete'}]:
   with self.subTest(change=change):self.assertFalse(recorded_quota_failure({**d,**change},False))
 def test_review_capacity_uses_spare_slots_without_exceeding_ten(self):
  self.assertEqual(slot_ceiling('review',6),4)
  self.assertEqual(slot_ceiling('review',8),2)
  self.assertEqual(slot_ceiling('source',6),4)
  self.assertEqual(slot_ceiling('source',10),0)
 def test_focused_reviews_count_against_shared_capacity(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)
   for name,status in [('task_x_v1.json','running'),('task_y_v2.json','running'),('task_z_v1.json','completed')]:
    (p/name).write_text(json.dumps({'taskId':name,'status':status}))
   self.assertEqual(live_count(p,'task_*.json'),2)
   self.assertEqual(live_count(p,'task_*.json',exclude_suffix='_v1.json'),1)

if __name__=='__main__':unittest.main()
