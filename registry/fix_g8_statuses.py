#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).parent

# 1. Correct tracker-facing bill status/text-verification fields.
p = root / 'bills.json'
data = json.loads(p.read_text())
updates = {
    'ok-hb3546-2026': {
        'stage': 'failed',
        'as_of': '2026-08-11',
        'source_url': 'https://www.oklegislature.gov/BillInfo.aspx?Bill=hb3546&Session=2600',
        'evidence': {
            'action': 'Last action: Placed on General Order in Senate 04/21/2026; 2026 regular session adjourned sine die without Senate passage',
            'date': '2026-04-21'
        },
        'basis': 'session_rule'
    },
    'sc-hb3796-2025': {
        'stage': 'failed',
        'as_of': '2026-08-11',
        'source_url': 'https://www.scstatehouse.gov/sess126_2025-2026/bills/3796.htm',
        'evidence': {
            'action': 'Last action: Referred to House Judiciary 01/28/2025; 126th regular session adjourned sine die 05/14/2026 without further action',
            'date': '2025-01-28'
        },
        'basis': 'session_rule'
    },
}
for bill in data['bills']:
    bid = bill.get('id')
    if bid in updates:
        bill['status'] = updates[bid]
        bill['last_verified'] = '2026-08-11'
        bill.setdefault('verification', {})['status'] = 'verified_primary'
        bill['verification']['last_verified'] = '2026-08-11'
    if bid == 'ok-hb3546-2026':
        bill['verification']['operative_text'] = 'read_in_full'
        bill['verification']['operative_text_note'] = 'Official introduced and House floor texts reviewed; operative personhood clause unchanged.'
        bill['notes'] = bill.get('notes','').replace(
            'Operative text not on the status page - still to be read.',
            'Official introduced and House floor texts reviewed 2026-08-11; operative personhood clause confirmed. STATUS CORRECTION: bill did not receive Senate floor passage before the 2026 session adjourned sine die, so current stage is failed.'
        )
    elif bid == 'sc-hb3796-2025':
        bill['verification']['operative_text'] = 'read_in_full'
        bill['verification']['operative_text_note'] = 'Official South Carolina bill text reviewed in full.'
        bill['notes'] = bill.get('notes','').replace(
            'Operative list not on the summary page - still to be read verbatim.',
            'Official bill text reviewed 2026-08-11; operative list confirmed. STATUS CORRECTION: no action followed the 2025 Judiciary referral before the 126th regular session adjourned sine die on 14 May 2026, so current stage is failed.'
        )
    elif bid == 'wa-hb2029-2025':
        bill['verification']['operative_text'] = 'read_in_full'
        bill['verification']['operative_text_note'] = 'Official Washington bill text reviewed in full during the tracker-focused G8 screen.'
        bill['verification']['last_verified'] = '2026-08-11'
        bill['last_verified'] = '2026-08-11'
    elif bid == 'ca-ab2023-2026':
        bill['verification']['operative_text'] = 'read_in_full'
        bill['verification']['operative_text_note'] = 'Current amended California text reviewed during G6; the chatbot sentience/consciousness/humanity clause was confirmed directly.'
        bill['verification']['last_verified'] = '2026-08-11'
        bill['last_verified'] = '2026-08-11'
        bill['notes'] = bill.get('notes','').replace(
            'The specific bar on chatbots claiming sentience/consciousness/humanity to children sits in the full text, not the status page - still to be read verbatim.',
            'The amended full text was reviewed directly on 2026-08-11; the covered/prohibited conduct includes a companion chatbot claiming that it is sentient, conscious, or human.'
        )
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

# 2. Update the existing South Carolina claim edge from an intermediate action
#    to the current, session-rule-derived terminal status.
ce_path = root / 'claim_evidence.json'
ce = json.loads(ce_path.read_text())
for record in ce['records']:
    if record.get('record_id') != 'sc-hb3796-2025':
        continue
    record['claims'] = [{
        'claim': {'field': 'status.stage'},
        'value': 'failed',
        'mode': 'derived',
        'supports': [
            {
                'source_ref': 'sc-hb3796-actions',
                'locator': '2025-01-28 — Referred to Committee on Judiciary; no later bill action'
            },
            {
                'source_ref': 'sc-2026-session-end',
                'locator': 'Regular annual session adjourned sine die on 2026-05-14'
            }
        ],
        'derivation': 'H.3796 received no action after its 2025 Judiciary referral before the 126th regular session adjourned sine die; it therefore failed at session end.'
    }]
    break
ce_path.write_text(json.dumps(ce, indent=2, ensure_ascii=False) + '\n')

# 3. Register the official session-end source used by that derived claim.
sc_path = root / 'source_catalog.json'
sc = json.loads(sc_path.read_text())
if not any(s.get('id') == 'sc-2026-session-end' for s in sc['sources']):
    sc['sources'].append({
        'id': 'sc-2026-session-end',
        'label': 'South Carolina General Assembly — 2026 regular-session sine die record',
        'kind': 'session_record',
        'url': 'https://www.scstatehouse.gov/sess126_2025-2026/sj26/20260515.htm',
        'jurisdiction': 'SC',
        'note': 'Official Senate Journal states that the regular annual session adjourned sine die on May 14, 2026.'
    })
sc_path.write_text(json.dumps(sc, indent=2, ensure_ascii=False) + '\n')

print('G8 tracker-facing verification corrections applied')
