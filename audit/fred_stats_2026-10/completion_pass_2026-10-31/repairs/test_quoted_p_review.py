import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import compare

class QuotedPReview(unittest.TestCase):
 def test_source_confirmed_quoted_operators_preserve_legacy_comparison(self):
  for operator,bound,value in [('<','l','0.001'),('=','e','0.003')]:
   row={'pval_value_r':value,'pval_type_r':'"'+operator+'"'}
   review={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_value':value,'correct_bound':bound}
   self.assertEqual(compare.comp('pval_value_r',value,{'value':value,'bound':bound},row),'not_comparable')
   self.assertTrue(compare.fresh_quoted_p_review(review,'pval_value_r',row))
 def test_unknown_or_different_metadata_and_stale_reviews_remain_held(self):
  row={'pval_value_r':'0.001','pval_type_r':'"<"'}
  review={'completion_pass':'2026-10-31','replaces_unverified':True,'target_match_confirmed':True,'verdict':'shipped_right','correct_value':'0.001','correct_bound':'l'}
  for change in [{'completion_pass':'old'},{'replaces_unverified':False},{'target_match_confirmed':False},{'verdict':'blind_right'},{'correct_value':'0.002'},{'correct_bound':'g'},{'correct_bound':None}]:
   self.assertFalse(compare.fresh_quoted_p_review({**review,**change},'pval_value_r',row),change)
  for bound in [None,'unknown','<','"less"','"<','<"']:
   self.assertFalse(compare.fresh_quoted_p_review(review,'pval_value_r',{**row,'pval_type_r':bound}),bound)
  self.assertFalse(compare.fresh_quoted_p_review({**review,'correct_value':'0'},'pval_value_r',{**row,'pval_value_r':'0'}))

if __name__=='__main__':unittest.main()
