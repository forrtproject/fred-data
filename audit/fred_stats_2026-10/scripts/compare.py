import json,csv,re,collections,datetime,hashlib,unicodedata
from functools import lru_cache
from pathlib import Path
from consistency import number,analytic_n,rounding,pinterval,p_parts
from schema import validate
from protect_enrichment import preserve_completed
B=Path(__file__).resolve().parents[1]
SOURCE_PROVENANCE=json.loads((B/'source_provenance.json').read_text()) if (B/'source_provenance.json').exists() else {}
FIELDS=['n_o','es_value_o','pval_value_o','n_r','es_value_r','pval_value_r','reported_success']
def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(s)).replace('−','-').replace('“','"').replace('”','"').replace('’',"'")).strip()
@lru_cache(maxsize=2048)
def source_text(path,mtime_ns):return norm(Path(path).read_text())
def quote_ok(e):
 if e.get('value') is None or not e.get('confident') or not e.get('quote') or not e.get('location'):return False
 p=Path(e.get('source_path',''))
 try:
  if not p.resolve().is_relative_to((B/'texts').resolve()):return False
  text=source_text(str(p),p.stat().st_mtime_ns);quote=norm(e['quote'])
  if quote in text:return True
  parts=[z.strip() for z in re.split(r'\[?\.{3}\]?|…',quote) if z.strip()]
  pos=0
  for z in parts:
   idx=text.find(z,pos)
   if idx<0:return False
   pos=idx+len(z)
  return bool(parts)
 except (OSError,ValueError):return False
def metric(s):
 s=str(s or '').strip().lower().replace('’',"'")
 aliases={"cohen's d":'d','pearson r':'r','pearson correlation':'r',"hedges g":"hedges' g",'partial eta squared':'etasq (partial)','partial eta-squared':'etasq (partial)','ηp2':'etasq (partial)','eta squared':'etasq','eta-squared':'etasq','η2':'etasq','standardized beta':'beta (std)','standardised beta':'beta (std)','unstandardized b':'b (unstd)','unstandardised b':'b (unstd)','odds ratio':'or'}
 aliases.update({
  'b (unstandardized)':'b (unstd)',
  'b (unstandardized regression coefficient)':'b (unstd)',
  'unstandardized regression coefficient':'b (unstd)',
  'unstandardized regression coefficient (estimate)':'b (unstd)',
  'unstandardized regression coefficient (b)':'b (unstd)',
  'unstandardized regression coefficient (thousands of dollars)':'b (unstd)',
  'b (unstandardized, replication_raw_stat)':'b (unstd)',
  'b (unstandardized regression coefficient; outcome log(price))':'b (unstd)',
  'β (standardized sem coefficient)':'beta (std)',
  'β (standardized regression coefficient)':'beta (std)',
  'standardized regression coefficient':'beta (std)',
  'standardized regression coefficient β':'beta (std)',
  'standardized regression coefficient (beta)':'beta (std)',
  'standardized regression coefficient (author table code b)':'beta (std)',
  'standardized beta (β)':'beta (std)',
  'standardized path coefficient (β)':'beta (std)',
  'partial η²':'etasq (partial)','partial η2':'etasq (partial)',
  'np2 (partial eta squared)':'etasq (partial)',
  'ŋ_p² (partial eta squared, as printed)':'etasq (partial)',
  'partial eta square':'etasq (partial)',
  'r²':'r-squared','φ':'phi',
  "cohen's f2":"cohen's f^2", "cohen's f²":"cohen's f^2",
  "cohen's f squared":"cohen's f^2",'f-squared':"cohen's f^2",
  'incidence rate ratio (irr)':'irr','odds ratio (or)':'or',
  "hedges's g":"hedges' g",
  'η² (printed as eta squared)':'etasq','eta-squared (η²)':'etasq',
  "cohen's d (author-derived standardized effect size)":'d',
  "cohen's d (authors' weighted table value)":'d',
  "cohen's d (author-derived table column rep_d_calc)":'d',
  "cohen's d (author-supplied table)":'d',
  "cohen's d (random-effects meta-analysis)":'d',
 })
 if s.startswith('partial eta squared') or s.startswith('partial eta-squared'):return 'etasq (partial)'
 if s in ['η²','η2','η² (eta squared)']:return 'etasq'
 if s in ['η²p','ηp²','ηp2','η2p']:return 'etasq (partial)'
 if s in ["pearson's r", "pearson's r (meta-analytic estimate)"]:return 'r'
 if re.fullmatch(r'[dr] \(author-derived[^)]*\)',s):return s[0]
 return aliases.get(s,s)
def parsed_stat(s):
 s=norm(s).replace('²','2').replace('χ','X')
 m=re.search(r'(?i)(F|t|z|X2|chi2|G2?)\s*(?:\(\s*([^)]*)\))?\s*=\s*([+-]?(?:\d*\.\d+|\d+\.?\d*))',s)
 if not m:return None
 kind=m[1].lower();kind='g' if kind in ['g','g2'] else 'chi2' if kind in ['x2','chi2'] else kind
 dfs=tuple(number(x) for x in (m[2] or '').split(',') if number(x) is not None)
 annotation=re.search(r'(?i)\bN\s*=\s*(\d+)',s)
 return kind,dfs,m[3],int(annotation[1]) if annotation else None
def overlap(a,b):return a is not None and b is not None and max(a[0],b[0])<=min(a[1],b[1])
def comp(field,raw,blind,r):
 val=blind['value']
 if field=='reported_success':return 'agree' if val==raw else 'soft' if {val,raw}=={'failed','mixed'} else 'differ'
 if field.startswith('n_'):
  a,b=analytic_n(raw),analytic_n(val)
  if a is None or b is None:return 'differ' if raw in [None,''] and b is not None else 'not_comparable'
  return 'agree' if a==b else 'near' if abs(a-b)/max(a,1)<=.05 else 'differ'
 if field.startswith('pval'):
  typ=str(r['pval_type_'+field[-1]] or '').split(' ')[0]
  ap,bp=p_parts(raw,typ),p_parts(val,blind['bound'])
  if raw in [None,''] and bp:return 'differ'
  if not ap or not bp:return 'not_comparable'
  aa,bb=pinterval(raw,typ),pinterval(val,blind['bound'])
  # Strict bounds at zero/one can represent an empty set, never an agreement.
  if any(t=='l' and x==0 or t=='g' and x==1 for x,t in [ap,bp]):return 'differ'
  if ap==bp and aa==bb:return 'identical'
  if not overlap(aa,bb):return 'differ'
  lo,hi=max(aa[0],bb[0]),min(aa[1],bb[1])
  if lo==hi:
   for value,bound in [ap,bp]:
    if bound=='l' and not lo<value:return 'differ'
    if bound=='g' and not lo>value:return 'differ'
  return 'compatible'
 if not metric(r['es_type_'+field[-1]]):return 'not_comparable'
 if metric(r['es_type_'+field[-1]])=='test statistic':
  a=parsed_stat(raw);b=parsed_stat(blind.get('test_statistic') or val)
  if raw in [None,''] and b:return 'differ'
  if not a or not b or a[0]!=b[0]:return 'not_comparable'
  if a[1]!=b[1]:return 'differ'
  if a[3] is not None and b[3] is not None and a[3]!=b[3]:return 'differ'
  return 'agree' if number(a[2])==number(b[2]) else 'compatible' if overlap(rounding(a[2]),rounding(b[2])) else 'differ'
 if metric(r['es_type_'+field[-1]])!=metric(blind['metric']):return 'not_comparable'
 if metric(r['es_type_'+field[-1]]) in ['etasq','etasq (partial)'] and any(re.match(r'^\s*[<>≤≥]',str(q or '')) for q in [raw,val]):
  aa,bb=pinterval(raw,'e'),pinterval(val,'e')
  if aa is None or bb is None:return 'not_comparable'
  return 'compatible' if overlap(aa,bb) else 'differ'
 a,b=number(raw),number(val)
 if a is None or b is None:return 'differ' if raw in [None,''] and b is not None else 'agree' if norm(raw)==norm(val) else 'not_comparable'
 if a*b<0:return 'differ'
 return 'agree' if a==b else 'compatible' if overlap(rounding(raw),rounding(val)) else 'differ'
def narrative_scope_unknown(x):
 if not x or x['replication']['status']!='locator_insufficient':return False
 text=str(x.get('notes',''))+' '+str(x['reported_success'].get('location',''))
 return bool(re.search(r'(?i)\b(?:paper[ -]level|overall narrative|overall paper)\b',text))
def adjudication_confirms_shipped(field,raw,a,row):
 if a.get('verdict')!='shipped_right' or a.get('correct_value') is None:return False
 if field.startswith('es_value'):
  requested=metric(row.get('es_type_'+field[-1]))
  if requested!='test statistic' and metric(a.get('correct_metric'))!=requested:return False
 e={'value':a['correct_value'],'bound':a.get('correct_bound') or row.get('pval_type_'+field[-1]),'metric':a.get('correct_metric'),'test_statistic':a['correct_value']}
 return comp(field,raw,e,row) in ['agree','identical','compatible']
def source_prefix(value):
 s=str(value or '').strip()
 if not s:return '(missing)'
 if '_' in s:return s.split('_',1)[0] or '(unprefixed)'
 if re.fullmatch(r'(?i)manylabs[1-6]',s):return s
 match=re.match(r'[^\W\d_]+',s,re.UNICODE)
 return match[0] if match else '(unprefixed)'
def original_secondary_source(e,row):
 info=SOURCE_PROVENANCE.get(e.get('source_path'))
 if info:return not (info.get('work_doi') and str(info['work_doi']).lower()==str(row.get('doi_o') or '').lower())
 doi=str(row.get('doi_r') or '').strip().lower()
 if not doi or str(row.get('doi_o') or '').strip().lower()==doi:return False
 key=hashlib.sha256(doi.encode()).hexdigest()[:24]
 return Path(e.get('source_path') or '').name.startswith(key)
def original_primary_evidence(e,row):
 path=e.get('source_path') or '';doi=str(row.get('doi_o') or '').strip().lower()
 if not doi:return False
 info=SOURCE_PROVENANCE.get(path)
 if info:return bool(info.get('work_doi') and str(info['work_doi']).lower()==doi)
 return Path(path).name.startswith(hashlib.sha256(doi.encode()).hexdigest()[:24])
def load_adjudications(root):
 """Review precedence follows recorded rounds, never mutable file mtimes."""
 tasks={}
 history=root/'adjudication_tasks.jsonl'
 if history.exists():
  for line in history.read_text().splitlines():
   if line:
    a=json.loads(line);tasks[a['key']]=a
 def priority(path):
  key=path.stem.removeprefix('validated_');a=tasks.get(key,{})
  return bool(a.get('focused_review')),a.get('started_at',''),a.get('attempt',0),key
 decisions={}
 for path in sorted((root/'adjudications').glob('validated_*.json'),key=priority):
  for a in json.loads(path.read_text()):decisions[(a['audit_id'],a['field'])]=a
 return decisions
def main():
 rows=json.loads((B/'parent_rows.json').read_text());results=[];candidates=[];invalid=[];coverage=collections.Counter();counts={f:collections.Counter() for f in FIELDS};projects=collections.defaultdict(lambda:{f:collections.Counter() for f in FIELDS});errors=[]
 adjud=load_adjudications(B)
 exhausted={(a['audit_id'],a['field']):a for a in json.loads((B/'adjudication_exhausted.json').read_text())} if (B/'adjudication_exhausted.json').exists() else {}
 holds={(a['audit_id'],a['field']) for a in json.loads((B/'adjudication_holds.json').read_text())} if (B/'adjudication_holds.json').exists() else set()
 target_overrides={}
 if (B/'target_overrides.json').exists():
  target_overrides={(a['audit_id'],a['side']):a for a in json.loads((B/'target_overrides.json').read_text())}
 obvious_path=B/'obvious_resolutions.json'
 if obvious_path.exists():
  for a in json.loads(obvious_path.read_text()):adjud[(a['audit_id'],a['field'])]=a
 for r in rows:
  aid=r['input_row_index'];path=B/'extractions'/f'{aid}.json';x=None
  if path.exists():
   try:x=validate(json.loads(path.read_text()));assert x['audit_id']==aid
   except Exception as e:invalid.append({'audit_id':aid,'error':str(e)[:400]});x=None
  if x:
   archive=B/'before_locator_enrichment'/f'{aid}.json'
   if archive.exists():x=preserve_completed(json.loads(archive.read_text()),x)
   coverage['checkpointed']+=1
   for side in ['original','replication']:
    if (aid,side) in target_overrides:x[side]['target_match']=target_overrides[(aid,side)]['target_match']
  z={'input_row_index':aid,'effect_id':r['effect_id'],'fred_id':r['fred_id']};full=True;side_ok={'o':True,'r':True};side_any={'o':False,'r':False};any_field=False
  for f in FIELDS:
   raw=r[f];side=None if f=='reported_success' else ('original' if f[-1]=='o' else 'replication');sub='n' if f.startswith('n_') else 'es' if f.startswith('es_value') else 'p'
   e=None if not x else x[f] if side is None else x[side][sub]
   v=None if not e else e.get('value');
   if f.startswith('pval'):
    z[f+'_shipped_bound']=r['pval_type_'+f[-1]];z[f+'_blind_bound']=e.get('bound') if e else None
   if f.startswith('es_value'):
    z[f+'_shipped_metric']=r['es_type_'+f[-1]];z[f+'_blind_metric']=e.get('metric') if e else None
    z[f+'_blind_printed_value']=v;z[f+'_blind_printed_metric']=e.get('metric') if e else None;z[f+'_blind_test_statistic']=e.get('test_statistic') if e else None;z[f+'_comparison_basis']='printed es value'
    if e and metric(r['es_type_'+f[-1]])=='test statistic' and parsed_stat(e.get('test_statistic')):
     v=e['test_statistic'];z[f+'_blind_metric']='test statistic';z[f+'_comparison_basis']='separately blind-extracted printed test_statistic (no conversion)'
   broad_success=bool(f=='reported_success' and narrative_scope_unknown(x))
   if f=='reported_success':z[f+'_scope_note']='Worker reports a broad paper narrative while the individual effect remains unidentified.' if broad_success else ''
   secondary=bool(e and side=='original' and original_secondary_source(e,r))
   if side:
    z[f+'_blind_source_path']=e.get('source_path') if e else None;z[f+'_evidence_basis']='replication source only (original unverified)' if secondary else 'paper evidence supplied' if e and e.get('source_path') else 'none'
   comparison='unverified';resolution='unresolved';verdict='unverified';suggestion='';location='';reason=''
   if secondary:reason='Original statistic is supported only by a replication paper/table; original primary-source verification remains unavailable.'
   elif broad_success and v is not None:comparison='mismatched_target';reason='Only broad paper-level narrative is identified; no individual-effect verdict established.'
   elif x and v is not None and (x[side or 'replication']['target_match'] is False or side is not None and x[side]['target_match'] is None and quote_ok({**e,'value':v,'confident':True})):comparison='mismatched_target'
   elif e and quote_ok({**e,'value':v}) and (side is None or x[side]['status']=='done' and x[side]['target_match'] is True):
    comparison=comp(f,raw,e,r)
    if comparison in ['agree','identical','compatible']:
     resolution='agree' if comparison in ['agree','identical'] else 'obvious';verdict='correct';reason='Compatible printed rounding intervals' if comparison=='compatible' else ''
    elif comparison=='not_comparable':verdict='not_comparable'
   elif e and v is not None:reason='Evidence, confidence or target match not validated'
   primary_adjud=bool(secondary and adjud.get((aid,f)) and original_primary_evidence(adjud[(aid,f)],r))
   if primary_adjud:
    comparison=comp(f,raw,e,r);z[f+'_evidence_basis']='secondary blind observation; original primary evidence validated during resolution'
   if comparison in ['differ','near','soft','mismatched_target'] or primary_adjud:
    a=adjud.get((aid,f))
    if (aid,f) in holds:a=None
    if a:
     resolution=a.get('resolution','argon');verdict={'shipped_right':'correct','blind_right':'error','both_wrong':'error','undeterminable':'unverified'}[a['verdict']];suggestion=a.get('correct_value','');location=a.get('location','');reason=a.get('reason','')
     if comparison=='mismatched_target':
      if broad_success and a.get('effect_specific_verdict_confirmed') is not True:verdict='unverified';reason='Paper-level narrative scope remains unresolved; '+reason
      elif broad_success:reason='Independent review establishes an effect-specific author verdict; '+reason
      elif adjudication_confirms_shipped(f,raw,a,r):reason='Argon independently located evidence confirming the shipped target value; '+reason
      else:verdict='unverified';reason='Target mismatch remains unresolved; '+reason
     if verdict=='error':errors.append({'audit_id':aid,'field':f,'shipped':raw,'error_kind':'coding omission' if raw in [None,''] else 'coded value/annotation','correction':suggestion,'location':location,'doi':r['doi_r' if side!='original' else 'doi_o'],'primary_source_url':next(iter(re.findall(r'https?://[^\s<>\"\]]+',str(r.get('url_r') or '')+' '+str(r.get('es_repr_r') or ''))), '').rstrip('.,;)') if side!='original' else next(iter(re.findall(r'https?://[^\s<>\"\]]+',str(r.get('es_repr_o') or ''))), '').rstrip('.,;)'),'reason':reason})
    else:candidates.append({'audit_id':aid,'field':f,'comparison':comparison,'shipped':raw,'shipped_metric':r.get('es_type_'+f[-1]) if side else None,'shipped_bound':r.get('pval_type_'+f[-1]) if side else None,'blind':e,'scope_note':(str(x['replication']['target_description'])+' '+str(x.get('notes',''))) if broad_success else None,'locator':{'study_o':r['study_o'],'study_r':r['study_r'],'description':next((a['description'] for a in json.loads((B/'inputs'/p.name).read_text()) if a['audit_id']==aid), '') if False else 'See assigned blind input'},'work_key':r['work_key']})
   if resolution=='unresolved' and (aid,f) in exhausted:reason=exhausted[(aid,f)]['reason']
   if comparison=='mismatched_target' and resolution=='unresolved':verdict='unverified'
   if verdict in ['correct','error']:
    any_field=True
    if side:side_any[f[-1]]=True
   if verdict not in ['correct','error']:full=False
   if side and verdict not in ['correct','error']:side_ok[f[-1]]=False
   counts[f][verdict]+=1;projects[source_prefix(r['fred_id'])][f][verdict]+=1
   for suffix,value in [('shipped',raw),('blind',v),('comparison',comparison),('resolution',resolution),('final_verdict',verdict),('suggested_correction',suggestion),('location',location),('reason',reason)]:z[f+'_'+suffix]=value
  for s,ok in side_ok.items():
   coverage[s+'_fully_checked']+=int(ok);coverage[s+'_any_stat_checked']+=int(side_any[s])
  coverage['any_field_checked']+=int(any_field)
  coverage['fully_checked_effects']+=int(full);results.append(z)
 with (B/'results.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=results[0]);w.writeheader();w.writerows(results)
 for name,value in [('disagreements.json',candidates),('validation_errors.json',invalid),('progress.json',{'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coverage':coverage,'field_counts':counts,'project_counts':projects,'confirmed_errors':errors})]:(B/name).write_text(json.dumps(value,indent=2,ensure_ascii=False))
 print({'coverage':coverage,'disagreements':len(candidates),'invalid':len(invalid),'confirmed_errors':len(errors)})
if __name__=='__main__':main()
