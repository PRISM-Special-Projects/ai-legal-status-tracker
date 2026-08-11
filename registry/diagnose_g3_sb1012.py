#!/usr/bin/env python3
"""One-shot diagnostic for G3 Missouri SB 1012 before migration."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
bills=json.loads((root/'bills.json').read_text())
rec=next(b for b in bills['bills'] if b['id']=='mo-sb1012-2026')
print('=== CURRENT BILL RECORD ===')
print(json.dumps(rec, indent=2, ensure_ascii=False))
ev=json.loads((root/'claim_evidence.json').read_text())
er=next((r for r in ev['records'] if r['record_id']=='mo-sb1012-2026'), None)
print('=== CURRENT CLAIM EVIDENCE ===')
print(json.dumps(er, indent=2, ensure_ascii=False))
print('=== EXISTING SB1012 TEXTS ===')
for p in sorted((root/'texts').glob('*sb1012*')):
    print(p.name, p.stat().st_size)
raise SystemExit('diagnostic only')
