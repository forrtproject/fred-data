#!/usr/bin/env python3
"""Draw the QA tripwire sample without exposing first reviews to the second reader."""
import json
import random
import sys

import build_field_ledger as L

FIRST = L.P / 'adversarial_20261103'
QA = L.P / 'adversarial_qa_20261103'
SEED = 20261103


def main(size=15):
    registry = L.read(L.T / 'adversarial_review_registry.json')
    eligible = sorted(k for k, v in registry['bundles'].items()
                      if v['verdict'] == 'supported' and v['confidence'] == 'high' and not v['failures'])
    chosen = random.Random(SEED).sample(eligible, min(size, len(eligible)))
    plan = {}
    for index, bundle in enumerate(chosen, 1):
        request_id = f'q{index:04d}'
        original = registry['bundles'][bundle]['request_id']
        request = json.loads((FIRST / original / 'request.json').read_text())
        request['request_id'] = request_id
        directory = QA / request_id
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'request.json').write_text(json.dumps(request, ensure_ascii=False, indent=1) + '\n')
        plan[request_id] = dict(bundle=bundle, first_request=original)
    (QA / 'parent_map.json').write_text(json.dumps(plan, indent=1) + '\n')
    instructions = (FIRST / 'REVIEWER_INSTRUCTIONS.md').read_text()
    instructions = instructions.replace('`python3 ../../../../independent_recode_20261101/adversary_read.py rNNNN 0`',
                                        '`ADVERSARY_FOLDER=adversarial_qa_20261103 python3 ../../../../independent_recode_20261101/adversary_read.py rNNNN 0`')
    instructions = instructions.replace('`rNNNN`', '`qNNNN`').replace('rNNNN', 'qNNNN').replace('r0001 supported high', 'q0001 supported high')
    (QA / 'REVIEWER_INSTRUCTIONS.md').write_text(instructions)
    print(json.dumps(dict(eligible=len(eligible), chosen=plan), indent=1))


if __name__ == '__main__':
    main(*map(int, sys.argv[1:]))
