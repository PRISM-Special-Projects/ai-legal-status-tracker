"""Schema, vocabulary and referential checks for bills.json."""
import json, csv, re, sys, collections, os, pathlib, hashlib

ROOT = pathlib.Path(__file__).resolve().parent
os.chdir(ROOT)   # registry paths are relative to this file, not the caller's cwd

STAGE={"introduced","in_committee","passed_one_chamber","enacted","failed","dead"}
TECH={"standalone_provision","amends_general_person_definition","amends_specific_statutes",
      "constitutional_amendment","hybrid"}
# The controlled vocabulary lives in one machine-readable file. It used to be
# duplicated here and in site/build.py, with SCHEMA.md and PROVISIONS.md as prose
# copies — four places for one object, which is how the vocabulary drifted before.
VOCAB=json.load(open(ROOT/"vocabulary.json"))
PROV={p["key"] for p in VOCAB["provisions"]}
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
ids={b["id"] for b in bills if isinstance(b, dict)}

# The summary must survive data the checks above have already objected to: a
# traceback there would hide every finding, which is how a malformed record used
# to escape the report entirely.
def d_(b, field):
    v = b.get(field) if isinstance(b, dict) else None
    return v if isinstance(v, dict) else {}

def vers(b):
    return [v for v in (b.get("versions") if isinstance(b, dict) else []) or []
            if isinstance(v, dict)]

# evidence ref_keys from the literature register
# A bill may cite an evidence record OR a literature record (e.g. a commentary piece).
evkeys=set()
for rel in (("..","literature","csv","Evidence.csv"), ("..","literature","csv","Literature.csv")):
    p=os.path.join(*rel)
    if os.path.exists(p): evkeys |= {r["ref_key"] for r in csv.DictReader(open(p))}

def chk(cond,msg,bucket=err):
    if not cond: bucket.append(msg)

# A malformed record must produce a validation error, not a traceback. Anything
# that gets subscripted or iterated below is fetched through this first, so a
# record with the wrong shape is reported and skipped rather than crashing the run
# and hiding every subsequent finding.
def shape(b, i, field, kind, label):
    v = b.get(field)
    if isinstance(v, kind):
        return v
    err.append(f"{i}: '{field}' should be {label}, got {type(v).__name__}")
    return kind() if kind in (dict, list) else None

TEXTS_ROOT = (ROOT / "texts").resolve()
URL_RE = re.compile(r"https?://[^\s]+$")

def check_url(u, i, what):
    chk(isinstance(u, str) and bool(URL_RE.fullmatch(u.strip())),
        f"{i}: {what} is not an http(s) URL: {u!r}")

# Hashes are only provenance if something compares them to the file.
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

seen=set()
for b in bills:
    if not isinstance(b, dict):
        err.append(f"<record {bills.index(b)}> is {type(b).__name__}, not an object"); continue
    i=b.get("id","<no id>")
    for f in REQUIRED: chk(f in b, f"{i}: missing field '{f}'")
    chk(i not in seen, f"{i}: duplicate id"); seen.add(i)
    chk(re.fullmatch(r"[a-z]{2}-[a-z]+\d+-\d{4}", i or ""), f"{i}: id format")
    chk(b.get("chamber") in CHAMBER, f"{i}: bad chamber {b.get('chamber')}")

    status = shape(b, i, "status", dict, "an object")
    stage = status.get("stage")
    chk(stage in STAGE, f"{i}: bad stage {stage}")
    chk(bool(status.get("source_url")), f"{i}: status has no source_url")
    if status.get("source_url"): check_url(status["source_url"], i, "status.source_url")
    # A terminal stage is a claim like any other and needs a citable action line.
    # This is the check that would have caught the Washington HB 2029 error.
    if stage in ("enacted","failed","dead") and not status.get("evidence"):
        warn.append(f"{i}: terminal stage '{stage}' with no status.evidence action line")

    chk(b.get("family") in FAM, f"{i}: bad family {b.get('family')}")
    chk(b.get("technique") in TECH, f"{i}: bad technique {b.get('technique')}")
    provisions = shape(b, i, "provisions", list, "a list")
    chk(provisions and set(provisions)<=PROV, f"{i}: bad provisions {provisions}")
    chk(b.get("definitional_anchor") in ANCHOR, f"{i}: bad definitional_anchor")
    chk(b.get("augmented_human_exposure") in AUG, f"{i}: bad augmented_human_exposure")
    chk(b.get("affects_algorithmic_entity_formation") in ALGO, f"{i}: bad algo field")
    chk(b.get("corporate_carve_out") in CARVE, f"{i}: bad corporate_carve_out")
    chk(b.get("verification_status") in VERIF, f"{i}: bad verification_status")
    shape(b, i, "jurisdiction", dict, "an object")
    shape(b, i, "session", dict, "an object")
    shape(b, i, "constitutional_exposure", (dict, list), "an object or list")

    # GATE: primary source URL
    sources = shape(b, i, "sources", dict, "an object")
    primary = sources.get("primary") or []
    chk(bool(primary), f"{i}: GATE FAIL - no primary source URL")
    for u in (primary if isinstance(primary, list) else [primary]):
        check_url(u, i, "sources.primary entry")

    # referential
    if b.get("derived_from"):
        chk(b["derived_from"] in ids, f"{i}: derived_from '{b['derived_from']}' not found")
        # every lineage edge must carry a label, or the genealogy graph has blank edges
        chk(bool(b.get("derived_from_changes")), f"{i}: derived_from set but derived_from_changes empty")
    for w in shape(b, i, "watch_dates", list, "a list"):
        if not isinstance(w, dict):
            err.append(f"{i}: watch_date entry is {type(w).__name__}, not an object"); continue
        chk(re.fullmatch(r"\d{4}-\d{2}-\d{2}", w.get("date","")), f"{i}: watch_date bad date {w.get('date')!r}")
        chk(bool(w.get("event")) and w.get("kind") in ("effective","expiry","report","ballot","deadline"), f"{i}: watch_date bad shape")

    for v in shape(b, i, "versions", list, "a list"):
        if not isinstance(v, dict):
            err.append(f"{i}: version entry is {type(v).__name__}, not an object"); continue
        chk(bool(v.get("source_url")), f"{i}: version '{v.get('label')}' has no source_url")
        if v.get("source_url"): check_url(v["source_url"], i, f"version '{v.get('label')}' source_url")
        tp = v.get("text_path")
        if not tp: continue
        # A text_path must resolve to a file inside registry/texts. Anything else -
        # an absolute path, or one escaping upward - would let the differ read a
        # file that is not stored legislative text.
        resolved = (ROOT / tp).resolve()
        if not str(resolved).startswith(str(TEXTS_ROOT) + os.sep):
            err.append(f"{i}: text_path escapes registry/texts: {tp}")
        elif not resolved.is_file():
            err.append(f"{i}: text_path missing on disk: {tp}")
        elif v.get("text_sha256"):
            actual = sha256_of(resolved)
            chk(actual == v["text_sha256"],
                f"{i}: stored text hash does not match file for {tp} "
                f"(recorded {str(v['text_sha256'])[:12]}…, actual {actual[:12]}…)")

    for r in shape(b, i, "evidence_refs", list, "a list"):
        chk(not evkeys or r in evkeys, f"{i}: evidence_ref '{r}' not in Evidence.csv", warn)

    # consistency
    if b.get("verification_status")=="seeded_unverified":
        chk(b.get("last_verified") is None, f"{i}: unverified but has last_verified")
    if stage=="enacted" and not b.get("codified_at"):
        warn.append(f"{i}: enacted but codified_at is null - needs primary-source verification")
    v=shape(b, i, "verification", dict, "an object")
    chk(v.get("operative_text") in ("read_in_full","partial","not_read"), f"{i}: bad verification.operative_text")
    chk(v.get("sponsors") in ("established","not_established"), f"{i}: bad verification.sponsors")
    if v.get("operative_text")!="read_in_full":
        chk(bool(v.get("operative_text_note")), f"{i}: operative_text not full but no note explaining what was checked")
    if str(b.get("verification_status","")).startswith("verified"):
        chk(b.get("last_verified") is not None, f"{i}: verified but no last_verified date")
    if b.get("definitional_anchor")=="taxonomic":
        chk(b.get("augmented_human_exposure")!="unanchored", f"{i}: taxonomic anchor but unanchored exposure")

# The vocabulary must be documented in both directions. Checking only that every
# tag in use is documented misses the reverse failure: a documented tag the code
# does not accept, or a vocabulary entry nobody ever wrote up.
for doc, path in (("SCHEMA.md", ROOT.parent/"SCHEMA.md"),
                  ("PROVISIONS.md", ROOT.parent/"PROVISIONS.md")):
    text = path.read_text() if path.exists() else ""
    for key in sorted(PROV):
        chk(f"`{key}`" in text, f"vocabulary key '{key}' is not documented in {doc}")
for key in sorted(re.findall(r"`([a-z][a-z_]{6,})`", (ROOT.parent/"PROVISIONS.md").read_text()
                             if (ROOT.parent/"PROVISIONS.md").exists() else "")):
    if key.startswith(("denies_","declares_","assigns_","bars_","restricts_","covers_",
                       "study_","imposes_","incident_","addresses_","provides_","defines_",
                       "creates_")):
        chk(key in PROV, f"PROVISIONS.md documents '{key}', which the validator does not accept")

# companion groups
for g,ms in collections.Counter(b.get("companion_group") for b in bills
                                if isinstance(b, dict) and b.get("companion_group")).items():
    chk(ms>=2, f"companion_group '{g}' has only {ms} member")

# Every hash in the source manifest must match the file it describes, or the
# manifest is decoration rather than provenance.
mpath = ROOT / "source_manifest.json"
if mpath.exists():
    man = json.load(open(mpath))
    for group in ("documents", "texts"):
        for rec in man.get(group, []):
            f = (ROOT / rec["path"]).resolve()
            if not f.is_file():
                err.append(f"source_manifest: {group} entry missing on disk: {rec['path']}")
            elif rec.get("sha256") and sha256_of(f) != rec["sha256"]:
                err.append(f"source_manifest: hash mismatch for {rec['path']}")


# ---------------------------------------------------------------- audit summary
def audit(bills, err, warn):
    """Zero validator errors is not the same as a strong evidentiary state.
    This prints what is actually known, so the gap cannot hide behind a green tick."""
    import collections as C
    n=len(bills)
    ot=C.Counter(d_(b,"verification").get("operative_text") for b in bills)
    vs=C.Counter(b.get("verification_status") for b in bills)
    sb=C.Counter(d_(b,"status").get("basis") for b in bills)
    enacted=[b for b in bills if d_(b,"status").get("stage")=="enacted"]
    code=sum(1 for b in enacted if d_(b,"verification").get("codified_at_source")=="code")
    ev=sum(1 for b in bills if d_(b,"status").get("evidence"))
    term=[b for b in bills if d_(b,"status").get("stage") in ("enacted","failed","dead")]
    vt=sum(1 for b in bills for v in vers(b) if v.get("text_path"))
    vp=sum(1 for b in bills for v in vers(b) if v.get("provisions") is not None)
    tv=sum(len(vers(b)) for b in bills)
    print("\n" + "="*66)
    print("AUDIT SUMMARY".center(66))
    print("="*66)
    print(f"  Records                                        {n}")
    print(f"  Status established from a primary/citable record {vs.get('verified_primary',0)}")
    print(f"    of which basis = explicit legislative action   {sb.get('explicit_action',0)}")
    print(f"    basis = session rule (derived, not recorded)   {sb.get('session_rule',0)}")
    print(f"    basis = secondary source                       {sb.get('secondary_source',0)}")
    print(f"  Operative text read in full                    {ot.get('read_in_full',0)} of {n}")
    print(f"    partial                                        {ot.get('partial',0)}")
    print(f"    NOT read                                       {ot.get('not_read',0)}")
    print(f"  Enacted laws                                   {len(enacted)}")
    print(f"    codified_at verified against the CODE           {code}")
    print(f"    codified_at from bill text only                 {len(enacted)-code}")
    print(f"  Status evidence present                        {ev} of {n}  (terminal: {sum(1 for b in term if d_(b,'status').get('evidence'))} of {len(term)})")
    print(f"  Versions                                       {tv}")
    print(f"    with stored text                               {vt}")
    print(f"    with provision tags                            {vp}")
    print("-"*66)
    print(f"  ERRORS   {len(err):>3}   (publication gate — must be zero)")
    print(f"  WARNINGS {len(warn):>3}   (publishable, but each needs a caveat on the record)")
    print("="*66)

print(f"bills: {len(bills)}  states: {len({d_(b,'jurisdiction').get('state') for b in bills})}")
print(f"stages: {dict(collections.Counter(d_(b,'status').get('stage') for b in bills))}")
print(f"families: {dict(collections.Counter(b.get('family') for b in bills))}")
print(f"verified: {dict(collections.Counter(b.get('verification_status') for b in bills))}")
print(f"lineage edges: {sum(1 for b in bills if isinstance(b, dict) and b.get('derived_from'))}")
print(f"\nERRORS ({len(err)}):"); [print('  ✗',e) for e in err] or print('  none')
if warn:
    print(f"\nWARNINGS ({len(warn)}) - publishable with a caveat:"); [print("  !",w) for w in warn]
audit(bills, err, warn)
sys.exit(1 if err else 0)
