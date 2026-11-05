import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from concurrency_limits import live_count,slot_ceiling,review_launch_paused,recorded_quota_failure,review_capacity_available,ordinary_review_ceiling

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
 def test_handoff_requires_dispatch_only_with_total_review_capacity(self):
  config={'review_slots':4,'source_slots':6,'max_combined_children':10}
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)
   for name in ['task_a_v1.json','task_b_v1.json','task_c_v1.json','task_identity_v2.json']:
    (p/name).write_text(json.dumps({'taskId':name,'status':'running'}))
   self.assertFalse(review_capacity_available(live_count(p,'task_*.json'),0,config))
   (p/'task_identity_v2.json').write_text(json.dumps({'taskId':'identity','status':'completed'}))
   self.assertTrue(review_capacity_available(live_count(p,'task_*.json'),0,config))
   self.assertFalse(review_capacity_available(3,7,config))
 def test_ordinary_dispatch_subtracts_focused_review_slots(self):
  config={'review_slots':4,'source_slots':6,'max_combined_children':10}
  self.assertEqual(ordinary_review_ceiling(0,1,config),3)
  self.assertEqual(ordinary_review_ceiling(6,1,config),3)
  self.assertEqual(ordinary_review_ceiling(8,1,config),1)
  self.assertEqual(ordinary_review_ceiling(0,4,config),0)

if __name__=='__main__':unittest.main()
