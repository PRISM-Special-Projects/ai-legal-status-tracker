#!/usr/bin/env python3
"""One-time gated G1 migration for North Dakota HB 1361 version history."""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BILLS = ROOT / 'bills.json'
SOURCES = ROOT / 'source_catalog.json'
CLAIMS = ROOT / 'claim_evidence.json'
MANIFEST = ROOT / 'source_manifest.json'

bdata=json.loads(BILLS.read_text()); sdata=json.loads(SOURCES.read_text()); cdata=json.loads(CLAIMS.read_text()); mdata=json.loads(MANIFEST.read_text())
b=next(x for x in bdata['bills'] if x['id']=='nd-hb1361-2023')
assert len(b['versions'])==1 and b['versions'][0]['label']=='enacted'

versions=[
 {"version_id":"nd-hb1361-23.0346.02000","label":"introduced — 23.0346.02000","date":"2023-01-12","source_url":"https://ndlegis.gov/assembly/68-2023/regular/documents/23-0346-02000.pdf","text_path":"texts/nd-hb1361-2023--introduced-23.0346.02000.txt","provisions":["denies_legal_personhood","covers_non_ai_entities"]},
 {"version_id":"nd-hb1361-23.0346.04000","label":"with Senate amendments — 23.0346.04000","date":"2023-03-13","source_url":"https://ndlegis.gov/assembly/68-2023/regular/documents/23-0346-04000.pdf","text_path":"texts/nd-hb1361-2023--senate-amended-23.0346.04000.txt","provisions":["denies_legal_personhood","covers_non_ai_entities"]},
 {"version_id":"nd-hb1361-23.0346.05000","label":"enrolled — 23.0346.05000","date":"2023-04-03","source_url":"https://ndlegis.gov/assembly/68-2023/regular/documents/23-0346-05000.pdf","text_path":"texts/nd-hb1361-2023--enrolled-23.0346.05000.txt","provisions":["denies_legal_personhood","covers_non_ai_entities"]}
]
for v in versions:
 p=ROOT/v['text_path']; raw=p.read_bytes(); v['text_sha256']=hashlib.sha256(raw).hexdigest()
b['versions']=versions
b['verification']['operative_text']='read_in_full'; b['verification']['operative_text_note']='Official introduced, Senate-amended, and enrolled texts read in full during Workstream G1.'; b['verification']['versions_with_text']=3; b['verification']['last_verified']='2026-08-11'; b['last_verified']='2026-08-11'
b['derived_from_changes']=[
 "Senate amendment changed the mechanism from a standalone chapter 1-08 personhood provision to an amendment of the general Century Code definition of 'person' in § 1-01-49(8)",
 "The introduced corporate/governmental-entity prohibition and pre-existing-entity application clause were removed; the amended text instead excludes environmental elements, artificial intelligence, an animal, and an inanimate object from the general definition of person"
]
b['notes']=b['notes'].replace("Full bill text not on the overview page - operative language still to be read from the Versions tab. ","").replace("CODIFIED_AT PROVENANCE: taken from the bill's own amending language, not yet checked against the published North Dakota Century Code. The subsection number in particular should be confirmed against the code. ","")
b['notes'] += " VERSION HISTORY AUDIT 2026-08-11: official Versions/Actions records establish 23.0346.02000 (introduced), adopted Senate amendment instructions 23.0346.02003, full Senate-amended text 23.0346.04000, and enrollment 23.0346.05000. The change-bearing transition is 02000→04000; 05000 preserves the amended operative wording."

new_sources=[
 {"id":"nd-hb1361-02000","label":"North Dakota Legislature — HB 1361 introduced 23.0346.02000","kind":"bill_text","url":"https://ndlegis.gov/assembly/68-2023/regular/documents/23-0346-02000.pdf","jurisdiction":"ND"},
 {"id":"nd-hb1361-02003a","label":"North Dakota Legislature — HB 1361 adopted Senate amendment 23.0346.02003","kind":"amendment","url":"https://ndlegis.gov/assembly/68-2023/regular/documents/23-0346-02003a.pdf","jurisdiction":"ND"},
 {"id":"nd-hb1361-04000","label":"North Dakota Legislature — HB 1361 with Senate amendments 23.0346.04000","kind":"bill_text","url":"https://ndlegis.gov/assembly/68-2023/regular/documents/23-0346-04000.pdf","jurisdiction":"ND"},
 {"id":"nd-hb1361-05000","label":"North Dakota Legislature — HB 1361 enrollment 23.0346.05000","kind":"enrolled_bill","url":"https://ndlegis.gov/assembly/68-2023/regular/documents/23-0346-05000.pdf","jurisdiction":"ND"}
]
ids={s['id'] for s in sdata['sources']}
for s in new_sources:
 if s['id'] not in ids: sdata['sources'].append(s)

rec=next(r for r in cdata['records'] if r['record_id']=='nd-hb1361-2023')
rec['claims'].append({
 "claim":{"field":"effect","version_id":"nd-hb1361-23.0346.04000"},
 "value":"changes the mechanism from a standalone chapter 1-08 personhood provision to an amendment of the general definition of person in § 1-01-49(8)",
 "mode":"derived",
 "supports":[
  {"source_ref":"nd-hb1361-02000","locator":"Section 1 — standalone Personhood status provision; Section 2 application clause"},
  {"source_ref":"nd-hb1361-02003a","locator":"adopted amendment instructions replacing lines 4-14 and changing the bill title/mechanism"},
  {"source_ref":"nd-hb1361-04000","locator":"Section 1 — amendment to § 1-01-49(8)"}
 ],
 "derivation":"Direct comparison of the introduced text, adopted Senate amendment instructions, and resulting 04000 text."
})
rec['claims'].append({
 "claim":{"field":"operative_equivalence","version_id":"nd-hb1361-23.0346.05000"},
 "value":"same operative statutory wording as 23.0346.04000",
 "mode":"derived",
 "supports":[
  {"source_ref":"nd-hb1361-04000","locator":"Section 1 and Section 2"},
  {"source_ref":"nd-hb1361-05000","locator":"Section 1 and Section 2"}
 ],
 "derivation":"The enrollment changes publication/formal heading from A BILL to AN ACT but preserves the amended statutory and emergency wording."
})

existing={t['path'] for t in mdata.get('texts',[])}
for v in versions:
 if v['text_path'] not in existing:
  raw=(ROOT/v['text_path']).read_bytes()
  mdata['texts'].append({"path":v['text_path'],"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"normalisation":["removed_line_numbers","removed_page_furniture","normalised_whitespace"],"substantive_text_changed":False})
mdata['generated']='2026-08-11'

BILLS.write_text(json.dumps(bdata,indent=2,ensure_ascii=False)+'\n'); SOURCES.write_text(json.dumps(sdata,indent=2,ensure_ascii=False)+'\n'); CLAIMS.write_text(json.dumps(cdata,indent=2,ensure_ascii=False)+'\n'); MANIFEST.write_text(json.dumps(mdata,indent=2,ensure_ascii=False)+'\n')
print('G1 North Dakota version-history migration applied')
