#!/usr/bin/env python3
import json
from pathlib import Path

p = Path(__file__).with_name('bills.json')
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
    if bill.get('id') in updates:
        bill['status'] = updates[bill['id']]
        bill['last_verified'] = '2026-08-11'
        bill.setdefault('verification', {})['status'] = 'verified_primary'
        bill['verification']['last_verified'] = '2026-08-11'
        if bill['id'] == 'ok-hb3546-2026':
            bill['verification']['operative_text'] = 'read_in_full'
            bill['verification']['operative_text_note'] = 'Official introduced and House floor texts reviewed; operative personhood clause unchanged.'
            bill['notes'] = bill.get('notes','').replace('Operative text not on the status page - still to be read.', 'Official introduced and House floor texts reviewed 2026-08-11; operative personhood clause confirmed. STATUS CORRECTION: bill did not receive Senate floor passage before the 2026 session adjourned sine die, so current stage is failed.')
        if bill['id'] == 'sc-hb3796-2025':
            bill['verification']['operative_text'] = 'read_in_full'
            bill['verification']['operative_text_note'] = 'Official South Carolina bill text reviewed in full.'
            bill['notes'] = bill.get('notes','').replace('Operative list not on the summary page - still to be read verbatim.', 'Official bill text reviewed 2026-08-11; operative list confirmed. STATUS CORRECTION: no action followed the 2025 Judiciary referral before the 126th regular session adjourned sine die on 14 May 2026, so current stage is failed.')
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
print('G8 substantive status corrections applied')
