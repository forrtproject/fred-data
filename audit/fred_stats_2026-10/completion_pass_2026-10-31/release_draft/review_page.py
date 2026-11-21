"""Build the private review page for correction decisions, with page screenshots.

The page shows every finding that needs a human decision (policy review queue), the
random Tier-1 sample, held findings and policy-not-applicable findings. Each card shows
the coded and proposed values, the review evidence, and a screenshot of the source page
around the quote when a cached PDF of the source contains it; otherwise an excerpt of
the private source text. Decisions are kept in the browser and exported as rows for
manual_decisions.csv.

Output contains private source material and must stay outside the fred-data repository:
  python3 .../release_draft/review_page.py --out /home/lukas/.cache/fred-audit-application-review
"""
import argparse, collections, csv, hashlib, html, json, os, re, shutil, subprocess, sys, unicodedata
from pathlib import Path

P = Path(__file__).resolve().parent
B = P.parents[1]
REPO = B.parents[1]
sys.path.insert(0, str(B / 'scripts'))
sys.path.insert(0, str(P))
from compare import load_adjudications, combine_obvious, parsed_stat, SOURCE_PROVENANCE  # noqa: E402
from consistency import pinterval, stat_interval  # noqa: E402
import policy_ledger  # noqa: E402

CLOUD = Path('/home/lukas/cloud-data')
AUDIT_SOURCES = CLOUD / 'fred-stats-2026-10-b48a7d6-20261029T092009Z'
PAPER_CACHE = [Path.home() / '.claude/cache/pdfs', CLOUD / 'paper-cache']
# Source PDFs fetched for this review, named <source text stem>.pdf (private).
REVIEW_SOURCES = AUDIT_SOURCES / 'review_sources_20261107'
SECTIONS = [
    ('d1', 'Direction (D1)', 'After correction the original and replication effects point in opposite directions. Apply only for a genuine reversal.'),
    ('t2', 'Model, sample role, metric or adaptation (T2)', 'The correction changes the test, the sample role, relies on a metric equivalence, or concerns an adapted test. Check that the new target is the row’s effect.'),
    ('coh', 'Corrected values contradict each other (D3)', 'All fields of the side are verified, but N, statistic and p do not fit together after correction.'),
    ('d2', 'Study-level author verdict (D2)', 'Apply only if an explicit author statement (or project coding rule) gives this verdict for the whole study. Reject auditor interpretation.'),
    ('t1', 'Random sample of automatic corrections (T1)', 'Thirty randomly drawn automatic corrections. If more than one is wrong, the automatic class needs a closer look.'),
    ('hold', 'Held (D3)', 'Held because sibling fields of the same side are unverified or not yet applied. Override only if the corrected row side is clearly coherent.'),
    ('na', 'Not applicable under study-level coding (D2)', 'Effects of the same study received different verdicts. Shown for completeness.'),
]


def txt(x):
    return '' if x is None else str(x)


def norm(s):
    s = unicodedata.normalize('NFKC', txt(s)).replace('−', '-').replace('–', '-').replace('’', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', s).strip().lower()


def section(r):
    pol, fin = r['policy'], r['final_decision']
    if fin == 'not_applicable':
        return 'na'
    if fin == 'hold':
        return 'hold'
    if fin == 'reject' or pol.startswith('D1'):
        return 'd1'
    if pol.startswith('T2'):
        return 't2'
    if pol == 'D3-coherence':
        return 'coh'
    if pol.startswith('D2'):
        return 'd2'
    if r['sample_check']:
        return 't1'
    return None


def fragments(quote):
    parts = [p.strip() for p in re.split(r'\[?\.{3}\]?|…', txt(quote)) if len(p.strip()) >= 12]
    return sorted(parts, key=len, reverse=True)


class Pdfs:
    def __init__(self, work):
        self.work = work; self.work.mkdir(parents=True, exist_ok=True)
        self.by_key = {}
        for root in ['drive_check_20261030', 'mac_continuation_1201', 'mac_source_followup_20261030', 'source_followup_20261029']:
            for path in (AUDIT_SOURCES / root).rglob('*.pdf'):
                m = re.match(r'([0-9a-f]{24})', path.name)
                if m:
                    self.by_key.setdefault(m[1], path)
        self.pages = {}

    def candidates(self, source_path, doi):
        stem = Path(txt(source_path)).stem
        if (REVIEW_SOURCES / f'{stem}.pdf').exists():
            yield REVIEW_SOURCES / f'{stem}.pdf'
        m = re.search(r'([0-9a-f]{24})', stem)
        if m and m[1] in self.by_key:
            yield self.by_key[m[1]]
        if doi:
            name = hashlib.md5(doi.strip().lower().encode()).hexdigest() + '.pdf'
            for cache in PAPER_CACHE:
                if (cache / name).exists():
                    yield cache / name
                    break

    def local(self, path):
        dest = self.work / (hashlib.sha256(str(path).encode()).hexdigest()[:16] + '.pdf')
        if not dest.exists():
            shutil.copyfile(path, dest)
        return dest

    def page_texts(self, pdf):
        if pdf not in self.pages:
            out = subprocess.run(['pdftotext', '-q', str(pdf), '-'], capture_output=True, text=True, errors='replace').stdout
            self.pages[pdf] = [compact(p) for p in out.split('\f')]
        return self.pages[pdf]


def compact(s):
    """Letters and digits only: robust to hyphenation, line breaks, ligatures and minus glyphs."""
    return re.sub(r'[^a-z0-9]', '', norm(s))


def probes(quote):
    for frag in fragments(quote):
        c = compact(frag)
        if len(c) < 14:
            continue
        mid = len(c) // 2
        for probe in (c[:60], c[max(0, mid - 30):mid + 30], c[-60:], c[:30], c[-30:]):
            if len(probe) >= 14:
                yield probe


def context_probes(source_path, quote):
    """Windows of the private source text around the quote: finds short table quotes in the same document version."""
    try:
        text = compact(Path(source_path).read_text(errors='replace'))
    except OSError:
        return
    parts = [x for x in re.split(r'\[?\.{3}\]?|…', txt(quote)) if len(compact(x)) >= 5]
    for frag in sorted(parts, key=len, reverse=True):
        c = compact(frag); pos = text.find(c)
        if pos < 0:
            continue
        for a, b in ((pos - 30, pos + len(c)), (pos, pos + len(c) + 30), (pos - 30, pos + len(c) + 30)):
            w = text[max(0, a):b]
            if len(w) >= 20:
                yield w


def find_page(pages, quote, extra=()):
    for probe in [*probes(quote), *extra]:
        hits = [i for i, t in enumerate(pages) if probe in t]
        if hits:
            return hits[0] + 1, probe
    return None, None


def crop(pdf, page, probe, out_png):
    """Render the band of the page around the matched text; return highlight box as fractions."""
    xml = subprocess.run(['pdftotext', '-q', '-bbox-layout', '-f', str(page), '-l', str(page), str(pdf), '-'],
                         capture_output=True, text=True, errors='replace').stdout
    pm = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', xml)
    if not pm:
        return None
    width, height = float(pm[1]), float(pm[2])
    words = [(float(a), float(b), float(c), float(d), compact(html.unescape(w)))
             for a, b, c, d, w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', xml)]
    joined, owner = '', []
    for i, w in enumerate(words):
        joined += w[4]; owner += [i] * len(w[4])
    pos = joined.find(probe)
    if pos < 0:
        return None
    span = words[owner[pos]:owner[pos + len(probe) - 1] + 1]
    y0, y1 = min(w[1] for w in span), max(w[3] for w in span)
    top, bottom = max(0, y0 - 90), min(height, max(y1, y0 + 20) + 150)
    dpi = 130; scale = dpi / 72
    subprocess.run(['pdftoppm', '-q', '-png', '-singlefile', '-r', str(dpi), '-f', str(page), '-l', str(page),
                    '-x', '0', '-y', str(int(top * scale)), '-W', str(int(width * scale)), '-H', str(int((bottom - top) * scale)),
                    str(pdf), str(out_png.with_suffix(''))], check=True)
    band = bottom - top
    return {'left': min(w[0] for w in span) / width, 'width': (max(w[2] for w in span) - min(w[0] for w in span)) / width,
            'top': (y0 - top) / band, 'height': (y1 - y0) / band, 'page': page}


def header_url(source_path):
    try:
        head = Path(source_path).read_text(errors='replace')[:1500]
    except OSError:
        return None
    for key in ('FRAME', r'SOURCE[_ ]URL', 'SOURCE', 'IDENTIFIER'):
        m = re.search(rf'^{key}:\s*(https?://\S+)', head, re.M | re.I)
        if m:
            return m[1]
    return None


UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36'


def ensure_pdf(url, stem):
    """Download a PDF-like source URL to private storage once; return its path when it is a PDF."""
    dest = REVIEW_SOURCES / f'{stem}.pdf'
    if dest.exists():
        return dest
    if not url or not re.search(r'(\.pdf($|\?)|osf\.io/download/|/bitstreams/|/content/view/|/download$)', url, re.I):
        return None
    tmp = dest.with_suffix('.part')
    subprocess.run(['curl', '-sSL', '--max-time', '120', '-A', UA, '-o', str(tmp), url])
    if tmp.exists() and tmp.read_bytes()[:5] == b'%PDF-':
        tmp.replace(dest); return dest
    tmp.unlink(missing_ok=True)
    return None


def resolve_html(url, stem):
    """Return a renderable URL: RPubs iframe target, or a local copy of raw GitHub HTML."""
    url = re.sub(r"[?]pdf=1$", "", url)
    if re.search(r'//rpubs\.com/', url):
        page = subprocess.run(['curl', '-sSL', '--max-time', '60', '-A', UA, url], capture_output=True, text=True, errors='replace').stdout
        m = re.search(r'(https?:)?//rstudio-pubs-static\.s3\.amazonaws\.com/[^"\'\s]+\.html', page)
        return ('https:' + m[0] if m[0].startswith('//') else m[0]) if m else url
    m = re.search(r'github\.com/([^/]+)/([^/]+)/blob/(.+)$', url)
    if m:
        url = f'https://raw.githubusercontent.com/{m[1]}/{m[2]}/{m[3]}'
    if 'raw.githubusercontent.com' in url:
        dest = REVIEW_SOURCES / 'html' / f'{stem}.html'; dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            subprocess.run(['curl', '-sSL', '--max-time', '60', '-A', UA, '-o', str(dest), url])
        return dest.as_uri() if dest.exists() and dest.stat().st_size else None
    return url


def table_view(source_path, quote, out_html, location=''):
    """Render the spreadsheet row that contains the quote as a column/value table."""
    try:
        text = Path(source_path).read_text(errors='replace')
    except OSError:
        return False
    lines = [l for l in text.splitlines() if l.strip()]
    tabbed = sum('\t' in l for l in lines[:50]) >= 5
    comma = not tabbed and sum(l.count(',') >= 5 for l in lines[:50]) >= 5
    if not (tabbed or comma):
        return False
    rows = [l.split('\t') for l in lines] if tabbed else list(csv.reader(lines))
    header = next((r for r in rows if len(r) >= 5), None)
    cells = dict(re.findall(r'\b([A-Z]{1,3})=(\S+)', txt(quote)))  # "AU=1.3e-56" style cell quotes
    loc_row = re.search(r'\brow\s+(\d+)', txt(location), re.I)
    def col_index(letters):
        n = 0
        for ch in letters:
            n = n * 26 + ord(ch) - 64
        return n - 1 + (1 if tabbed and header and header[0].strip().isdigit() else 0)
    hit_cols = {col_index(c) for c in cells}
    if loc_row and tabbed:
        match = next((r for r in rows if r and r[0].strip() == loc_row[1]), None)
    else:
        targets = [compact(x) for x in [*re.split(r'\[?\.{3}\]?|…', txt(quote)), *cells.values()] if len(compact(x)) >= 6]
        match = next((r for r in rows if r is not header and len(r) >= 5 and any(t in compact(''.join(r)) for t in targets)), None)
    if not header or not match:
        return False
    qc = compact(quote)
    def hit(i, v):
        return i in hit_cols or (not hit_cols and i > 0 and len(compact(v)) >= 4 and compact(v) in qc)
    body = ''.join(f"<tr class='{'hit' if hit(i, v) else ''}'><th>{html.escape(h)}</th><td>{html.escape(v)}</td></tr>"
                   for i, (h, v) in enumerate(zip(header, match)))
    out_html.write_text("<!doctype html><meta charset='utf-8'><style>body{font:14px system-ui;margin:16px}table{border-collapse:collapse}"
                        "th,td{border:1px solid #ccc;padding:3px 8px;text-align:left;vertical-align:top;max-width:700px}th{background:#f3f3f3;font-weight:600}"
                        "tr.hit td,tr.hit th{background:rgba(255,200,0,.35)}</style>"
                        f"<p>Spreadsheet row from {html.escape(Path(source_path).name)} (private source text)</p><table>{body}</table>")
    return True


def best_page_view(pdf, quote, out_png):
    """Full page with the most quote tokens; highlight the quoted numbers on it. For tables and reflowed text."""
    tokens = {compact(t) for t in re.split(r'[\s,;:()\[\]=<>]+', norm(quote)) if len(compact(t)) >= 2}
    numeric = {t for t in tokens if re.search(r'\d', t)}
    words_needed = {t for t in tokens if len(t) >= 4} | numeric
    if len(words_needed) < 3:
        return None
    out = subprocess.run(['pdftotext', '-q', str(pdf), '-'], capture_output=True, text=True, errors='replace').stdout
    best, score = None, 0.0
    for i, page in enumerate(out.split('\f'), 1):
        have = {compact(w) for w in norm(page).split()}
        sc = len(words_needed & have) / len(words_needed)
        if sc > score:
            best, score = i, sc
    if not best or score < 0.6:
        return None
    xml = subprocess.run(['pdftotext', '-q', '-bbox-layout', '-f', str(best), '-l', str(best), str(pdf), '-'], capture_output=True, text=True, errors='replace').stdout
    pm = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', xml)
    if not pm:
        return None
    width, height = float(pm[1]), float(pm[2])
    boxes = [{'left': float(a) / width, 'top': float(b) / height, 'width': (float(c) - float(a)) / width, 'height': (float(d) - float(b)) / height}
             for a, b, c, d, w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', xml)
             if compact(html.unescape(w)) in numeric]
    subprocess.run(['pdftoppm', '-q', '-png', '-singlefile', '-r', '110', '-f', str(best), '-l', str(best), str(pdf), str(out_png.with_suffix(''))], check=True)
    return {'page': best, 'score': score, 'boxes': boxes[:40]}


def location_page(pdf, location, out_png):
    """Render the page named by an explicit 'PDF p. N' locator when the quote itself is not located."""
    info = subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout
    pages = re.search(r'Pages:\s*(\d+)', info)
    if not pages:
        return None
    m = re.search(r'PDF\s*(?:p(?:age)?\.?|pp\.)\s*(\d+)', txt(location), re.I)
    page = int(m[1]) if m else None
    if page is None:
        printed = re.search(r'(?<![A-Za-z])pp?\.\s*(\d+)', txt(location))
        if printed:
            # Find the PDF page whose header or footer carries the printed page number.
            text = subprocess.run(['pdftotext', '-q', '-layout', str(pdf), '-'], capture_output=True, text=True, errors='replace').stdout.split('\f')
            for i, pg in enumerate(text, 1):
                lines = [l for l in pg.splitlines() if l.strip()]
                if any(re.search(rf'(^|\s){printed[1]}(\s|$)', l) for l in lines[:3] + lines[-3:]):
                    page = i; break
    if not page or page > int(pages[1]):
        return None
    subprocess.run(['pdftoppm', '-q', '-png', '-singlefile', '-r', '100', '-f', str(page), '-l', str(page), str(pdf), str(out_png.with_suffix(''))], check=True)
    return page


def excerpt(source_path, quote):
    try:
        text = Path(source_path).read_text(errors='replace')
    except OSError:
        return None
    flat = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', text))
    for frag in fragments(quote):
        words = unicodedata.normalize('NFKC', frag).split()[:12]
        m = re.search(r'\s*'.join(re.escape(w) for w in words), flat, re.I)
        if m:
            a, b = max(0, m.start() - 400), min(len(flat), m.end() + 400)
            return html.escape(flat[a:m.start()]) + '<mark>' + html.escape(flat[m.start():m.end()]) + '</mark>' + html.escape(flat[m.end():b])
    return None


def side_table(row, res, s):
    label = 'Original' if s == 'o' else 'Replication'
    cells = []
    for f, name in [('n', 'N'), ('es_value', 'Effect'), ('pval_value', 'p')]:
        field = f'{f}_{s}'
        extra = f" <span class='muted'>{html.escape(txt(row.get('es_type_' + s)))}</span>" if f == 'es_value' else (
            f" <span class='muted'>{html.escape(txt(row.get('pval_type_' + s)))}</span>" if f == 'pval_value' else '')
        cells.append(f"<td><b>{name}</b> {html.escape(txt(row[field]))}{extra}<br><span class='v v-{res[field + '_final_verdict']}'>{res[field + '_final_verdict']}</span>"
                     + (f" → {html.escape(txt(res[field + '_suggested_correction']))}" if res[field + '_final_verdict'] == 'error' else '') + '</td>')
    return f"<tr><th>{label}<br><span class='muted'>study {html.escape(txt(row['study_' + s]))}</span></th>{''.join(cells)}</tr>"


class Evidence:
    """Find and render the source view for one quote; web and table views are rendered in one batch at the end."""

    def __init__(self, out, pdfs, html_targets):
        self.out, self.pdfs, self.html_targets = out, pdfs, html_targets
        self.jobs, self.pending, self.stats = [], {}, collections.Counter()

    def view(self, key, source, quote, location, doi, label):
        if not quote or not source:
            return ''
        extra = list(context_probes(source, quote))
        ensure_pdf(header_url(source), Path(source).stem)
        tried, shot = [], None
        for pdf in self.pdfs.candidates(source, doi):
            local = self.pdfs.local(pdf); tried.append(local)
            page, probe = find_page(self.pdfs.page_texts(local), quote, extra)
            if page:
                shot = crop(local, page, probe, self.out / 'shots' / f'{key}.png')
                if shot:
                    break
        head = f"<div class='panel-h'>{label}</div>"
        if shot:
            self.stats['pdf page with quote'] += 1
            return (f"<figure class='shot'>{head}<div class='imgwrap'><img loading='lazy' src='shots/{key}.png' alt='Source page {shot['page']} around the quote'>"
                    f"<span class='hl' style='left:{shot['left']*100:.1f}%;top:{shot['top']*100:.1f}%;width:{shot['width']*100:.1f}%;height:{max(shot['height'],0.04)*100:.1f}%'></span></div>"
                    f"<figcaption>Source PDF, page {shot['page']}</figcaption></figure>")
        url = header_url(source) or self.html_targets.get(Path(source).name)
        if url and not re.search(r'osf\.io/download|drive\.google|\.pdf($|\?)', url):
            target = resolve_html(url, Path(source).stem)
            if target:
                self.jobs.append({'id': key, 'url': target, 'probes': [*probes(quote), *extra], 'out': str(self.out / 'shots' / f'{key}.png'), 'shown': url, 'stem': Path(source).stem})
        if table_view(source, quote, self.out / 'tables' / f'{key}.html', location):
            self.jobs.append({'id': key + '#table', 'url': (self.out / 'tables' / f'{key}.html').as_uri(), 'selector': 'tr.hit', 'out': str(self.out / 'shots' / f'{key}.png')})
        best = fallback = None
        for local in tried:
            best = best_page_view(local, quote, self.out / 'shots' / f'{key}-page.png')
            if best:
                break
        for local in tried if not best else []:
            fallback = location_page(local, location, self.out / 'shots' / f'{key}-page.png')
            if fallback:
                break
        self.pending[key] = {'source': source, 'quote': quote, 'page': fallback, 'best': best, 'head': head}
        return f'@@EVIDENCE:{key}@@'

    def finish(self, cards):
        rendered = {}
        if self.jobs:
            jobfile = self.out / 'render_jobs.json'; jobfile.write_text(json.dumps(self.jobs))
            subprocess.run(['uvx', '--with', 'playwright', 'python', str(P / 'render_html.py'), str(jobfile), str(self.out / 'render_results.json')], check=True)
            rendered = json.loads((self.out / 'render_results.json').read_text()); jobfile.unlink()
        shown = {j['id']: j.get('shown') for j in self.jobs}
        for j in self.jobs:
            res = rendered.get(j['id']) or {}
            if 'Download is starting' in res.get('error', '') and j.get('stem'):
                # The 'web page' was a file download: keep the PDF for the next run.
                dest = REVIEW_SOURCES / f"{j['stem']}.pdf"; tmp = dest.with_suffix('.part')
                subprocess.run(['curl', '-sSL', '--max-time', '120', '-A', UA, '-o', str(tmp), j['url']])
                if tmp.exists() and tmp.read_bytes()[:5] == b'%PDF-' and not dest.exists():
                    tmp.replace(dest); self.stats['downloaded for next run'] += 1
                tmp.unlink(missing_ok=True)
        fill = {}
        for key, info in self.pending.items():
            web, table, head = rendered.get(key), rendered.get(key + '#table'), info['head']
            if web and 'error' not in web:
                self.stats['web page with quote'] += 1
                ev = (f"<figure class='shot'>{head}<div class='imgwrap'><img loading='lazy' src='shots/{key}.png' alt='Source web page around the quote'></div>"
                      f"<figcaption>Source web page: <a href='{html.escape(shown[key])}' target='_blank' rel='noopener'>{html.escape(shown[key][:90])}</a></figcaption></figure>")
            elif table and 'error' not in table:
                self.stats['spreadsheet row'] += 1
                ev = f"<figure class='shot'>{head}<div class='imgwrap'><img loading='lazy' src='shots/{key}.png' alt='Spreadsheet row'></div><figcaption>Source spreadsheet row (highlighted cells appear in the quote)</figcaption></figure>"
            elif info['best']:
                self.stats['pdf page best match'] += 1
                b = info['best']
                boxes = ''.join(f"<span class='hl' style='left:{x['left']*100:.2f}%;top:{x['top']*100:.2f}%;width:{x['width']*100:.2f}%;height:{x['height']*100:.2f}%'></span>" for x in b['boxes'])
                ev = (f"<figure class='shot'>{head}<div class='imgwrap'><img loading='lazy' src='shots/{key}-page.png' alt='Source page best matching the quote'>{boxes}</div>"
                      f"<figcaption>Source PDF, page {b['page']}: best match to the quote ({b['score']:.0%} of quote words); quoted numbers highlighted.</figcaption></figure>")
            elif info['page']:
                self.stats['pdf page from locator'] += 1
                ex = excerpt(info['source'], info['quote'])
                ev = (f"<figure class='shot'>{head}<div class='imgwrap'><img loading='lazy' src='shots/{key}-page.png' alt='Source page from locator'></div>"
                      f"<figcaption>Source PDF, page {info['page']} (from the page locator); the quote itself was not located automatically.</figcaption></figure>"
                      + (f"<div class='excerpt'><div class='muted'>Private source text:</div>{ex}</div>" if ex else ''))
            else:
                ex = excerpt(info['source'], info['quote'])
                self.stats['text excerpt only' if ex else 'no evidence view'] += 1
                ev = (f"<div class='excerpt'>{head}<div class='muted'>No source page found; private source text:</div>{ex}</div>" if ex
                      else f"<div class='excerpt'>{head}<div class='muted'>No source page or text excerpt located.</div></div>")
            fill[f'@@EVIDENCE:{key}@@'] = ev
        pattern = re.compile(r'@@EVIDENCE:[^@]+@@')
        for k in cards:
            cards[k] = [pattern.sub(lambda m: fill.get(m[0], ''), c) for c in cards[k]]


def consistency_table(row, row_after, s):
    """N, effect, p and what the statistic implies, before and after the row's audit corrections."""
    def cells(r):
        interval, kind = stat_interval(txt(r['es_value_' + s]).replace('–', '-'), r['es_type_' + s], r['n_' + s], r['nested_' + s], r['pval_tails_' + s])
        parsed = parsed_stat(txt(r['es_value_' + s]).replace('–', '-'))
        df = parsed[1][-1] if parsed and parsed[1] else None
        implied = f"{interval[0]:.3g}–{interval[1]:.3g}" if interval else '—'
        if interval and interval[1] - interval[0] < 1e-12:
            implied = f"{interval[0]:.3g}"
        tails = '' if not kind or 'tails_assumed_two' not in kind else ' (two-tailed assumed)'
        p = pinterval(r['pval_value_' + s], txt(r['pval_type_' + s]).split(' ')[0])
        fits = '' if not interval or p is None else ('✓ fits' if max(interval[0], float(p[0])) <= min(interval[1], float(p[1])) else '✗ does not fit')
        return (f"<td>{html.escape(txt(r['n_' + s]))}</td><td>{html.escape(txt(r['es_value_' + s]))}</td><td>{html.escape(txt(r['pval_value_' + s]))} {html.escape(txt(r['pval_type_' + s]))}</td>"
                f"<td>{implied}{tails} <b>{fits}</b></td><td>{'' if df is None else f'{df:g}'}</td>")
    label = 'Original' if s == 'o' else 'Replication'
    return (f"<table class='cons'><tr><th>{label}</th><th>N</th><th>Effect</th><th>p (coded)</th><th>p implied by statistic</th><th>error df</th></tr>"
            f"<tr><th>Coded</th>{cells(row)}</tr><tr><th>After this row's audit corrections</th>{cells(row_after)}</tr></table>")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', required=True)
    out = Path(ap.parse_args().out).resolve()
    assert not out.is_relative_to(REPO.resolve()), 'Review output holds private source material; keep it outside the repository'
    (out / 'shots').mkdir(parents=True, exist_ok=True); (out / 'tables').mkdir(exist_ok=True)
    ledger = list(csv.DictReader((P / 'application_decisions.csv').open(encoding='utf-8-sig')))
    by_key = {(int(r['audit_id']), r['field']): r for r in ledger}
    parent = json.loads((B / 'parent_rows.json').read_text())
    results = {int(r['input_row_index']): r for r in csv.DictReader((B / 'results.csv').open(encoding='utf-8-sig'))}
    decisions = combine_obvious(load_adjudications(B), json.loads((B / 'obvious_resolutions.json').read_text()))
    errors = json.loads((B / 'progress.json').read_text())['confirmed_errors']
    row_errors = collections.defaultdict(list)
    for e in errors:
        row_errors[e['audit_id']].append(e)
    groups = collections.defaultdict(list)
    for i, row in enumerate(parent, 1):
        groups[policy_ledger.study_key(row)].append(i)
    targets_file = REVIEW_SOURCES / 'html_targets.json'
    html_targets = {t['source']: t['url'] for t in json.loads(targets_file.read_text())} if targets_file.exists() else {}
    ev = Evidence(out, Pdfs(Path(os.environ.get('FRED_REVIEW_PDF_WORK', '/tmp/claude-1000/fred-review-pdfs'))), html_targets)
    cards = collections.defaultdict(list); counts = collections.Counter()

    def extraction(aid):
        path = B / 'extractions' / f'{aid}.json'
        return json.loads(path.read_text()) if path.exists() else {}

    def side_doi(row, s, source):
        return (SOURCE_PROVENANCE.get(source) or {}).get('work_doi') or row['doi_o' if s == 'o' else 'doi_r'] or ''

    def es_panel(cid, aid, row, s, what):
        x = extraction(aid).get('original' if s == 'o' else 'replication', {}).get('es') or {}
        if not x.get('quote'):
            return f"<p class='muted'>{what}: no located quote in the blind extraction.</p>"
        src = x.get('source_path') or ''
        return (f"<div class='panel'><p><b>{what}</b> (blind extraction): {html.escape(txt(x.get('test_statistic') or x.get('value')))} "
                f"<span class='muted'>{html.escape(txt(x.get('metric')))} · {html.escape(txt(x.get('location')))}</span><br><q>{html.escape(txt(x.get('quote')))}</q></p>"
                + ev.view(f"{cid}--{s}es", src, x.get('quote'), x.get('location'), side_doi(row, s, src), what) + "</div>")

    def conclusion_panel(cid, aid, row):
        """What the replication authors concluded: the coded verdict and quote, the blind extraction and the audit verdict."""
        x = extraction(aid); rs = x.get('reported_success') or {}
        res = results[aid]
        src = rs.get('source_path') or (x.get('replication', {}).get('es') or {}).get('source_path') or ''
        doi = side_doi(row, 'r', src)
        verdict = res['reported_success_final_verdict']
        audit = {'correct': 'confirmed by the audit', 'error': f"audit finding: should be <b>{html.escape(txt(res['reported_success_suggested_correction']))}</b> "
                 f"(ledger: {html.escape(by_key.get((aid, 'reported_success'), {}).get('final_decision', '—'))})", 'unverified': 'not verified by the audit',
                 'not_comparable': 'not comparable'}.get(verdict, verdict)
        parts = [f"<div class='panel'><div class='panel-h'>Replication authors' conclusion</div>"
                 f"<p>Coded <b>{html.escape(txt(row['reported_success']))}</b> ({audit}). Coded quote ({html.escape(txt(row['reported_success_quote_source']))}): "
                 f"<q>{html.escape(txt(row['reported_success_quote']))}</q></p>",
                 ev.view(f"{cid}--coded", src, txt(row['reported_success_quote']), '', doi, 'Coded author quote in the replication source')]
        if rs.get('quote') and compact(rs['quote']) != compact(row['reported_success_quote']):
            parts += [f"<p>Blind extraction: <b>{html.escape(txt(rs.get('value')))}</b> <span class='muted'>{html.escape(txt(rs.get('location')))}</span><br><q>{html.escape(txt(rs['quote']))}</q></p>",
                      ev.view(f"{cid}--blindrs", rs.get('source_path') or src, rs['quote'], rs.get('location'), doi, 'Blind-extracted author verdict')]
        if verdict == 'error' and (aid, 'reported_success') in decisions:
            a = decisions[(aid, 'reported_success')]
            parts += [f"<p>Audit's verdict quote: <q>{html.escape(txt(a.get('quote')))}</q> <span class='muted'>{html.escape(txt(a.get('location')))}</span></p>"]
        return ''.join(parts) + '</div>'

    for r in ledger:
        sec = section(r)
        if not sec:
            continue
        aid, field = int(r['audit_id']), r['field']; row = parent[aid - 1]; res = results[aid]; d = decisions[(aid, field)]
        cid = r['correction_id']; s = 'r' if field == 'reported_success' else field[-1]
        source = d.get('source_path') or ''; doi = side_doi(row, s, source)
        main_ev = ev.view(cid, source, d.get('quote'), d.get('location'), doi, 'Evidence for the proposed value') if sec != 'na' else ''
        panels = []
        if field != 'reported_success':
            side_errs = [e for e in row_errors[aid] if e['field'].endswith('_' + s) and e['field'] != 'reported_success']
            after = policy_ledger.patched(row, side_errs, decisions)
            panels.append("<div class='panel'><div class='panel-h'>Do N, statistic and p fit together?</div>" + consistency_table(row, after, s) + "</div>")
            other = 'o' if s == 'r' else 'r'
            if sec in ('d1', 't2', 'coh', 'hold', 't1'):
                panels.append(es_panel(cid, aid, row, other, 'Original effect' if other == 'o' else 'Replication effect'))
            if sec in ('d1',) or 'conceptual_adaptation' in r['tags'] or sec == 't2':
                panels.append(conclusion_panel(cid, aid, row))
        else:
            members = groups[policy_ledger.study_key(row)]
            lis = []
            for j in members:
                v = results[j]['reported_success_final_verdict']
                q = decisions.get((j, 'reported_success'), {}).get('quote') if v == 'error' else ''
                lis.append(f"<li><b>{j}</b>: {html.escape(txt(parent[j-1]['reported_success']))} <span class='v v-{v}'>{v}</span>"
                           + (f" → <b>{html.escape(results[j]['reported_success_suggested_correction'])}</b> <span class='muted'>({html.escape(by_key.get((j, 'reported_success'), {}).get('final_decision', ''))})</span>" if v == 'error' else '')
                           + f" <span class='muted'>{html.escape(txt(parent[j-1]['description'])[:120])}</span>" + (f"<br><q>{html.escape(q)}</q>" if q else '') + "</li>")
            panels.append(f"<div class='panel'><div class='panel-h'>All {len(members)} effect(s) of this study (reported_success is coded per study)</div><ul>{''.join(lis)}</ul></div>")
            if sec != 'na':
                src = (extraction(aid).get('reported_success') or {}).get('source_path') or source
                panels.append(f"<div class='panel'><div class='panel-h'>Currently coded verdict</div><p><b>{html.escape(txt(row['reported_success']))}</b> "
                              f"({html.escape(txt(row['reported_success_quote_source']))}): <q>{html.escape(txt(row['reported_success_quote']))}</q></p>"
                              + ev.view(f"{cid}--coded", src, txt(row['reported_success_quote']), '', side_doi(row, 'r', src), 'Coded author quote in the replication source') + "</div>")
        claim = '' if compact(row['claim_text_o']) == compact(row['description']) or not txt(row['claim_text_o']) else \
            f"<p class='muted'><b>Original claim</b> (p. {html.escape(txt(row['claim_page_o']))}): {html.escape(txt(row['claim_text_o']))}</p>"
        doi_link = f"<a href='https://doi.org/{html.escape(doi)}' target='_blank' rel='noopener'>doi:{html.escape(doi)}</a>" if doi else ''
        cards[sec].append(f"""
<article class="card" id="{cid}" data-id="{cid}" data-auto="{r['final_decision']}">
 <header><h3>{html.escape(cid)}</h3><span class="pill">{html.escape(r['policy'])}</span><span class="pill auto-{r['final_decision']}">{r['final_decision']}</span></header>
 <p class="desc">{html.escape(txt(row['description']))}</p>{claim}
 <p class="muted">{html.escape(txt(row['fred_id']))} · {html.escape(txt(row['ref_o'] if s == 'o' else row['ref_r'])[:160])} {doi_link}</p>
 <div class="change"><span class="old">{html.escape(r['old_value']) or '<i>blank</i>'}</span> → <span class="new">{html.escape(r['new_value'])}</span> <span class="muted">({field})</span></div>
 <table class="sides">{side_table(row, res, 'o')}{side_table(row, res, 'r')}</table>
 <p><b>Why flagged:</b> {html.escape(r['manual_note'] or r['auto_reason'])} <span class="muted">{html.escape(r['tags'])}</span></p>
 <p><b>Review reason:</b> {html.escape(txt(d.get('reason')))}</p>
 <p><b>Location:</b> {html.escape(txt(d.get('location')))} · <b>Quote:</b> <q>{html.escape(txt(d.get('quote')))}</q></p>
 {main_ev}
 {''.join(panels)}
 <div class="decide"><button data-d="apply">Apply</button><button data-d="reject">Reject</button><button data-d="hold">Hold</button>
 <input class="note" placeholder="Note (optional)"><span class="state"></span></div>
</article>""")
        counts[sec] += 1
    ev.finish(cards)
    nav = ''.join(f"<a href='#sec-{k}'>{t} <span class='count' data-sec='{k}'>{len(cards[k])}</span></a>" for k, t, _ in SECTIONS if cards[k])
    body = ''.join(f"<section id='sec-{k}'><h2>{t} <span class='muted'>({len(cards[k])})</span></h2><p class='lead'>{lead}</p>{''.join(cards[k])}</section>"
                   for k, t, lead in SECTIONS if cards[k])
    page = TEMPLATE.replace('__NAV__', nav).replace('__BODY__', body).replace('__STATS__', html.escape(json.dumps({**counts, **ev.stats})))
    (out / 'index.html').write_text(page)
    print(json.dumps({**counts, **ev.stats}))


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FReD Correction Review</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔍</text></svg>">
<style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1b;--muted:#6b6b66;--line:#deded8;--accent:#2b5fab;--ok:#2e7d32;--bad:#b3261e;--warn:#9a6700;--hl:rgba(255,200,0,.35)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#151514;--card:#1f1f1d;--ink:#ecece8;--muted:#a3a39c;--line:#3a3a36;--accent:#8ab4f8;--ok:#81c995;--bad:#f28b82;--warn:#fdd663;--hl:rgba(255,200,0,.3)}}
:root[data-theme="dark"]{--bg:#151514;--card:#1f1f1d;--ink:#ecece8;--muted:#a3a39c;--line:#3a3a36;--accent:#8ab4f8;--ok:#81c995;--bad:#f28b82;--warn:#fdd663}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
.top{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px}
.top h1{font-size:18px;margin:0 0 6px}.nav{display:flex;flex-wrap:wrap;gap:8px}.nav a{color:var(--accent);text-decoration:none;font-size:13px;border:1px solid var(--line);border-radius:999px;padding:2px 10px}
.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px;font-size:13px}
main{max-width:1000px;margin:0 auto;padding:16px}section,.card{scroll-margin-top:150px}h2{margin-top:32px}.lead{color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:14px 0}
.card header{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.card h3{margin:0;font-size:15px;font-family:ui-monospace,monospace}
.pill{font-size:12px;border:1px solid var(--line);border-radius:999px;padding:0 8px;color:var(--muted)}
.desc{font-weight:600;margin:8px 0 2px}.muted{color:var(--muted);font-size:13px}
.change{font-size:17px;margin:8px 0}.old{text-decoration:line-through;color:var(--bad)}.new{color:var(--ok);font-weight:600}
.sides{width:100%;border-collapse:collapse;font-size:13px;margin:6px 0}.sides th,.sides td{border-top:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}
.v{font-size:11px;border-radius:4px;padding:0 4px}.v-error{color:var(--bad)}.v-correct{color:var(--ok)}.v-unverified,.v-not_comparable{color:var(--warn)}
.shot{margin:8px 0}.imgwrap{position:relative;display:inline-block;max-width:100%;border:1px solid var(--line)}.imgwrap img{display:block;max-width:100%;height:auto;background:#fff}
.hl{position:absolute;background:var(--hl);outline:2px solid rgba(255,170,0,.8);pointer-events:none}
.panel{border-left:3px solid var(--line);padding:2px 0 2px 12px;margin:12px 0}.panel-h{font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted);margin:4px 0}.cons{border-collapse:collapse;font-size:13px;width:100%}.cons th,.cons td{border-top:1px solid var(--line);padding:3px 6px;text-align:left}
.excerpt{font-size:13px;background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:8px;overflow-wrap:anywhere}mark{background:var(--hl);color:inherit}
.decide{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:10px}.decide button{border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:6px;padding:4px 12px;cursor:pointer}
.decide button.on[data-d=apply]{background:var(--ok);color:#fff}.decide button.on[data-d=reject]{background:var(--bad);color:#fff}.decide button.on[data-d=hold]{background:var(--warn);color:#000}
.note{flex:1;min-width:180px;padding:4px 8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
.card.decided{opacity:.75}body.hide-decided .card.decided{display:none}q{font-style:italic}details{font-size:13px}
input,button{font:inherit}
</style></head><body>
<div class="top"><h1>FReD correction review</h1><nav class="nav">__NAV__</nav>
<div class="tools"><label>Reviewer <input id="reviewer" value="Lukas Wallrich"></label><span id="progress"></span>
<label><input type="checkbox" id="hide"> Hide decided</label><button id="export">Download manual_decisions rows</button><span class="muted" title="__STATS__">Private: contains source excerpts.</span></div></div>
<main>__BODY__</main>
<script>
const KEY='fred-correction-review-2026-11';let st={};try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}};
function paint(card){const s=st[card.dataset.id];card.querySelectorAll('button[data-d]').forEach(b=>b.classList.toggle('on',!!s&&s.d===b.dataset.d));
card.classList.toggle('decided',!!(s&&s.d));card.querySelector('.state').textContent=s&&s.d?('decided '+(s.date||'')):'';const n=card.querySelector('.note');if(s&&s.note&&!n.value)n.value=s.note}
function progress(){const all=document.querySelectorAll('.card').length,done=Object.values(st).filter(s=>s.d).length;document.getElementById('progress').textContent=done+' of '+all+' decided'}
document.querySelectorAll('.card').forEach(card=>{paint(card);card.querySelectorAll('button[data-d]').forEach(b=>b.onclick=()=>{const id=card.dataset.id,cur=st[id]||{};
if(cur.d===b.dataset.d){delete cur.d}else{cur.d=b.dataset.d;cur.date=new Date().toISOString().slice(0,10)}st[id]=cur;save();paint(card);progress()});
card.querySelector('.note').oninput=e=>{const id=card.dataset.id;st[id]=Object.assign(st[id]||{},{note:e.target.value});save()}});
document.getElementById('hide').onchange=e=>document.body.classList.toggle('hide-decided',e.target.checked);
document.getElementById('export').onclick=()=>{const rev=document.getElementById('reviewer').value.trim()||'reviewer';const q=v=>'"'+String(v||'').replace(/"/g,'""')+'"';
const rows=['correction_id,decision,reviewer,date,note'].concat(Object.entries(st).filter(([k,s])=>s.d).map(([k,s])=>[k,s.d,q(rev),s.date,q(s.note)].join(',')));
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([rows.join('\n')+'\n'],{type:'text/csv'}));a.download='manual_decisions_review.csv';a.click()};
progress();
</script></body></html>"""

if __name__ == '__main__':
    main()
