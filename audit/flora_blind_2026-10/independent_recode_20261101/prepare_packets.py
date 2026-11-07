#!/usr/bin/env python3
"""Offline parent-only preparation. Never dispatches, codes, or modifies shared state.
Run from project root with python3. All inputs remain immutable. Reruns compare bytes.
"""
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'audit/flora_blind_2026-10'
OUT = Path(__file__).resolve().parent
E = B / 'evidence_followup'
C = E / 'private/sol_closure_20261031'
PACKETS = E / 'private/independent_recode_20261101'
META = ('work_key', 'status', 'evidence_level', 'source_url', 'retrieved_at', 'text_sha256', 'parser')
RESERVED = '6070e18087845e69'
BAD = re.compile(r'correction_proposals|expected_before|input_row_index|proposed_value|confirmed_value|parent_gate|audit conclusion|reviewer identit|prior judgment|target_index|canonical_targets', re.I)
INSTRUCTIONS = '''Read codebook.md and coding_schema.json completely. Independently code this document from scratch using only these packet files. Do not search elsewhere or inspect any parent directory. Read EVERY chunk listed in chunks.json in order with untruncated model-visible output, including references and appendices. article.txt is the exact UTF-8 source; offsets refer to its zero-based Unicode code points and UTF-8 bytes, end exclusive. Reading via a script, hashes, searches or summaries alone is not full reading. Return coding.json strictly following coding_schema.json and copying metadata.json exactly. No extra schema keys. Every nonempty quote must be one literal contiguous span of article.txt; do not repair whitespace, join sentences or normalize Unicode. Separately return reading_manifest.json documenting all model-visible chunk ranges and source SHA256, and quote_spans.json giving field paths, literal quotes, character/byte start/end and quote SHA256. Discover every target yourself under the codebook. For a collection or source with multiple clearly labeled reports, preserve report boundaries and identify which report supports each target; do not pool separate reports as a single experiment. Never claim visual coverage of images absent from the supplied text. Record actual source limits in the schema reasoning. Do not delegate or use external APIs. Output only in the output location supplied by the dispatcher, outside this immutable packet.
'''

def read(p):
    return json.loads(Path(p).read_bytes().decode('utf-8-sig'))
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def path(s):
    p = Path(s)
    return p if p.is_absolute() else ROOT / p

def save(p, raw, immutable=False):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and p.read_bytes() == raw:
        return
    if immutable and p.exists():
        raise ValueError('Refuse to overwrite existing packet file: ' + str(p))
    p.write_bytes(raw)

def js(p, value, immutable=False):
    save(p, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode(), immutable)

def check_source(p, expected):
    result = {'path': str(p), 'exists': p.is_file(), 'expected_sha256': expected}
    if not p.is_file():
        result['limit'] = 'Registered primary source file missing'
        return result, None
    raw = p.read_bytes()
    result.update(raw_sha256=sha(raw), utf8_bytes=len(raw))
    if not expected or sha(raw) != expected:
        result['limit'] = 'Registered hash absent or differs from actual source bytes'
        return result, None
    try:
        txt = raw.decode('utf-8')
    except UnicodeDecodeError:
        result['limit'] = 'Primary extraction is not strict UTF-8'
        return result, None
    result['unicode_characters'] = len(txt)
    if not txt.strip():
        result['limit'] = 'Registered source is empty'
        return result, None
    # Technical contamination screen only; not a scientific completeness judgment.
    matches = sorted(set(m.group() for m in BAD.finditer(txt)))
    if matches:
        result.update(limit='Source contains parent/audit marker; cannot certify sanitized primary body', markers=matches)
        return result, None
    return result, raw

def strict_result(packet, result):
    """Parent validator; never runs a coder. Reject schema extras and nonliteral spans."""
    import jsonschema
    schema = read(packet / 'coding_schema.json')
    schema['additionalProperties'] = False
    schema['properties']['targets']['items']['additionalProperties'] = False
    jsonschema.validate(result, schema)
    meta = read(packet / 'metadata.json')
    assert {k: result[k] for k in META} == meta
    raw = (packet / 'article.txt').read_bytes()
    assert sha(raw) == meta['text_sha256']
    txt = raw.decode('utf-8')
    spans = []
    def visit(v, prefix='$'):
        if isinstance(v, dict):
            for k, val in v.items():
                key = prefix + '.' + k
                if (k.endswith('_quote') or k == 'record_type_quote') and val:
                    start = txt.find(val)
                    assert start >= 0, key + ': nonliteral quote'
                    end = start + len(val)
                    spans.append(dict(field=key, character_start=start, character_end=end,
                                      utf8_byte_start=len(txt[:start].encode()), utf8_byte_end=len(txt[:end].encode()), quote_sha256=sha(val.encode())))
                visit(val, key)
        elif isinstance(v, list):
            for i, val in enumerate(v): visit(val, prefix + '[' + str(i) + ']')
    visit(result)
    return spans

def reading_coverage(packet, manifest):
    raw = (packet / 'article.txt').read_bytes()
    n = len(raw.decode('utf-8'))
    assert manifest['text_sha256'] == sha(raw), 'Reading manifest source mismatch'
    ranges = []
    for interval in manifest['model_visible_character_ranges']:
        if isinstance(interval, dict):
            assert set(interval) == {'character_start', 'character_end'}, 'Invalid named reading range'
            start, end = interval['character_start'], interval['character_end']
        else:
            assert isinstance(interval, (list, tuple)) and len(interval) == 2, 'Invalid reading range'
            start, end = interval
        assert type(start) is int and type(end) is int and 0 <= start < end <= n
        ranges.append([start, end])
    ranges.sort()
    merged = []
    for start, end in ranges:
        assert type(start) is int and type(end) is int and 0 <= start < end <= n
        if merged and start <= merged[-1][1]: merged[-1][1] = max(end, merged[-1][1])
        else: merged.append([start, end])
    assert merged == [[0, n]], 'Incomplete declared model-visible reading coverage'
    assert manifest['full_source_read'] is True
    assert manifest.get('untruncated_tool_evidence'), 'Missing model-visible tool-output receipts'
    return {'declared_complete_union': True, 'requires_parent_tool_receipt_inspection': True}

def prepare():
    assert not PACKETS.is_symlink(), 'Active packets must remain on local SSD'
    proposals = read(B / 'handoff/correction_proposals.json')
    manifest = {int(r['input_row_index']): r for r in csv.DictReader((B / 'manifest.csv').open(encoding='utf-8-sig'))}
    changes = proposals['changes']
    cohort = collections.defaultdict(list)
    for x in changes:
        row = int(x['input_row_index'])
        cohort[manifest[row]['file_key']].append({'input_row_index': row, 'field': x['field']})
    assert len(changes) == 562 and len({x['input_row_index'] for x in changes}) == 515 and len(cohort) == 469
    works = {r['file_key']: r['work_key'] for r in manifest.values()}
    work_to_fk = {v.rstrip('/').lower(): k for k, v in works.items()}
    documents = []
    queue = []
    accesses = read(E / 'acquisition/parent_verification.json')['works']
    promotions = read(E / 'integration/source_promotions.json')['promotions']
    promoted = {v['file_key']: v for v in promotions}
    approved = read(E / 'additional_reports/approved_sources.json')['reports']
    # Parent ledgers only; preserve relationships and historical attempts without exposing them.
    input_files = [B/'handoff/correction_proposals.json', B/'manifest.csv', E/'additional_reports/approved_sources.json',
                   E/'integration/source_promotions.json', E/'acquisition/parent_verification.json',
                   B/'handoff/current_source_decisions.json', B/'publication/completed_report_reviews_20261101.json',
                   B/'publication/record_scope_review_20261101.json', B/'blinding_incidents.json']
    by_identity = {}
    def add(fk, p, metadata, receipt, role, priority, coding=None, genuine=False, active=True):
        if fk not in cohort: return None
        check, raw = check_source(p, metadata.get('text_sha256'))
        key = (fk, check.get('raw_sha256'), str(p) if not raw else '')
        if key in by_identity:
            doc = by_identity[key]
            doc['source_receipts'].append(receipt)
            doc['source_paths'].append(str(p))
            if priority > doc['priority']:
                doc.update(priority=priority, role=role)
            if coding and genuine and raw: reusable(doc, coding, metadata['text_sha256'])
            return doc
        doc = dict(parent_file_key=fk, parent_work_key=works[fk], source_checks=check, source_paths=[str(p)],
                   source_receipts=[receipt], role=role, priority=priority, active=active,
                   metadata={k:metadata.get(k) for k in META}, prior_blind_sol=[], status='ready' if raw else 'source_preparation_limit')
        by_identity[key] = doc
        documents.append(doc)
        if raw and coding and genuine: reusable(doc, coding, metadata['text_sha256'])
        if not raw: queue.append({'parent_file_key':fk,'source_path':str(p),'source_check':check,'required_action':check['limit']})
        return doc
    def reusable(doc, coding, expected):
        cp = path(coding)
        if not cp.is_file(): return
        # Read metadata only; prior target values never enter packets.
        data = read(cp)
        if data.get('text_sha256') == expected and data.get('status') == 'done':
            entry = {'path':str(cp),'coding_sha256':sha(cp.read_bytes()),'exact_source_sha256':expected,
                     'scope':'whole document; parent must check complete-read receipt before comparison', 'status':'exact_version_candidate_requires_parent_read_receipt'}
            if entry not in doc['prior_blind_sol']:doc['prior_blind_sol'].append(entry)
    original_blind_tasks = collections.defaultdict(list)
    for line in (B/'tasks.jsonl').read_text().splitlines():
        task=json.loads(line)
        if task.get('model')=='gpt-6.1-sol' and task.get('batch') and task.get('prompt_path'):
            for fk in task.get('files',[]): original_blind_tasks[fk].append(task)
    input_files.append(B/'tasks.jsonl')
    base_docs = {}
    for fk in sorted(cohort):
        cp = B/'codings'/f'{fk}.json'
        metadata = read(cp) if cp.exists() else {}
        base_docs[fk] = add(fk,B/'texts'/f'{fk}.txt',metadata,{'registry':str(cp),'source_promotion':promoted.get(fk)},'registered_base_document',10,
                            coding=cp, genuine=bool(original_blind_tasks.get(fk)) and fk not in promoted)
        base_docs[fk]['identity_registry_check'] = {'coding_work_key_matches_manifest':metadata.get('work_key')==works[fk], 'manifest_file_key_matches_coding_filename':cp.stem==fk}
        assert metadata.get('work_key') == works[fk], 'Base source identity registration mismatch: '+fk
        base_docs[fk]['original_blind_task_candidates'] = original_blind_tasks.get(fk,[])
        # Existing primary registry is evidence of source level, not independent full-reading evidence.
        if metadata.get('evidence_level') not in ('full_text','abstract') or metadata.get('status') != 'done':
            base_docs[fk]['status'] = 'source_preparation_limit'
            queue.append({'parent_file_key':fk,'source_path':str(B/'texts'/f'{fk}.txt'), 'source_check':base_docs[fk]['source_checks'],
                          'required_action':'No usable completed primary-source registration at full_text or abstract level', 'metadata_status':metadata.get('status')})
    for r in approved:
        fk = r['collection_file_key']
        if fk not in cohort:continue
        cp = path(r['blind_coding_path']) if r.get('blind_coding_path') else None
        md = read(cp) if cp and cp.exists() else {}
        md.update({k:r[k] for k in ('text_sha256','evidence_level','source_url') if k in r})
        md['status']='done'
        add(fk,path(r['text_path']),md,{'registry':str(E/'additional_reports/approved_sources.json'),'report':r},
            'individual_primary_report' if r.get('input_row_index') else 'verified_source_version_or_supplement',30,cp,False)
    # The final sanitized ledgers establish source approval and genuinely blind provenance separately.
    for lp in sorted(C.glob('sanitized_*/ledger.json')):
        ledger=read(lp); mp=lp.parent/'metadata.json'
        if not mp.exists():continue
        md=read(mp); row=ledger.get('parent_row_binding')
        fk=manifest[int(row)]['file_key'] if row is not None else work_to_fk.get(str(md.get('work_key','')).rstrip('/').lower())
        if fk not in cohort:continue
        active=not str(ledger.get('status','')).startswith('superseded')
        if active and not ('validated' in str(ledger.get('status','')) or ledger.get('schema_passed')):
            queue.append({'parent_file_key':fk,'source_path':str(lp.parent/'article.txt'),'required_action':'Sanitized ledger does not establish source approval','ledger':ledger})
            continue
        input_files.append(lp)
        doc=add(fk,lp.parent/'article.txt',md,{'registry':str(lp),'ledger':ledger},
                'individual_primary_report' if 'student_doc' in lp.parent.name else 'final_verified_document_version',50,
                lp.parent/'coding.json',ledger.get('model','').endswith('sol'),active)
        if doc and not active:doc['status']='superseded_preserved_not_dispatched'
    # Recovered completed reports take precedence over their prospective base drafts.
    decisions=read(B/'handoff/current_source_decisions.json')['decisions']
    reviews={r['file_key']:r for r in read(B/'publication/completed_report_reviews_20261101.json')['reviews']}
    for d in decisions:
        fk=d['file_key']; s=d['source_read_manifest']; review=reviews[fk]
        binding=review['report_binding']
        md={'text_sha256':s['sha256'],'status':'done','evidence_level':'full_text','source_url':binding['report_links'][0],
            'retrieved_at':None,'parser':'pdftotext -layout; complete primary report including appendices'}
        add(fk,path(s['source_path']),md,{'decision_registry':str(B/'handoff/current_source_decisions.json'),
            'identity_receipt':str(B/'publication/completed_report_reviews_20261101.json'),'report_binding':binding},'completed_report_superseding_plan',100)
    # Existing primary-report labels provide lossless technical boundaries, not target selections.
    # Split EVERY report, including ones unrelated to proposals; preserve all parent bytes.
    collection_splits=[]
    for base in list(documents):
        if base['priority'] != 10 or base['status'] != 'ready': continue
        raw=Path(base['source_paths'][0]).read_bytes(); text=raw.decode('utf-8')
        markers=list(re.finditer(r'(?m)^PRIMARY PROJECT REPORT[^\r\n]*',text))
        if len(markers)<2: continue
        bounds=[0]+[m.start() for m in markers]+[len(text)]
        ranges=list(zip(bounds,bounds[1:])); assert all(a<z for a,z in ranges)
        rebuilt=[]
        for index,(start,end) in enumerate(ranges):
            body=text[start:end].encode(); rebuilt.append(body)
            metadata=dict(base['metadata']); metadata.update(text_sha256=sha(body),parser='Lossless UTF-8 character-range extraction at existing primary document boundaries')
            if index:
                # Retrieval metadata is a technical header only; preserve it verbatim in article text.
                head=text[start:min(end,start+1500)]
                url=re.search(r'(?m)^(?:SOURCE URL|SOURCE):[ \t]*(https?://[^\r\n]+)',head)
                if url: metadata['source_url']=url.group(1).strip()
            derived={'parent_file_key':base['parent_file_key'],'parent_work_key':base['parent_work_key'],
                     'source_paths':list(base['source_paths']), 'source_character_range':[start,end],
                     'source_receipts':[{'parent_source_checks':base['source_checks'],
                         'boundary_basis':'All explicit PRIMARY PROJECT REPORT labels in registered complete collection, no target-based selection',
                         'component_index':index,'character_start':start,'character_end':end}],
                     'source_checks':{'path':base['source_paths'][0],'exists':True,'expected_sha256':sha(body),'raw_sha256':sha(body),
                                      'utf8_bytes':len(body),'unicode_characters':end-start},
                     'role':'individual_primary_report' if index else 'collection_overview_and_labeled_supplements',
                     'priority':40,'active':True,'metadata':metadata,'prior_blind_sol':[],'status':'ready'}
            # A whole-collection result is never reused as coding of a sliced individual report.
            documents.append(derived)
        assert b''.join(rebuilt)==raw
        base.update(active=False,status='collection_container_preserved_components_dispatched')
        collection_splits.append({'parent_file_key':base['parent_file_key'],'parent_raw_sha256':sha(raw),
                                  'individual_primary_reports':len(markers),'overview_units':1,
                                  'exact_lossless_partition':True,'ranges':ranges})
    # Explicit source-level limits do not become scientific verdicts or administrative holds.
    for doc in documents:
        if doc['metadata'].get('evidence_level') == 'abstract':
            queue.append({'parent_file_key':doc['parent_file_key'], 'source_path':doc['source_paths'][0],
                          'source_check':doc['source_checks'], 'kind':'full_report_completeness_limit',
                          'required_action':'Only registered primary abstract bytes are available in this version; full report completeness is not established. Packet is ready for coding at abstract evidence level only.',
                          'existing_access_verification':accesses.get(doc['parent_file_key']),
                          'attempt_records':str(E/'acquisition/results.jsonl')})
        if re.search(r'image.only|image separate|not transcribed',str(doc['metadata'].get('parser')),re.I):
            queue.append({'parent_file_key':doc['parent_file_key'],'source_path':doc['source_paths'][0],
                          'source_check':doc['source_checks'],'kind':'visual_supplement_limit',
                          'required_action':'Registered extraction does not represent all embedded visual output. Do not claim complete visual-source coverage; preserve original visual receipts for parent verification.'})
    conflict_path=E/'integration/abstract_delta_parent_dispositions.json'
    input_files.append(conflict_path)
    conflicts=read(conflict_path)['identity_or_version_limits']
    for item in conflicts:
        if item['file_key'] in cohort:
            queue.append({'parent_file_key':item['file_key'],'kind':'registered_identity_or_version_limit',
                          'existing_identity_verification':item,'required_action':'Resolve exact report identity using preserved primary registrations; no scientific verdict inferred.'})
    historical_versions=[]
    for promotion in promotions:
        fk=promotion['file_key']
        if fk in cohort:
            oldpath=E/'private/old_texts'/f'{fk}.txt'
            check,_=check_source(oldpath,promotion.get('old_text_sha256'))
            historical_versions.append({'parent_file_key':fk,'relationship':'superseded_source_preserved_not_dispatched',
                                        'source_check':check,'promotion_receipt':promotion})
    # Record the inspected completed-report receipts even when their rows are outside this finite cohort.
    completed_scope=[{'parent_file_key':d['file_key'],'in_frozen_cohort':d['file_key'] in cohort,
                      'source_read_manifest':d['source_read_manifest']} for d in decisions]
    # Durable allocation: reserve document_0001 and retain any IDs from our earlier preparation.
    old=read(OUT/'source_inventory.json') if (OUT/'source_inventory.json').exists() else {}
    ids={(x['parent_file_key'],x['source_checks'].get('raw_sha256')):x['document_id'] for x in old.get('documents',[])}
    used={1}|{int(x.split('_')[1]) for x in ids.values()}
    nextid=max(used)+1
    for doc in documents:
        fk=doc['parent_file_key']; digest=doc['source_checks'].get('raw_sha256')
        if fk==RESERVED:
            assert digest==base_docs[fk]['source_checks']['raw_sha256']
            doc.update(document_id='document_0001',status='reserved_running_parent_owned')
        elif (fk,digest) in ids:doc['document_id']=ids[fk,digest]
        else:
            doc['document_id']=f'document_{nextid:04d}'; nextid+=1
        doc['packet_path']=str(PACKETS/doc['document_id'])
        doc['sol_comparison']='exact_version_candidate_parent_receipt_required' if doc['prior_blind_sol'] else 'fresh_blind_Sol_required'
    # Preferred complete source supersedes plans; collection overviews remain separate from individual reports.
    for fk in cohort:
        current=[d for d in documents if d['parent_file_key']==fk and d['active'] and d['status'] in ('ready','reserved_running_parent_owned')]
        high=max((d['priority'] for d in current),default=0)
        for doc in current:
            doc['dispatch_role']='current' if doc['priority']==high or doc['role']=='individual_primary_report' else 'separate_verified_version_or_collection_context'
            if high==100 and doc['priority']<100:
                doc.update(dispatch_role='superseded_plan_history',active=False)
    for doc in documents:
        if doc['status']!='ready' or not doc['active']:continue
        dest=Path(doc['packet_path']); raw=Path(doc['source_paths'][0]).read_bytes(); txt=raw.decode('utf-8')
        if 'source_character_range' in doc:
            a,z=doc['source_character_range'];txt=txt[a:z];raw=txt.encode()
        md={k:doc['metadata'].get(k) for k in META};md.update(work_key=doc['document_id'],status='done',text_sha256=sha(raw))
        # Free-form parser metadata is omitted if it contains parent/audit vocabulary.
        if md.get('parser') and (BAD.search(md['parser']) or re.search(r'blind|audit|parent|coding|verdict|target',md['parser'],re.I)):
            md['parser']=None
        assert set(md)==set(META) and not BAD.search(json.dumps(md))
        save(dest/'article.txt',raw,True);js(dest/'metadata.json',md,True)
        for name in ('codebook.md','coding_schema.json'):save(dest/name,(B/name).read_bytes(),True)
        save(dest/'instructions.txt',INSTRUCTIONS.encode(),True)
        chunks=[]
        for i,start in enumerate(range(0,len(txt),12000)):
            end=min(len(txt),start+12000); data=txt[start:end].encode(); name=f'chunks/chunk_{i+1:05d}.txt'
            save(dest/name,data,True)
            chunks.append({'file':name,'character_start':start,'character_end':end,'sha256':sha(data)})
        js(dest/'chunks.json',{'text_sha256':sha(raw),'unicode_characters':len(txt),'chunks':chunks},True)
        assert b''.join((dest/x['file']).read_bytes() for x in chunks)==raw
        assert read(dest/'metadata.json')['text_sha256']==sha((dest/'article.txt').read_bytes())
        doc['packet_validation']={'hash':True,'exact_chunk_reconstruction':True,'metadata_allowlist':True,'generic_instructions':True,
                                  'chunks':len(chunks),'full_read_required':True,'strict_schema_and_literal_validator':str(OUT/'prepare_packets.py')}
    # Check reserved packet read-only, no adding codebook/schema/chunks or changing contents.
    reserved=PACKETS/'document_0001'; reserved_check={}
    if reserved.exists():
        rmd=read(reserved/'metadata.json'); rr=(reserved/'article.txt').read_bytes()
        reserved_check={'metadata_work_key':rmd.get('work_key'),'raw_sha256':sha(rr),'matches_base':sha(rr)==base_docs[RESERVED]['source_checks']['raw_sha256'],
                        'files':[x.name for x in reserved.iterdir()]}
        assert reserved_check['matches_base']
    works_out=[]
    for fk in sorted(cohort):
        ds=[d for d in documents if d['parent_file_key']==fk]
        ready=[d['document_id'] for d in ds if d['status'] in ('ready','reserved_running_parent_owned') and d['active']]
        works_out.append({'parent_file_key':fk,'parent_work_key':works[fk],'frozen_row_field_mapping':cohort[fk],
                          'document_ids':[d['document_id'] for d in ds], 'ready_document_ids':ready,
                          'status':'represented_in_ready_packets' if ready else 'substantive_source_preparation_limit',
                          'existing_acquisition_identity_checks':accesses.get(fk),
                          'existing_access_attempts_preserved_at':[str(E/'acquisition/results.jsonl'), str(E/'acquisition/parent_verification.json')],
                          'limits':[q for q in queue if q['parent_file_key']==fk]})
    # Deterministic 1–3 document groups; long documents alone; no truncation or omission.
    groups=[]; pending=[]; chars=0
    def flush():
        nonlocal pending,chars
        if pending:
            groups.append({'group_id':f'group_{len(groups)+1:04d}','document_ids':pending,'source_characters':chars,
                           'requires_full_untruncated_reading':True,'long_document_alone':chars>180000,
                           'model':'claude-opus-5-5','status':'prepared_not_dispatched'})
        pending=[];chars=0
    for doc in documents:
        if doc['status']!='ready' or not doc['active']:continue
        n=doc['source_checks']['unicode_characters']
        if pending and (len(pending)==3 or chars+n>180000):flush()
        pending.append(doc['document_id']);chars+=n
        if n>180000:flush()
    flush()
    dispatched=[k for g in groups for k in g['document_ids']]
    assert len(dispatched)==len(set(dispatched)) and 'document_0001' not in dispatched
    expected={d['document_id'] for d in documents if d['status']=='ready' and d['active']}
    assert set(dispatched)==expected
    assert all(1<=len(g['document_ids'])<=3 and (g['source_characters']<=180000 or len(g['document_ids'])==1) for g in groups)
    assert {w['parent_file_key'] for w in works_out}==set(cohort)
    summary={'proposal_fields':562,'frozen_rows':515,'cohort_works':469,'works_with_ready_packets':sum(bool(w['ready_document_ids']) for w in works_out),
             'works_with_source_preparation_limits_only':sum(not w['ready_document_ids'] for w in works_out),
             'new_ready_packets':len(expected),'reserved_running_packets':1,'preserved_document_versions':len(documents),
             'dispatch_groups':len(groups),'long_document_groups':sum(g['long_document_alone'] for g in groups),
             'source_verification_queue_items':len(queue),'abstract_document_versions':sum(d['metadata'].get('evidence_level')=='abstract' for d in documents),'exact_version_Sol_candidates':sum(bool(d['prior_blind_sol']) for d in documents),'fresh_blind_Sol_required_documents':sum(not d['prior_blind_sol'] for d in documents),'active_exact_version_Sol_candidates':sum(bool(d['prior_blind_sol']) for d in documents if d['document_id'] in expected),'active_fresh_blind_Sol_required':sum(not d['prior_blind_sol'] for d in documents if d['document_id'] in expected),'exact_cohort_completeness':True,'incremental_API_spend_USD':0}
    inventory={'parent_only':True,'summary':summary,'input_receipts':[{'path':str(p),'sha256':sha(p.read_bytes())} for p in input_files],
               'source_selection_policy':'Use exact verified source bytes; keep distinct reports and versions separate; completed reports precede superseded plans. Source levels are inherited from approvals, not inferred from length. No scientific coding performed.',
               'works':works_out,'documents':documents,'historical_source_versions':historical_versions,'completed_report_scope_reconciliation':completed_scope,'registered_identity_version_limits':conflicts,'collection_partitions':collection_splits,'source_verification_queue':queue,'reserved_packet_readonly_check':reserved_check}
    # Remove sanitized metadata from parent documents only after constructing packets? Retain for provenance.
    js(OUT/'source_inventory.json',inventory)
    js(OUT/'dispatch_plan.json',{'parent_only':True,'summary':summary,'reservation':{'document_id':'document_0001','parent_file_key':RESERVED,
        'status':'already_running_parent_owned_do_not_redispatch','packet_readonly_check':reserved_check},'groups':groups,
        'rules':['Every child must be fresh and receive only its packet directories and separate output paths.',
                 'Parent dispatch owns provider options, concurrency, scientific comparison and shared state.',
                 'No dispatch performed by this preparation script. Never give this plan or inventory to a blind coder.',
                 'Prior blind Sol matches are exact source-version candidates only; parent must establish complete-reading receipts, otherwise fresh blind Sol required.',
                 'Schema and literal spans validate separately from scientific adjudication. Run prepare_packets.py --validate PACKET RESULT.',
                 'Long sources are never omitted or truncated. Read all 12000-character chunks and document their complete union.']})
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--validate',nargs=2,metavar=('PACKET','RESULT')); args=parser.parse_args()
    if args.validate:
        packet=path(args.validate[0]); result_path=path(args.validate[1])
        print(json.dumps({'literal_spans':strict_result(packet,read(result_path)), 'reading_coverage':reading_coverage(packet,read(result_path.parent/'reading_manifest.json'))},indent=2))
    else:prepare()
