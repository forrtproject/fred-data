"""A capped source assignment must not hide its unattempted rows."""
import contextlib,csv,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import prepare_continuation as prep
class ContinuationDedupe(unittest.TestCase):
 def test_new_row_in_already_assigned_source_remains_eligible(self):
  with tempfile.TemporaryDirectory() as directory:
   b=Path(directory);f=b/'completion';f.mkdir();(b/'inputs').mkdir();source=b/'primary.txt';source.write_text('Fixture primary source')
   neutral=[{'audit_id':aid,'doi_o':'10.example/fixture','ref_o':'Fixture paper','description':'Distinct target '+str(aid),'text_paths':{'o':str(source)}} for aid in [1,2]]
   (b/'inputs/source.json').write_text(json.dumps(neutral));(b/'source_provenance.json').write_text(json.dumps({str(source):{'work_doi':'10.example/fixture'}}))
   with (b/'results.csv').open('w',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=['input_row_index']+[k+'_final_verdict' for k in prep.FIELDS]);writer.writeheader()
    for aid in [1,2]:writer.writerow({'input_row_index':aid,**{k+'_final_verdict':'unverified' if k.endswith('_o') else 'correct' for k in prep.FIELDS}})
   gates=b/'gates.csv';gates.write_text('audit_id,field,gate\n')
   old=f/'old_input.json';old.write_text(json.dumps([{'audit_id':1,'unfinished_fields':['n_o','es_value_o','pval_value_o']}]))
   (f/'work_queue.json').write_text(json.dumps([{'key':'old','phase':'pilot','source':'10.example/fixture','side':'original','input':str(old)}]))
   with patch.object(prep,'SOURCE_MANIFESTS',[]),patch.object(prep,'GATES_PATH',gates),patch.object(prep,'F',f),patch.object(prep,'B',b),patch.object(sys,'argv',['prepare','--batch','continuation_test','--limit','1']),contextlib.redirect_stdout(io.StringIO()):prep.main()
   queue=json.loads((f/'continuation_test/queue.json').read_text());self.assertEqual(len(queue),1)
   records=json.loads(Path(queue[0]['input']).read_text());self.assertEqual([r['audit_id'] for r in records],[2]);self.assertEqual(set(records[0]['unfinished_fields']),{'n_o','es_value_o','pval_value_o'})
if __name__=='__main__':unittest.main()
