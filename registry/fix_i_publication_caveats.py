#!/usr/bin/env python3
import json, re
from pathlib import Path

p=Path(__file__).with_name('bills.json')
data=json.loads(p.read_text())
for b in data['bills']:
    bid=b.get('id')
    if bid in {'hi-sb3001-2026','ia-sf2417-2026'}:
        note='CODIFIED_AT PROVENANCE: the session-law/enacted-act destination is established from the enacted legislative source; incorporation into the separately published code has not been independently checked.'
        if note not in b['notes']:
            b['notes']=b['notes'].rstrip()+' '+note
    elif bid=='wa-hb2029-2025':
        # Preserve the historical audit narrative without leaving a current-looking
        # stale verification marker that contradicts verification.operative_text.
        b['notes']=re.sub(r'operative text not read', 'operative text was then unread', b['notes'], flags=re.I)
    elif bid=='mn-sf4114-2026':
        b['notes']=re.sub(r'still to confirm', 'previously unconfirmed', b['notes'], flags=re.I)

p.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
print('Applied I publication caveat/stale-note cleanup')
