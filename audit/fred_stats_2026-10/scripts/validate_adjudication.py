import json,re,sys
from pathlib import Path
from compare import quote_ok
B=Path(__file__).resolve().parents[1]
def validate_item(a):
 required=['audit_id','field','verdict','correct_value','location','quote','source_path','reason']
 assert all(k in a for k in required),'missing required keys'
 assert a['verdict'] in ['shipped_right','blind_right','both_wrong','undeterminable'],'bad verdict'
 assert a['reason'] and a['location'],'missing reason/location'
 assert quote_ok({**a,'value':a['correct_value'] if a['correct_value'] is not None else 'undeterminable','confident':True}),'quote not found in text'
 a['resolution']='argon';return a
if __name__=='__main__':
 queue=json.loads((B/'adjudication_queue.json').read_text());results=[]
 # Past queue snapshots survive even when current disagreements grow.
 for prompt in (B/'adjudications').glob('prompt_*.txt'):
  key=prompt.stem.removeprefix('prompt_');out=B/'adjudications'/f'raw_{key}.txt';dest=B/'adjudications'/f'validated_{key}.json'
  if not out.exists() or not out.stat().st_size or dest.exists():continue
  try:
   text=out.read_text();answer=text.split('## Answer')[-1].strip();answer=re.sub(r'^```(?:json)?\s*|\s*```$','',answer).strip();data=json.loads(answer);assert isinstance(data,list)
   body=prompt.read_text();start=body.index('\n\n[')+2;payload=json.JSONDecoder().raw_decode(body[start:])[0];expected={(x['audit_id'],x['field']) for x in payload};got={(x['audit_id'],x['field']) for x in data};assert got==expected and len(data)==len(expected),'item coverage mismatch'
   data=[validate_item(a) for a in data];dest.write_text(json.dumps(data,indent=2,ensure_ascii=False));results.append({'key':key,'status':'valid','items':len(data)})
  except Exception as e:results.append({'key':key,'status':'failed','error':str(e)})
 (B/'adjudication_validation.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
