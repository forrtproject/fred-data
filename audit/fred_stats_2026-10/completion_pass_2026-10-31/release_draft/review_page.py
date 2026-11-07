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
from compare import load_adjudications, combine_obvious, SOURCE_PROVENANCE  # noqa: E402
import policy_ledger  # noqa: E402

CLOUD = Path('/home/lukas/cloud-data')
AUDIT_SOURCES = CLOUD / 'fred-stats-2026-10-b48a7d6-20261029T092009Z'
PAPER_CACHE = [Path.home() / '.claude/cache/pdfs', CLOUD / 'paper-cache']
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
        m = re.search(r'([0-9a-f]{24})', Path(txt(source_path)).name)
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
            self.pages[pdf] = [norm(p) for p in out.split('\f')]
        return self.pages[pdf]


def find_page(pages, quote):
    for frag in fragments(quote):
        f = norm(frag)
        for probe in (f[:80], f[:40]):
            if len(probe) < 12:
                continue
            hits = [i for i, t in enumerate(pages) if probe in t]
            if hits:
                return hits[0] + 1, frag
    return None, None


def crop(pdf, page, frag, out_png):
    """Render the band of the page around the matched fragment; return highlight box as fractions."""
    xml = subprocess.run(['pdftotext', '-q', '-bbox-layout', '-f', str(page), '-l', str(page), str(pdf), '-'],
                         capture_output=True, text=True, errors='replace').stdout
    pm = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', xml)
    if not pm:
        return None
    width, height = float(pm[1]), float(pm[2])
    words = [(float(a), float(b), float(c), float(d), norm(html.unescape(w)))
             for a, b, c, d, w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', xml)]
    target = norm(frag).split()
    if not target or not words:
        return None
    probe = target[:min(5, len(target))]
    tokens = [w[4] for w in words]
    start = next((i for i in range(len(tokens) - len(probe) + 1) if all(probe[k] in tokens[i + k] or tokens[i + k] in probe[k] for k in range(len(probe)))), None)
    if start is None:
        return None
    end = min(len(words), start + max(len(target), len(probe)))
    span = words[start:end]
    y0, y1 = min(w[1] for w in span), max(w[3] for w in span)
    top, bottom = max(0, y0 - 60), min(height, max(y1, y0 + 20) + 150)
    dpi = 130; scale = dpi / 72
    subprocess.run(['pdftoppm', '-q', '-png', '-singlefile', '-r', str(dpi), '-f', str(page), '-l', str(page),
                    '-x', '0', '-y', str(int(top * scale)), '-W', str(int(width * scale)), '-H', str(int((bottom - top) * scale)),
                    str(pdf), str(out_png.with_suffix(''))], check=True)
    band = bottom - top
    return {'left': min(w[0] for w in span) / width, 'width': (max(w[2] for w in span) - min(w[0] for w in span)) / width,
            'top': (y0 - top) / band, 'height': (y1 - y0) / band, 'page': page}


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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', required=True)
    out = Path(ap.parse_args().out).resolve()
    assert not out.is_relative_to(REPO.resolve()), 'Review output holds private source material; keep it outside the repository'
    (out / 'shots').mkdir(parents=True, exist_ok=True)
    ledger = list(csv.DictReader((P / 'application_decisions.csv').open(encoding='utf-8-sig')))
    parent = json.loads((B / 'parent_rows.json').read_text())
    results = {int(r['input_row_index']): r for r in csv.DictReader((B / 'results.csv').open(encoding='utf-8-sig'))}
    decisions = combine_obvious(load_adjudications(B), json.loads((B / 'obvious_resolutions.json').read_text()))
    groups = collections.defaultdict(list)
    for i, row in enumerate(parent, 1):
        groups[policy_ledger.study_key(row)].append(i)
    pdfs = Pdfs(Path('/tmp/claude-1000/fred-review-pdfs'))
    cards = collections.defaultdict(list); stats = collections.Counter()
    for r in ledger:
        sec = section(r)
        if not sec:
            continue
        aid, field = int(r['audit_id']), r['field']; row = parent[aid - 1]; res = results[aid]; d = decisions[(aid, field)]
        s = 'r' if field == 'reported_success' else field[-1]
        source = d.get('source_path') or ''
        doi = (SOURCE_PROVENANCE.get(source) or {}).get('work_doi') or row['doi_o' if s == 'o' else 'doi_r'] or ''
        evidence, shot = '', None
        if sec != 'na':
            for pdf in pdfs.candidates(source, doi):
                local = pdfs.local(pdf)
                page, frag = find_page(pdfs.page_texts(local), d.get('quote'))
                if page:
                    png = out / 'shots' / f"{r['correction_id']}.png"
                    shot = crop(local, page, frag, png)
                    if shot:
                        break
            if shot:
                stats['screenshot'] += 1
                evidence = (f"<figure class='shot'><div class='imgwrap'><img loading='lazy' src='shots/{r['correction_id']}.png' alt='Source page {shot['page']} around the quote'>"
                            f"<span class='hl' style='left:{shot['left']*100:.1f}%;top:{shot['top']*100:.1f}%;width:{shot['width']*100:.1f}%;height:{max(shot['height'],0.04)*100:.1f}%'></span></div>"
                            f"<figcaption>Cached PDF, page {shot['page']}</figcaption></figure>")
            else:
                ex = excerpt(source, d.get('quote'))
                stats['text excerpt' if ex else 'no evidence view'] += 1
                evidence = f"<div class='excerpt'><div class='muted'>No cached PDF page found; private source text:</div>{ex}</div>" if ex else "<div class='muted'>No cached PDF or text excerpt located.</div>"
        doi_link = f"<a href='https://doi.org/{html.escape(doi)}' target='_blank' rel='noopener'>doi:{html.escape(doi)}</a>" if doi else ''
        rs_block = ''
        if field == 'reported_success':
            members = groups[policy_ledger.study_key(row)]
            lis = ''.join(f"<li>{j}: {html.escape(txt(parent[j-1]['reported_success']))} <span class='v v-{results[j]['reported_success_final_verdict']}'>{results[j]['reported_success_final_verdict']}</span>"
                          + (f" → {html.escape(results[j]['reported_success_suggested_correction'])}" if results[j]['reported_success_final_verdict'] == 'error' else '')
                          + f" <span class='muted'>{html.escape(txt(parent[j-1]['description'])[:110])}</span></li>" for j in members)
            rs_block = (f"<details><summary>Study has {len(members)} effect(s)</summary><ul>{lis}</ul></details>"
                        f"<p><b>Coded author quote</b> ({html.escape(txt(row['reported_success_quote_source']))}): <q>{html.escape(txt(row['reported_success_quote']))}</q></p>")
        cards[sec].append(f"""
<article class="card" id="{r['correction_id']}" data-id="{r['correction_id']}" data-auto="{r['final_decision']}">
 <header><h3>{html.escape(r['correction_id'])}</h3><span class="pill">{html.escape(r['policy'])}</span><span class="pill auto-{r['final_decision']}">{r['final_decision']}</span></header>
 <p class="desc">{html.escape(txt(row['description']))}</p>
 <p class="muted">{html.escape(txt(row['fred_id']))} · {html.escape(txt(row['ref_o'] if s == 'o' else row['ref_r'])[:160])} {doi_link}</p>
 <div class="change"><span class="old">{html.escape(r['old_value']) or '<i>blank</i>'}</span> → <span class="new">{html.escape(r['new_value'])}</span> <span class="muted">({field})</span></div>
 <table class="sides">{side_table(row, res, 'o')}{side_table(row, res, 'r')}</table>
 {rs_block}
 <p><b>Why flagged:</b> {html.escape(r['manual_note'] or r['auto_reason'])} <span class="muted">{html.escape(r['tags'])}</span></p>
 <p><b>Review reason:</b> {html.escape(txt(d.get('reason')))}</p>
 <p><b>Location:</b> {html.escape(txt(d.get('location')))}</p>
 <p><b>Quote:</b> <q>{html.escape(txt(d.get('quote')))}</q></p>
 {evidence}
 <div class="decide"><button data-d="apply">Apply</button><button data-d="reject">Reject</button><button data-d="hold">Hold</button>
 <input class="note" placeholder="Note (optional)"><span class="state"></span></div>
</article>""")
        stats[sec] += 1
    nav = ''.join(f"<a href='#sec-{k}'>{t} <span class='count' data-sec='{k}'>{len(cards[k])}</span></a>" for k, t, _ in SECTIONS if cards[k])
    body = ''.join(f"<section id='sec-{k}'><h2>{t} <span class='muted'>({len(cards[k])})</span></h2><p class='lead'>{lead}</p>{''.join(cards[k])}</section>"
                   for k, t, lead in SECTIONS if cards[k])
    page = TEMPLATE.replace('__NAV__', nav).replace('__BODY__', body).replace('__STATS__', html.escape(json.dumps(dict(stats))))
    (out / 'index.html').write_text(page)
    print(json.dumps(dict(stats)))


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
