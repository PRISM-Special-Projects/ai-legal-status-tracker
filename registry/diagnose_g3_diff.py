#!/usr/bin/env python3
"""Inspect SB 1012 parse signatures and trace 16F subsection recognition; write nothing."""
import collections,pathlib,re,sys
root=pathlib.Path(__file__).resolve().parent.parent
site=root/'site'; texts=root/'registry'/'texts'
sys.path.insert(0,str(site))
import legdiff as L
for f in sorted(texts.glob('mo-sb1012-2026--*.txt')):
    raw=L.strip_preamble(f.read_text()); p=L.parse(raw)
    sig=[len(p.nodes),len(p.nodes)-len({n.path for n in p.nodes}),len(p.warnings)]
    print(f'FILE {f.name}: {sig}')
    for w in p.warnings: print(f'  WARNING {w}')
    groups=collections.defaultdict(list)
    for n in p.nodes: groups[n.path].append(n)
    for path,nodes in groups.items():
        if len(nodes)<2: continue
        print('  DUPPATH',repr(path),'COUNT',len(nodes))
        for n in nodes: print('    ',repr(' '.join(n.text.split())[:180]))
    if '16F' in f.name:
        sec=raw[raw.find('1.2058.'):raw.find('130.165.')]
        print('  16F NUMERIC LINES')
        for line in sec.splitlines():
            if re.match(r'^\d',line): print('   ',repr(line))
        masked=L._mask_citations(L._unify(sec))
        print('  16F ACCEPTED MARKERS')
        for m in L.MARKER_RE.finditer(masked):
            kind=m.lastgroup; s=m.start(kind)
            if L._context_ok(masked,s,kind): print('   ',kind,repr(sec[m.start(kind):m.end(kind)]))
raise SystemExit('diagnostic only — inspect 16F marker recognition before pinning')
