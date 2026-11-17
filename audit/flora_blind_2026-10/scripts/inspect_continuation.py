#!/usr/bin/env python3
"""Print uninspected terminal replies with their primary-source context."""
import json
import re
import sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
inspection = json.loads((R/'continuation_inspection.json').read_text())['works']
keys = list(dict.fromkeys(i['file_key'] for i in json.loads((R/'adjudication_selection_continuation.json').read_text())['items']))
shown = 0
for fk in keys:
    if fk in inspection:
        continue
    p = R/'argon'/f'{fk}.state.json'
    state = json.loads(p.read_text()) if p.exists() else {}
    if state.get('status') not in ('validated', 'unresolved'):
        continue
    print('\nWORK', fk, 'STATE', state.get('status'), 'ATTEMPTS', state.get('attempts'), state.get('reason', ''))
    p = R/'adjudications'/f'{fk}.json'
    obj = json.loads(p.read_text()) if p.exists() else {'decisions': []}
    source = (R/'texts'/f'{fk}.txt').read_text()
    source = re.sub(r'(?<=\w)[-\u00ad][ \t]*\n[ \t]*(?=\w)', '', source)
    source = re.sub(r'\s+', ' ', source)
    for d in obj['decisions']:
        print(json.dumps(d, ensure_ascii=False))
        quote = re.sub(r'\s+', ' ', d['quote'])
        start = source.find(quote)
        if start >= 0:
            print('CONTEXT:', source[max(0, start-450):start+len(quote)+650])
        else:
            print('Review literal whitespace/hyphenation context separately.')
    shown += 1
    if shown >= int(sys.argv[1] if len(sys.argv)>1 else 6):
        break
