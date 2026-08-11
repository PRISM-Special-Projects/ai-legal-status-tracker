#!/usr/bin/env python3
"""Pin the newly admitted HB 1746 introduced text in the structural-differ corpus fixture."""
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'site'/'test_diff.py'
s=p.read_text()
needle='  "mo-hb1462-2025--introduced.txt": [26, 0, 0],\n'
entry='  "mo-hb1746-2026--introduced-3891H.01I.txt": [26, 0, 0],\n'
assert needle in s
assert entry not in s
s=s.replace(needle, needle+entry)
p.write_text(s)
print('G2 differ fixture pinned')
