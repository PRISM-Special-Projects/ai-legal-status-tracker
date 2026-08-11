#!/usr/bin/env python3
"""Tracker-focused publication audit.

This is deliberately narrower than the provenance/differ machinery. It catches
publication-facing contradictions that could make the tracker materially wrong or
misleading. It does not require exhaustive version graphs or perfect PDF parsing.
"""
import json, pathlib, collections, sys

ROOT = pathlib.Path(__file__).resolve().parent
data = json.loads((ROOT / 'bills.json').read_text())
bills = data['bills']
errors=[]
warnings=[]

def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)

ids=set()
states=set()
groups=collections.defaultdict(list)
for b in bills:
    bid=b.get('id','<no id>')
    state=(b.get('jurisdiction') or {}).get('state')
    states.add(state)
    if bid in ids: err(f'{bid}: duplicate record id')
    ids.add(bid)

    status=b.get('status') or {}
    ver=b.get('verification') or {}
    stage=status.get('stage')

    # P1/P2: publication should not claim a record is verified while the operative
    # text is still unread.
    if ver.get('operative_text') != 'read_in_full':
        err(f"{bid}: operative_text={ver.get('operative_text')!r}, not read_in_full")

    notes=(b.get('notes') or '').lower()
    stale_markers=(
        'still to be read', 'operative text not read', 'still to be read verbatim',
        'still to confirm', 'needs primary-source verification',
    )
    for marker in stale_markers:
        if marker in notes:
            warn(f'{bid}: notes contain stale-review marker {marker!r}')

    # P1: terminal/current-state claims need an evidentiary action line.
    if stage in {'enacted','failed','dead'} and not status.get('evidence'):
        err(f'{bid}: terminal status {stage} lacks status.evidence')

    # P1: enacted laws must tell a reader where the law landed and when it took effect.
    if stage == 'enacted':
        if not b.get('codified_at'): err(f'{bid}: enacted but codified_at is empty')
        if not b.get('effective_date'): err(f'{bid}: enacted but effective_date is empty')

    # P4: every publication record must expose a primary source.
    primary=(b.get('sources') or {}).get('primary') or []
    if not primary: err(f'{bid}: no primary source')

    # P2: a record must explain its operative legal proposition somewhere readable.
    if not b.get('key_clause') and not b.get('notes'):
        err(f'{bid}: neither key_clause nor explanatory notes present')

    if b.get('companion_group'):
        groups[b['companion_group']].append(bid)

for g,members in groups.items():
    if len(members) < 2:
        err(f'companion_group {g!r} has only one member: {members}')

# Cross-record sanity checks for the current publication corpus.
if len(bills) != 29:
    warn(f'expected current H-gate corpus of 29 records; found {len(bills)}')
if len(states) != 16:
    warn(f'expected current H-gate corpus of 16 states; found {len(states)}')

stage_counts=collections.Counter((b.get('status') or {}).get('stage') for b in bills)
print(f'PUBLICATION AUDIT: {len(bills)} records across {len(states)} states')
print('stages:', dict(sorted(stage_counts.items())))
print(f'errors: {len(errors)}  warnings: {len(warnings)}')
for x in errors: print('ERROR:', x)
for x in warnings: print('WARN:', x)
if errors:
    sys.exit(1)
