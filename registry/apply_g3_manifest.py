#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent; p=R/'source_manifest.json'; m=json.loads(p.read_text()); m['generated']='2026-08-11'
def sh(x):return hashlib.sha256(x.read_bytes()).hexdigest()

def upsert(rows,path,file,extra=None):
    item=next((x for x in rows if x['path']==path),None)
    vals={'path':path,'sha256':sh(file),'bytes':file.stat().st_size}
    if extra: vals.update(extra)
    if item is None: rows.append(vals)
    else: item.update(vals)

for f in sorted((R/'incoming').glob('mo-sb1012-2026--*.pdf')):
    upsert(m['documents'],'incoming/'+f.name,f)
for f in sorted((R/'texts').glob('mo-sb1012-2026--*.txt')):
    upsert(m['texts'],'texts/'+f.name,f,{
        'normalisation':['removed_line_numbers','removed_page_furniture','preserved_subsection_structure','normalised_whitespace'],
        'substantive_text_changed':False})
p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');print('G3 source manifest refreshed')
