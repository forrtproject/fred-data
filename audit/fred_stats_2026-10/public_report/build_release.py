"""Build public corrections from the final validated audit, without changing FReD."""
import collections,csv,hashlib,json,re,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent
sys.path.insert(0,str(B/'scripts'))
from compare import load_adjudications,metric,parsed_stat,quote_ok
from consistency import p_parts,number,analytic_n,pinterval,stat_interval
KEY=['entry_id','effect_id','fred_id']
GUARD=KEY+['ref_o','doi_o','study_o','ref_r','doi_r','url_r','study_r','description','es_type_o','es_type_r','nested_o','nested_r','pval_tails_o','pval_tails_r']
FIELDS=['n_o','es_value_o','pval_value_o','n_r','es_value_r','pval_value_r','reported_success']
def txt(x):return '' if x is None else str(x)
def write_csv(name,rows,cols=None):
 with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols or list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def build():
 manifest=json.loads((B/'run_manifest.json').read_text());progress=json.loads((B/'progress.json').read_text());parent=json.loads((B/'parent_rows.json').read_text());results={int(r['input_row_index']):r for r in csv.DictReader((B/'results.csv').open(encoding='utf-8-sig'))}
 assert hashlib.sha256((B.parents[1]/'output/FReD.xlsx').read_bytes()).hexdigest()==manifest['input_sha256']
 decisions=load_adjudications(B)
 for d in json.loads((B/'obvious_resolutions.json').read_text()):decisions[d['audit_id'],d['field']]=d
 corrections=[];patches=[];seen=set();guard_ids=set();bound_inferences=[]
 def patch(row,e,cid,column,new,role):
  old=txt(row[column]);new=txt(new)
  if old.replace('\r\n','\n').strip()==new.replace('\r\n','\n').strip():return
  key=(row['input_row_index'],column);assert key not in seen,key;seen.add(key)
  patches.append({'correction_id':cid,'audit_id':row['input_row_index'],**{k:row[k] for k in KEY},'audit_field':e['field'],'target_column':column,'old_value':old,'new_value':new,'role':role,'source_url':source_url,'source_location':d['location']})
 for e in progress['confirmed_errors']:
  aid,field=e['audit_id'],e['field'];row=parent[aid-1];d=decisions[aid,field];assert results[aid][field+'_final_verdict']=='error';assert e['correction']==d['correct_value'];assert quote_ok({**d,'value':d['correct_value'],'confident':True})
  x=json.loads((B/'extractions'/f'{aid}.json').read_text());blind=x['reported_success'] if field=='reported_success' else x['original' if field.endswith('_o') else 'replication']['n' if field.startswith('n_') else 'es' if field.startswith('es_') else 'p']
  source_url='https://doi.org/'+e['doi'] if e.get('doi') else e.get('primary_source_url') or txt(row['url_r'])
  source_ref=row['ref_o'] if field.endswith('_o') else row['ref_r'];new=e['correction'];pbound='';esmetric='';cid=f'FRED202610-{aid:04d}-{field}';before_count=len(patches)
  if field.startswith('pval'):
   fallback=d.get('correct_bound');parts=p_parts(new,fallback)
   if parts is None and fallback is None and d['verdict']=='blind_right' and number(new)==number(blind['value']):parts=p_parts(new,blind['bound'])
   if parts is None:
    # Two historical both-wrong decisions give an explicit equality in their validated quote.
    assert aid in [900,902] and field=='pval_value_r';assert re.search(r'p\s*[=\u2009 ]+\s*\.?'+('0004' if aid==900 else '45'),d['quote']);parts=p_parts(new,'e');bound_inferences.append({'audit_id':aid,'field':field,'correct_bound':'e','basis':'Explicit p equality in the already validated primary quote.','quote':d['quote']})
   assert parts;new,pbound=str(parts[0]),parts[1]
   patch(row,e,cid,field,new,'confirmed_value')
   patch(row,e,cid,'pval_type_'+field[-1],{'e':'e (=)','l':'l (<)','g':'g (>)','le':'le (<=)','ge':'ge (>=)'}[pbound],'associated_p_bound')
  else:
   if field.startswith('n_'):
    n=analytic_n(new);assert n and n.is_integer();new=str(int(n))
   patch(row,e,cid,field,new,'confirmed_value')
  if field.startswith('es_'):
   esmetric=d.get('correct_metric') or ('test statistic' if parsed_stat(new) else None)
   if not esmetric and d['verdict']=='blind_right' and number(new)==number(blind['value']):esmetric=blind['metric']
   assert esmetric and metric(esmetric)==metric(row['es_type_'+field[-1]]),(aid,field)
   patch(row,e,cid,'es_repr_'+field[-1],f"{source_url}; {d['location']}",'associated_source_locator')
  if field=='reported_success':
   patch(row,e,cid,'reported_success_quote',d['quote'],'associated_author_quote')
   patch(row,e,cid,'reported_success_quote_source',f"{source_url}; {d['location']}",'associated_author_quote_source')
  assert len(patches)>before_count,(aid,field,'No physical change for confirmed error')
  corrections.append({'correction_id':cid,'audit_id':aid,**{k:row[k] for k in KEY},'field':field,'old_value':txt(row[field]),'new_value':new,'printed_correction':e['correction'],'requested_metric':txt(row.get('es_type_'+field[-1])) if field.startswith('es_') else '', 'corrected_metric':esmetric,'old_p_bound':txt(row.get('pval_type_'+field[-1])) if field.startswith('pval') else '', 'new_p_bound':pbound,'error_kind':e['error_kind'],'resolution':results[aid][field+'_resolution'],'source_url':source_url,'source_reference':source_ref,'source_location':d['location'],'reason':d['reason']})
  guard_ids.add(aid)
 assert len(corrections)==493 and len(guard_ids)==381
 write_csv('confirmed_corrections.csv',corrections);write_csv('fred_fixes.csv',patches);write_csv('row_guard.csv',[{k:txt(parent[i-1][k]) for k in GUARD} for i in sorted(guard_ids)],GUARD)
 write_csv('field_summary.csv',[{'field':f,**{k:progress['field_counts'][f].get(k,0) for k in ['correct','error','unverified','not_comparable']},'evaluable':progress['field_counts'][f].get('correct',0)+progress['field_counts'][f].get('error',0)} for f in FIELDS])
 write_csv('availability_followups.csv',[{'audit_id':a['audit_id'],'side':a['side'],'reference':a['reference'],'reference_url':a['url'],'coded_work_url':a['coded_work_url'],'flag':a['flag'],'status':a['status'],'requested_action':a['requested_parent_action']} for a in json.loads((B/'safe_source_addendum/availability_followups.json').read_text())])
 # Recheck the original diagnostic flags against the complete physical patch.
 updated=[dict(r) for r in parent]
 for change in patches:updated[change['audit_id']-1][change['target_column']]=change['new_value']
 screen=[]
 for flag_row in csv.DictReader((B/'consistency.csv').open(encoding='utf-8-sig')):
  aid=int(flag_row['input_row_index']);row=updated[aid-1]
  for flag in filter(None,flag_row['flags'].split(';')):
   side=flag[-1];ok=None
   if flag.startswith('n_range'):
    n=analytic_n(row['n_'+side]);ok=bool(n and n>0 and n.is_integer())
   elif flag.startswith('p_range'):ok=pinterval(row['pval_value_'+side],row['pval_type_'+side]) is not None
   elif flag.startswith('r_range'):
    v=number(row['es_value_'+side]);ok=v is not None and -1<=v<=1
   elif flag.startswith('p_consistency'):
    a,_=stat_interval(row['es_value_'+side],row['es_type_'+side],row['n_'+side],row['nested_'+side],row['pval_tails_'+side]);b=pinterval(row['pval_value_'+side],row['pval_type_'+side]);ok=None if a is None or b is None else max(a[0],b[0])<=min(a[1],b[1])
   screen.append({'audit_id':aid,'flag':flag,'status':'passes_after_confirmed_patch' if ok is True else 'still_flagged' if ok is False else 'not_recomputable'})
 write_csv('screen_recheck.csv',screen)
 # Public export omits source files, private filesystem paths, raw model logs and full texts.
 summary={'audit_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'frozen_workbook_sha256':manifest['input_sha256'],'snapshot_effects':2164,'replication_works':432,'confirmed_field_errors':493,'affected_effect_rows':381,'physical_cell_updates':len(patches),'patch_roles':dict(collections.Counter(p['role'] for p in patches)),'coding_omissions':31,'exact_source_coverage':'249/255 initially missing source groups','coverage':progress['coverage'],'six_numeric_fields_complete':147,'field_counts':progress['field_counts'],'all_row_uncertainty_bounds_not_confidence_intervals':True,'bound_metadata_recovered_from_validated_equality_quotes':bound_inferences,'manual_availability_flags':4,'removals_in_patch':0,'screen_recheck':dict(collections.Counter(r['status'] for r in screen))}
 (P/'release_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
 r=P/'merge_fred_fixes.R';code=r.read_text()
 for key,file in [('FIX','fred_fixes.csv'),('GUARD','row_guard.csv')]:
  code=re.sub(r'(FRED_'+key+r'_SHA256 <- ")[^"]+(")',lambda m:m[1]+hashlib.sha256((P/file).read_bytes()).hexdigest()+m[2],code)
 r.write_text(code)
 print({k:summary[k] for k in ['confirmed_field_errors','affected_effect_rows','physical_cell_updates','patch_roles']})
if __name__=='__main__':build()
