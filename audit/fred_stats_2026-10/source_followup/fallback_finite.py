#!/usr/bin/env python3
"""Finite targeted fallback for the 11 non-DOI/reference-only sources.

Rules (from the authorised follow-up brief):
- one title/reference web search or metadata lookup per source
- max 2 NEW distinct download URLs per source, no repeating old endpoints
- <=60 s per source; never just classify no_identifier without a real attempt
- corrections of prior records preserve prior evidence with traceable reasons
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

SF = "/home/lukas/.t3/worktrees/fred-data/audit-fred-stats-2026-10/audit/fred_stats_2026-10/source_followup"
SCRATCH = "/home/lukas/.cache/fred-source-followup-20261029"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}]{msg}", flush=True)

def norm(t):
    return " ".join(re.findall(r"[^\W_]+", (t or "").lower()))

def frac(title, text):
    want = norm(title).split()
    have = set(norm(text[:6000]).split())
    return sum(1 for w in want if w in have) / len(want) if want else 0.0

def fetch(url, timeout=40, accept="application/pdf,*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.geturl(), r.headers.get("Content-Type", "")

def run(cmd, timeout=45):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, errors="replace", start_new_session=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        try:
            import signal
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
        return None, out, err

def pdf_pages(path):
    code, out, _ = run(["pdfinfo", path], 20)
    if code == 0:
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        if m:
            return int(m.group(1))

def pdf_text(path):
    code, out, _ = run(["pdftotext", "-layout", path, "-"], 60)
    return out if code == 0 else ""

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

ABSTRACT_HOSTS = ("pubmed.ncbi.nlm.nih.gov", "researchgate.net", "scholar.google.")

def verify_pdf(path, title, key):
    with open(path, "rb") as f:
        if f.read(5) != b"%PDF-":
            return False, {}, "not a PDF"
    if os.path.getsize(path) < 20000:
        return False, {}, "too small"
    pages = pdf_pages(path)
    text = pdf_text(path)
    if not text.strip():
        return False, {"pages": pages}, "no extractable text"
    front = "\n".join(text.split("\f")[:3])
    f = frac(title, front)
    ev = {"pages": pages, "title_fraction_front3": round(f, 3), "chars": len(text)}
    if pages is not None and pages < 2:
        return False, ev, "single-page preview"
    if f >= 0.8:
        return True, ev, "title match on front pages"
    return False, ev, f"identity check failed (title {f:.0%})"

def html_to_text(html):
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?is)<br\s*/?>", "\n", html)
    html = re.sub(r"(?is)</(p|div|h[1-6]|li|tr|section)>", "\n", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'")):
        text = text.replace(a, b)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def verify_html(text, title, url):
    host = urllib.parse.urlparse(url or "").netloc.lower()
    f = frac(title, text)
    methods = bool(re.search(r"(?mi)^[ \t]*(methods?|methodology|materials and methods)[ \t]*:?[ \t]*$", text))
    results = bool(re.search(r"(?mi)^[ \t]*(results?|findings)[ \t]*:?[ \t]*$", text))
    ev = {"title_fraction": round(f, 3), "chars": len(text),
          "methods_heading": methods, "results_heading": results, "host": host}
    if any(h in host for h in ABSTRACT_HOSTS):
        return False, ev, f"abstract/metadata host rejected ({host})"
    ok = len(text) >= 12000 and f >= 0.6 and methods and results and \
        bool(re.search(r"(?mi)^[ \t]*(references|bibliography)[ \t]*:?[ \t]*$", text))
    return ok, ev, "full-text HTML" if ok else \
        f"HTML not article body (chars={len(text)}, title={f:.0%})"

def web_search(title, extra):
    """One search per source, returns up to 5 candidate URLs."""
    q = urllib.parse.quote(f"{title} {extra} pdf")
    code, out, err = run(["python3", "-c", f"""
import json,urllib.request,urllib.parse
q=urllib.parse.quote({q!r})
url='https://html.duckduckgo.com/html/?q='+q
req=urllib.request.Request(url,headers={{'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) Chrome/122.0'}})
html=urllib.request.urlopen(req,timeout=20).read().decode('utf-8','replace')
import re
res=[]
for m in re.finditer(r'class="result__url"\\s+href="([^"]+)"',html):
    u=m.group(1)
    if u.startswith('//duckduckgo.com/l/?uddg='):
        u=urllib.parse.unquote(re.split(r'uddg=',u)[1].split('&')[0])
    res.append(u)
print(json.dumps(res[:6]))
"""])
    if code != 0:
        return []
    try:
        return json.loads(out)
    except Exception:
        return []

def accept_body(body, final, ctype, key, title):
    """Save + verify one downloaded body; returns (artifact,text,ev,reason)."""
    if body.startswith(b"%PDF-"):
        pdf_path = os.path.join(SCRATCH, "pdfs", f"{key}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(body)
        ok, ev, reason = verify_pdf(pdf_path, title, key)
        if not ok:
            os.unlink(pdf_path)
            return None, None, ev, reason
        text = pdf_text(pdf_path)
        text_path = os.path.join(SCRATCH, "texts", f"{key}.txt")
        with open(text_path, "w") as f:
            f.write(text)
        ev.update({"pdf_sha256": sha256(pdf_path), "text_sha256": sha256(text_path)})
        return pdf_path, text_path, ev, "fallback: verified PDF"
    head = body[:400].lstrip().lower()
    if head.startswith((b"<?xml", b"<article")) or "xml" in (ctype or "").lower():
        xml = body.decode("utf-8", "replace")
        xml = re.sub("(?is)<(ref-list|back)[^>]*>", "\n", xml)
        xml = re.sub("(?is)<(p|sec|title|td|th|caption|label)[^>]*>", "\n", xml)
        text = re.sub("(?s)<[^>]+>", " ", xml)
        text = re.sub(r"[ \t]+", " ", text)
        ok, ev, reason = verify_html(text, title, final)
        if ok:
            xml_path = os.path.join(SCRATCH, "html", f"{key}.xml")
            with open(xml_path, "wb") as f:
                f.write(body)
            text_path = os.path.join(SCRATCH, "texts", f"{key}.txt")
            with open(text_path, "w") as f:
                f.write(text)
            ev.update({"xml_sha256": sha256(xml_path), "text_sha256": sha256(text_path)})
            return xml_path, text_path, ev, "fallback: full-text JATS XML"
        return None, None, ev, reason
    if "html" in (ctype or "").lower() or head.startswith((b"<!doctype", b"<html")):
        try:
            html = body.decode("utf-8", "replace")
        except Exception:
            return None, None, {}, "undecodable HTML"
        text = html_to_text(html)
        ok, ev, reason = verify_html(text, title, final)
        if not ok:
            return None, None, ev, reason
        html_path = os.path.join(SCRATCH, "html", f"{key}.html")
        with open(html_path, "w") as f:
            f.write(html)
        text_path = os.path.join(SCRATCH, "texts", f"{key}.txt")
        with open(text_path, "w") as f:
            f.write(text)
        ev.update({"html_sha256": sha256(html_path), "text_sha256": sha256(text_path)})
        return html_path, text_path, ev, "fallback: full-text HTML"
    return None, None, {"ctype": ctype}, f"not PDF/HTML ({ctype})"

def wayback(url):
    try:
        body, _, _ = fetch("https://archive.org/wayback/available?url=" +
                           urllib.parse.quote(url, safe=""), timeout=15,
                           accept="application/json")
        snap = json.loads(body).get("archived_snapshots", {}).get("closest")
        if snap and snap.get("available"):
            return re.sub(r"/web/(\d+)/", r"/web/\1id_/", snap["url"], count=1)
    except Exception:
        pass
    return None

# ---------------------------------------------------------------- routes ----
def osf_files(guid):
    """Metadata lookup: OSF file listing for one GUID (node or deleted-file)."""
    try:
        body, _, _ = fetch(f"https://api.osf.io/v2/guids/{guid}/", timeout=20,
                           accept="application/json")
        data = json.loads(body)["data"]["links"]["self"]
        m = re.search(r"/nodes/([a-z0-9]+)/", data)
        if not m:
            return {"lookup": f"guid {guid}: not a node (deleted file),"
                    f" tried_url={data}", "files": []}
        body, _, _ = fetch(f"https://api.osf.io/v2/nodes/{m.group(1)}/files/osfstorage/?page%5Bsize%5D=100",
                           timeout=20, accept="application/json")
        out = []
        for item in json.loads(body)["data"]:
            links = item.get("links", {})
            dl = links.get("download") or item.get("attributes", {}).get("download")
            out.append({"kind": item["attributes"].get("kind"),
                        "name": item["attributes"].get("name"),
                        "size": item["attributes"].get("size"),
                        "download": dl})
        return {"lookup": f"guid {guid}: node {m.group(1)}", "files": out}
    except Exception as e:
        return {"lookup": f"guid {guid}: {type(e).__name__}: {e}", "files": []}

ROUTES = {
    # Catalogued sources are keyed by their acquisition key. Each returns a
    # list of confidence-ranked (url, note) candidates, at most the first 2
    # fresh (not previously used) ones being downloaded.
    "d174d412261234f92287a43f": lambda t, ref: [
        (u, "search") for u in web_search(t, "thekeep.eiu.edu")[:2]
        if u and "thekeep.eiu.edu" in u
    ] + [("https://thekeep.eiu.edu/cgi/viewcontent.cgi?article=5025&context=theses",
          "bepress viewcontent pattern")],
    "dc2be5699ecb95777c8d3a0d": lambda t, ref: [
        (u, "search") for u in web_search(t, "thekeep.eiu.edu")[:2]
        if u and "thekeep.eiu.edu" in u
    ] + [("https://thekeep.eiu.edu/cgi/viewcontent.cgi?article=4783&context=theses",
          "bepress viewcontent pattern")],
    "5dca96fa93c1b207f21c0ae9": lambda t, ref: [
        ("https://helda.helsinki.fi/handle/10138/576172", "HELDA item page (old endpoint was a direct bitstream)")],
    "0e6d6370e935472b9e5ccadd": lambda t, ref: [
        (u, "search") for u in web_search(t, "Individual Differences Research")[:2]],
    "3c9dc4eb71655e6bb2680ec7": lambda t, ref: [
        ("https://digitalcommons.memphis.edu/cgi/viewcontent.cgi?article=3538&context=etd",
         "bepress viewcontent pattern"),
        ("https://digitalcommons.memphis.edu/cgi/viewcontent.cgi?article=3539&context=etd",
         "bepress viewcontent pattern, neighbour id")],
    "9bac021c36f78dc5c196ef94": lambda t, ref: [
        ("https://scholars.indianastate.edu/etds/2136", "referenced repository id"),
        ("https://scholars.indianastate.edu/cgi/viewcontent.cgi?article=2136&context=etds",
         "bepress viewcontent pattern")],
    "c0d05e32d65a048d722a1fef": lambda t, ref: [
        ("https://docs.google.com/document/d/10OKLI0-Kw2D7SDyLU_Ieql88gLtbnYGSyZhCBqsEAyk/export?format=pdf",
         "Google Docs public export")]
        + [(u, "search") for u in web_search(t, "replication")[:2]
           if "docs.google.com" not in u][:1],
    "c5e34edf1bf7307237d96f7c": lambda t, ref: [
        (u, "search") for u in web_search(t, "PsychFileDrawer OR osf")[:2]],
}

OSF_SOURCE_FILES = {
    "7d30e63912afd3f7f7aea3f6": ["zybuc", "u5d2y"],
    "8b09983689330d048ce1acf9": ["2vmgw", "mjfwp"],
    "e249db49ad0a6cbc2daa6e40": ["esw45", "g6fkp"],
}

def main():
    manifest = {s["key"]: s for s in json.load(open(os.path.join(SF, "missing_sources.json")))}
    only = set(sys.argv[1:])
    keys = [k for k in ["d174d412261234f92287a43f", "dc2be5699ecb95777c8d3a0d",
            "5dca96fa93c1b207f21c0ae9", "0e6d6370e935472b9e5ccadd",
            "7d30e63912afd3f7f7aea3f6", "3c9dc4eb71655e6bb2680ec7",
            "8b09983689330d048ce1acf9", "9bac021c36f78dc5c196ef94",
            "c0d05e32d65a048d722a1fef", "c5e34edf1bf7307237d96f7c",
            "e249db49ad0a6cbc2daa6e40"] if not only or k in only]
    results = {}
    for key in keys:
        src = manifest[key]
        title = src.get("title") or src["reference"][:120]
        ref = src["reference"]
        prior_path = os.path.join(SF, "acquisitions", f"{key}.json")
        prior = json.load(open(prior_path)) if os.path.exists(prior_path) else None
        log(f"== {key} :: {title[:70]}")
        started = time.time()
        tried_urls = [u for u in ((src.get("url") and [src["url"]]) or [])]
        if prior:
            tried_urls += [u for u in prior.get("attempted_routes", []) if u.startswith("http")]
        candidates, note = [], "no route"
        log_path = os.path.join(SCRATCH, "logs", f"fallback_{key}.log")
        loglines = [f"fallback for {key} ({prior['status'] if prior else 'no record'})"]

        if key in OSF_SOURCE_FILES:
            # metadata lookup: the OSF file listing for both GUIDs
            listings = [{"guid": g, **osf_files(g)} for g in OSF_SOURCE_FILES[key]]
            files = [f for l in listings for f in l["files"]]
            # pick real manuscript candidates first (title fragment/docx/pdf)
            frag = None
            mr = re.search(r"([A-Z][a-z]+)_(Journ\w+|Eur\w+)_", title)
            if mr:
                frag = mr.group(1)
            def score(f):
                n = (f["name"] or "").lower()
                if f["kind"] != "file":
                    return 9
                d = 0 if re.search(r"\.(docx?|pdf)\b", n) else 3
                if re.search(r"\.(zip|rdata|csv|xlsx|dta|txt|sav|dat|do|spv|r)\b", n):
                    d += 6
                if frag and frag.lower() not in n:
                    d += 2
                return d + (1 if f.get("size") and f["size"] > 20000 else 0)
            doclike = sorted(files, key=score)[:2]
            used = sum(l["files"] and 1 or 0 for l in listings)
            listings_note = "; ".join(l["lookup"] for l in listings)
            doc_names = "; ".join([os.path.basename((f.get("name") or "?")) + " (" + str(f.get("size")) + "B)" for l in listings for f in (l["files"] or [])])
            note = f"OSF file listing: {len(files)} files; {listings_note}"
            loglines.append(note)
            loglines.append(f"  files: {doc_names[:400]}")
            candidates = [(f["download"], f"osf file: {f['name']}") for f in doclike]
        else:
            candidates = ROUTES.get(key, lambda t, r: [])(
                title.rstrip(".") if len(title) > 15 else ref[:200], ref)
        # dedupe against previously used endpoints
        fresh, seen = [], set(tried_urls)
        seen_bases = {u.split("?")[0] for u in seen}
        for u, note_i in candidates:
            if not u:
                continue
            base = urllib.parse.urljoin(u, u.split("?")[0])
            keyb = u.split("?")[0]
            if u in seen or keyb in seen_bases:
                continue
            if len(fresh) >= 2:
                break
            seen.add(u); seen_bases.add(keyb)
            fresh.append((u, note_i))
        status_out = prior["status"] if prior else "no_identifier"
        new_routes, artifact = [], None
        for u, note_i in fresh:
            if time.time() - started > 60:
                loglines.append("60s budget exhausted")
                break
            loglines.append(f"try {u[:120]} ({note_i})")
            try:
                body, final, ctype = fetch(u)
                art, tp, ev, reason = accept_body(body, final, ctype, key, title.rstrip("."))
                loglines.append(f"  -> {reason} ev={json.dumps(ev)[:150]}")
                new_routes.append(u)
                if art:
                    artifact = (art, tp, ev, reason, final, note_i)
                    break
            except Exception as e:
                loglines.append(f"  -> {type(e).__name__}: {e}")
                new_routes.append(u)
        elapsed = round(time.time() - started, 1)
        loglines.append(f"elapsed {elapsed}s")
        with open(log_path, "w") as f:
            f.write("\n".join(loglines) + "\n")

        # ---- record update
        rec_out = dict(prior) if prior else None
        if artifact:
            art, tp, ev, reason, final, note_i = artifact
            if rec_out is None:
                rec_out = {"key": key, "doi": src.get("doi"), "reference": ref,
                           "status": "no_identifier", "attempted_routes": [],
                           "started_at": None, "finished_at": None,
                           "artifact_path": None, "text_path": None,
                           "source_url": src.get("url"), "identity_evidence": {},
                           "reason": "", "affected_sides": len(src["targets"]),
                           "title": title}
            rec_out.update(status="retrieved", artifact_path=art, text_path=tp,
                           identity_evidence=ev,
                           source_url=final, reason=reason,
                           classified_route=note_i,
                           finished_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"))
        else:
            if rec_out is None:
                rec_out = {"key": key, "doi": src.get("doi"), "reference": ref,
                           "status": "no_identifier", "attempted_routes": [],
                           "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                           "finished_at": None, "artifact_path": None,
                           "text_path": None, "source_url": src.get("url"),
                           "identity_evidence": {}, "reason": "",
                           "affected_sides": len(src["targets"]), "title": title}
            rec_out.update(finished_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                           fallback_attempted=len(new_routes) > 0,
                           fallback_routes=new_routes)
            if note.startswith("OSF file listing"):
                rec_out["reason"] = (rec_out.get("reason") or "") + \
                    f"; fallback: {note}"
            elif not new_routes:
                rec_out["reason"] = (rec_out.get("reason") or "") + \
                    "; fallback: no new distinct endpoint found (single search/metadata lookup done)"
            else:
                rec_out["reason"] = (rec_out.get("reason") or "") + \
                    f"; fallback: {len(new_routes)} new endpoint(s) tried, none verified as full text"
        tmp = prior_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(rec_out, f, indent=2)
        os.replace(tmp, prior_path)
        results[key] = {"status": rec_out["status"], "article": artifact is not None,
                        "elapsed": elapsed}
        log(f"   => {rec_out['status']} ({artifact is not None}) {elapsed}s")
    with open(os.path.join(SF, "fallbacks_run.json"), "w") as f:
        json.dump({"ran_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "results": results}, f, indent=2)

if __name__ == "__main__":
    main()
