#!/usr/bin/env python3
"""Batch acquisition runner for the FReD source follow-up (2026-10-29).

Reads missing_sources.json in manifest order and, for every source, runs the
download-paper skill's download_paper.py once, then a bounded fallback sweep of
at most two further distinct URLs. Writes one atomic acquisitions/<key>.json per
source plus progress.json heartbeat.

Paper bytes/texts live only under SCRATCH (ignored local SSD). No network keys
are read, printed or written; the metered SerpAPI route is disabled by forcing
its environment variables empty.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request

DOWNLOADER = "/home/lukas/agent-skills/download-paper/download_paper.py"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)
PRIMARY_TIMEOUT = 150
FALLBACK_TIMEOUT = 60
WORKERS = 6
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
CONTACT_EMAIL = "unpaywall@impactstory.org"   # replaced privately at startup
ABOUT_ME = "/home/lukas/.config/agent-instructions/about-me.md"


def load_contact_email():
    """Authorised work email, read privately and never logged."""
    try:
        text = open(ABOUT_ME, encoding="utf-8", errors="replace").read()
        m = re.search(r"Work email:\s*([\w.+-]+@[\w.-]+)", text)
        if m:
            return m.group(1)
    except OSError:
        pass
    return CONTACT_EMAIL


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def norm(text):
    return " ".join(re.findall(r"[^\W_]+", (text or "").lower()))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def title_fraction(title, text):
    """Share of title tokens present, in order-tolerant bag form."""
    want = norm(title).split()
    have = set(norm(text).split())
    if not want:
        return 0.0
    return sum(1 for w in want if w in have) / len(want)


def fetch(url, timeout=45, accept="application/pdf,*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.geturl(), resp.headers.get("Content-Type", "")


def run_cmd(cmd, timeout, env=None):
    """Run a command in its own process group; kill descendants on timeout."""
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, errors="replace", start_new_session=True, env=env)
    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out, err, False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
        return None, out, err, True


def pdf_pages(path):
    code, out, _, _ = run_cmd(["pdfinfo", path], 20)
    if code == 0:
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        if m:
            return int(m.group(1))
    return None


def pdf_text(path, layout=True):
    cmd = ["pdftotext"] + (["-layout"] if layout else []) + [path, "-"]
    code, out, _, _ = run_cmd(cmd, 120)
    return out if code == 0 else ""


def verify_pdf(path, title, doi):
    """Return (ok, evidence dict, reason). Rejects previews and other papers."""
    with open(path, "rb") as f:
        if f.read(5) != b"%PDF-":
            return False, {}, "not a PDF"
    if os.path.getsize(path) < 20000:
        return False, {}, f"too small ({os.path.getsize(path)} bytes)"
    pages = pdf_pages(path)
    text = pdf_text(path)
    if not text.strip():
        return False, {"pages": pages}, "no extractable text (scanned?)"
    front = "\n".join(text.split("\f")[:3])
    doi_found = doi.lower() in front.lower().replace("\n", "") if doi else False
    frac = title_fraction(title, front)
    ev = {"pages": pages, "title_fraction_front3": round(frac, 3),
          "doi_in_front3": doi_found, "chars": len(text)}
    if pages is not None and pages < 2:
        return False, ev, "single-page preview"
    if doi_found and frac >= 0.7:
        return True, ev, "DOI and title match on front pages"
    if frac >= 0.85:
        return True, ev, "title match on front pages"
    return False, ev, f"identity check failed (title {frac:.0%}, doi={doi_found})"


def html_to_text(html):
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?is)<br\s*/?>", "\n", html)
    html = re.sub(r"(?is)</(p|div|h[1-6]|li|tr|section)>", "\n", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
                .replace("&#39;", "'"))
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


ABSTRACT_HOSTS = ("pubmed.ncbi.nlm.nih.gov", "www.ncbi.nlm.nih.gov/pubmed",
                 "europepmc.org/abstract", "semanticscholar.org/paper",
                 "researchgate.net/publication", "scholar.google.")


def verify_html(text, title, url=""):
    """An article body, not a PubMed/abstract/index or navigation page."""
    host = (urllib.parse.urlparse(url or "").netloc or "").lower()
    frac = title_fraction(title, text[:6000])
    methods = bool(re.search(r"(?mi)^\s*(methods?|methodology|materials and methods|"
                             r"method and materials)\s*:?\s*$", text))
    results = bool(re.search(r"(?mi)^\s*(results?|findings)\s*:?\s*$", text))
    ev = {"title_fraction": round(frac, 3), "chars": len(text),
          "methods_heading": methods, "results_heading": results, "host": host}
    if any(h in host for h in ABSTRACT_HOSTS):
        return False, ev, f"abstract/metadata host rejected ({host})"
    ok = (len(text) >= 12000 and frac >= 0.6 and methods and results
          and bool(re.search(r"(?mi)^\s*(references|bibliography)\s*:?\s*$", text)))
    return ok, ev, ("full-text HTML" if ok else
                    f"HTML not article body (chars={len(text)}, title={frac:.0%}, "
                    f"methods={methods}, results={results})")


def resolve_title(src, timeout=8, attempts=1):
    """A real paper title: Crossref for a DOI, else parsed from the reference."""
    doi = src.get("doi") or ""
    if DOI_RE.match(doi):
        try:
            msg = {}
            for attempt in range(attempts):
                try:
                    body, _, _ = fetch(
                        f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}"
                        f"?mailto={CONTACT_EMAIL}", timeout=timeout,
                        accept="application/json")
                    msg = json.loads(body).get("message", {})
                    break
                except Exception:
                    if attempt == attempts - 1:
                        raise
                    time.sleep(1.0)
            title = re.sub(r"<[^>]+>", "", (msg.get("title") or [""])[0] or "")
            sub = re.sub(r"<[^>]+>", "", (msg.get("subtitle") or [""])[0] or "")
            if title:
                return f"{title}: {sub}" if sub else title
        except Exception as e:
            log(f"    crossref title failed: {e}")
    ref = src.get("reference") or ""
    m = re.search(r"\(\d{4}[a-z]?\)\.\s*(.+)", ref)
    cand = m.group(1) if m else ref
    cand = re.split(r"\.\s+(?=[A-Z][a-z])", cand)[0]
    cand = cand.strip().rstrip(".")
    return cand if len(cand) >= 15 else ref[:200]


def jats_text(xml):
    """Plain text from a JATS/PMC XML record (body + back matter)."""
    xml = re.sub(r"(?is)<(ref-list|back)[^>]*>", "\n", xml)
    xml = re.sub(r"(?is)<(p|sec|title|td|th|caption|label)[^>]*>", "\n", xml)
    text = re.sub(r"(?s)<[^>]+>", " ", xml)
    text = (text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                .replace("&quot;", '"').replace("&#x2013;", "-").replace("&#8217;", "'"))
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def oa_candidates(doi):
    """Repository/OA locations from OpenAlex and Unpaywall (free APIs)."""
    urls = []
    try:
        body, _, _ = fetch(f"https://api.openalex.org/works/doi:{doi}",
                           timeout=20, accept="application/json")
        work = json.loads(body)
        for loc in work.get("locations") or []:
            for key in ("pdf_url", "landing_page_url"):
                if loc.get(key):
                    urls.append(loc[key])
    except Exception as e:
        log(f"    openalex candidates failed: {e}")
    try:
        body, _, _ = fetch(
            f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi, safe='/')}"
            f"?email={urllib.parse.quote(CONTACT_EMAIL)}", timeout=20, accept="application/json")
        up = json.loads(body)
        for loc in up.get("oa_locations") or []:
            for key in ("url_for_pdf", "url"):
                if loc.get(key):
                    urls.append(loc[key])
    except Exception as e:
        log(f"    unpaywall candidates failed: {e}")
    seen, out = set(), []
    for u in urls:
        u = u.split("#")[0]
        if u and u not in seen:
            seen.add(u)
            out.append(u)
    return out


def wayback(url):
    try:
        body, _, _ = fetch("https://archive.org/wayback/available?url="
                           + urllib.parse.quote(url, safe=""), timeout=20,
                           accept="application/json")
        snap = json.loads(body).get("archived_snapshots", {}).get("closest")
        if snap and snap.get("available"):
            # snap["url"] is already an archive URL: /web/<ts>/<original>
            return re.sub(r"/web/(\d+)/", r"/web/\1id_/", snap["url"], count=1)
    except Exception:
        pass
    return None


def pmc_candidates(doi):
    """PMCIDs whose record carries this DOI, via NCBI E-utilities."""
    out = []
    try:
        q = urllib.parse.quote(f'"{doi}"[DOI]')
        body, _, _ = fetch(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            f"?db=pmc&retmode=json&term={q}", timeout=20,
            accept="application/json")
        ids = json.loads(body)["esearchresult"].get("idlist") or []
        for pid in ids[:2]:
            out.append(("pmc_xml", pid))
    except Exception:
        pass
    return out


def save_pdf_artifact(pdf_bytes, key, scratch, title, doi):
    pdf_path = os.path.join(scratch, "pdfs", f"{key}.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    ok, ev, reason = verify_pdf(pdf_path, title, doi)
    if not ok:
        os.unlink(pdf_path)
        return None, None, ev, reason
    text = pdf_text(pdf_path)
    text_path = os.path.join(scratch, "texts", f"{key}.txt")
    with open(text_path, "w") as f:
        f.write(text)
    ev.update({"pdf_sha256": sha256(pdf_path), "text_sha256": sha256(text_path)})
    return pdf_path, text_path, ev, reason


def save_html_artifact(body, key, scratch, title, doi, source_url):
    try:
        html = body.decode("utf-8", "replace")
    except Exception:
        return None, None, {}, "undecodable HTML"
    text = html_to_text(html)
    ok, ev, reason = verify_html(text, title, source_url)
    if not ok:
        return None, None, ev, reason
    html_path = os.path.join(scratch, "html", f"{key}.html")
    text_path = os.path.join(scratch, "texts", f"{key}.txt")
    with open(html_path, "w") as f:
        f.write(html)
    with open(text_path, "w") as f:
        f.write(text)
    ev.update({"html_sha256": sha256(html_path), "text_sha256": sha256(text_path),
               "source_url": source_url})
    return html_path, text_path, ev, reason


def fetch_and_accept(url, key, scratch, title, doi, timeout=FALLBACK_TIMEOUT):
    """Download one URL and accept it only if it verifies as the full paper."""
    body, final_url, ctype = fetch(url, timeout=timeout)
    if body.startswith(b"%PDF-") and len(body) > 20000:
        pdf_path, text_path, ev, reason = save_pdf_artifact(
            body, key, scratch, title, doi)
        return pdf_path, text_path, ev, reason, final_url
    head = body[:400].lstrip().lower()
    if head.startswith(b"<?xml") or b"<article" in head or "xml" in (ctype or "").lower():
        text = jats_text(body.decode("utf-8", "replace"))
        ok, ev, reason = verify_html(text, title, final_url)
        if ok:
            text_path = os.path.join(scratch, "texts", f"{key}.txt")
            with open(text_path, "w") as f:
                f.write(text)
            xml_path = os.path.join(scratch, "html", f"{key}.xml")
            with open(xml_path, "wb") as f:
                f.write(body)
            ev.update({"xml_sha256": sha256(xml_path), "text_sha256": sha256(text_path),
                       "source_url": final_url})
            return xml_path, text_path, ev, "full-text JATS XML", final_url
        return None, None, ev, reason, final_url
    if "html" in (ctype or "").lower() or head.startswith((b"<!doctype", b"<html")):
        html_path, text_path, ev, reason = save_html_artifact(
            body, key, scratch, title, doi, final_url)
        return html_path, text_path, ev, reason, final_url
    return None, None, {"ctype": ctype}, f"not PDF/HTML ({ctype})", final_url


def fallback_sweep(src, scratch, tried):
    """At most two further distinct URLs, 60 s each."""
    key, doi, title, url = src["key"], src.get("doi") or "", src.get("title") or resolve_title(src), src.get("url")
    candidates = []
    if url:
        candidates.append(url)
    deadline = time.time() + 25          # discovery budget, bounded per source
    if DOI_RE.match(doi or ""):
        try:
            candidates += oa_candidates(doi)
        except Exception as e:
            log(f"    oa discovery failed: {e}")
        if time.time() < deadline:
            try:
                for kind, pid in pmc_candidates(doi):
                    candidates.append(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                        f"?db=pmc&id={pid}&rettype=xml")
            except Exception as e:
                log(f"    pmc discovery failed: {e}")
        if time.time() < deadline:
            snap = wayback(f"https://doi.org/{doi}")
            if snap:
                candidates.append(snap)

    distinct, seen = [], set(tried)
    for u in candidates:
        base = u.split("?")[0]
        if u not in seen and base not in seen:
            seen.add(u)
            distinct.append(u)
    used = []
    for u in distinct[:2]:
        used.append(u)
        try:
            a, t, ev, reason, final = fetch_and_accept(u, key, scratch, title, doi)
            if a:
                return a, t, ev, reason, used, final
        except Exception as e:
            ev, reason, final = {}, f"{type(e).__name__}: {e}", u
        log(f"    fallback miss {u[:100]}: {reason}")
    return None, None, {}, "no fallback URL verified", used, None


def process_source(src, scratch, acq_dir, titles, titles_lock, titles_path):
    key = src["key"]
    doi = src.get("doi") or ""
    title = src.get("title")
    if not title:
        with titles_lock:
            title = titles.get(key)
        if not title:
            title = resolve_title(src, timeout=8, attempts=1)
            with titles_lock:
                titles[key] = title
                tmp = titles_path + ".tmp"
                with open(tmp, "w") as f:
                    json.dump(titles, f, indent=1)
                os.replace(tmp, titles_path)
        src["title"] = title
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    rec = {
        "key": key, "doi": src.get("doi"), "reference": src["reference"],
        "status": "error", "attempted_routes": [], "started_at": started,
        "finished_at": None, "artifact_path": None, "text_path": None,
        "source_url": src.get("url"), "identity_evidence": {},
        "reason": "", "affected_sides": len(src["targets"]),
        "title": title,
    }
    log_path = os.path.join(scratch, "logs", f"{key}.log")
    env = dict(os.environ)
    env.update({"SERPAPI_API_KEY": "", "SERPAPI_API_KEYS": "",
                "RESEARCHER_EMAIL": CONTACT_EMAIL, "EMAIL": CONTACT_EMAIL})

    artifact = text_path = None
    if DOI_RE.match(doi):
        rec["attempted_routes"].append("download_paper.py (fetchpdf+web+PMC)")
        cmd = [DOWNLOADER, "--doi", doi, "--title", title,
               "--cache-dir", os.path.join(scratch, "cache"), "--no-browser"]
        code, out, err, timed_out = run_cmd(cmd, PRIMARY_TIMEOUT, env=env)
        with open(log_path, "w") as f:
            f.write(f"$ {' '.join(cmd)}\n--- stdout ---\n{out}\n--- stderr ---\n{err}\n")
        if code == 0 and out.strip():
            cand = out.strip().splitlines()[-1]
            if os.path.exists(cand):
                ok, ev, reason = verify_pdf(cand, title, doi)
                if ok:
                    artifact = os.path.join(scratch, "pdfs", f"{key}.pdf")
                    shutil.copyfile(cand, artifact)
                    text = pdf_text(artifact)
                    text_path = os.path.join(scratch, "texts", f"{key}.txt")
                    with open(text_path, "w") as f:
                        f.write(text)
                    ev.update({"pdf_sha256": sha256(artifact),
                               "text_sha256": sha256(text_path)})
                    rec.update(status="retrieved", artifact_path=artifact,
                               text_path=text_path, identity_evidence=ev,
                               source_url=f"https://doi.org/{doi}",
                               reason=f"download_paper.py: {reason}")
        if not artifact:
            rec["reason"] = ("download_paper.py timed out" if timed_out
                             else "download_paper.py found no verified full text")
    elif doi:
        rec["attempted_routes"].append("non-DOI identifier: direct URL only")
    else:
        rec["attempted_routes"].append("no identifier: direct URL only")

    if not artifact:
        tried = [f"https://doi.org/{doi}"] if DOI_RE.match(doi) else []
        a, t, ev, reason, used, final = fallback_sweep(src, scratch, tried)
        rec["attempted_routes"] += used
        if a:
            artifact, text_path = a, t
            rec.update(status="retrieved", artifact_path=a, text_path=t,
                       identity_evidence=ev, source_url=final or (used[-1] if used else None),
                       reason=f"fallback: {reason}")
        else:
            rec["reason"] = rec["reason"] or reason
            if not rec["identity_evidence"]:
                rec["identity_evidence"] = ev

    if rec["status"] != "retrieved":
        if not doi:
            rec["status"] = "no_identifier"
        elif not rec["attempted_routes"] or all("direct URL" in r for r in rec["attempted_routes"]):
            rec["status"] = "unavailable"
        else:
            rec["status"] = "unavailable"

    rec["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    tmp = os.path.join(acq_dir, f".{key}.json.tmp")
    with open(tmp, "w") as f:
        json.dump(rec, f, indent=2)
    os.replace(tmp, os.path.join(acq_dir, f"{key}.json"))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True, help="source_followup dir")
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--minutes", type=float, default=100.0)
    args = ap.parse_args()

    # Own the runner PID inside Python: shell `$!` may identify a wrapper.
    os.makedirs(args.scratch, exist_ok=True)
    runner_lock = open(os.path.join(args.scratch, 'acquisition.lock'), 'a+')
    try:
        fcntl.flock(runner_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log('A source acquisition runner already owns the lock; no duplicate started')
        return
    owner = {'pid': os.getpid(), 'cwd': os.getcwd(),
             'start_ticks': int(open('/proc/self/stat').read().split(') ', 1)[1].split()[19]),
             'started_at': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
    with open(os.path.join(args.scratch, 'runner_owner.json'), 'w') as file:
        json.dump(owner, file, indent=2)

    global CONTACT_EMAIL
    CONTACT_EMAIL = load_contact_email()
    os.environ["RESEARCHER_EMAIL"] = CONTACT_EMAIL
    os.environ["EMAIL"] = CONTACT_EMAIL
    acq_dir = os.path.join(args.out, "acquisitions")
    os.makedirs(acq_dir, exist_ok=True)
    for sub in ("cache", "logs", "texts", "pdfs", "html"):
        os.makedirs(os.path.join(args.scratch, sub), exist_ok=True)

    sources = json.load(open(args.manifest))
    if args.limit:
        sources = sources[:args.limit]

    titles_path = os.path.join(args.scratch, "titles.json")
    titles = json.load(open(titles_path)) if os.path.exists(titles_path) else {}
    titles_lock = threading.Lock()

    state = {"done": 0, "retrieved": 0, "active": 0, "last_key": None,
             "last_completion": time.time(), "stop": None}
    lock = threading.Lock()
    t0 = time.time()

    def write_progress():
        with lock:
            snap = dict(state)
        snap.update({
            "attempted": snap["done"], "remaining": len(sources) - snap["done"],
            "total": len(sources), "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "elapsed_seconds": round(time.time() - t0, 1),
        })
        tmp = os.path.join(args.out, ".progress.json.tmp")
        with open(tmp, "w") as f:
            json.dump(snap, f, indent=2)
        os.replace(tmp, os.path.join(args.out, "progress.json"))

    def heartbeat():
        while True:
            time.sleep(30)
            write_progress()

    threading.Thread(target=heartbeat, daemon=True).start()
    write_progress()

    def worker(src):
        with lock:
            if state["stop"]:
                return None
        existing = os.path.join(acq_dir, f"{src['key']}.json")
        if os.path.exists(existing):
            try:
                rec = json.load(open(existing))
                if rec.get("status") in ("retrieved", "unavailable", "no_identifier"):
                    return rec
            except Exception:
                pass
        with lock:
            if state["stop"]:
                return None
            state["active"] += 1
        try:
            return process_source(src, args.scratch, acq_dir, titles, titles_lock, titles_path)
        except Exception as e:
            key = src["key"]
            rec = {"key": key, "doi": src.get("doi"), "reference": src["reference"],
                   "status": "error", "attempted_routes": [], "started_at": None,
                   "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                   "artifact_path": None, "text_path": None,
                   "source_url": src.get("url"), "identity_evidence": {},
                   "reason": f"{type(e).__name__}: {e}",
                   "affected_sides": len(src["targets"]), "title": src.get("title") or ""}
            tmp = os.path.join(acq_dir, f".{key}.json.tmp")
            with open(tmp, "w") as f:
                json.dump(rec, f, indent=2)
            os.replace(tmp, os.path.join(acq_dir, f"{key}.json"))
            return rec
        finally:
            with lock:
                state["active"] -= 1

    consecutive_errors = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(worker, s): s for s in sources}
        for fut in concurrent.futures.as_completed(futures):
            rec = fut.result()
            if rec is None:
                continue
            with lock:
                state["done"] += 1
                if rec["status"] == "retrieved":
                    state["retrieved"] += 1
                    consecutive_errors = 0
                elif rec["status"] == "error":
                    consecutive_errors += 1
                state["last_key"] = rec["key"]
                state["last_completion"] = time.time()
                n_done, n_ret = state["done"], state["retrieved"]
            log(f"{n_done}/{len(sources)} {rec['status']:<11} {rec['key']} "
                f"sides={rec['affected_sides']} :: {rec['reason'][:90]}")
            write_progress()
            if consecutive_errors >= 10:
                with lock:
                    state["stop"] = "10 consecutive source errors"
                log("STOP: 10 consecutive source errors")
                break
            if time.time() - t0 > args.minutes * 60:
                with lock:
                    state["stop"] = "total acquisition time cap reached"
                log("STOP: time cap")
                break

    write_progress()
    log(f"finished: {state['done']} attempted, {state['retrieved']} retrieved, "
        f"{len(sources) - state['done']} not attempted, "
        f"{round((time.time() - t0) / 60, 1)} min")


if __name__ == "__main__":
    main()
