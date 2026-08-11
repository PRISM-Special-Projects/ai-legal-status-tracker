#!/usr/bin/env python3
import json
from pathlib import Path

p = Path(__file__).with_name('bills.json')
data = json.loads(p.read_text())
existing = {b['id'] for b in data['bills']}

common = {
    'derived_from': None,
    'definitional_anchor': 'none',
    'augmented_human_exposure': 'unclear',
    'affects_algorithmic_entity_formation': 'not_analysed',
    'corporate_carve_out': 'unknown',
    'constitutional_exposure': [],
    'evidence_refs': [],
    'provenance': 'Added during 2026 corpus-completeness sweep (Workstream H); verified directly against primary legislative/governor sources.',
    'verification_status': 'verified_primary',
    'last_verified': '2026-08-11',
    'watch_dates': [],
    'derived_from_changes': [],
    'provision_changes': [],
}

records = [
{
    **common,
    'id':'az-hb2371-2026','jurisdiction':{'country':'US','level':'state','state':'AZ'},
    'bill_number':'HB 2371','chamber':'house','session':{'legislature':'57th','session':'2nd Reg. Sess.','year_introduced':2026},
    'companion_group':None,'codified_at':None,
    'sponsors':[{'name':'Teresa Martinez','party':None,'role':'sponsor'}],
    'versions':[{'label':'House text reviewed','date':'2026','source_url':'https://www.azleg.gov/legtext/57leg/2r/bills/hb2371h.htm','text_path':None,'provisions':['denies_legal_personhood']}],
    'key_clause':{'text':'The artificial intelligence-assisted arbitration system is not a legal person and does not exercise independent legal authority.','source':'Arizona HB 2371 (2026), AI-assisted arbitration provision'},
    'notes':'Added in Workstream H completeness sweep. Context-specific legal-status rule for AI-assisted divorce arbitration: the computational arbitration system is expressly not a legal person and lacks independent legal authority. Passed the House and advanced in the Senate but did not receive final Senate passage before the 2026 session ended.',
    'status':{'stage':'failed','as_of':'2026-08-11','source_url':'https://www.azleg.gov/legtext/57leg/2R/summary/H.HB2371_021226_CAUCUSCOW.DOCX.htm','evidence':{'action':'Passed House and advanced through Senate committee process; no final Senate passage before session end','date':'2026-06-30'},'basis':'session_rule'},
    'family':'other','technique':'amends_specific_statutes','provisions':['denies_legal_personhood'],
    'sources':{'primary':['https://www.azleg.gov/legtext/57leg/2R/summary/H.HB2371_021226_CAUCUSCOW.DOCX.htm','https://www.azleg.gov/legtext/57leg/2r/bills/hb2371h.htm'],'tracker':[]},
    'effective_date':None,
    'verification':{'status':'verified_primary','operative_text':'read_in_full','operative_text_note':'Official Arizona bill text reviewed for the legal-person/authority clause.','sponsors':'established','codified_at_source':'n/a','versions_with_text':0,'last_verified':'2026-08-11'}
},
{
    **common,
    'id':'az-hb2311-2026','jurisdiction':{'country':'US','level':'state','state':'AZ'},
    'bill_number':'HB 2311','chamber':'house','session':{'legislature':'57th','session':'2nd Reg. Sess.','year_introduced':2026},
    'companion_group':None,'codified_at':None,
    'sponsors':[{'name':'Tony Rivero','party':None,'role':'sponsor'}],
    'versions':[{'label':'House engrossed','date':'2026-03-02','source_url':'https://www.azleg.gov/legtext/57leg/2r/bills/hb2311h.htm','text_path':None,'provisions':['restricts_chatbot_claims','imposes_safety_duties']}],
    'key_clause':{'text':'Reasonable measures must prevent explicit claims that the conversational AI service is sentient or human.','source':'Arizona HB 2311 (2026), House engrossed text'},
    'notes':'Added in Workstream H completeness sweep. Conversational-AI safeguards for minors expressly target claims that the service is sentient or human. Passed both chambers; vetoed by Governor Katie Hobbs on 19 June 2026.',
    'status':{'stage':'failed','as_of':'2026-08-11','source_url':'https://azgovernor.gov/office-arizona-governor/news/2026/06/governor-katie-hobbs-legislative-action-update-0','evidence':{'action':'Vetoed by Governor','date':'2026-06-19'},'basis':'explicit_action'},
    'family':'other','technique':'hybrid','provisions':['restricts_chatbot_claims','imposes_safety_duties'],
    'sources':{'primary':['https://www.azleg.gov/legtext/57leg/2r/bills/hb2311h.htm','https://azgovernor.gov/office-arizona-governor/news/2026/06/governor-katie-hobbs-legislative-action-update-0'],'tracker':[]},
    'effective_date':None,
    'verification':{'status':'verified_primary','operative_text':'read_in_full','operative_text_note':'Official House engrossed text reviewed; veto confirmed from Governor action release.','sponsors':'established','codified_at_source':'n/a','versions_with_text':0,'last_verified':'2026-08-11'}
},
{
    **common,
    'id':'hi-sb3001-2026','jurisdiction':{'country':'US','level':'state','state':'HI'},
    'bill_number':'SB 3001','chamber':'senate','session':{'legislature':'33rd','session':'2026 Reg. Sess.','year_introduced':2026},
    'companion_group':None,'codified_at':'2026 Haw. Sess. Laws Act 248; adds a new section to HRS ch. 481B, pt. I',
    'sponsors':[{'name':'Jarrett Keohokalole','party':None,'role':'sponsor'}],
    'versions':[{'label':'Conference draft CD1 / enacted text','date':'2026','source_url':'https://data.capitol.hawaii.gov/sessions/session2026/bills/SB3001_CD1_.HTM','text_path':None,'provisions':['restricts_chatbot_claims','imposes_safety_duties']}],
    'key_clause':{'text':'An operator shall institute reasonable measures to prevent an AI companion from making a representation or statement that would lead a reasonable person to believe that the person is interacting with a human where the user is seeking or receiving crisis intervention services.','source':'Hawaii SB 3001 CD1 (2026)'},
    'notes':'Added in Workstream H completeness sweep. Enacted AI-companion safety law. Final conference text restricts representations that could lead a user in crisis services to believe the companion is human; an earlier House text expressly covered human or sentient-being representations. Act 248 approved 14 July 2026.',
    'status':{'stage':'enacted','as_of':'2026-08-11','source_url':'https://data.capitol.hawaii.gov/advreports/advreport.aspx?measuretype=HB%2CSB&report=deadline&rpt_type=gov_acts&title=Acts&year=2026','evidence':{'action':'Act 248, approved','date':'2026-07-14'},'basis':'explicit_action'},
    'family':'other','technique':'hybrid','provisions':['restricts_chatbot_claims','imposes_safety_duties'],
    'sources':{'primary':['https://data.capitol.hawaii.gov/sessions/session2026/bills/SB3001_CD1_.HTM','https://data.capitol.hawaii.gov/advreports/advreport.aspx?measuretype=HB%2CSB&report=deadline&rpt_type=gov_acts&title=Acts&year=2026'],'tracker':[]},
    'effective_date':'2026-07-14',
    'verification':{'status':'verified_primary','operative_text':'read_in_full','operative_text_note':'Final conference text and official act status reviewed.','sponsors':'established','codified_at_source':'bill','versions_with_text':0,'last_verified':'2026-08-11'}
},
{
    **common,
    'id':'ia-sf2417-2026','jurisdiction':{'country':'US','level':'state','state':'IA'},
    'bill_number':'SF 2417','chamber':'senate','session':{'legislature':'91st','session':'2026','year_introduced':2026},
    'companion_group':None,'codified_at':'2026 Iowa Acts ch. 1068',
    'sponsors':[{'name':'Senate Committee on Technology','party':None,'role':'sponsor of record (committee bill)'}],
    'versions':[{'label':'enacted / Acts ch. 1068','date':'2026-05-02','source_url':'https://www.legis.iowa.gov/docs/publications/iactc/91.2/CH1068.pdf','text_path':None,'provisions':['restricts_chatbot_claims','imposes_safety_duties']}],
    'key_clause':{'text':'The required safeguards include preventing statements that would lead a reasonable person to believe the conversational AI service is sentient or human.','source':'2026 Iowa Acts ch. 1068 (SF 2417)'},
    'notes':'Added in Workstream H completeness sweep. Enacted conversational-AI legislation expressly reaches statements that would lead a reasonable person to believe the service is sentient or human. Signed 2 May 2026; effective 1 July 2026; applicability begins 1 July 2027.',
    'status':{'stage':'enacted','as_of':'2026-08-11','source_url':'https://www.legis.iowa.gov/legislation/billTracking/billHistory?billName=SF2417&ga=91','evidence':{'action':'Signed by Governor','date':'2026-05-02'},'basis':'explicit_action'},
    'family':'other','technique':'hybrid','provisions':['restricts_chatbot_claims','imposes_safety_duties'],
    'sources':{'primary':['https://www.legis.iowa.gov/legislation/billTracking/billHistory?billName=SF2417&ga=91','https://www.legis.iowa.gov/docs/publications/iactc/91.2/CH1068.pdf'],'tracker':[]},
    'effective_date':'2026-07-01',
    'watch_dates':[{'date':'2027-07-01','event':'Act applicability begins','kind':'effective'}],
    'verification':{'status':'verified_primary','operative_text':'read_in_full','operative_text_note':'Enacted Act 1068 reviewed for the sentient/human representation rule.','sponsors':'established','codified_at_source':'bill','versions_with_text':0,'last_verified':'2026-08-11'}
},
{
    **common,
    'id':'va-hb635-2026','jurisdiction':{'country':'US','level':'state','state':'VA'},
    'bill_number':'HB 635','chamber':'house','session':{'legislature':None,'session':'2026 Regular Session; continued to 2027','year_introduced':2026},
    'companion_group':'va-chatbot-safety-2026','codified_at':None,
    'sponsors':[{'name':'Michelle Lopes Maldonado','party':None,'role':'chief patron'}],
    'versions':[{'label':'House committee substitute','date':'2026-02-04','source_url':'https://lis.virginia.gov/bill-details/20271/HB635/text/HB635HC1','text_path':None,'provisions':['restricts_chatbot_claims','imposes_safety_duties']}],
    'key_clause':{'text':'An operator shall include a static, persistent disclaimer that a companion chatbot is not a human.','source':'Virginia HB 635 committee substitute'},
    'notes':'Added in Workstream H completeness sweep. Companion-chatbot bill with explicit not-human disclosure and human/sentient framing. Continued into the 2027 session in House Communications, Technology and Innovation; therefore still live.',
    'status':{'stage':'in_committee','as_of':'2026-08-11','source_url':'https://lis.virginia.gov/bill-details/20271/HB635','evidence':{'action':'Continued from last session / continued to 2027 in House Communications, Technology and Innovation','date':'2026-07-21'},'basis':'explicit_action'},
    'family':'other','technique':'hybrid','provisions':['restricts_chatbot_claims','imposes_safety_duties'],
    'sources':{'primary':['https://lis.virginia.gov/bill-details/20271/HB635','https://lis.virginia.gov/bill-details/20271/HB635/text/HB635HC1'],'tracker':[]},
    'effective_date':None,
    'verification':{'status':'verified_primary','operative_text':'read_in_full','operative_text_note':'Current House committee substitute reviewed.','sponsors':'established','codified_at_source':'n/a','versions_with_text':0,'last_verified':'2026-08-11'}
},
{
    **common,
    'id':'va-sb796-2026','jurisdiction':{'country':'US','level':'state','state':'VA'},
    'bill_number':'SB 796','chamber':'senate','session':{'legislature':None,'session':'2026 Regular Session; continued to 2027','year_introduced':2026},
    'companion_group':'va-chatbot-safety-2026','codified_at':None,
    'sponsors':[{'name':'Tara A. Durant','party':None,'role':'chief patron'}],
    'versions':[{'label':'House committee substitute','date':'2026-03-02','source_url':'https://lis.virginia.gov/bill-details/20271/SB796/text/SB796HC1','text_path':None,'provisions':['restricts_chatbot_claims','imposes_safety_duties','incident_reporting_duty']}],
    'key_clause':{'text':'A covered entity shall ensure that a chatbot does not make a materially false representation that it is a human being.','source':'Virginia SB 796 House committee substitute'},
    'notes':'Added in Workstream H completeness sweep. Senate-passed chatbot bill; House substitute expressly bars materially false representations that a chatbot is a human being and requires persistent not-human disclosures. Continued into the 2027 session in House Communications, Technology and Innovation.',
    'status':{'stage':'passed_one_chamber','as_of':'2026-08-11','source_url':'https://lis.virginia.gov/bill-details/20271/SB796','evidence':{'action':'Passed Senate; continued from last session in House committee for 2027','date':'2026-07-21'},'basis':'explicit_action'},
    'family':'other','technique':'hybrid','provisions':['restricts_chatbot_claims','imposes_safety_duties','incident_reporting_duty'],
    'sources':{'primary':['https://lis.virginia.gov/bill-details/20271/SB796','https://lis.virginia.gov/bill-details/20271/SB796/text/SB796HC1'],'tracker':[]},
    'effective_date':None,
    'verification':{'status':'verified_primary','operative_text':'read_in_full','operative_text_note':'Current House committee substitute reviewed; Senate passage and carryover status checked in LIS.','sponsors':'established','codified_at_source':'n/a','versions_with_text':0,'last_verified':'2026-08-11'}
},
]

added=[]
for rec in records:
    if rec['id'] not in existing:
        data['bills'].append(rec); added.append(rec['id'])

p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
print('Added', len(added), 'H7 omissions:', ', '.join(added) if added else 'none')
