"""A matching broad author label cannot certify a mismatched effect."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'scripts'))
from compare import narrative_scope_unknown
class NarrativeScopeTests(unittest.TestCase):
 def test_done_numeric_mismatch_can_hold_broad_author_label(self):
  x={'replication':{'status':'done','target_match':False},'reported_success':{'location':'Discussion'},'notes':'The observed author label concerns the study as a whole.'}
  self.assertFalse(narrative_scope_unknown(x))
  self.assertTrue(narrative_scope_unknown(x,{'field':'reported_success','target_match':False}))
 def test_existing_unidentified_scope_is_not_cleared_by_target_flag(self):
  x={'replication':{'status':'locator_insufficient'},'reported_success':{'location':'Discussion'},'notes':'Overall paper narrative; individual effect unidentified.'}
  self.assertTrue(narrative_scope_unknown(x,{'field':'reported_success','target_match':True}))
if __name__=='__main__':unittest.main()
