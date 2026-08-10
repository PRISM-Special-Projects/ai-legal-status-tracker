"""Schema, vocabulary and referential checks for bills.json."""
import json, csv, re, sys, collections, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
os.chdir(ROOT)   # registry paths are relative to this file, not the caller's cwd

STAGE={"introduced","in_committee","passed_one_chamber","enacted","failed","dead"}
TECH={"standalone_provision","amends_general_person_definition","amends_specific_statutes",
      "constitutional_amendment","hybrid"}
PROV={"denies_legal_personhood","declares_non_sentient","assigns_liability_to_humans",
      "restricts_ai_speech_rights","restricts_chatbot_claims","restricts_person_like_training",
      "covers_non_ai_entities","study_only",
      # added 2026-08-10 from the Ohio HB 469 text - the Family C bills do considerably
      # more than deny personhood and declare non-sentience
      "bars_marriage_or_union","bars_property_ownership","bars_corporate_office",
      "imposes_safety_duties","incident_reporting_duty","addresses_corporate_veil",
      # WI AB 959 negates AI liability without assigning it to anyone - distinct from
      # OH s 1357.06, which affirmatively assigns it. Keep the two separable.
      "bars_ai_liability","provides_compliance_safe_harbor"}
FAM={"A","B","C","other"}
ANCHOR={"taxonomic","enumerated_only","none","unknown"}
AUG={"anchored","unanchored","unclear"}
ALGO={"bars","does_not_bar","untested","not_analysed"}
CARVE={"express_saving_clause","prospective_only","none","unknown"}
VERIF={"verified_primary","verified_secondary","seeded_unverified"}
CHAMBER={"house","senate","joint"}
REQUIRED=["id","jurisdiction","bill_number","chamber","session","status","family","technique",
          "provisions","definitional_anchor","augmented_human_exposure",
          "affects_algorithmic_entity_formation","corporate_carve_out","constitutional_exposure",
          "sponsors","versions","evidence_refs","sources","provenance","verification_status",
          "last_verified","notes","companion_group","codified_at","derived_from","key_clause","effective_date",
          "derived_from_changes","watch_dates","verification"]

d=json.load(open("bills.json")); bills=d["bills"]; err=[]; warn=[]
ids={b["id"] for b in bills}

# evidence ref_keys from the literature register
# A bill may cite an evidence record OR a literature record (e.g. a commentary piece).
evkeys=set()
for rel in (("..","literature","csv","Evidence.csv"), ("..","literature","csv","Literature.csv")):
    p=os.path.join(*rel)
    if os.path.exists(p): evkeys |= {r["ref_key"] for r in csv.DictReader(open(p))}

def chk(cond,msg,bucket=err):
    if not cond: bucket.append(msg)

seen=set()
for b in bills:
    i=b.get("id","<no id>")
    for f in REQUIRED: chk(f in b, f"{i}: missing field '{f}'")
    chk(i not in seen, f"{i}: duplicate id"); seen.add(i)
    chk(re.fullmatch(r"[a-z]{2}-[a-z]+\d+-\d{4}", i or ""), f"{i}: id format")
    chk(b["chamber"] in CHAMBER, f"{i}: bad chamber {b['chamber']}")
    chk(b["status"]["stage"] in STAGE, f"{i}: bad stage {b['status']['stage']}")
    chk(bool(b["status"].get("source_url")), f"{i}: status has no source_url")
    # A terminal stage is a claim like any other and needs a citable action line.
    # This is the check that would have caught the Washington HB 2029 error.
    if b["status"]["stage"] in ("enacted","failed","dead") and not b["status"].get("evidence"):
        warn.append(f"{i}: terminal stage '{b['status']['stage']}' with no status.evidence action line")
    chk(b["family"] in FAM, f"{i}: bad family {b['family']}")
    chk(b["technique"] in TECH, f"{i}: bad technique {b['technique']}")
    chk(b["provisions"] and set(b["provisions"])<=PROV, f"{i}: bad provisions {b['provisions']}")
    chk(b["definitional_anchor"] in ANCHOR, f"{i}: bad definitional_anchor")
    chk(b["augmented_human_exposure"] in AUG, f"{i}: bad augmented_human_exposure")
    chk(b["affects_algorithmic_entity_formation"] in ALGO, f"{i}: bad algo field")
    chk(b["corporate_carve_out"] in CARVE, f"{i}: bad corporate_carve_out")
    chk(b["verification_status"] in VERIF, f"{i}: bad verification_status")
    # GATE: primary source URL
    chk(bool(b["sources"].get("primary")), f"{i}: GATE FAIL - no primary source URL")
    # referential
    if b["derived_from"]:
        chk(b["derived_from"] in ids, f"{i}: derived_from '{b['derived_from']}' not found")
        # every lineage edge must carry a label, or the genealogy graph has blank edges
        chk(bool(b["derived_from_changes"]), f"{i}: derived_from set but derived_from_changes empty")
    for w in b["watch_dates"]:
        chk(re.fullmatch(r"\d{4}-\d{2}-\d{2}", w.get("date","")), f"{i}: watch_date bad date {w.get('date')!r}")
        chk(bool(w.get("event")) and w.get("kind") in ("effective","expiry","report","ballot","deadline"), f"{i}: watch_date bad shape")
    for v in b["versions"]:
        if v.get("text_path"): chk(os.path.exists(v["text_path"]), f"{i}: text_path missing on disk: {v['text_path']}")
    for r in b["evidence_refs"]:
        chk(not evkeys or r in evkeys, f"{i}: evidence_ref '{r}' not in Evidence.csv", warn)
    for v in b["versions"]: chk(bool(v.get("source_url")), f"{i}: version '{v.get('label')}' has no source_url")
    # consistency
    if b["verification_status"]=="seeded_unverified":
        chk(b["last_verified"] is None, f"{i}: unverified but has last_verified")
    if b["status"]["stage"]=="enacted" and not b["codified_at"]:
        warn.append(f"{i}: enacted but codified_at is null - needs primary-source verification")
    v=b.get("verification") or {}
    chk(v.get("operative_text") in ("read_in_full","partial","not_read"), f"{i}: bad verification.operative_text")
    chk(v.get("sponsors") in ("established","not_established"), f"{i}: bad verification.sponsors")
    if v.get("operative_text")!="read_in_full":
        chk(bool(v.get("operative_text_note")), f"{i}: operative_text not full but no note explaining what was checked")
    if b["verification_status"].startswith("verified"):
        chk(b["last_verified"] is not None, f"{i}: verified but no last_verified date")
    if b["definitional_anchor"]=="taxonomic":
        chk(b["augmented_human_exposure"]!="unanchored", f"{i}: taxonomic anchor but unanchored exposure")

# companion groups
for g,ms in collections.Counter(b["companion_group"] for b in bills if b["companion_group"]).items():
    chk(ms>=2, f"companion_group '{g}' has only {ms} member")

print(f"bills: {len(bills)}  states: {len({b['jurisdiction']['state'] for b in bills})}")
print(f"stages: {dict(collections.Counter(b['status']['stage'] for b in bills))}")
print(f"families: {dict(collections.Counter(b['family'] for b in bills))}")
print(f"verified: {dict(collections.Counter(b['verification_status'] for b in bills))}")
print(f"lineage edges: {sum(1 for b in bills if b['derived_from'])}")
print(f"\nERRORS ({len(err)}):"); [print('  ✗',e) for e in err] or print('  none')
print(f"WARNINGS ({len(warn)}):"); [print('  !',w) for w in warn] or print('  none')
sys.exit(1 if err else 0)
