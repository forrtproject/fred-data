import json,csv,collections,datetime,hashlib
from pathlib import Path
B=Path(__file__).resolve().parents[1]
def main():
 p=json.loads((B/'progress.json').read_text());m=json.loads((B/'run_manifest.json').read_text());r=list(csv.DictReader((B/'results.csv').open(encoding='utf-8-sig')));flags=list(csv.DictReader((B/'consistency.csv').open(encoding='utf-8-sig')))
 errors=p['confirmed_errors'];N=len(r);cov=p['coverage'];nflag=sum(int(x['flag_count'])>0 for x in flags);confirmed=sum(any(y['audit_id']==int(x['input_row_index']) for y in errors) for x in flags if int(x['flag_count'])>0)
 error_keys={(e['audit_id'],e['field']) for e in errors}
 confirmed_checks=[]
 for flagrow in flags:
  for flag in flagrow['flags'].split(';'):
   if not flag:continue
   side=flag[-1];field='n_'+side if flag.startswith('n_range') else 'es_value_'+side if flag.startswith('r_range') else 'pval_value_'+side if flag.startswith(('p_range','p_consistency')) else None
   if (int(flagrow['input_row_index']),field) in error_keys:confirmed_checks.append((flagrow['input_row_index'],flag))
 confirmed_flag_effects=len({a[0] for a in confirmed_checks})
 total_checks=sum(int(a['flag_count']) for a in flags)
 t=['# FReD statistics audit','',f'**Interim checkpoint — {p["updated_at"]}.** {len(errors)} confirmed field errors have been identified so far. Paper checking is still in progress; the deterministic screen alone is not verification.','',f'The frozen workbook contains {N:,} effects in {m["work_count"]} replication works. Part A screened every effect and flagged {nflag}. {len(confirmed_checks)}/{total_checks} individual flags have a confirmed error in the corresponding field, affecting {confirmed_flag_effects}/{nflag} flagged effects. Separately, {confirmed} flagged effects contain any confirmed field error.', '',f'Paper checkpoints exist for {cov.get("checkpointed",0)}/{N} effects. All three original statistics are evaluable for {cov.get("o_fully_checked",0)}/{N}; all three replication statistics for {cov.get("r_fully_checked",0)}/{N}. All seven fields, including author-reported success, are checked for {cov.get("fully_checked_effects",0)}/{N}. Individual-field coverage is below.','', 'Coverage depends on paper access and target identification. These results are not a representative sample of FReD. Bounds below describe remaining identification uncertainty, not binomial sampling intervals. Different metrics remain not comparable unless a documented transformation is reproduced.','', '| Field | Confirmed errors / evaluable | Unverified | Not comparable | All-row error bounds |','|---|---:|---:|---:|---:|']
 for field,c in p['field_counts'].items():
  e=c.get('error',0);ev=e+c.get('correct',0);u=c.get('unverified',0);nc=c.get('not_comparable',0);t.append(f'| {field} | {e}/{ev}'+(f' ({100*e/ev:.1f}%)' if ev else '')+f' | {u} | {nc} | {100*e/N:.2f}%–{100*(e+u+nc)/N:.2f}% |')
 t+=['','Provenance-prefix breakdown uses the leading text before an underscore or digit in `fred_id`; `fred_id` is provenance, not an effect key. Each cell gives **errors/evaluable (unverified; not comparable)**. The complete machine-readable rates, denominators and uncertainty bounds are in [field_summary_by_project.csv](field_summary_by_project.csv).','','| Project prefix | Original n | Original ES | Original p | Replication n | Replication ES | Replication p | Success |','|---|---|---|---|---|---|---|---|']
 summary=[]
 for prefix,fs in sorted(p['project_counts'].items()):
  cells=[]
  for field,c in fs.items():
   e=c.get('error',0);ev=e+c.get('correct',0);u=c.get('unverified',0);nc=c.get('not_comparable',0);n=ev+u+nc
   cells.append(f'{e}/{ev} ({u}; {nc})')
   summary.append({'fred_id_prefix':prefix,'field':field,'errors':e,'evaluable':ev,'error_rate_evaluable':e/ev if ev else None,'unverified':u,'not_comparable':nc,'total':n,'lower_all_row_error_bound':e/n if n else None,'upper_all_row_error_bound':(e+u+nc)/n if n else None})
  t.append('| '+(prefix or '(blank/numeric)')+' | '+' | '.join(cells)+' |')
 with (B/'field_summary_by_project.csv').open('w',encoding='utf-8-sig',newline='') as file:
  writer=csv.DictWriter(file,fieldnames=summary[0]);writer.writeheader();writer.writerows(summary)
 t+=['','## Confirmed errors','']
 if not errors:t.append('None confirmed at this checkpoint.')
 for e in errors:
  link=f'https://doi.org/{e["doi"]}' if e['doi'] else ''
  t.append(f'- Effect row {e["audit_id"]}, `{e["field"]}`: `{e["shipped"]}` → `{e["correction"]}`. {e["location"]}. {e["reason"]}'+(f' [Paper]({link}).' if link else ''))
 statuses=collections.Counter();reasons=collections.Counter()
 for f in (B/'extractions').glob('*.json'):
  try:x=json.loads(f.read_text())
  except:continue
  for s in ['original','replication']:
   statuses[s+': '+x[s]['status']]+=1
   if x[s]['status']!='done':reasons[x[s]['target_description']]+=1
 t+=['','## Unverified and skipped work','',f'{N-cov.get("checkpointed",0)} effects have no paper checkpoint yet. A checkpoint with unavailable or insufficient fields is not a verified effect.','']
 t += [f'- {k}: {v} sides.' for k,v in sorted(statuses.items())]
 t+=['','Detailed access/target reasons are retained in the per-effect JSON checkpoints. Frequent reasons at this checkpoint:','']
 t += [f'- {n} sides: {reason}' for reason,n in reasons.most_common(15)]
 t+=['','## Method and limits','','Extraction workers received references, studies, neutral descriptions, requested metric labels, and sanitised page/table/primary-source URLs, with no shipped n, estimates, p-values or success verdicts. The first 20 sanitised descriptions and later batch samples were inspected. Original and replication statistics were extracted separately, with printed metric and bound type. Comparisons require confident matching targets and validated source quotes. Non-obvious disagreements go to Gemini 4 Argon (High); obvious decisions retain a reason and evidence location.','', 'The screen checks positive-integer n, p and r ranges, recognized F/t/chi-square/z reports, and non-nested Pearson r with coded analytic n. Missing tails are labelled as an assumed two-sided screen. The codebook does not enumerate every allowed metric, so unfamiliar labels are not declared invalid. No source-project success rule has been established for automatic significance/direction checks. Rounding intervals use stored cell strings; XLSX may already have lost printed precision.','',f'Frozen input SHA256: `{m["input_sha256"]}`. No dataset changes are made. Full texts are excluded from Git. See `run_log.md`, `consistency.csv`, `results.csv` and `extractions/` for decisions, diagnostics and short evidence quotes.']
 (B/'REPORT.md').write_text('\n'.join(t)+'\n');print({'report':str(B/'REPORT.md'),'errors':len(errors)})
if __name__=='__main__':main()
