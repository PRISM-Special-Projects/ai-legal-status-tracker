#!/usr/bin/env python3
"""Pin observed parse signatures for the G1/G2 texts admitted to the registry."""
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'site'/'test_diff.py'
s=p.read_text()
needle='  "mo-hb1462-2025--introduced.txt": [26, 0, 0],\n'
entries=(
 '  "mo-hb1746-2026--introduced-3891H.01I.txt": [26, 0, 0],\n'
 '  "nd-hb1361-2023--enrolled-23.0346.05000.txt": [3, 0, 0],\n'
 '  "nd-hb1361-2023--introduced-23.0346.02000.txt": [3, 0, 0],\n'
 '  "nd-hb1361-2023--senate-amended-23.0346.04000.txt": [3, 0, 0],\n'
)
assert needle in s
for entry in entries:
    assert entry not in s
s=s.replace(needle, needle+entries)
p.write_text(s)
print('G1/G2 differ fixtures pinned from diagnostic signatures')
