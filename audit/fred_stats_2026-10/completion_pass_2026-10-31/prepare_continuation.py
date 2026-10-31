"""Prepare fresh source-grouped blind inputs; never redispatch the pilot sources."""
import argparse,collections,copy,csv,hashlib,json
from pathlib import Path
F=Path(__file__).resolve().parent;B=F.parent
FIELDS=['n_o','es_value_o','pval_value_o','n_r','es_value_r','pval_value_r','reported_success']
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--batch',default='continuation_01');parser.add_argument('--limit',type=int,default=12);args=parser.parse_args()
 assert args.batch.startswith('continuation_') and args.limit>0
 with (B/'results.csv').open(encoding='utf-8-sig') as stream:results={int(r['input_row_index']):r for r in csv.DictReader(stream)}
 neutral={}
 for p in sorted((B/'inputs').glob('*.json')):
  for r in json.loads(p.read_text()):neutral.setdefault(r['audit_id'],r)
 provenance=json.loads((B/'source_provenance.json').read_text());bydoi=collections.defaultdict(list)
 for path,info in provenance.items():
  if info.get('work_doi'):bydoi[str(info['work_doi']).lower()].append(path)
 existing=json.loads((F/('work_queue.json' if (F/'work_queue.json').exists() else 'pilot_queue.json')).read_text());pilot={(g['source'],g['side']) for g in existing if g.get('phase')!=args.batch}
 gates={}
 with Path('/home/lukas/.cache/fred-audit-coverage-diagnostic/remaining_fields.csv').open() as stream:
  for r in csv.DictReader(stream):gates[int(r['audit_id']),r['field']]=r['gate']
 pdfs={}
 manifests=[Path('/home/lukas/work/fred-mac-recovery-20261030/final_box_source_manifest.json'),Path('/home/lukas/work/fred-mac-recovery-20261030/continuation-1201/final_box_source_manifest.json'),Path('/home/lukas/work/fred-mac-recovery-20261030/drive-check/final_box_source_manifest.json')]
 for manifest in manifests:
  for entry in json.loads(manifest.read_text())['sources'].values():
   doi=str(entry.get('doi') or '').lower();artifact=entry.get('artifact_path')
   if doi and artifact:pdfs[doi]=(artifact,entry.get('source_version','Primary source'))
 groups={};unavailable=[]
 for aid,r in neutral.items():
  if aid not in results:continue
  for side,short in [('original','o'),('replication','r')]:
   doi=str(r.get('doi_'+short) or '').strip().lower();source=doi or str(r.get('url_r') or '')
   if not source or (source,side) in pilot:continue
   fields=[f for f in FIELDS if (f.endswith('_'+short) or f=='reported_success' and short=='r') and results[aid][f+'_final_verdict'] not in ['correct','error']]
   if not fields:continue
   candidates=[]
   p=r.get('text_paths',{}).get(short)
   if p and (not doi or str(provenance.get(p,{}).get('work_doi','')).lower()==doi):candidates.append(p)
   candidates+=bydoi.get(doi,[])
   candidates=[p for p in dict.fromkeys(candidates) if Path(p).is_file()]
   if not candidates:unavailable.append({'audit_id':aid,'side':side,'source':source});continue
   sourcepath=candidates[0];key=hashlib.sha256((source+'|'+side).encode()).hexdigest()[:16];g=groups.setdefault(key,{'key':key,'source':source,'side':side,'rows':[],'near_complete_rows':0,'literal_evidence_fields':0})
   item={k:v for k,v in r.items() if k in ['ref_o','ref_r','doi_o','doi_r','url_r','study_o','study_r','description','es_type_o','es_type_r','locators_o','locators_r']};item.update(audit_id=aid,target_side=side,unfinished_fields=fields,text_paths={short:sourcepath},source_pdf_path=pdfs.get(doi,(None,None))[0],source_version_note=pdfs.get(doi,(None,'Canonical primary source provenance; independently inspect document identity on use.'))[1])
   g['rows'].append(item);g['near_complete_rows']+=sum(results[aid][f+'_final_verdict'] in ['correct','error'] for f in FIELDS)==6;g['literal_evidence_fields']+=sum('fails literal evidence' in gates.get((aid,f),'') for f in fields)
 queue=sorted(groups.values(),key=lambda g:(-g['near_complete_rows'],-g['literal_evidence_fields'],len(g['rows']),g['key']))
 # Keep each source together. Larger sources are retained for a later deliberate whole-source assignment.
 eligible=[g for g in queue if len(g['rows'])<=30];selected=eligible[:args.limit]
 out=F/args.batch;(out/'inputs').mkdir(parents=True,exist_ok=True);(out/'outputs').mkdir(exist_ok=True)
 for g in selected:
  p=out/'inputs'/f"{g['key']}.json";encoded=json.dumps(g['rows'],indent=2,ensure_ascii=False)+'\n'
  if p.exists() and any((F/'tasks'/f"{g['key']}.json").exists() for g in selected):assert p.read_text()==encoded,'Inputs changed after dispatch'
  else:p.write_text(encoded)
  g.update(input=str(p),output=str(out/'outputs'/g['key']),audit_ids=[r['audit_id'] for r in g['rows']],unfinished_fields=sum(len(r['unfinished_fields']) for r in g['rows']),source_text=g['rows'][0]['text_paths'][g['side'][0]],all_source_rows=len(g['rows']),status='queued');del g['rows']
 (out/'queue.json').write_text(json.dumps(selected,indent=2)+'\n');(out/'selection.json').write_text(json.dumps({'candidate_source_groups':len(queue),'chosen_source_groups':len(selected),'oversized_source_groups_deferred':sum(len(g.get('rows',[]))>30 for g in queue),'unavailable_rows':unavailable,'rule':'Exclude every previously assigned source-side; all unfinished fields for every row in chosen source-side, prioritise rows one field short then literal evidence failures; at most 30 rows/source and a bounded source count selected by --limit. This prepares inputs only; no tasks launched.'},indent=2)+'\n');print(json.dumps({'sources':len(selected),'rows':sum(len(g['audit_ids']) for g in selected),'fields':sum(g['unfinished_fields'] for g in selected)}))
if __name__=='__main__':main()
