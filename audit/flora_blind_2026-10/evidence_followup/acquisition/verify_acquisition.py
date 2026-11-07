#!/usr/bin/env python3
"""Offline acquisition guard review; append immutable corrections, never code science.
Run after acquire.py exits. Latest record per file_key supersedes earlier proposals.
"""
import collections, json, pathlib, os, sys
sys.dont_write_bytecode=True
from acquire import BASE,HERE,PRIVATE,Page,assess,jats_structure,digest,dump,UTC,VERSION

def main():
    source=HERE/'results.jsonl';lines=source.read_text().splitlines();latest={}
    for l in lines:
        if l.strip():
            r=json.loads(l);latest[r['file_key']]=r
    works={w['file_key']:w for w in json.loads((HERE/'works.json').read_text())}
    corrections=[]
    for key,r in latest.items():
        changes=[];revised=[]
        for old in r.get('candidates',[]):
            c=dict(old);path=BASE/c['filepath'];txt=BASE/c['text_filepath']
            assert path.is_file() and txt.is_file(),key
            assert digest(path.read_bytes())==c['sha256'],key
            kind=path.suffix.lstrip('.');headings=[]
            if kind in ('html','xml'):
                p=Page();p.feed(path.read_bytes().decode(errors='replace'));headings=p.headings
            check=assess(works[key],txt.read_text(),kind,c['url'],headings,jats_structure(path.read_bytes()) if kind=='xml' else None)
            if old['status']!=check['status']:changes.append(dict(filepath=c['filepath'],before=old['status'],after=check['status']))
            c.update(check);revised.append(c)
        logs=PRIVATE/key/r.get('source_attempt_id',r['attempt_id'])
        artifacts=[dict(filepath=str(p.relative_to(BASE)),sha256=digest(p.read_bytes()),parser='intact skill-cache artifact; see candidate verification or independently inspect',parent_verification_required=True)
                   for p in sorted((logs/'skill_cache').rglob('*')) if p.is_file() and p.suffix.lower() in ('.pdf','.html','.xml','.docx','.txt')]
        artifacts_changed=artifacts!=r.get('additional_private_artifacts',[])
        if not changes and not artifacts_changed:continue
        r=dict(r);previous=digest(json.dumps(r,sort_keys=True).encode())
        r.update(record_type='acquisition_guard_correction',supersedes_record_sha256=previous,
                 source_attempt_id=r['attempt_id'],attempt_id=r['attempt_id']+'.guard-review',
                 guard_reviewed_at=UTC(),guard_version=VERSION,guard_changes=changes,candidates=revised,additional_private_artifacts=artifacts)
        r['status']='proposed_full_text' if any(c['status']=='proposed_full_text' for c in revised) else 'partial' if any(c['status']=='partial' for c in revised) else 'wrong_identity' if revised else 'not_found'
        cp=PRIVATE/key/r['source_attempt_id']/'guard_correction.json'
        if cp.exists():
            existing=json.loads(cp.read_text());assert existing['supersedes_record_sha256']==previous,'Refusing to alter immutable correction'
            r=existing
        else:
            with cp.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2)
        with source.open('a') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        latest[key]=r;corrections.append(key)
    progress=json.loads((HERE/'progress.json').read_text())
    progress.update(updated_at=UTC(),completed_work_records=len(latest),remaining_works=len(works)-len(latest),
                    counts=dict(collections.Counter(r['status'] for r in latest.values())),
                    result_records=sum(1 for l in source.read_text().splitlines() if l.strip()),
                    guard_corrections_added=len(corrections),guard_corrections_total=sum(json.loads(l).get('record_type')=='acquisition_guard_correction' for l in source.read_text().splitlines() if l.strip()),guard_version=VERSION,offline_guard_review_complete=True,
                    state='acquisition_queue_complete' if len(latest)==len(works) else progress['state'],
                    queue_complete=len(latest)==len(works),scientific_verification_complete=False,
                    result_semantics='Immutable JSONL: latest record per file_key is current acquisition proposal; scientific verification remains required.')
    dump(HERE/'progress.json',progress)
    print(json.dumps(dict(completed=len(latest),counts=progress['counts'],corrections=len(corrections))))
if __name__=='__main__':main()
