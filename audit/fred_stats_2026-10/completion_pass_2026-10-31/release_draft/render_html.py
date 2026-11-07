"""Screenshot the region of a web page (or local HTML table) around a quote, with the quote highlighted.

Run under Playwright, e.g. `uvx --with playwright python render_html.py jobs.json results.json`.
Each job: {"id", "url", "probes": [compact letter/digit strings], "out": png path}.
"""
import glob, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

FIND = r"""
(probes) => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let joined = '', map = [], node;
  while ((node = walker.nextNode())) {
    const t = node.textContent.normalize('NFKC').toLowerCase();
    for (let i = 0; i < t.length; i++) {
      if (/[a-z0-9]/.test(t[i])) { joined += t[i]; map.push([node, i]); }
    }
  }
  for (const p of probes) {
    const pos = joined.indexOf(p);
    if (pos < 0) continue;
    const [n0, o0] = map[pos], [n1, o1] = map[pos + p.length - 1];
    const range = document.createRange();
    range.setStart(n0, o0); range.setEnd(n1, o1 + 1);
    const rects = [...range.getClientRects()];
    const hl = document.createElement('div'); hl.id = '__hl';
    document.body.appendChild(hl);
    const box = range.getBoundingClientRect();
    window.scrollTo(0, Math.max(0, window.scrollY + box.top - 250));
    const b = range.getBoundingClientRect();
    for (const r of [...range.getClientRects()]) {
      const d = document.createElement('div');
      Object.assign(d.style, {position: 'absolute', left: (r.left + window.scrollX) + 'px', top: (r.top + window.scrollY) + 'px',
        width: r.width + 'px', height: r.height + 'px', background: 'rgba(255,200,0,.35)', outline: '2px solid rgba(255,170,0,.85)',
        zIndex: 2147483647, pointerEvents: 'none'});
      hl.appendChild(d);
    }
    return {top: b.top, bottom: b.bottom, probe: p};
  }
  return null;
}
"""


def main():
    jobs = json.loads(Path(sys.argv[1]).read_text())
    exe = sorted(glob.glob(str(Path.home() / '.cache/ms-playwright/chromium-*/chrome-linux*/chrome')))
    results = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=exe[-1] if exe else None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1100, 'height': 900}, device_scale_factor=1)
        loaded = None
        for job in jobs:
            try:
                if job['url'] != loaded:
                    page.goto(job['url'], wait_until='networkidle', timeout=90000)
                    page.wait_for_timeout(1500)
                    loaded = job['url']
                else:
                    page.evaluate("document.getElementById('__hl') && document.getElementById('__hl').remove()")
                if job.get('selector'):
                    hit = page.evaluate("""(sel) => { const els = [...document.querySelectorAll(sel)]; if (!els.length) return null;
                        els[0].scrollIntoView({block: 'center'}); let t = Infinity, b = -Infinity;
                        for (const e of els) { const r = e.getBoundingClientRect(); t = Math.min(t, r.top); b = Math.max(b, r.bottom); }
                        return {top: t, bottom: b}; }""", job['selector'])
                else:
                    hit = page.evaluate(FIND, job['probes'])
                if not hit:
                    results[job['id']] = None
                    continue
                page.wait_for_timeout(300)
                top = max(0, hit['top'] - 160)
                height = min(900 - top, max(hit['bottom'] - hit['top'], 20) + 320)
                page.screenshot(path=job['out'], clip={'x': 0, 'y': top, 'width': 1100, 'height': height})
                results[job['id']] = {'url': job['url'], 'top': (hit['top'] - top) / height, 'height': (hit['bottom'] - hit['top']) / height}
            except Exception as e:  # keep going; the card falls back to the text excerpt
                results[job['id']] = {'error': str(e)[:200]}
        browser.close()
    Path(sys.argv[2]).write_text(json.dumps(results, indent=1))


if __name__ == '__main__':
    main()
