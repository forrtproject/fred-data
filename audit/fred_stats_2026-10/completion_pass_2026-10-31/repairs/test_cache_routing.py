"""Cache candidates outside the provenance index still need blind identity inspection."""
import contextlib,csv,hashlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import prepare_continuation as prep

class CacheRouting(unittest.TestCase):
 def test_unindexed_doi_hash_is_candidate_not_accepted_identity(self):
  with tempfile.TemporaryDirectory() as directory:
   b=Path(directory);f=b/'completion';f.mkdir();(b/'inputs').mkdir();(b/'texts').mkdir()
   doi='10.example/unindexed';source=b/'texts'/(hashlib.sha256(doi.encode()).hexdigest()[:24]+'.txt');source.write_text('Unverified primary-text candidate')
   (b/'inputs/source.json').write_text(json.dumps([{'audit_id':1,'doi_o':doi,'ref_o':'Fixture primary work','description':'Identifiable target','text_paths':{}}]))
   (b/'source_provenance.json').write_text('{}');(f/'work_queue.json').write_text('[]')
   with (b/'results.csv').open('w',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=['input_row_index']+[k+'_final_verdict' for k in prep.FIELDS]);writer.writeheader();writer.writerow({'input_row_index':1,**{k+'_final_verdict':'unverified' if k.endswith('_o') else 'correct' for k in prep.FIELDS}})
   gates=b/'gates.csv';gates.write_text('audit_id,field,gate\n')
   with patch.object(prep,'SOURCE_MANIFESTS',[]),patch.object(prep,'GATES_PATH',gates),patch.object(prep,'F',f),patch.object(prep,'B',b),patch.object(sys,'argv',['prepare','--batch','continuation_test','--limit','1']),contextlib.redirect_stdout(io.StringIO()):prep.main()
   queue=json.loads((f/'continuation_test/queue.json').read_text());self.assertEqual(len(queue),1)
   record=json.loads(Path(queue[0]['input']).read_text())[0];self.assertEqual(record['text_paths']['o'],str(source));self.assertIs(record['source_identity_pending'],True)
   self.assertEqual(json.loads((b/'source_provenance.json').read_text()),{})

if __name__=='__main__':unittest.main()
