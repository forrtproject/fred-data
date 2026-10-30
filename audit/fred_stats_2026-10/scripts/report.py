import json,csv,collections,datetime,hashlib
from pathlib import Path
from urllib.parse import quote
from confirm_flags import confirm_flags
B=Path(__file__).resolve().parents[1]
def main():
 p=json.loads((B/'progress.json').read_text());m=json.loads((B/'run_manifest.json').read_text());r=list(csv.DictReader((B/'results.csv').open(encoding='utf-8-sig')));flags=list(csv.DictReader((B/'consistency.csv').open(encoding='utf-8-sig')))
 errors=p['confirmed_errors'];N=len(r);cov=p['coverage'];nflag=sum(int(x['flag_count'])>0 for x in flags);confirmed=sum(any(y['audit_id']==int(x['input_row_index']) for y in errors) for x in flags if int(x['flag_count'])>0)
 rows=json.loads((B/'parent_rows.json').read_text());flag_checks=confirm_flags(rows,flags,errors)
 with (B/'flag_confirmation.csv').open('w',encoding='utf-8-sig',newline='') as file:
  writer=csv.DictWriter(file,fieldnames=['input_row_index','flag','confirmation','confirmed_corrections']);writer.writeheader();writer.writerows(flag_checks)
 confirmed_checks=[a for a in flag_checks if a['confirmation']=='resolved_by_confirmed_correction']
 confirmed_flag_effects=len({a['input_row_index'] for a in confirmed_checks});total_checks=len(flag_checks)
 final_state=json.loads((B/'final_report_state.json').read_text()) if (B/'final_report_state.json').exists() else None
 lead=(f'**Completed — {final_state["completed_at"]}.** {len(errors)} confirmed field errors were identified. {final_state["stop_reason"]} The deterministic screen alone is not verification.' if final_state else f'**Interim checkpoint — {p["updated_at"]}.** {len(errors)} confirmed field errors have been identified so far. Paper checking is still in progress; the deterministic screen alone is not verification.')
 followup=B/'source_followup';followup_note=None
 if (followup/'integration.json').exists():
  followup_state=json.loads((followup/'state.json').read_text());baseline=json.loads((followup/'baseline.json').read_text())['baseline_counts']
  followup_status='completed' if followup_state.get('status')=='complete' else 'in progress'
  lead=f'**Source follow-up {followup_status} — {p["updated_at"]}.** Current integrated results contain {len(errors)} confirmed field errors. Source retrieval alone is not verification; the deterministic screen alone is not verification.'
  followup_note=(f'The original bounded audit finished on {final_state["completed_at"]} with {baseline["confirmed_errors"]} confirmed field errors across {baseline["error_rows"]} rows, {baseline["any_verified_effects"]} effects with at least one verified field and {baseline["all_verified_effects"]} with all seven. A separately authorised source-acquisition follow-up is recorded in [source_followup/README.md](source_followup/README.md). Current counts below include only integrated, evidence-validated follow-up results; the original deadlines and completion record are unchanged.')
 t=['# FReD statistics audit','',lead,'',f'Confirmed errors affect {len({e["audit_id"] for e in errors})} effect rows. Counts refer to field instances; an original statistic repeated across replication rows can contribute more than once.','',f'The frozen workbook contains {N:,} effects in {m["work_count"]} replication works. Part A screened every effect and flagged {nflag}. {len(confirmed_checks)}/{total_checks} individual flags are resolved when source-confirmed corrections are applied in memory, affecting {confirmed_flag_effects}/{nflag} flagged effects (see `flag_confirmation.csv`). This includes corrected test statistics or analytic n as well as p-values. Separately, {confirmed} flagged effects contain any confirmed field error.', '',f'Paper checkpoints exist for {cov.get("checkpointed",0)}/{N} effects. All three original statistics are evaluable for {cov.get("o_fully_checked",0)}/{N}; all three replication statistics for {cov.get("r_fully_checked",0)}/{N}. All seven fields, including author-reported success, are checked for {cov.get("fully_checked_effects",0)}/{N}. At least one original statistic is evaluable for {cov.get("o_any_stat_checked",0)}/{N}, at least one replication statistic for {cov.get("r_any_stat_checked",0)}/{N}, and any of the seven fields for {cov.get("any_field_checked",0)}/{N}. Individual-field coverage is below.','', '**Decision to review:** reported success is evaluated for the identified study/outcome. A broad paper-level verdict without a defensible mapping to an individual row remains unverified; the original narrative observation is retained. This conservative scope rule avoids assigning a mixed article outcome to every unidentified component effect.\n\nConfirmed errors include coding omissions only when adjudication establishes the requested statistic from the matching primary source; their count is reported separately. Coverage depends on paper access and target identification. These results are not a representative sample of FReD. Bounds below describe remaining identification uncertainty, not binomial sampling intervals. Different metrics remain not comparable unless a documented transformation is reproduced.','', '| Field | Confirmed errors / evaluable | Unverified | Not comparable | All-row error bounds |','|---|---:|---:|---:|---:|']
 for field,c in p['field_counts'].items():
  e=c.get('error',0);ev=e+c.get('correct',0);u=c.get('unverified',0);nc=c.get('not_comparable',0);t.append(f'| {field} | {e}/{ev}'+(f' ({100*e/ev:.1f}%)' if ev else '')+f' | {u} | {nc} | {100*e/N:.2f}%–{100*(e+u+nc)/N:.2f}% |')
 if final_state and cov.get('any_field_checked',0)<.8*N:
  t.insert(4,f'The run did not reach the 80% verification goal: even the looser any-field coverage measure is {100*cov.get("any_field_checked",0)/N:.1f}%; all-seven-field coverage is {100*cov.get("fully_checked_effects",0)/N:.1f}%. Access failures, unresolved target identity and unavailable matching metrics remain explicit rather than being counted as verified.')
  t.insert(5,'')
 if followup_note:t[4:4]=[followup_note,'']
 t+=['','Provenance-prefix breakdown uses text before the first underscore in `fred_id` (preserving project years); legacy codes without underscores use leading letters, with literal ManyLabs1–6 preserved; `fred_id` is provenance, not an effect key. Each cell gives **errors/evaluable (unverified; not comparable)**. The complete machine-readable rates, denominators and uncertainty bounds are in [field_summary_by_project.csv](field_summary_by_project.csv).','','| Project prefix | Original n | Original ES | Original p | Replication n | Replication ES | Replication p | Success |','|---|---|---|---|---|---|---|---|']
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
 t+=['','## Confirmed errors','',f'{sum(e.get("error_kind")=="coding omission" for e in errors)} confirmed errors are blank coded fields for which the primary source supplies the requested statistic. Each entry below gives the proposed correction and source location; full reasons and retained blind observations are in [results.csv](results.csv).','']
 if not errors:t.append('None confirmed.')
 for e in errors:
  link='https://doi.org/'+quote(e['doi'],safe='/') if e['doi'] else ''
  t.append(f'- Row {e["audit_id"]}, `{e["field"]}`: `{e["shipped"]}` → `{e["correction"]}`. {e["location"]}.'+(f' [Paper]({link}).' if link else '')+(f' [Locator URL]({e["primary_source_url"]}).' if e.get('primary_source_url') else ''))
 statuses=collections.Counter();reasons=collections.Counter()
 for f in (B/'extractions').glob('*.json'):
  try:x=json.loads(f.read_text())
  except:continue
  for s in ['original','replication']:
   statuses[s+': '+x[s]['status']]+=1
   if x[s]['status']!='done':reasons[x[s]['target_description'].strip() or str(x.get('notes') or '').strip() or ('No narrative reason recorded; status '+x[s]['status']+'; inspect the checkpoint and shared acquisition miss record.')]+=1
 t+=['','## Unverified and skipped work','',f'{N-cov.get("checkpointed",0)} effects have no paper checkpoint yet. A checkpoint with unavailable or insufficient fields is not a verified effect.','']
 exhausted=json.loads((B/'adjudication_exhausted.json').read_text()) if (B/'adjudication_exhausted.json').exists() else []
 queue=json.loads((B/'adjudication_queue.json').read_text()) if (B/'adjudication_queue.json').exists() else []
 t.append(f'{len(exhausted)} fields exhausted the allowed adjudication attempts and remain unresolved. The remaining dispatch queue contains {sum(len(a["items"]) for a in queue)} fields in {len(queue)} source groups; after the dispatch cutoff these remain unverified. Failed or truncated replies establish no error unless an individual complete response passes source validation.')
 if (followup/'adjudication_queue.json').exists():
  pending=0
  obvious_keys={(x['audit_id'],x['field']) for x in json.loads((B/'obvious_resolutions.json').read_text())}
  for item in json.loads((followup/'adjudication_queue.json').read_text()):
   resolved=B/'adjudications'/f'validated_{item["key"]}.json'
   keys={(x['audit_id'],x['field']) for x in json.loads(resolved.read_text())} if resolved.exists() else set()
   pending+=sum((x['audit_id'],x['field']) not in keys|obvious_keys for x in item['items'])
  t.append(f'The separately authorised source follow-up has {pending} additional fields awaiting validated adjudication. These remain unverified until their evidence and target identity pass review.')
 t.append('')
 t += [f'- {k}: {v} sides.' for k,v in sorted(statuses.items())]
 t+=['','Detailed access/target reasons are retained in the per-effect JSON checkpoints. Frequent access/target reasons:','']
 t += [f'- {n} sides: {reason}' for reason,n in reasons.most_common(15)]
 t+=['','## Method and limits','','Effect identifiers are one-based data-row indices, excluding the header (worksheet row = input_row_index + 1). T3 sanitisation and extraction workers used Codex gpt-6.1-sol with medium reasoning. Extraction workers received references, studies, neutral descriptions, requested metric labels, and sanitised page/table/primary-source URLs, with no shipped n, estimates, p-values or success verdicts. The first 20 sanitised descriptions and later batch samples were inspected. Original and replication statistics were extracted separately, with printed metric and bound type. Original statistics reproduced only in replication papers or summary tables remain unverified against the original primary source; their secondary evidence is retained. Comparisons require confident matching targets and validated source quotes. Non-obvious disagreements go to Gemini 4 Argon (High); obvious decisions retain a reason and evidence location.','', 'The screen checks positive-integer n, p and r ranges, recognized F/t/chi-square/z reports, and non-nested Pearson r with coded analytic n. Missing tails are labelled as an assumed two-sided screen. The codebook does not enumerate every allowed metric, so unfamiliar labels are not declared invalid. No source-project success rule has been established for automatic significance/direction checks. Rounding intervals use stored cell strings; XLSX may already have lost printed precision. P-value formatting is normalised with exact decimal arithmetic, including scientific notation and strict bounds. Explicit metric synonyms are aligned without converting numbers; partial metrics and unspecified standardisation remain separate. Published corrections take precedence over superseded article text where directly verified. A prior blind target mismatch can be resolved by independent primary evidence confirming the shipped target value, while unresolved wrong-target proposed errors remain unverified.','',f'Frozen input SHA256: `{m["input_sha256"]}`. No dataset changes are made. Full texts are excluded from Git. See `run_log.md`, `consistency.csv`, `results.csv` and `extractions/` for decisions, diagnostics and short evidence quotes.']
 t[-1:-1]=['Documented contrast direction can justify a sign reversal of the printed effect. In nested models, participant or cluster counts and repeated observations have distinct sample roles; an unidentified counting unit remains unverified. Inferred df or N annotations require positive contradictory evidence from the design, counts, reference distribution or reported p before being counted as errors.','']
 (B/'REPORT.md').write_text('\n'.join(t)+'\n');print({'report':str(B/'REPORT.md'),'errors':len(errors)})
if __name__=='__main__':main()
