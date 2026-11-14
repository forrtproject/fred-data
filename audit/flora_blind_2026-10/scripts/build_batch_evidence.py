"""Expose existing source reviews for batch inspection, without changing approvals."""
import csv
import hashlib
import json
import re
from pathlib import Path
B=Path(__file__).resolve().parents[1]
H=B/'handoff'
ROOT=B.parents[1]

def load_json(value):
    try:return json.loads(value) if isinstance(value,str) else value
    except (TypeError,ValueError):return {}

def build():
    batch=json.loads((H/'batch_review.json').read_text())
    cases={c['id']:c for c in json.loads((H/'review_queue.json').read_text())}
    final={d['case_id']:d for d in json.loads((H/'sol_review_decisions.json').read_text())['decisions']}
    with (H/'confirmed_missing_pairs.csv').open(encoding='utf-8-sig') as f:
        pairs={f"pair:{p['file_key']}:{p['target_index']}":p for p in csv.DictReader(f)}
    with Path('/home/lukas/audit_inputs_2026-10/flora_b48a7d6.csv').open(encoding='utf-8-sig') as f:frozen=list(csv.DictReader(f))
    with (B/'results.csv').open(encoding='utf-8-sig') as f:results=list(csv.DictReader(f))
    by_work={}
    for r in results:by_work.setdefault(r['work_key'],[]).append(int(r['input_row_index']))
    verified=0
    def proof(p):
        nonlocal verified
        keys=['quote','section','location','proof_id','sha256','raw_sha256','character_start','character_end','utf8_byte_start','utf8_byte_end']
        out={k:p[k] for k in keys if k in p}
        path=p.get('source_path')
        if path and 'character_start' in p and 'character_end' in p:
            source=Path(path) if Path(path).is_absolute() else ROOT/path
            raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
            assert sha==p.get('raw_sha256',p.get('sha256')),source
            text=raw.decode('utf-8');quote=text[p['character_start']:p['character_end']]
            if p.get('quote') is not None:assert quote==p['quote'],source
            if 'utf8_byte_start' in p:assert raw[p['utf8_byte_start']:p['utf8_byte_end']].decode('utf-8')==quote,source
            out['quote']=quote;out['sha256']=sha;out['source_verified']=True;verified+=1
        return out
    def identity(i,side):
        row=frozen[i]
        people=load_json(row.get(f'author_{side}',''))
        authors='; '.join(', '.join(filter(None,[person.get('family') or person.get('literal'),person.get('given')])) for person in people if isinstance(person,dict)) if isinstance(people,list) else row.get(f'author_{side}','')
        result={k:row[f'{c}_{side}'] for k,c in [('title','title'),('authors','author'),('year','year'),('doi','doi')] if row.get(f'{c}_{side}') not in ('','NA')}
        if authors:result['authors']=authors
        return result
    items={}
    for group in batch['groups']:
        for item in group['items']:
            if item.get('case_id'):
                c=cases[item['case_id']];review=final.get(c['id'],{}).get('fields',{})
                fields={}
                for field in item['fields']:
                    r=review.get(field,{})
                    fields[field]={k:r[k] for k in ['disposition','rationale','contrary_evidence','limits','missing_evidence_or_policy_choice'] if r.get(k)}
                    fields[field]['proofs']=[proof(p) for p in r.get('proofs',[])]
                    audit=c.get('evidence',{}).get(field,{})
                    fields[field]['reason']=audit.get('reason','')
                    quote=audit.get('quote','');words=list(re.finditer(r'\S+',quote))
                    fields[field]['quoted_passages']=([{'quote':quote,'section':audit.get('location','Cited passage')} ] if quote else [])
                    if len(words)>25:fields[field]['quoted_passages'].append({'quote':quote[words[-25].start():],'section':'End of cited passage','location':audit.get('location',''),'quote_is_excerpt':True})
                items[item['id']]={'kind':'row','case_id':c['id'],'fields':fields,'evidence_reference':c.get('final_review_reference','correction_proposals.json')}
            else:
                p=pairs[item['id']];ev=load_json(p['evidence']);target=load_json(p['blind_target']);indices=by_work.get(p['work_key'],[])
                proofs=[]
                if ev.get('quote'):proofs.append({k:ev[k] for k in ['quote','location','method'] if ev.get(k)})
                proofs.extend(proof(x) for x in ev.get('source_proof_locators',[]))
                if target.get('evidence_quote') and target['evidence_quote']!=ev.get('quote'):proofs.append({'quote':target['evidence_quote'],'section':'Target identification in the blind coding'})
                items[item['id']]={'kind':'pair','work_key':p['work_key'],'replication':identity(indices[0],'r') if indices else {'doi':p['work_key']},'original':item['operations'][0]['original'],'already_in_flora':[{'row':i,**identity(i,'o')} for i in indices], 'reason':ev.get('reason',ev.get('rationale','')),'proofs':proofs,'evidence_level':p['evidence_level'],'evidence_reference':'confirmed_missing_pairs.csv','outcome_status':'not_adjudicated'}
    result={'schema_version':1,'baseline_sha256':batch['baseline_sha256'],'items':items,'verified_proof_slices':verified,'canonical_changes_applied':False}
    (H/'batch_evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result
if __name__=='__main__':
    data=build();print(json.dumps({'items':len(data['items']),'verified_proof_slices':data['verified_proof_slices']}))
