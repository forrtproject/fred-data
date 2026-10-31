import json,re,sys
from pathlib import Path
from compare import quote_ok
B=Path(__file__).resolve().parents[1]
def parse_response(text):
 answer=text.split('## Answer')[-1].strip();answer=re.sub(r'^```(?:json)?\s*|\s*```$','',answer).strip()
 try:return json.loads(answer),'complete_json'
 except json.JSONDecodeError as original:
  # Stream/timeout output can end mid-object. Preserve only complete JSON objects
  # from the beginning of the answer array; each still passes the full validator.
  if not answer.startswith('['):raise
  decoder=json.JSONDecoder();pos=1;items=[]
  while True:
   while pos<len(answer) and answer[pos].isspace():pos+=1
   if pos>=len(answer) or answer[pos]==']':break
   try:item,end=decoder.raw_decode(answer,pos)
   except json.JSONDecodeError:break
   if not isinstance(item,dict):break
   items.append(item);pos=end
   while pos<len(answer) and answer[pos].isspace():pos+=1
   if pos>=len(answer) or answer[pos]!=',':break
   pos+=1
  if not items:raise original
  return items,'complete_object_prefix'
def validate_item(a):
 required=['audit_id','field','verdict','correct_value','location','quote','source_path','reason']
 assert all(k in a for k in required),'missing required keys'
 assert a['verdict'] in ['shipped_right','blind_right','both_wrong','undeterminable'],'bad verdict'
 assert a['reason'] and a['location'],'missing reason/location'
 assert quote_ok({**a,'value':a['correct_value'] if a['correct_value'] is not None else 'undeterminable','confident':True}),'quote not found in text'
 a['resolution']='argon';return a
def validate_batch(data,payload):
 assert isinstance(data,list),'response is not an array'
 expected={(a['audit_id'],a['field']) for a in payload};bykey={};good=[];failed=[]
 for a in data:
  key=(a.get('audit_id'),a.get('field')) if isinstance(a,dict) else (None,None)
  bykey.setdefault(key,[]).append(a)
 for key in sorted(expected):
  try:
   candidates=bykey.get(key,[]);assert len(candidates)==1,'missing or duplicate field response'
   good.append(validate_item(candidates[0]))
  except Exception as error:failed.append({'audit_id':key[0],'field':key[1],'error':str(error)})
 return good,failed
if __name__=='__main__':
 import hashlib
 results=[]
 for prompt in (B/'adjudications').glob('prompt_*.txt'):
  key=prompt.stem.removeprefix('prompt_');out=B/'adjudications'/f'raw_{key}.txt';dest=B/'adjudications'/f'validated_{key}.json';state=B/'adjudications'/f'validation_{key}.json'
  if not out.exists() or not out.stat().st_size:continue
  digest=hashlib.sha256(out.read_bytes()).hexdigest()
  if state.exists() and json.loads(state.read_text()).get('raw_sha256')==digest and json.loads(state.read_text()).get('validator_version')==2:continue
  # Older fully validated responses have already passed the strict validator.
  if dest.exists() and not state.exists():continue
  try:
   data,parse_mode=parse_response(out.read_text())
   body=prompt.read_text();start=body.index('\n\n[')+2;payload=json.JSONDecoder().raw_decode(body[start:])[0]
   good,failed=validate_batch(data,payload)
   prior=json.loads(dest.read_text()) if dest.exists() else [];merged={(a['audit_id'],a['field']):a for a in prior}
   for a in good:merged[(a['audit_id'],a['field'])]=a
   if merged:dest.write_text(json.dumps(list(merged.values()),indent=2,ensure_ascii=False))
   status='valid' if not failed else 'partial' if merged else 'failed';result={'key':key,'status':status,'parse_mode':parse_mode,'items':len(merged),'failed_fields':failed,'raw_sha256':digest}
  except Exception as error:result={'key':key,'status':'failed','error':str(error),'raw_sha256':digest}
  result['validator_version']=2;state.write_text(json.dumps(result,indent=2));results.append(result)
 (B/'adjudication_validation.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
