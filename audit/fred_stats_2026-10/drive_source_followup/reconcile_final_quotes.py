"""Reconcile late quote-only finalisation without changing extracted statistics."""
import copy,hashlib,json,sys
from pathlib import Path
F=Path(__file__).resolve().parent;B=F.parent;sys.path.insert(0,str(B/'scripts'))
from compare import quote_ok
from validate_adjudication import parse_response

def main():
 ledger=json.loads((F/'integration.json').read_text());rp=F/'post_integration_quote_reconciliation.json';repairs=json.loads(rp.read_text()) if rp.exists() else []
 for k,r in ledger.items():
  batch,aid,side=k.rsplit(':',2);p=F/'validation_extractions'/batch/f'{aid}.json';newhash=hashlib.sha256(p.read_bytes()).hexdigest()
  if newhash==r['result_sha256']:continue
  raw=json.loads(p.read_text());dest=B/'extractions'/f'{aid}.json';current=json.loads(dest.read_text());left=copy.deepcopy(current[side]);right=copy.deepcopy(raw[side]);oldquote=left['n']['quote'];newquote=right['n']['quote'];left['n']['quote']=newquote;assert left==right,(aid,'Nonquote difference');assert quote_ok({**right['n'],'value':'source evidence','confident':True});backup=F/'quote_repairs'/'post_integration'/f'{aid}.json';backup.parent.mkdir(parents=True,exist_ok=True)
  if not backup.exists():backup.write_bytes(dest.read_bytes())
  current[side]['n']['quote']=newquote;dest.write_text(json.dumps(current,indent=2,ensure_ascii=False)+'\n');repairs.append({'audit_id':int(aid),'old_output_hash':r['result_sha256'],'final_output_hash':newhash,'field':'n.quote','old_quote':oldquote,'final_quote':newquote,'semantic_fields_unchanged':True});r['result_sha256']=newhash
  rp.write_text(json.dumps(repairs,indent=2,ensure_ascii=False)+'\n');(F/'integration.json').write_text(json.dumps(ledger,indent=2)+'\n')
 print('quote-only reconciliation records',len(repairs))
 key='drivefollowup_cf8da9e0ec49253c';p=B/'adjudications'/f'raw_{key}.txt';rows,_=parse_response(p.read_text());r=next(r for r in rows if r['field']=='n_r');quote='was removed from the data. The remaining 119 participants ranged in … age from 18 to 22 years';assert quote_ok({**r,'quote':quote,'value':r['correct_value'],'confident':True});rp=F/'adjudication_evidence_repairs.json';rs=json.loads(rp.read_text())
 if not any(x['key']==key and x['field']=='n_r' for x in rs):rs.append({'key':key,'audit_id':r['audit_id'],'field':r['field'],'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'original_quote':r['quote'],'repaired_quote':quote,'reason':'Explicit omission for interleaved primary PDF text; no verdict/value/target change.'});rp.write_text(json.dumps(rs,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
