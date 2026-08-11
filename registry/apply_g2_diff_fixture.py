#!/usr/bin/env python3
"""Diagnose parse signatures for all newly admitted, unpinned registry texts."""
import ast
import pathlib
import sys

root=pathlib.Path(__file__).resolve().parent.parent
site=root/'site'; texts=root/'registry'/'texts'
sys.path.insert(0,str(site))
import legdiff as L

test=(site/'test_diff.py').read_text()
mod=ast.parse(test)
pinned={}
for node in mod.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CORPUS_PARSE' for t in node.targets):
        pinned=ast.literal_eval(node.value)
        break
assert pinned
for f in sorted(texts.glob('*.txt')):
    if f.name in pinned:
        continue
    p=L.parse(L.strip_preamble(f.read_text()))
    sig=[len(p.nodes),len(p.nodes)-len({n.path for n in p.nodes}),len(p.warnings)]
    print(f'UNPINNED {f.name}: {sig}')
raise SystemExit('diagnostic only — inspect signatures before pinning')
