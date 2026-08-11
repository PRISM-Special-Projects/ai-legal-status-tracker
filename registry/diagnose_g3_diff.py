#!/usr/bin/env python3
"""Inspect unpinned SB 1012 parse signatures and duplicate structural paths; write nothing."""
import ast,collections,pathlib,sys
root=pathlib.Path(__file__).resolve().parent.parent
site=root/'site'; texts=root/'registry'/'texts'
sys.path.insert(0,str(site))
import legdiff as L
mod=ast.parse((site/'test_diff.py').read_text()); pinned={}
for node in mod.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CORPUS_PARSE' for t in node.targets):
        pinned=ast.literal_eval(node.value); break
assert pinned
for f in sorted(texts.glob('mo-sb1012-2026--*.txt')):
    p=L.parse(L.strip_preamble(f.read_text()))
    sig=[len(p.nodes),len(p.nodes)-len({n.path for n in p.nodes}),len(p.warnings)]
    print(f'FILE {f.name}: {sig}')
    for w in p.warnings: print(f'  WARNING {w}')
    groups=collections.defaultdict(list)
    for n in p.nodes: groups[n.path].append(n)
    for path,nodes in groups.items():
        if len(nodes)<2: continue
        print('  DUPPATH',repr(path),'COUNT',len(nodes))
        for n in nodes:
            body=' '.join(n.text.split())
            print('    ',repr(body[:180]))
raise SystemExit('diagnostic only — inspect duplicate path causes before pinning')
