#!/usr/bin/env python3
"""One-time gated G2 migration for Missouri HB 1746 version history."""
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BILLS=ROOT/'bills.json'; SOURCES=ROOT/'source_catalog.json'; CLAIMS=ROOT/'claim_evidence.json'; MANIFEST=ROOT/'source_manifest.json'
bdata=json.loads(BILLS.read_text()); sdata=json.loads(SOURCES.read_text()); cdata=json.loads(CLAIMS.read_text()); mdata=json.loads(MANIFEST.read_text())
b=next(x for x in bdata['bills'] if x['id']=='mo-hb1746-2026')
assert len(b['versions'])==2
assert b['versions'][0]['text_path'] is None
assert b['versions'][1]['text_path']=='texts/mo-hb1746-2026--hcs.txt'

intro_path='texts/mo-hb1746-2026--introduced-3891H.01I.txt'
hcs_path='texts/mo-hb1746-2026--hcs.txt'
def sha(path): return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
intro_provisions=['denies_legal_personhood','declares_non_sentient','assigns_liability_to_humans','bars_marriage_or_union','bars_property_ownership','bars_corporate_office','bars_ai_liability','imposes_safety_duties','incident_reporting_duty','addresses_corporate_veil']
hcs_provisions=['denies_legal_personhood','declares_non_sentient','assigns_liability_to_humans','bars_marriage_or_union','bars_property_ownership','bars_corporate_office','bars_ai_liability','imposes_safety_duties','incident_reporting_duty','provides_compliance_safe_harbor']
intro_label='introduced — 3891H.01I'
hcs_label='House Committee Substitute — HCS HBs 1746 & 1769, 3891H.04C'
b['versions']=[
 {'version_id':'mo-hb1746-3891H.01I','label':intro_label,'date':'2025-12-01','source_url':'https://documents.house.mo.gov/billtracking/bills261/hlrbillspdf/3891H.01I.pdf','text_path':intro_path,'provisions':intro_provisions,'text_sha256':sha(intro_path)},
 {'version_id':'mo-hb1746-3891H.04C','label':hcs_label,'date':'2026-02-25','source_url':'https://documents.house.mo.gov/billtracking/bills261/hlrbillspdf/3891H.04C.pdf','text_path':hcs_path,'provisions':hcs_provisions,'text_sha256':sha(hcs_path)}
]
b['sponsors']=[{'name':'Scott Miller','party':None,'role':'sponsor (District 069)'}]
b['status']={'stage':'in_committee','as_of':'2026-08-11','source_url':'https://house.mo.gov/BillActions.aspx?bill=HB1746&code=&year=2026','evidence':{'action':'03/30/2026 - Reported Do Pass (H) - AYES: 9 NOES: 0 PRESENT: 0','date':'2026-03-30'},'basis':'explicit_action'}
b['verification']['operative_text']='read_in_full'; b['verification']['operative_text_note']='Official introduced 3891H.01I and committee substitute 3891H.04C read in full during Workstream G2.'; b['verification']['sponsors']='established'; b['verification']['versions_with_text']=2; b['verification']['last_verified']='2026-08-11'; b['last_verified']='2026-08-11'
b['provision_changes']=[{'from':intro_label,'to':hcs_label,'removed':['addresses_corporate_veil'],'added':['provides_compliance_safe_harbor'],'retained':['assigns_liability_to_humans','bars_ai_liability','bars_corporate_office','bars_marriage_or_union','bars_property_ownership','declares_non_sentient','denies_legal_personhood','imposes_safety_duties','incident_reporting_duty']}]
b['notes']=b['notes'].replace('SOURCE NOTE: the house.mo.gov URL cited in the paper 404s; text supplied from the LegiScan record. ','').replace('ACTION HISTORY VERIFIED 2026-08-10 (and the house.mo.gov URL works; my earlier 404 was a blocked fetch, not a dead link).','ACTION HISTORY RECHECKED 2026-08-11 against the official Missouri House record.')
b['notes'] += ' VERSION HISTORY AUDIT 2026-08-11: official Bill Text lists 3891H.01I (Introduced) and 3891H.04C (Committee). Direct comparison confirms the introduced bill carried the corporate-veil provision at § 1.2045(13); the HCS removes it and adds the NIST-based compliance safe harbour. Both official texts are now stored and read in full. STATUS RECHECK: the official action history continues beyond the previously recorded 11 March referral through 30 March 2026, when Rules - Administrative reported the HCS do pass 9-0.'

new_sources=[
 {'id':'mo-hb1746-intro','label':'Missouri House — HB 1746 introduced 3891H.01I','kind':'bill_text','url':'https://documents.house.mo.gov/billtracking/bills261/hlrbillspdf/3891H.01I.pdf','jurisdiction':'MO'},
 {'id':'mo-hb1746-actions','label':'Missouri House — HB 1746 official actions','kind':'action_history','url':'https://house.mo.gov/BillActions.aspx?bill=HB1746&code=&year=2026','jurisdiction':'MO','note':'Official action history through 30 March 2026.'}
]
ids={s['id'] for s in sdata['sources']}
for s in new_sources:
 if s['id'] not in ids: sdata['sources'].append(s)

records={r['record_id']:r for r in cdata['records']}
rec=records.get('mo-hb1746-2026')
if rec is None:
 rec={'record_id':'mo-hb1746-2026','claims':[]}; cdata['records'].append(rec)
assert not rec['claims']
rec['claims']=[
 {'claim':{'field':'provisions','version_id':'mo-hb1746-3891H.01I','item':'addresses_corporate_veil'},'value':True,'assessment':'present','mode':'direct','supports':[{'source_ref':'mo-hb1746-intro','locator':'proposed § 1.2045(13)'},{'source_ref':'provision-tests','locator':'addresses_corporate_veil operational test'}]},
 {'claim':{'field':'provisions','version_id':'mo-hb1746-3891H.04C','item':'addresses_corporate_veil'},'value':False,'assessment':'checked_absent','mode':'direct','supports':[{'source_ref':'mo-hcs-3891H04C','locator':'full proposed § 1.2045; no corporate-veil subsection'},{'source_ref':'provision-tests','locator':'addresses_corporate_veil operational test'}]},
 {'claim':{'field':'provisions','version_id':'mo-hb1746-3891H.01I','item':'provides_compliance_safe_harbor'},'value':False,'assessment':'checked_absent','mode':'direct','supports':[{'source_ref':'mo-hb1746-intro','locator':'full proposed § 1.2045; no NIST safe-harbour language'},{'source_ref':'provision-tests','locator':'provides_compliance_safe_harbor operational test'}]},
 {'claim':{'field':'provisions','version_id':'mo-hb1746-3891H.04C','item':'provides_compliance_safe_harbor'},'value':True,'assessment':'present','mode':'direct','supports':[{'source_ref':'mo-hcs-3891H04C','locator':'proposed § 1.2045(9), NIST AI RMF oversight standard'},{'source_ref':'provision-tests','locator':'provides_compliance_safe_harbor operational test'}]},
 {'claim':{'field':'provision_change','from_version_id':'mo-hb1746-3891H.01I','to_version_id':'mo-hb1746-3891H.04C','item':'addresses_corporate_veil'},'value':'removed','mode':'derived','supports':[{'source_ref':'mo-hb1746-intro','locator':'§ 1.2045(13)'},{'source_ref':'mo-hcs-3891H04C','locator':'full proposed § 1.2045'},{'source_ref':'provision-tests','locator':'addresses_corporate_veil operational test'}],'derivation':'The operational-test clause is present in 3891H.01I and checked absent in 3891H.04C.'},
 {'claim':{'field':'provision_change','from_version_id':'mo-hb1746-3891H.01I','to_version_id':'mo-hb1746-3891H.04C','item':'provides_compliance_safe_harbor'},'value':'added','mode':'derived','supports':[{'source_ref':'mo-hb1746-intro','locator':'full proposed § 1.2045'},{'source_ref':'mo-hcs-3891H04C','locator':'§ 1.2045(9)'},{'source_ref':'provision-tests','locator':'provides_compliance_safe_harbor operational test'}],'derivation':'The operational-test clause is checked absent in 3891H.01I and present in 3891H.04C.'},
 {'claim':{'field':'status.stage'},'value':'in_committee','mode':'direct','supports':[{'source_ref':'mo-hb1746-actions','locator':'2026-03-30 — Reported Do Pass (H), AYES 9 NOES 0'}]}
]

existing={t['path'] for t in mdata.get('texts',[])}
if intro_path not in existing:
 raw=(ROOT/intro_path).read_bytes(); mdata['texts'].append({'path':intro_path,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'normalisation':['removed_line_numbers','removed_page_furniture','normalised_whitespace'],'substantive_text_changed':False})
mdata['generated']='2026-08-11'

BILLS.write_text(json.dumps(bdata,indent=2,ensure_ascii=False)+'\n'); SOURCES.write_text(json.dumps(sdata,indent=2,ensure_ascii=False)+'\n'); CLAIMS.write_text(json.dumps(cdata,indent=2,ensure_ascii=False)+'\n'); MANIFEST.write_text(json.dumps(mdata,indent=2,ensure_ascii=False)+'\n')
print('G2 Missouri HB 1746 version-history migration applied')
