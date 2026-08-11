#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent; p=R/'source_manifest.json'; m=json.loads(p.read_text()); m['generated']='2026-08-11'
def sh(x):return hashlib.sha256(x.read_bytes()).hexdigest()
d={x['path'] for x in m['documents']}; t={x['path'] for x in m['texts']}
for f in sorted((R/'incoming').glob('mo-sb1012-2026--*.pdf')):
 q='incoming/'+f.name
 if q not in d:m['documents'].append({'path':q,'sha256':sh(f),'bytes':f.stat().st_size})
for f in sorted((R/'texts').glob('mo-sb1012-2026--*.txt')):
 q='texts/'+f.name
 if q not in t:m['texts'].append({'path':q,'sha256':sh(f),'bytes':f.stat().st_size,'normalisation':['removed_line_numbers','removed_page_furniture','normalised_whitespace'],'substantive_text_changed':False})
p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');print('G3 source manifest applied')
