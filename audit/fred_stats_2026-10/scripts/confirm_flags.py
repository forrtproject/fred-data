"""Recompute diagnostic flags using only source-confirmed corrections."""
import json,csv
from pathlib import Path
from consistency import number,analytic_n,pinterval,stat_interval
B=Path(__file__).resolve().parents[1]
def confirm_flags(rows,flags,errors):
 corrections={}
 for e in errors:corrections.setdefault(e['audit_id'],{})[e['field']]=e['correction']
 out=[]
 for fr in flags:
  aid=int(fr['input_row_index']);changes=corrections.get(aid,{});r={**rows[aid-1],**changes}
  for flag in fr['flags'].split(';'):
   if not flag:continue
   side=flag[-1]
   relevant=({'n_'+side} if flag.startswith('n_range') else {'pval_value_'+side} if flag.startswith('p_range') else {'es_value_'+side} if flag.startswith('r_range') else {'n_'+side,'es_value_'+side,'pval_value_'+side} if flag.startswith('p_consistency') else set())&changes.keys()
   status='no_relevant_confirmed_correction'
   if relevant:
    passed=None
    if flag.startswith('n_range'):
     n=analytic_n(r['n_'+side]);passed=n is not None and n>0 and n.is_integer()
    elif flag.startswith('p_range'):
     interval=pinterval(r['pval_value_'+side],r['pval_type_'+side]);passed=interval is not None
    elif flag.startswith('r_range'):
     es=number(r['es_value_'+side]);passed=es is not None and -1<=es<=1
    elif flag.startswith('p_consistency'):
     interval,_=stat_interval(r['es_value_'+side],r['es_type_'+side],r['n_'+side],r['nested_'+side],r['pval_tails_'+side]);reported=pinterval(r['pval_value_'+side],r['pval_type_'+side])
     if interval is not None and reported is not None:passed=max(interval[0],reported[0])<=min(interval[1],reported[1])
    status='resolved_by_confirmed_correction' if passed is True else 'still_flagged' if passed is False else 'cannot_recompute'
   out.append({'input_row_index':aid,'flag':flag,'confirmation':status,'confirmed_corrections':json.dumps({f:changes[f] for f in sorted(relevant)},ensure_ascii=False)})
 return out
if __name__=='__main__':
 rows=json.loads((B/'parent_rows.json').read_text());flags=list(csv.DictReader((B/'consistency.csv').open(encoding='utf-8-sig')));errors=json.loads((B/'progress.json').read_text())['confirmed_errors'];out=confirm_flags(rows,flags,errors)
 with (B/'flag_confirmation.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['input_row_index','flag','confirmation','confirmed_corrections']);w.writeheader();w.writerows(out)
 print({'flags':len(out),'resolved_by_confirmed_correction':sum(z['confirmation']=='resolved_by_confirmed_correction' for z in out)})
