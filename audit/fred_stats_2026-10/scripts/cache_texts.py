from prepare import *
rows=json.loads((B/'parent_rows.json').read_text());dois=sorted(set(str(r['doi_'+s]).strip().lower() for r in rows for s in ['o','r'] if r['doi_'+s]))
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e: results=list(e.map(cache,dois))
print({'cache_dois':len(dois),'hits':sum(p is not None for p in results)})
