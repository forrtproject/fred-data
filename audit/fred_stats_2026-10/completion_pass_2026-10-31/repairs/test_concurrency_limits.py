import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from concurrency_limits import live_count,slot_ceiling

class ConcurrencyLimits(unittest.TestCase):
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
