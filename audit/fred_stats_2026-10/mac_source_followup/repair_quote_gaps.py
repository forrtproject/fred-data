"""Mark omitted interleaved PDF text explicitly; never change extracted values."""
import datetime
import json
import shutil
import sys
from pathlib import Path
F=Path(__file__).resolve().parent
sys.path.insert(0,str(F.parent/'scripts'))
from compare import norm,quote_ok


def proposed_quote(quote, source):
    words=norm(quote.replace('\\n','\n')).split()
    text=norm(source)
    pos=0; consumed=0; parts=[]
    while consumed<len(words):
        found=None
        for end in range(len(words),consumed,-1):
            phrase=' '.join(words[consumed:end]);at=text.find(phrase,pos)
            if at>=0 and (not parts or at-pos<1500):
                found=(end,at,phrase);break
        if not found:return None
        end,at,phrase=found
        parts.append(phrase);pos=at+len(phrase);consumed=end
        if len(parts)>8:return None
    return ' … '.join(parts)


def main():
    repairs_path=F/'quote_repairs/repairs.json'
    repairs=json.loads(repairs_path.read_text()) if repairs_path.exists() else []
    accepted=json.loads((F/'accepted_sources.json').read_text())
    changed=[];blocked=[]
    for batch in json.loads((F/'validation_queue.json').read_text()):
        rows=json.loads(Path(batch['input']).read_text());side=rows[0]['target_side']
        proof=accepted[batch['source_key']]
        for p in Path(batch['output']).glob('*.json'):
            r=json.loads(p.read_text());original=p.read_bytes();fields=[]
            for name in ['n','es','p'] + (['reported_success'] if side=='replication' else []):
                evidence=r[name] if name=='reported_success' else r[side][name]
                if evidence.get('source_path') and Path(evidence['source_path']).resolve()==Path(proof['source_pdf_path']).resolve():
                    evidence['source_path']=proof['text_path']
                    fields.append(name+':source_path')
                value=evidence['value'] or evidence.get('test_statistic')
                if not value or not evidence['confident'] or quote_ok({**evidence,'value':value}):continue
                try:
                    quote=proposed_quote(evidence['quote'],Path(evidence['source_path']).read_text())
                except (OSError,UnicodeError):
                    blocked.append([r['audit_id'],name,'unreadable or nontext source']);continue
                if quote and quote_ok({**evidence,'value':value,'quote':quote}):
                    fields.append(name);evidence['quote']=quote
                else:blocked.append([r['audit_id'],name])
            if fields:
                backup=F/'quote_repairs'/batch['batch']/p.name;backup.parent.mkdir(parents=True,exist_ok=True)
                if not backup.exists():backup.write_bytes(original)
                p.write_text(json.dumps(r,indent=2)+'\n')
                repairs.append({'audit_id':r['audit_id'],'batch':batch['batch'],'fields':fields,
                    'original_output':str(backup),'repair':'Original quoted tokens retained in order, with explicit ellipses for interleaved/omitted PDF text and literal newline decoding. At most8contiguous source fragments and1500normalised characters between fragments. Where recorded, an exact accepted PDF citation was mapped to its hash-verified canonical text from that same PDF; no source substitution. Exact-source quote check required separately at integration; no target/value/metric/bound/confidence changed.',
                    'reviewed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()});changed.append([r['audit_id'],fields])
    repairs_path.parent.mkdir(exist_ok=True);repairs_path.write_text(json.dumps(repairs,indent=2)+'\n')
    print(json.dumps({'repaired_records':changed,'remaining_unmatched_fields':blocked}))

if __name__=='__main__':main()
