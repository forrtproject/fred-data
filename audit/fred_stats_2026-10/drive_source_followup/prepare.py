"""Verify the private Drive handoff and prepare neutral, unresolved-side inputs."""
import collections,datetime,hashlib,json,re,subprocess,unicodedata
from pathlib import Path
F=Path(__file__).resolve().parent;B=F.parent
D=Path('/home/lukas/work/fred-mac-recovery-20261030/drive-check')
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tokens(s):return set(re.findall(r'[^\W_]{3,}',unicodedata.normalize('NFKC',s).lower()))
def main():
 mp=D/'final_box_source_manifest.json';assert sha(mp)=='29c160b7952005f0214ed1437d5dcd5dee48cb667bab701f177a161dd5f998cf';m=json.loads(mp.read_text());assert len(m['sources'])==129
 subprocess.run(['mountpoint','-q','/home/lukas/cloud-data'],check=True)
 if (F/'state.json').exists():
  print('Existing prepared queue retained; use native_job.py to resume, never regenerate live inputs/state.')
  return
 if not (F/'baseline.json').exists():
  files={str(p.relative_to(B)):sha(p) for folder in ['source_followup','mac_source_followup','mac_continuation_followup'] for p in (B/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
  for name in ['COMPLETE.json','run_manifest.json','watchdog.json','scope_holds.json','target_overrides.json']:
   if (B/name).exists():files[name]=sha(B/name)
  save(F/'baseline.json',{'commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'confirmed_errors':441,'any_verified_effects':1646,'all_seven_verified_effects':95,'files':files})
 prior={k for folder in ['source_followup','mac_source_followup','mac_continuation_followup'] for k,v in json.loads((B/folder/'accepted_sources.json').read_text()).items() if not v.get('source_kind')}
 inputs={r['audit_id']:r for p in (B/'inputs').glob('*.json') for r in json.loads(p.read_text())}
 checks=[];accepted={};queue=[];skips=collections.Counter();reserved=set()
 (F/'validation_inputs').mkdir(exist_ok=True)
 for key,s in m['sources'].items():
  assert key not in prior,key
  pdf=Path(s['artifact_path']);text=Path(s['text_path']);neutral=Path(s['neutral_input_path']);assert sha(pdf)==s['artifact_sha256'] and sha(text)==s['text_sha256'],key
  ni=json.loads(neutral.read_text());assert ni['key']==key and ni['doi']==s['doi']
  info=subprocess.check_output(['pdfinfo',str(pdf)],text=True);pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1]);assert pages==s['pages'],key
  header=subprocess.check_output(['pdftotext','-f','1','-l',str(min(4,pages)),str(pdf),'-'],text=True)
  tt=tokens(s.get('title') or s['reference']);match=len(tt&tokens(header))/max(1,len(tt));full=text.read_text();refs=bool(re.search(r'(?im)^\s*(references|bibliography|literature cited|works cited)\s*$',full))
  checks.append({'key':key,'pages':pages,'title_token_match':round(match,3),'reference_heading':refs,'needs_content_review':match<.65 or not refs,'header_excerpt':header[:1800],'ending_excerpt':full[-2500:],'version':s['source_version'],'identity_completeness_evidence':s['identity_completeness_evidence']})
  dest=B/'texts'/f'followup_drive_{key}.txt'
  if dest.exists():assert sha(dest)==s['text_sha256']
  else:dest.write_bytes(text.read_bytes())
  accepted[key]={k:s[k] for k in ['doi','reference','pages','artifact_path','artifact_sha256','text_sha256','retrieval_url','drive_file_id','source_version','identity_completeness_evidence']};accepted[key].update(text_path=str(dest),source_pdf_path=str(pdf),neutral_input_sha256=sha(neutral),parent_review='Transfer hashes, actual PDF page count, freshly parsed PDF header and canonical endmatter checked; additional content flags require review before dispatch.')
  sides=collections.defaultdict(list)
  for t in ni['targets']:
   aid,side=t['audit_id'],t['side'];before=json.loads((B/'extractions'/f'{aid}.json').read_text())
   if before[side]['status']!='paper_unavailable':skips[before[side]['status']]+=1;continue
   assert (aid,side) not in reserved;reserved.add((aid,side));row=dict(inputs[aid]);row.update(target_side=side,description=t['description'],source_version_note=s['source_version']+'; '+s['identity_completeness_evidence'],source_pdf_path=str(pdf),text_paths={side[0]:str(dest)});row['locators_'+side[0]]=t['locator'];row['es_type_'+side[0]]=t['requested_metric'];sides[side].append(row)
  for side,rows in sides.items():
   for start in range(0,len(rows),15):
    batch=f'drive01_{key}_{side}_{start:03d}';p=F/'validation_inputs'/f'{batch}.json';save(p,rows[start:start+15]);queue.append({'batch':batch,'source_key':key,'chunk':start,'input':str(p),'output':str(F/'validation_extractions'/batch),'audit_ids':[r['audit_id'] for r in rows[start:start+15]]})
 save(F/'parent_source_checks.json',checks);save(F/'accepted_sources.json',accepted);save(F/'validation_queue.json',sorted(queue,key=lambda x:(x['chunk'],-len(x['audit_ids']),x['batch'])));save(F/'exceptions.json',json.loads(Path(m['exceptions_path']).read_text()))
 save(F/'state.json',{'status':'active','phase':'parent_source_review','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':json.loads((F/'baseline.json').read_text())['commit'],'manifest':str(mp),'manifest_sha256':sha(mp),'sources':len(accepted),'eligible_sides':len(reserved),'validation_batches':len(queue),'skipped_statuses':dict(skips),'maximum_validation_children':3,'new_schedules_created':0,'historical_records_immutable':True,'related1979_source_held':True,'pull_request':'https://github.com/forrtproject/fred-data/pull/155','delegation_transport':'native Codex subagents; T3 MCP tools unavailable in current runtime'})
 print(json.dumps({'sources':len(accepted),'eligible_sides':len(reserved),'batches':len(queue),'skipped':dict(skips),'content_review_flags':[c['key'] for c in checks if c['needs_content_review']]}))
if __name__=='__main__':main()
