import json,re,csv,math,decimal,unicodedata
from pathlib import Path
from scipy import stats
B=Path(__file__).resolve().parents[1]
def number(v):
 try:return float(str(v).replace('−','-'))
 except (ValueError,TypeError):return None
def rounding(v):
 try:
  d=decimal.Decimal(str(v).strip().replace('−','-'));h=float(decimal.Decimal(10)**d.as_tuple().exponent)/2;return float(d)-h,float(d)+h
 except:return None
def p_parts(value,bound):
 """Normalise p formatting without discarding printed precision or inequalities."""
 if value is None:return None
 s=unicodedata.normalize('NFKC',str(value)).strip().lower().replace('−','-').replace('–','-')
 s=s.replace('\\times','×').replace('\\cdot','×').replace('$','').replace('{','').replace('}','')
 s=re.sub(r'^p(?:[- ]?value)?\s*','',s);s=re.sub(r'\s+','',s)
 match=re.match(r'^(<=|>=|≤|≥|<|>|=)',s)
 t=match[1] if match else str(bound or '').split(' ')[0]
 if match:s=s[match.end():]
 t={'=':'e','<':'l','>':'g','<=':'le','≤':'le','>=':'ge','≥':'ge'}.get(t,t)
 if t not in ['e','l','g','le','ge']:return None
 s=re.sub(r'(?:(?:×|\*)10\^)([+-]?\d+)$',r'e\1',s)
 s=re.sub(r'^10\^([+-]?\d+)$',r'1e\1',s)
 if not re.fullmatch(r'[+-]?(?:\d*\.\d+|\d+\.?\d*)(?:e[+-]?\d+)?',s):return None
 try:
  x=decimal.Decimal(s)
  if not x.is_finite() or not 0<=x<=1:return None
  return x,t
 except decimal.InvalidOperation:return None

def pinterval(v,t):
 parts=p_parts(v,t)
 if parts is None:return None
 x,t=parts;zero=decimal.Decimal(0);one=decimal.Decimal(1)
 if t=='e':
  h=decimal.Decimal(10)**x.as_tuple().exponent/2
  return max(zero,x-h),min(one,x+h)
 if t in ['l','le']:return zero,x
 if t in ['g','ge']:return x,one
 return None
def stat_interval(value,typ,n,nested,tails):
 s=str(value or '').replace('−','-').replace('χ','X').replace('²','2');num=r'([+-]?(?:\d*\.\d+|\d+\.?\d*))'
 patterns=[('f',r'F\s*\(\s*'+num+r'\s*,\s*'+num+r'\s*\)\s*=\s*'+num),('t',r't\s*\(\s*'+num+r'\s*\)\s*=\s*'+num),('chi',r'(?:X2|chi[ -]?square(?:d)?|chisq)\s*\(\s*'+num+r'(?:\s*,[^)]*)?\)\s*=\s*'+num),('z',r'\bz\s*=\s*'+num)]
 for kind,pat in patterns:
  m=re.search(pat,s,re.I)
  if not m:continue
  vals=list(map(float,m.groups()));a,b=rounding(m.groups()[-1]);a,b=((0,max(abs(a),abs(b))) if a<=0<=b else tuple(sorted([abs(a),abs(b)]))) if kind in ['t','z'] else (a,b)
  tail=1 if str(tails).startswith('1') else 2
  if kind=='f':fn=lambda q:stats.f.sf(q,vals[0],vals[1])
  elif kind=='chi':fn=lambda q:stats.chi2.sf(q,vals[0])
  elif kind=='t':fn=lambda q:stats.t.sf(q,vals[0])*tail
  else:fn=lambda q:stats.norm.sf(q)*tail
  return sorted([float(fn(a)),float(fn(b))]),kind+('_tails_assumed_two' if kind in ['t','z'] and tails is None else '')
 # Pearson inference only for non-nested analytic n as defined by codebook.
 if str(typ).lower()=='r' and str(nested).lower()=='no' and number(n) and number(n)>2 and number(value) is not None and abs(number(value))<=1:
  lo,hi=rounding(value); ab=[0,max(abs(lo),abs(hi))] if lo<=0<=hi else sorted([abs(lo),abs(hi)]);tail=1 if str(tails).startswith('1') else 2
  fn=lambda q:stats.t.sf(min(.999999999999, q)*math.sqrt((number(n)-2)/(1-min(.999999999999,q)**2)),number(n)-2)*tail
  return sorted([float(fn(ab[0])),float(fn(ab[1]))]),'pearson_coded_analytic_n'+('_tails_assumed_two' if tails is None else '')
 return None,'not_applicable'
def main():
 rows=json.loads((B/'parent_rows.json').read_text());out=[]
 for r in rows:
  z={'input_row_index':r['input_row_index'],'effect_id':r['effect_id']};flags=[]
  for s in ['o','r']:
   n=number(r['n_'+s]);p=number(r['pval_value_'+s]);es=number(r['es_value_'+s]);typ=str(r['es_type_'+s] or '').lower()
   for name,val in [('n_range','missing' if r['n_'+s] is None else 'pass' if n and n>0 and n.is_integer() else 'flag'),('p_range','missing' if r['pval_value_'+s] is None else 'pass' if p is not None and 0<=p<=1 else 'flag'),('r_range','not_applicable' if typ!='r' else 'pass' if es is not None and -1<=es<=1 else 'flag'),('es_type','missing' if not typ else 'not_enumerated_in_codebook')]:
    z[name+'_'+s]=val
    if val=='flag':flags.append(name+'_'+s)
   pi,method=stat_interval(r['es_value_'+s],r['es_type_'+s],r['n_'+s],r['nested_'+s],r['pval_tails_'+s]);reported=pinterval(r['pval_value_'+s],r['pval_type_'+s]);z['p_method_'+s]=method;z['recomputed_p_interval_'+s]=json.dumps(pi)
   z['p_consistency_'+s]='not_applicable' if pi is None or reported is None else ('pass' if max(pi[0],reported[0])<=min(pi[1],reported[1]) else 'flag')
   if z['p_consistency_'+s]=='flag':flags.append('p_consistency_'+s)
  z['success_rule']='not_applicable_no_project_rule_established';z['flag_count']=len(flags);z['flags']=';'.join(flags);out.append(z)
 with (B/'consistency.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
 print({'rows':len(out),'flagged_effects':sum(bool(z['flag_count']) for z in out)})
if __name__=='__main__':main()
