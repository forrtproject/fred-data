"""Transport a reviewed prompt as an argv item, without shell interpolation."""
import json
import os
import sys
from pathlib import Path

F = Path(__file__).resolve().parent
B = F.parent
key = sys.argv[1]
records = json.loads((F / 'adjudication_queue.json').read_text())
record = next(r for r in records if r['key'] == key)
prompt = Path(record['prompt']).read_text()
os.execvp('agy', ['agy', '-p', prompt, '--model', 'Gemini 4 Argon (High)',
                 '--sandbox', '--add-dir', str((B / 'texts').absolute()),
                 '--add-dir', str((B / 'texts').resolve()),
                 '--add-dir', '/home/lukas/work/fred-mac-recovery-20261030',
                 '--print-timeout', '10m'])
