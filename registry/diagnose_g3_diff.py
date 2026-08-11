#!/usr/bin/env python3
"""Print parse signatures for all currently unpinned stored texts; write nothing."""
import ast,pathlib,sys
root=pathlib.Path(__file__).resolve().parent.parent
site=root/'site'; texts=root/'registry'/'texts'
sys.path.insert(0,str(site))
import legdiff as L
mod=ast.parse((site/'test_diff.py').read_text()); pinned={}
for node in mod.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CORPUS_PARSE' for t in node.targets):
        pinned=ast.literal_eval(node.value); break
assert pinned
un=[]
for f in sorted(texts.glob('*.txt')):
    if f.name in pinned: continue
    p=L.parse(L.strip_preamble(f.read_text()))
    sig=[len(p.nodes),len(p.nodes)-len({n.path for n in p.nodes}),len(p.warnings)]
    un.append((f.name,sig,p.warnings))
for name,sig,warnings in un:
    print(f'UNPINNED {name}: {sig}')
    for w in warnings: print(f'  WARNING {w}')
if not un: print('No unpinned texts')
raise SystemExit('diagnostic only — inspect signatures before pinning')
