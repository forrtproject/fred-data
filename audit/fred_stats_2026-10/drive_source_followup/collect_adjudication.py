"""Validate one complete independent Mac-source adjudication response."""
import hashlib
import json
import sys
from pathlib import Path
F=Path(__file__).resolve().parent
B=F.parent
sys.path.insert(0,str(B/'scripts'))
from validate_adjudication import parse_response, validate_batch
from compare import quote_ok


def main():
    key=sys.argv[1]
    records=[json.loads(l) for l in (F/'adjudication_tasks.jsonl').read_text().splitlines() if l]
    record=next(r for r in records if r['key']==key)
    out=Path(record['output']);prompt=Path(record['prompt']).read_text()
    assert out.stat().st_size>0,'No response yet'
    start=prompt.index('\n\n[')+2;payload=json.JSONDecoder().raw_decode(prompt[start:])[0]
    data,mode=parse_response(out.read_text())
    assert mode=='complete_json','Incomplete reply cannot be validated'
    repairs_path=F/'adjudication_evidence_repairs.json'
    repairs=json.loads(repairs_path.read_text()) if repairs_path.exists() else []
    for repair in [r for r in repairs if r['key']==key]:
        assert repair['raw_sha256']==hashlib.sha256(out.read_bytes()).hexdigest()
        item=next(r for r in data if (r['audit_id'],r['field'])==(repair['audit_id'],repair['field']))
        assert item['quote']==repair['original_quote']
        item['quote']=repair['repaired_quote']
    metadata_path=F/'adjudication_metadata_repairs.json'
    metadata=json.loads(metadata_path.read_text()) if metadata_path.exists() else []
    for repair in [r for r in metadata if r['key']==key]:
        assert repair['raw_sha256']==hashlib.sha256(out.read_bytes()).hexdigest()
        item=next(r for r in data if (r['audit_id'],r['field'])==(repair['audit_id'],repair['field']))
        assert repair['metadata_field']=='correct_metric'
        assert item.get('correct_metric') is None
        assert repair['literal_review_statement'] in item['reason']
        assert quote_ok({**repair['primary_evidence'],'value':'metric identity','confident':True})
        item['correct_metric']=repair['value']
        item['parent_metadata_note']=repair['reason']
    good,failed=validate_batch(data,payload)
    assert not failed, failed
    assert len(good)==len(record['items'])
    (B/'adjudications'/f'validated_{key}.json').write_text(json.dumps(good,ensure_ascii=False,indent=2)+'\n')
    result={'key':key,'status':'valid','parse_mode':mode,'items':len(good),'failed_fields':[],
            'raw_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'validator_version':2}
    (B/'adjudications'/f'validation_{key}.json').write_text(json.dumps(result,indent=2)+'\n')
    path=F/'adjudication_status.json';statuses=json.loads(path.read_text()) if path.exists() else {}
    statuses[key]={'validation':'valid','items':len(good),'session_id':record['session_id']}
    path.write_text(json.dumps(statuses,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':main()
