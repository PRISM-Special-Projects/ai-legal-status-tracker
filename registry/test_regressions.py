#!/usr/bin/env python3
"""One test per bug actually found. Every failure here has happened before.

Run: python3 registry/test_regressions.py
"""
import json, os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
os.chdir(ROOT)
REG = json.load(open("bills.json"))
BILLS = {b["id"]: b for b in REG["bills"]}
SCHEMA = (ROOT.parent / "SCHEMA.md").read_text()
fails = []

def check(cond, msg):
    if not cond: fails.append(msg)

# --- Found 2026-08-10 by external review: cited the bill's proposed sections, not the code
u = BILLS["ut-hb249-2024"]
check("63G-32-101" in u["codified_at"] and "63G-32-102" in u["codified_at"],
      "Utah codified_at must cite 63G-32-101/102 (the Code), not 63G-31 (the enrolled bill)")
check("63G-31-101" not in u["codified_at"],
      "Utah codified_at still contains the superseded 63G-31 citation")

# --- Found 2026-08-10 in follow-up: we inferred life from the absence of a terminal action
w = BILLS["wa-hb2029-2025"]
check(w["status"]["stage"] == "failed",
      "WA HB 2029 must be 'failed' — it died at sine die 12 Mar 2026; a carryover resolution is not life")
check("sine die" in (w["status"].get("evidence") or {}).get("action","").lower(),
      "WA HB 2029 status evidence must name the sine die adjournment")

# --- Wisconsin's mechanism is an explicit action line, unlike Washington's silence
for i in ("wi-ab959-2026","wi-sb932-2026"):
    ev = (BILLS[i]["status"].get("evidence") or {}).get("action","")
    check("Senate Joint Resolution 1" in ev,
          f"{i} must cite the explicit 'Failed to pass pursuant to Senate Joint Resolution 1' line")

# --- verification_status describes STATUS only; it must not imply the text was read
for b in REG["bills"]:
    v = b.get("verification") or {}
    check(v.get("operative_text") in ("read_in_full","partial","not_read"),
          f"{b['id']}: verification.operative_text missing or invalid")
    if v.get("operative_text") != "read_in_full":
        check(bool(v.get("operative_text_note")),
              f"{b['id']}: operative text not read in full but no note saying what was checked")

# --- every terminal status must cite an action of record
for b in REG["bills"]:
    if b["status"]["stage"] in ("enacted","failed","dead"):
        check(bool(b["status"].get("evidence")),
              f"{b['id']}: terminal status with no action of record")

# --- enacted codified_at must be code-sourced, or explicitly flagged as not yet
for b in REG["bills"]:
    if b["status"]["stage"]=="enacted" and b["codified_at"]:
        src = (b.get("verification") or {}).get("codified_at_source")
        check(src=="code" or "CODIFIED_AT PROVENANCE" in b["notes"],
              f"{b['id']}: enacted codified_at is bill-sourced and not flagged as such")

# --- documented vocabulary and validator vocabulary must agree
val = (ROOT/"validate.py").read_text()
vocab = set(re.findall(r'"([a-z_]+)"', val[val.index("PROV={"):val.index("}", val.index("PROV={"))]))
for p in vocab:
    check(f"`{p}`" in SCHEMA, f"provision '{p}' accepted by validator but not documented in SCHEMA.md")
used = {p for b in REG["bills"] for p in b["provisions"]}
check(used <= vocab, f"provisions in use but not in validator vocabulary: {used - vocab}")

# --- lineage edges must resolve and be labelled
for b in REG["bills"]:
    if b["derived_from"]:
        check(b["derived_from"] in BILLS, f"{b['id']}: derived_from points at a missing record")
        check(bool(b["derived_from_changes"]), f"{b['id']}: lineage edge with no stated differences")

# --- stored texts must exist
for b in REG["bills"]:
    for v in b["versions"]:
        if v.get("text_path"):
            check(os.path.exists(v["text_path"]), f"{b['id']}: missing stored text {v['text_path']}")

# --- machine-facing lineage fields must stay free of evaluative language
BAD = r"soften|degrad|overbroad|generous|made up its mind|weaken|remarkable|wisely|worse|better than"
for b in REG["bills"]:
    m = re.search(BAD, " ".join(b["derived_from_changes"]), re.I)
    check(not m, f"{b['id']}: evaluative language in derived_from_changes: {m.group() if m else ''}")

# --- temporal metadata must not be ambiguous
check("baseline_snapshot" in REG and "verified_as_of" in REG,
      "registry must separate baseline_snapshot from verified_as_of")
check("as_of" not in REG, "ambiguous top-level 'as_of' has returned")

print(f"{len(fails)} failure(s)")
for f in fails: print("  ✗", f)
if not fails: print("  all regression tests pass")
sys.exit(1 if fails else 0)
