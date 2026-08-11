#!/usr/bin/env python3
"""One-shot G4 correction: represent the material SA1113 -> HA1260 study rewrites."""
import json
from pathlib import Path

p = Path(__file__).with_name('bills.json')
data = json.loads(p.read_text())
ids = {'tn-hb1455-2025', 'tn-sb1493-2025'}
sa_url = 'https://www.capitol.tn.gov/Bills/114/Amend/SA1113.pdf'

for b in data['bills']:
    if b.get('id') not in ids:
        continue
    versions = b.setdefault('versions', [])
    if not any('SA1113' in (v.get('label') or '') for v in versions):
        v = {
            'label': 'Senate Amendment 3 (SA1113) — rewrites bill as Tennessee AI Advisory Council study',
            'date': '2026-04-23',
            'source_url': sa_url,
            'text_path': None,
            'provisions': ['study_only']
        }
        idx = next((i for i,x in enumerate(versions) if 'HA1260' in (x.get('label') or '')), len(versions))
        versions.insert(idx, v)
    prim = b.setdefault('sources', {}).setdefault('primary', [])
    if sa_url not in prim:
        prim.append(sa_url)
    old = 'MECHANISM OF REMOVAL: Amendment No. 4 (HA1260), moved by Rep. ZACHARY, again by \'deleting all language after the enacting clause and substituting\' - the whole criminal-and-civil scheme replaced by the TACIR study.'
    new = ('MATERIAL AMENDMENT HISTORY: the criminal-and-civil scheme was removed in two stages on 23 April 2026. '
           'The Senate first adopted Amendment No. 3 (SA1113), which rewrote the bill as a Tennessee Artificial Intelligence Advisory Council study with a 31 December 2026 report. '
           'The House then adopted Amendment No. 4 (HA1260), another whole-bill substitute, replacing that council study with the TACIR study enacted in Public Chapter 1066.')
    notes = b.get('notes','')
    if old in notes:
        b['notes'] = notes.replace(old, new)
    elif 'MATERIAL AMENDMENT HISTORY:' not in notes:
        b['notes'] = notes + ' ' + new
    changes = b.setdefault('derived_from_changes', [])
    statement = ('SA1113 first replaced the introduced criminal/civil AI-training regime with an AI Advisory Council study; HA1260 then replaced that study with the final TACIR study.')
    if statement not in changes:
        changes.append(statement)

p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
print('G4 Tennessee substantive history reconciled')
