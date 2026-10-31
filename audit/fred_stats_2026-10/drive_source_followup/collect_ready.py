"""Collect only terminal, complete replies; quarantine mechanical quote failures."""
import hashlib,json,subprocess,sys
from pathlib import Path
F=Path(__file__).resolve().parent;B=F.parent;sys.path.insert(0,str(B/'scripts'));sys.path.insert(0,str(F))
from validate_adjudication import parse_response
from compare import quote_ok
from repair_quote_gaps import proposed_quote

def main():
 status_path=F/(sys.argv[1] if len(sys.argv)>1 else 'review_round_03_queue_status.json');transport=json.loads(status_path.read_text());collected=json.loads((F/'adjudication_status.json').read_text());history={r['key']:r for r in [json.loads(l) for l in (F/'adjudication_tasks.jsonl').read_text().splitlines() if l]};rp=F/'adjudication_evidence_repairs.json';repairs=json.loads(rp.read_text());failures={};good=[]
 for key,t in transport.items():
  if not t.get('terminal') or not t.get('complete_reply_candidate') or collected.get(key,{}).get('validation')=='valid':continue
  out=Path(history[key]['output']);data,mode=parse_response(out.read_text());assert mode=='complete_json'
  for item in data:
   evidence={**item,'value':item.get('correct_value') or 'undeterminable','confident':True}
   if quote_ok(evidence):continue
   if any(r['key']==key and (r['audit_id'],r['field'])==(item['audit_id'],item['field']) for r in repairs):continue
   source=Path(item['source_path']).read_text();quote=proposed_quote(item['quote'],source)
   if quote and quote_ok({**evidence,'quote':quote}):repairs.append({'key':key,'audit_id':item['audit_id'],'field':item['field'],'raw_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'original_quote':item['quote'],'repaired_quote':quote,'reason':'Explicit ordered omissions of interleaved canonical source text only; no numeric/target/verdict change.'})
  rp.write_text(json.dumps(repairs,indent=2,ensure_ascii=False)+'\n');r=subprocess.run([sys.executable,str(F/'collect_adjudication.py'),key],capture_output=True,text=True)
  if r.returncode:failures[key]=r.stderr[-1200:]
  else:
   collected=json.loads((F/'adjudication_status.json').read_text());collected[key].update(terminal=True,process_exit_code=t['exit_code']);(F/'adjudication_status.json').write_text(json.dumps(collected,indent=2)+'\n');good.append(key)
 p=F/'collection_errors.json';old=json.loads(p.read_text()) if p.exists() else {};old.update(failures)
 for k in good:old.pop(k,None)
 p.write_text(json.dumps(old,indent=2)+'\n');print(json.dumps({'new_valid_replies':len(good),'needs_parent_quote_review':len(old),'keys':good}))
if __name__=='__main__':main()
