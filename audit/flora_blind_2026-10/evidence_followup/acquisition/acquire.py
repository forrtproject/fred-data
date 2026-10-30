#!/usr/bin/env python3
"""Finite, resumable primary-source acquisition. No scientific coding.
Run using download-paper's cached Python, or Python with requests + ddgs + fetchpdf.
All input is the sanitized works.json. All candidates require parent verification.
"""
import concurrent.futures as cf
import collections, datetime, hashlib, html, importlib.util, json, os, pathlib, re
import signal, subprocess, sys, threading, time, unicodedata, urllib.parse, zipfile
from html.parser import HTMLParser
import requests
HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE.parent
PRIVATE=BASE/'private'/'acquisition'
TEXTS=BASE/'private'/'new_texts'
SKILL=pathlib.Path('/home/lukas/.codex/skills/download-paper')
EXCLUDED=('forrt.org','github.com/forrtproject','forrtproject.github.io','citestamp.com')
EXCLUSIONS=' -site:forrt.org -site:github.com/forrtproject -site:forrtproject.github.io -site:citestamp.com -"FORRT dataset" -"FReD database"'
VERSION='renewed-free-v2-html-guard'
UTC=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(path,obj):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2));os.replace(tmp,path)
def digest(b):return hashlib.sha256(b).hexdigest()
def excluded(url):return any(x in str(url).lower() for x in EXCLUDED)
def norm(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).strip()
def words(s):return set(norm(s).split())
class Page(HTMLParser):
    def __init__(self):super().__init__();self.out=[];self.links=[];self.meta={};self.skip=0;self.headings=[];self.in_heading=False
    def handle_starttag(self,t,a):
        a=dict(a)
        if re.fullmatch(r'h[1-6]',t) or t=='title':self.in_heading=True
        if t in ('script','style','noscript'):self.skip+=1
        if t in ('a','link') and a.get('href'):self.links.append((a['href'],a.get('type','')))
        if t=='meta':self.meta[(a.get('name') or a.get('property') or '').lower()]=a.get('content','')
        if t in ('p','div','h1','h2','h3','section','br','article','title'):self.out.append('\n')
    def handle_endtag(self,t):
        if re.fullmatch(r'h[1-6]',t) or t=='title':self.in_heading=False
        if t in ('script','style','noscript'):self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip:self.out.append(d)
        if self.in_heading:self.headings.append(d)

def jats_structure(data):
    import xml.etree.ElementTree as ET
    try:
        root=ET.fromstring(data)
        local=lambda e:e.tag.rsplit('}',1)[-1]
        body=next((e for e in root.iter() if local(e)=='body'),None)
        refs=next((e for e in root.iter() if local(e)=='ref-list'),None)
        return dict(body_present=body is not None,body_characters=len(' '.join(body.itertext())) if body is not None else 0,
          body_paragraphs=sum(local(e)=='p' for e in body.iter()) if body is not None else 0,
          reference_entries=sum(local(e)=='ref' for e in refs.iter()) if refs is not None else 0)
    except Exception:return {}

def assess(work,text,kind='pdf',url='',headings=None,structure=None):
    front=text[:16000] if kind!='pdf' else '\f'.join(text.split('\f')[:2])[:18000]
    target=words(work.get('title_r',''));title_match=len(target&words(front))/max(1,len(target))
    try:authors=[a.get('family','') for a in json.loads(work.get('author_r') or '[]')]
    except (ValueError,TypeError):authors=[]
    author_matches=[a for a in authors if norm(a) and norm(a) in norm(front)]
    doi=work.get('doi_r','');doi=doi if doi and doi!='NA' else ''
    doi_front=bool(doi and doi.lower() in front.lower())
    year=str(work.get('year_r',''));year_present=bool(year and year!='NA' and year in front)
    markers={k:bool(re.search(p,text,re.I)) for k,p in {
      'methods':r'\b(methods?|methodology|participants|materials and methods)\b',
      'results':r'\b(results|findings)\b','discussion':r'\b(discussion|conclusions?|general discussion)\b',
      'references':r'\b(references|bibliography|literature cited)\b'}.items()}
    challenge=bool(re.search(r'(verify (?:that )?you are human|access denied|captcha|checking your browser|enable javascript and cookies)',text[:4000],re.I))
    supplement=bool(re.search(r'^\s*(supporting information|supplementary (?:materials?|information)|supplemental (?:materials?|information))',front[:800],re.I))
    identity=title_match>=.75 and (doi_front or bool(author_matches))
    # All section markers + substantial body needed; never length alone. Short notes stay partial.
    citation_shell=bool(re.search(r'(/reference/|referencespapers|/articlecitations| - References - )',url+' '+text[:1500],re.I))
    headings=headings or []
    heading_markers={k:any(re.search(p,h,re.I) for h in headings) for k,p in {
      'methods':r'\b(methods?|methodology|participants|materials and methods)\b',
      'results':r'\b(results|findings)\b','discussion':r'\b(discussion|conclusions?)\b',
      'references':r'\b(references|bibliography|literature cited)\b'}.items()}
    body_structure=(kind in ('pdf','docx') or all(heading_markers.values()))
    structure=structure or {}
    structured_complete=kind=='xml' and structure.get('body_present') and structure.get('body_characters',0)>1000 and structure.get('body_paragraphs',0)>=2 and structure.get('reference_entries',0)>0
    complete=((all(markers.values()) and len(text)>9000 and body_structure) or structured_complete) and not challenge and not supplement and not citation_shell
    status='proposed_full_text' if identity and complete else 'partial'
    if (title_match<.4 and len(front)>500 and not challenge) or supplement or citation_shell:status='wrong_identity'
    evidence=[]
    # Excerpts confined to actual front matter, capped at 600 chars total.
    for line in front.splitlines():
        if any(a.lower() in line.lower() for a in author_matches) or (doi and doi.lower() in line.lower()) or len(words(line)&target)>=max(2,len(target)*.35):evidence.append(line.strip())
    excerpt=' | '.join(evidence)[:600]
    return dict(status=status,title_front_fraction=round(title_match,3),author_matches=author_matches,
      year_in_front=year_present,doi_in_front=doi_front,identity_evidence_excerpt=excerpt,
      completeness_note='Conservative automated acquisition proposal only; parent must inspect complete body, identity, year and references. '+json.dumps(dict(section_markers=markers,characters=len(text),challenge=challenge,supplement=supplement,citation_shell=citation_shell,heading_markers=heading_markers,jats_structure=structure)),parent_verification_required=True)

class Acquisition:
    def __init__(self,w,attempt):
        self.w=w;self.attempt=attempt;self.start=time.monotonic();self.deadline=self.start+90
        self.dir=TEXTS/w['file_key']/attempt;self.dir.mkdir(parents=True,exist_ok=False)
        self.logs=PRIVATE/w['file_key']/attempt;self.logs.mkdir(parents=True,exist_ok=True)
        self.routes=[];self.candidates=[];self.seen=set();self.promising=[];self.exposures=[];self.search_cache={}
        self.session=requests.Session();self.session.headers['User-Agent']='Mozilla/5.0 (compatible; primary-text-acquisition/1.0)'
    def remain(self):return self.deadline-time.monotonic()
    def request(self,url,route):
        if self.remain()<1 or not url or excluded(url) or url in self.seen:return None
        self.seen.add(url);rec=dict(route=route,url=url,retrieved_at=UTC());self.routes.append(rec)
        try:
            r=self.session.get(url,timeout=(min(3,max(.5,self.remain())),min(7,max(.5,self.remain()))),allow_redirects=True,stream=True)
            rec.update(http_status=r.status_code,final_url=r.url)
            self.seen.add(r.url)
            if excluded(r.url):rec['outcome']='excluded_domain';return None
            if r.status_code!=200:rec['outcome']='http_failure';return None
            chunks=[];size=0
            for b in r.iter_content(65536):
                if self.remain()<0:raise TimeoutError('work budget exhausted')
                size+=len(b)
                if size>35_000_000:raise ValueError('35MB candidate limit')
                chunks.append(b)
            data=b''.join(chunks);rec['outcome']='retrieved';rec['bytes']=len(data)
            return data,r.url,r.headers.get('content-type','')
        except Exception as e:rec.update(outcome='request_error',error=type(e).__name__);return None
        finally:dump(self.logs/'routes.json',self.routes)
    def api(self,url,route):
        got=self.request(url,route)
        if got:
            try:return json.loads(got[0])
            except (ValueError,UnicodeError):self.routes[-1]['outcome']='invalid_json'
        return {}
    def candidate(self,data,url,ctype,route):
        if not data:return False
        h=digest(data)
        if any(c['sha256']==h for c in self.candidates):return False
        kind='pdf' if data.startswith(b'%PDF-') else 'docx' if data.startswith(b'PK') and ('word' in ctype or 'officedocument' in ctype) else 'xml' if b'<article' in data[:3000] and (b'<body' in data or b'<article-title' in data) else 'html'
        idx=len(self.candidates)+1;path=self.dir/f'{idx:02d}_{h[:12]}.{kind}';path.write_bytes(data)
        text='';parser='';headings=[]
        try:
            if kind=='pdf':
                p=subprocess.run(['pdftotext','-layout',str(path),'-'],capture_output=True,timeout=max(1,min(8,self.remain())))
                text=p.stdout.decode(errors='replace');parser='pdftotext -layout'
            elif kind=='docx':
                with zipfile.ZipFile(path) as z:text=re.sub('<[^>]+>',' ',z.read('word/document.xml').decode())
                parser='zipfile + word/document.xml'
            else:
                p=Page();p.feed(data.decode('utf-8',errors='replace'));text=html.unescape(' '.join(p.out));headings=p.headings;parser='stdlib.HTMLParser (complete source retained)'
                if kind=='xml':parser='stdlib.HTMLParser JATS body and ref-list retained'
        except Exception as e:parser='parse_error:'+type(e).__name__
        tp=path.with_suffix(path.suffix+'.txt');tp.write_text(text)
        item=dict(filepath=str(path.relative_to(BASE)),text_filepath=str(tp.relative_to(BASE)),sha256=h,url=url,
                  retrieved_at=UTC(),parser=parser,route=route,**assess(self.w,text,kind,url,headings,jats_structure(data) if kind=='xml' else None))
        self.candidates.append(item)
        dump(self.logs/'candidates.json',self.candidates)
        return item['status']=='proposed_full_text'
    def visit(self,url,route,depth=0):
        # OSF/PsyArXiv's public API avoids a JS-only preprint landing page.
        osfid=re.search(r'(?:osf\.io/preprints/(?:psyarxiv/)?|psyarxiv\.com/)([a-z0-9]+)',url,re.I)
        if osfid and depth==0:
            j=self.api('https://api.osf.io/v2/preprints/'+osfid.group(1)+'/','osf_preprint_api')
            relation=j.get('data',{}).get('relationships',{}).get('primary_file',{}).get('links',{}).get('related',{}).get('href')
            if relation:
                f=self.api(relation,'osf_primary_file_api');download=f.get('data',{}).get('links',{}).get('download')
                if download and self.visit(download,'osf_primary_download',depth+1):return True
        got=self.request(url,route)
        if not got:return False
        data,final,ctype=got
        if self.candidate(data,final,ctype,route):return True
        if data.startswith(b'%PDF-') or depth>=1:return False
        p=Page()
        try:p.feed(data.decode(errors='replace'))
        except Exception:return False
        links=[]
        for key in ('citation_pdf_url','wkhealth_pdf_url'):
            if p.meta.get(key):links.append(p.meta[key])
        links.extend(u for u,t in p.links if 'pdf' in t or re.search(r'(\.pdf(?:[?#]|$)|/download/|/bitstream/|/doi/(?:pdf|epdf)/)',u,re.I))
        for u in list(dict.fromkeys(links))[:3]:
            u=urllib.parse.urljoin(final,u);self.promising.append(u)
            if self.visit(u,route+':linked_document',depth+1):return True
        return False
    def execute(self):
        doi=self.w.get('doi_r','');doi=doi if doi and doi!='NA' else ''
        title=self.w.get('title_r','');urls=[]
        if doi:
            oa=self.api('https://api.openalex.org/works/https://doi.org/'+urllib.parse.quote(doi,safe='/'),'openalex_locations')
        else:
            j=self.api('https://api.openalex.org/works?search='+urllib.parse.quote(title)+'&per-page=2','openalex_title')
            hits=j.get('results',[]);oa=next((x for x in hits if len(words(title)&words(x.get('title','')))/max(1,len(words(title)))>.8),{})
        locations=oa.get('locations',[])
        # Repository PDFs first; no duplicate unchanged endpoints.
        locations=sorted(locations,key=lambda l:(not (l.get('source') or {}).get('type')=='repository',not bool(l.get('pdf_url'))))
        for loc in locations:
            if loc.get('pdf_url'):urls.append((loc['pdf_url'],'openalex_pdf'))
            elif loc.get('landing_page_url') and loc.get('is_oa'):urls.append((loc['landing_page_url'],'openalex_repository_or_oa'))
        if self.w.get('url_r') not in (None,'','NA'):urls.append((self.w['url_r'],'supplied_url'))
        for url,route in urls[:5]:
            if self.visit(url,route):return self.result()
        # Europe PMC lookup exposes both PMCID and free full-text locations.
        if self.remain()>25:
            q=('DOI:'+doi) if doi else ('TITLE:"'+title+'"')
            ep=self.api('https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&query='+urllib.parse.quote(q),'europe_pmc_lookup')
            for hit in ep.get('resultList',{}).get('result',[])[:2]:
                pmc=hit.get('pmcid')
                if pmc:
                    for u,route in [('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/fullTextXML','europe_pmc_xml'),('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='+pmc+'&rettype=xml','ncbi_eutils_xml_bypass')]:
                        if self.visit(u,route):return self.result()
        if doi and self.remain()>20:
            up=self.api('https://api.unpaywall.org/v2/'+urllib.parse.quote(doi,safe='/')+'?email=unpaywall@impactstory.org','unpaywall')
            for loc in up.get('oa_locations',[])[:3]:
                u=loc.get('url_for_pdf') or loc.get('url')
                if u and self.visit(u,'unpaywall_location'):return self.result()
        if doi and self.remain()>25:
            cr=self.api('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='/'),'crossref_primary_links')
            for link in cr.get('message',{}).get('link',[])[:3]:
                if link.get('URL') and self.visit(link['URL'],'crossref_primary_document'):return self.result()
        if doi and self.remain()>20:
            if self.visit('https://doi.org/'+doi,'doi_landing'):return self.result()
        # Free search is guaranteed before the optional skill chain can consume remaining budget.
        if self.remain()>10:
            try:
                from ddgs import DDGS
                query='"'+title+'" pdf'+EXCLUSIONS
                started=UTC();self.search_cache[query]=[];hits=DDGS(timeout=min(6,max(1,int(self.remain()-2)))).text(query,max_results=7,backend='bing') or [];self.search_cache[query]=hits
                self.routes.append(dict(route='free_title_search',query=query,retrieved_at=started,outcome='search_returned',hits=len(hits)))
                for hit in hits:
                    u=hit.get('href','');snippet=hit.get('body','')+' '+hit.get('title','')
                    if re.search(r'FORRT|FReD database',snippet,re.I):self.exposures.append(dict(url=u,note='Search snippet contained FORRT/FReD; excluded from primary evidence; no coding used'));continue
                    if excluded(u):continue
                    if len(words(title)&words(hit.get('title','')))/max(1,len(words(title)))<.45:continue
                    if self.visit(u,'free_title_search_primary'):return self.result()
            except Exception as e:self.routes.append(dict(route='free_title_search',outcome='search_error',error=type(e).__name__,retrieved_at=UTC()))
        # Concrete PDF URL archive fallback, never a generic DOI-page archive.
        if self.remain()>8:
            for u in list(dict.fromkeys(self.promising+[u for u,r in urls if '.pdf' in u or '/pdf/' in u]))[:2]:
                j=self.api('https://archive.org/wayback/available?url='+urllib.parse.quote(u,safe=''),'wayback_availability')
                snap=j.get('archived_snapshots',{}).get('closest',{})
                if snap.get('available'):
                    if self.deadline==self.start+90:self.deadline+=30
                    archive=snap['url'].replace('http://','https://',1);archive=re.sub(r'/web/(\d+)/',r'/web/\1id_/',archive)
                    if self.visit(archive,'wayback_actual_bytes'):return self.result()
        if doi and self.remain()>6:self.skill(doi,title)
        return self.result()
    def skill(self,doi,title):
        # Local import wrapper: explicit billing/browser disable; all caches local/private.
        # Suppress fetchpdf's optional dotenv credential-file discovery.
        import dotenv
        dotenv.load_dotenv=lambda *a,**kw:False
        dotenv.find_dotenv=lambda *a,**kw:''
        sys.path.insert(0,str(SKILL));import download_paper as dp
        dp.serpapi_keys=lambda keys:[]
        dp.load_key_file=lambda:{}
        dp.WEB_RESULTS=7;dp.WEB_MAX_PDFS=2
        import ddgs
        original_ddgs=ddgs.DDGS
        owner=self
        class SingleEngineSearch:
            def __init__(self,*a,**kw):self.impl=original_ddgs(*a,**kw)
            def text(self,*a,**kw):
                kw['backend']='bing'
                hits=self.impl.text(*a,**kw) or [];safe=[]
                for hit in hits:
                    if excluded(hit.get('href','')):continue
                    if re.search(r'FORRT|FReD database',hit.get('body','')+' '+hit.get('title',''),re.I):
                        owner.exposures.append(dict(url=hit.get('href',''),note='Skill search snippet contained FORRT/FReD; excluded without using any coding'))
                    else:safe.append(hit)
                return safe
        ddgs.DDGS=SingleEngineSearch
        origsearch=dp.web_search
        def search_once(q,c):
            query=q+EXCLUSIONS
            if query in self.search_cache:return [h for h in self.search_cache[query] if not excluded(h.get('href','')) and not re.search(r'FORRT|FReD database',h.get('body','')+' '+h.get('title',''),re.I)]
            hits=[h for h in origsearch(query,c) if not excluded(h.get('href',''))]
            self.search_cache[query]=hits
            self.routes.append(dict(route='skill_free_search',query=query,outcome='search_returned',hits=len(hits),retrieved_at=UTC()))
            return hits
        dp.web_search=search_once
        origfetch=dp.fetch_url
        def guarded(url,*a,**kw):
            if excluded(url) or url in self.seen:return None
            self.seen.add(url);kw['timeout']=min(6,max(1,self.remain()))
            data=origfetch(url,*a,**kw)
            self.routes.append(dict(route='skill_http',url=url,retrieved_at=UTC(),outcome='bytes' if data else 'failed'))
            if data and data.startswith(b'%PDF-'):self.candidate(data,url,'application/pdf','skill_http')
            return data
        dp.fetch_url=guarded
        # Trace actual chain endpoints and suppress unchanged misses/challenges.
        original_request=requests.sessions.Session.request
        def traced(session,method,url,*args,**kwargs):
            if excluded(url) or str(url) in self.seen:
                raise requests.RequestException('Excluded or already attempted endpoint')
            self.seen.add(str(url))
            rec=dict(route='skill_fetchpdf_http',url=str(url),retrieved_at=UTC())
            self.routes.append(rec)
            try:
                kwargs['timeout']=min(5,max(.5,self.remain()))
                response=original_request(session,method,url,*args,**kwargs)
                self.seen.add(response.url)
                rec.update(http_status=response.status_code,final_url=response.url,outcome='retrieved' if response.status_code==200 else 'http_failure')
                if excluded(response.url):raise requests.RequestException('Excluded redirect')
                if response.status_code==200 and 'pdf' in response.headers.get('content-type',''):
                    data=response.content
                    if len(data)<35_000_000 and data.startswith(b'%PDF-'):self.candidate(data,response.url,'application/pdf','skill_fetchpdf_http')
                return response
            except Exception as e:
                rec.update(outcome='request_error',error=type(e).__name__);raise
        requests.sessions.Session.request=traced
        origchain=dp.fetchpdf_download
        def chain(*a,**kw):
            signal.setitimer(signal.ITIMER_REAL,min(8,max(1,self.remain()-3)))
            try:return origchain(*a,**kw)
            except TimeoutError:return False
            finally:signal.setitimer(signal.ITIMER_REAL,max(1,self.remain()))
        dp.fetchpdf_download=chain
        signal.signal(signal.SIGALRM,lambda *a:(_ for _ in ()).throw(TimeoutError('free-chain budget')))
        signal.setitimer(signal.ITIMER_REAL,max(1,self.remain()))
        try:
            path,candidates=dp.download_paper(doi,title=title,cache_dir=str(self.logs/'skill_cache'),use_browser=False,use_playwright=False)
            if path:self.candidate(pathlib.Path(path).read_bytes(),'https://doi.org/'+doi,'application/pdf','download_paper_free_chain')
            self.routes.append(dict(route='download_paper_free_chain',outcome='downloaded' if path else 'not_found',candidates=candidates,retrieved_at=UTC(),scholar_disabled=True))
        except Exception as e:self.routes.append(dict(route='download_paper_free_chain',outcome='bounded_failure',error=type(e).__name__,retrieved_at=UTC(),scholar_disabled=True))
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
            requests.sessions.Session.request=original_request
            ddgs.DDGS=original_ddgs
    def private_artifacts(self):
        return [dict(filepath=str(p.relative_to(BASE)),sha256=digest(p.read_bytes()),parser='intact skill-cache artifact; see candidate verification or independently inspect',parent_verification_required=True)
                for p in sorted((self.logs/'skill_cache').rglob('*')) if p.is_file() and p.suffix.lower() in ('.pdf','.html','.xml','.docx','.txt')]
    def result(self):
        best=next((c for c in self.candidates if c['status']=='proposed_full_text'),None)
        status='proposed_full_text' if best else 'partial' if any(c['status']=='partial' for c in self.candidates) else 'wrong_identity' if self.candidates else 'not_found'
        return dict(file_key=self.w['file_key'],work_key=self.w.get('work_key'),input_sha256=digest(json.dumps(self.w,sort_keys=True).encode()),attempt_id=self.attempt,runner_version=VERSION,runner_sha256=digest((HERE/'acquire.py').read_bytes()),status=status,candidates=self.candidates,additional_private_artifacts=self.private_artifacts(),routes=self.routes,provenance_exposure=self.exposures,elapsed_seconds=round(time.monotonic()-self.start,2),completed_at=UTC(),acquisition_only=True,parent_verification_required=True)

def worker(key,attempt):
    works=json.loads((HERE/'works.json').read_text());w=next(w for w in works if w['file_key']==key)
    a=Acquisition(w,attempt)
    finished=threading.Event()
    def enforce_budget():
        while not finished.is_set():
            if time.monotonic()>=a.deadline:
                r=json.loads(json.dumps(a.result()));r['budget_exhausted']=True
                dump(a.logs/'result.json',r)
                os._exit(0)  # Parent owns and reaps this process group and its children.
            finished.wait(min(.25,max(.01,a.deadline-time.monotonic())))
    threading.Thread(target=enforce_budget,daemon=True).start()
    try:r=a.execute()
    except Exception as e:
        r=a.result();r['infrastructure_failure']=type(e).__name__
    finished.set()
    dump(a.logs/'result.json',r)

OWNED={};LOCK=threading.Lock()
def run_one(w):
    attempt=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    logdir=PRIVATE/w['file_key']/attempt;logdir.mkdir(parents=True,exist_ok=False)
    with (logdir/'worker.log').open('xb') as log:
        env=os.environ.copy();env['TMPDIR']=str(logdir);env['PYTHONDONTWRITEBYTECODE']='1';env['XDG_CACHE_HOME']=str(logdir/'cache')
        # No service credentials used by the chain; avoid reading credential files.
        for k in list(env):
            if any(s in k.upper() for s in ('SERPAPI','ELSEVIER','CORE_API','OPENALEX_API','API_KEY','APIKEY')):env.pop(k,None)
        p=subprocess.Popen([sys.executable,str(HERE/'acquire.py'),'--worker',w['file_key'],attempt],stdout=log,stderr=log,env=env,start_new_session=True)
        with LOCK:OWNED[p.pid]=p
        timed_out=False
        try:p.wait(timeout=125)
        except subprocess.TimeoutExpired:timed_out=True
        finally:
            # Kill/reap exact owned group, including any lingering parser/downloader children.
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGKILL);p.wait()
            try:os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            with LOCK:OWNED.pop(p.pid,None)
    rp=logdir/'result.json'
    if rp.exists():return json.loads(rp.read_text())
    # Recovery preserves all candidate artifacts even on a hard process timeout.
    cp=logdir/'candidates.json';c=json.loads(cp.read_text()) if cp.exists() else []
    r=dict(file_key=w['file_key'],work_key=w.get('work_key'),input_sha256=digest(json.dumps(w,sort_keys=True).encode()),attempt_id=attempt,runner_version=VERSION,status='partial' if c else 'not_found',candidates=c,routes=json.loads((logdir/'routes.json').read_text()) if (logdir/'routes.json').exists() else [],elapsed_seconds=125 if timed_out else 0,completed_at=UTC(),infrastructure_failure='owned_worker_timeout' if timed_out else 'worker_exit_'+str(p.returncode),acquisition_only=True,parent_verification_required=True,log_filepath=str((logdir/'worker.log').relative_to(BASE)))
    dump(rp,r);return r

def main():
    works=json.loads((HERE/'works.json').read_text());assert len(works)==339
    assert len({w['file_key'] for w in works})==339
    for w in works:assert not any(k.endswith('_o') for k in w)
    done={};out=HERE/'results.jsonl'
    if out.exists():
        for line in out.read_text().splitlines():
            if line.strip():
                r=json.loads(line);done[(r['file_key'],r['input_sha256'])]=r
    # Reconcile durable per-attempt records if interruption preceded JSONL append.
    for w in works:
        identity=(w['file_key'],digest(json.dumps(w,sort_keys=True).encode()))
        if identity in done:continue
        for rp in sorted((PRIVATE/w['file_key']).glob('*/result.json')):
            r=json.loads(rp.read_text())
            if r.get('input_sha256')==identity[1]:
                with out.open('a') as stream:
                    stream.write(json.dumps(r,ensure_ascii=False)+'\n');stream.flush();os.fsync(stream.fileno())
                done[identity]=r;break
    pending=[w for w in works if (w['file_key'],digest(json.dumps(w,sort_keys=True).encode())) not in done]
    completed=[done[(w['file_key'],digest(json.dumps(w,sort_keys=True).encode()))] for w in works if (w['file_key'],digest(json.dumps(w,sort_keys=True).encode())) in done]
    failures=0;last=time.monotonic();stopped=False
    def checkpoint(state):
        dump(HERE/'progress.json',dict(updated_at=UTC(),runner_version=VERSION,total_works=len(works),completed_work_records=len(completed),remaining_works=len(works)-len(completed),counts=dict(collections.Counter(r['status'] for r in completed)),state=state,acquisition_only=True,parent_verification_required=True,queue_complete=len(completed)==len(works),scientific_verification_complete=False))
    checkpoint('running')
    pool=cf.ThreadPoolExecutor(max_workers=2);futures={}
    try:
        it=iter(pending)
        for w in list(pending[:2]):futures[pool.submit(run_one,w)]=w;next(it)
        while futures:
            ready,_=cf.wait(futures,timeout=10,return_when=cf.FIRST_COMPLETED)
            if not ready and time.monotonic()-last>300:stopped=True;break
            for f in ready:
                w=futures.pop(f);r=f.result()
                with out.open('a') as stream:stream.write(json.dumps(r,ensure_ascii=False)+'\n');stream.flush();os.fsync(stream.fileno())
                completed.append(r);last=time.monotonic();failures=failures+1 if r.get('infrastructure_failure') else 0
                checkpoint('running');print(json.dumps(dict(completed=len(completed),total=339,file_key=w['file_key'],status=r['status'],elapsed=r['elapsed_seconds'])),flush=True)
                if failures>=10:stopped=True;break
                nw=next(it,None)
                if nw is not None:futures[pool.submit(run_one,nw)]=nw
            if stopped:break
    finally:
        if stopped:
            with LOCK:
                for p in OWNED.values():
                    try:os.killpg(p.pid,signal.SIGTERM)
                    except ProcessLookupError:pass
        pool.shutdown(wait=True,cancel_futures=True)
        checkpoint('stopped_for_infrastructure_diagnosis' if stopped else 'acquisition_queue_complete')
if __name__=='__main__':
    if '--worker' in sys.argv:worker(sys.argv[2],sys.argv[3])
    elif '--self-test' in sys.argv:
        w=dict(title_r='A specific replication study',doi_r='10.1234/example',author_r='[{"family":"Smith"}]',year_r='2020')
        good='A specific replication study\nSmith 2020 10.1234/example\nMethods\n'+'body '*2500+'\nResults\nDiscussion\nReferences'
        assert assess(w,good)['status']=='proposed_full_text'
        assert assess(w,'Other unrelated article\n'+('unrelated '*1000)+' References 10.1234/example')['status']!='proposed_full_text'
        assert assess(w,'A specific replication study Smith 2020 10.1234/example Abstract')['status']=='partial'
        assert assess(w,'CAPTCHA verify you are human')['status']!='proposed_full_text'
        assert assess(w,'Supplementary information\n'+good)['status']=='wrong_identity'
        assert assess(w,'A specific replication study Smith 2020 '+('abstract '*2000))['status']=='partial'
        assert assess(w,good,'html','https://example.org/reference/referencespapers')['status']=='wrong_identity'
        assert assess(w,good,'html')['status']=='partial'
        assert assess(w,good,'html',headings=['Methods','Results','Discussion','References'])['status']=='proposed_full_text'
        xml=('<article><body><p>'+('letter text '*100)+'</p><p>'+('continued '*100)+'</p></body><back><ref-list><ref>source</ref></ref-list></back></article>').encode()
        short='A specific replication study Smith 2020 10.1234/example '+('letter text '*200)
        assert assess(w,short,'xml',structure=jats_structure(xml))['status']=='proposed_full_text'
        assert assess(w,short,'xml',structure=jats_structure(b'<article><front><abstract>abstract</abstract></front></article>'))['status']=='partial'
        print('PASS: full-body proposal, cited DOI, shell, challenge, supplement and abstract-only guards')
    else:
        import fcntl
        with (PRIVATE/'queue.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            main()
