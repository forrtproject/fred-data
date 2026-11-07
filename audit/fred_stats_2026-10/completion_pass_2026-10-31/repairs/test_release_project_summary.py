import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[1]/'release_draft/build_release.py'
spec=importlib.util.spec_from_file_location('completion_release_builder',path)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class ReleaseProjectSummary(unittest.TestCase):
 def test_project_counts_reconcile_and_preserve_uncertainty(self):
  projects={'a':{'n_o':{'correct':2,'error':1,'unverified':3,'not_comparable':4}},'b':{'n_o':{'correct':1,'error':2}}}
  overall={'n_o':{'correct':3,'error':3,'unverified':3,'not_comparable':4}}
  rows=builder.project_summary(projects,overall)
  self.assertEqual(sum(r['evaluable'] for r in rows),6)
  self.assertEqual(sum(r['total'] for r in rows),13)
  self.assertEqual(rows[0]['lower_all_row_error_bound'],0.1)
  self.assertEqual(rows[0]['upper_all_row_error_bound'],0.8)
 def test_stale_project_totals_fail_closed(self):
  with self.assertRaises(AssertionError):
   builder.project_summary({'a':{'n_o':{'error':1}}},{'n_o':{'error':2}})

if __name__=='__main__':unittest.main()
