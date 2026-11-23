"""Fetch the source documents behind review items that have no matching cached PDF page.

For each private source text without a screenshot, use the URL the audit recorded (text
header, coded url_r) or the work DOI. PDFs go to private cloud storage as
<source text stem>.pdf; HTML reports are listed for browser rendering. Open routes only:
direct public URLs and the download-paper skill's open-access chain (no signed-in browser).

  python3 .../release_draft/fetch_review_sources.py missing_sources.json
"""
import json, re, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import review_page as rp  # noqa: E402

DOWNLOAD_PAPER = Path.home() / '.claude/skills/download-paper/download_paper.py'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36'


def pdf_url(url):
    u = url.split('#')[0]
    m = re.search(r'drive\.google\.com/file/d/([\w-]+)', u)
    if m:
        return f'https://drive.google.com/uc?export=download&id={m[1]}'
    m = re.fullmatch(r'https?://osf\.io/([a-z0-9]{5})/?', u)
    if m:
        return f'https://osf.io/download/{m[1]}/'
    m = re.search(r'github\.com/([^/]+)/([^/]+)/blob/(.+\.pdf)$', u)
    if m:
        return f'https://raw.githubusercontent.com/{m[1]}/{m[2]}/{m[3]}'
    if re.search(r'(\.pdf$|[?&]pdf=1|/pdf$|osf\.io/download/|/bitstreams/)', u.split('?')[0] + ('?pdf=1' if 'pdf=1' in u else ''), re.I):
        return u
    return None


def is_pdf(path):
    try:
        return path.read_bytes()[:5] == b'%PDF-'
    except OSError:
        return False


def curl(url, dest):
    tmp = dest.with_suffix('.part')
    r = subprocess.run(['curl', '-sSL', '--max-time', '120', '-A', UA, '-o', str(tmp), url], capture_output=True, text=True)
    if r.returncode == 0 and is_pdf(tmp):
        tmp.replace(dest); return True
    tmp.unlink(missing_ok=True); return False


def main():
    rows = json.loads(Path(sys.argv[1]).read_text())
    rp.REVIEW_SOURCES.mkdir(parents=True, exist_ok=True)
    report, html_targets = [], []
    for r in rows:
        stem = Path(r['source']).stem
        dest = rp.REVIEW_SOURCES / f'{stem}.pdf'
        status = 'exists' if is_pdf(dest) else None
        urls = [u for u in [r['url'], r['row_url_r']] if u and u.startswith('http')]
        for u in urls if not status else []:
            direct = pdf_url(u)
            if direct and curl(direct, dest):
                status = 'url:' + direct; break
        if not status and r['doi'] and not r['cached_pdf']:
            out = subprocess.run([str(DOWNLOAD_PAPER), '--doi', r['doi'], '--no-browser'], capture_output=True, text=True, timeout=600)
            path = out.stdout.strip().splitlines()[-1] if out.returncode == 0 and out.stdout.strip() else ''
            if path and is_pdf(Path(path)):
                dest.write_bytes(Path(path).read_bytes()); status = 'download-paper'
        if not status:
            html = next((u for u in urls if not pdf_url(u)), None)
            if html:
                html_targets.append({'source': r['source'], 'url': html}); status = 'html'
        report.append({'source': r['source'], 'items': r['n_items'], 'status': status or 'not_found', 'doi': r['doi'], 'url': r['url'] or r['row_url_r']})
        print(json.dumps(report[-1]), flush=True)
    (rp.REVIEW_SOURCES / 'fetch_report.json').write_text(json.dumps(report, indent=1))
    (rp.REVIEW_SOURCES / 'html_targets.json').write_text(json.dumps(html_targets, indent=1))


if __name__ == '__main__':
    main()
