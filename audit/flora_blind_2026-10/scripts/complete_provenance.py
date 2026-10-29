#!/usr/bin/env python3
"""Complete cache provenance only; never alter blind judgments or source bytes.
Run with flora-extractor's interpreter, bytecode disabled, cache read-only.
"""
import datetime,hashlib,json,pathlib,re,sys,os
sys.dont_write_bytecode=True
os.environ['FLORA_CACHE_DIR']='/home/lukas/flora-extractor/cache'
sys.path.insert(0,'/home/lukas/flora-extractor')
from shared.pdf_parsing import parse_cache_path,read_parse_cache,best_parse_result
R=pathlib.Path(__file__).resolve().parents[1]
updates=[];unresolved=[]
for p in (R/'codings').glob('*.json'):
 if not re.fullmatch(r'[0-9a-f]{16}',p.stem):continue
 try:c=json.loads(p.read_text())
 except (OSError,ValueError):continue
 if c.get('status')!='done':continue
 missing=[k for k in ['source_url','retrieved_at','text_sha256','parser'] if not isinstance(c.get(k),str) or not c[k].strip()]
 if not missing:continue
 if 'cache' not in str(c.get('parser','')).lower():
  unresolved.append({'file_key':p.stem,'missing':missing,'reason':'not identified as cache-supplied; no provenance inferred'});continue
 source=R/'texts'/f'{p.stem}.txt';cache=pathlib.Path(parse_cache_path(c['work_key']))
 if not source.exists() or not cache.exists():
  unresolved.append({'file_key':p.stem,'missing':missing,'reason':'cache or saved text absent'});continue
 # Verify this is exactly the tested helper's source, including appended references.
 best=best_parse_result(read_parse_cache(c['work_key'])) or {};original=best.get('raw_text') or '';refs=best.get('references') or []
 if refs:original+='\n\nREFERENCES (as parsed)\n'+'\n'.join(x if isinstance(x,str) else ' '.join(str(v) for v in x.values() if v) for x in refs)
 if source.read_bytes()!=original.encode():
  unresolved.append({'file_key':p.stem,'missing':missing,'reason':'saved bytes differ from tested helper output; no cache provenance inferred'});continue
 before={k:c.get(k) for k in missing}
 values={'source_url':cache.resolve().as_uri(),'retrieved_at':datetime.datetime.fromtimestamp(source.stat().st_mtime,datetime.timezone.utc).isoformat(),'text_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'parser':'cached_text.sh: best_parse_result ('+str(best.get('source','unspecified'))+')'}
 for key in missing:c[key]=values[key]
 c['parent_provenance_completion']={'filled_fields':missing,'original_values':before,'source_url_basis':'actual local parse-cache file URI; upstream retrieval URL not recorded','retrieved_at_basis':'mtime of verified audit copy; upstream retrieval date not recorded','cache_parser':str(best.get('source','unspecified'))}
 tmp=p.with_suffix('.provenance.tmp');tmp.write_text(json.dumps(c,indent=2,ensure_ascii=False)+'\n');tmp.replace(p)
 updates.append({'file_key':p.stem,'filled_fields':missing})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'updated':updates,'unresolved':unresolved}
with (R/'provenance_completions.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
print(json.dumps(result))
