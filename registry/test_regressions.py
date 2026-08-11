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

# --- documented vocabulary and machine vocabulary must agree
# This test used to regex the PROV set out of validate.py, which is the brittle
# source-parsing the vocabulary file was introduced to end. It reads the file now.
VOCAB = json.load(open("vocabulary.json"))
vocab = {p["key"] for p in VOCAB["provisions"]}
check(len(vocab) == len(VOCAB["provisions"]), "duplicate key in vocabulary.json")
for p in vocab:
    check(f"`{p}`" in SCHEMA, f"provision '{p}' in the vocabulary but not documented in SCHEMA.md")
used = {p for b in REG["bills"] for p in b["provisions"]}
check(used <= vocab, f"provisions in use but not in the vocabulary: {used - vocab}")
# The site's matrix columns must be a subset, or a column would render with no label.
labels = {p["key"] for p in VOCAB["provisions"] if p.get("in_matrix")}
check(labels <= vocab, "in_matrix keys must exist in the vocabulary")
check(used <= labels | {p["key"] for p in VOCAB["provisions"] if not p.get("in_matrix")},
      "a provision in use appears in no vocabulary group")

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

# --- The validator's own checks must fire. A check that never fails is decoration,
# --- which is precisely the criticism external review made of the stored hashes.
# --- Each case below breaks one thing in a throwaway copy and asserts the message.
import shutil, subprocess, tempfile

def validator_says(mutate, expect):
    """Run validate.py over a mutated copy of the registry; assert it objects."""
    with tempfile.TemporaryDirectory() as td:
        dst = pathlib.Path(td) / "registry"
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("__pycache__", "incoming"))
        # The validator reads SCHEMA.md and PROVISIONS.md from the repo root, so the
        # copy needs them too or every vocabulary check fires spuriously.
        for doc in ("SCHEMA.md", "PROVISIONS.md"):
            shutil.copy(ROOT.parent / doc, pathlib.Path(td) / doc)
        data = json.loads((dst / "bills.json").read_text())
        mutate(data)
        (dst / "bills.json").write_text(json.dumps(data))
        r = subprocess.run([sys.executable, str(dst / "validate.py")],
                           capture_output=True, text=True, timeout=120)
        out = r.stdout + r.stderr
        check("Traceback" not in out, f"validator crashed instead of reporting: {expect}")
        check(expect in out, f"validator did not report {expect!r}\n{out[-700:]}")

def _first(data):
    return data["bills"][0]

def validator_says_vocab(mutate, expect):
    """Same, but mutating vocabulary.json rather than bills.json."""
    with tempfile.TemporaryDirectory() as td:
        dst = pathlib.Path(td) / "registry"
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("__pycache__", "incoming"))
        for doc in ("SCHEMA.md", "PROVISIONS.md"):
            shutil.copy(ROOT.parent / doc, pathlib.Path(td) / doc)
        vocab = json.loads((dst / "vocabulary.json").read_text())
        mutate(vocab)
        (dst / "vocabulary.json").write_text(json.dumps(vocab))
        r = subprocess.run([sys.executable, str(dst / "validate.py")],
                           capture_output=True, text=True, timeout=120)
        out = r.stdout + r.stderr
        check("Traceback" not in out, f"validator crashed instead of reporting: {expect}")
        check(expect in out, f"validator did not report {expect!r}\n{out[-500:]}")

validator_says(lambda d: _first(d).__setitem__("status", "failed"),
               "'status' should be an object")
validator_says(lambda d: _first(d).__setitem__("watch_dates", {"date": "2026-01-01"}),
               "'watch_dates' should be a list")
validator_says(lambda d: _first(d).__setitem__("versions", "introduced"),
               "'versions' should be a list")
validator_says(lambda d: _first(d)["status"].__setitem__("source_url", "javascript:alert(1)"),
               "is not an http(s) URL")

def _escape_path(d):
    for b in d["bills"]:
        for v in b["versions"]:
            if v.get("text_path"):
                v["text_path"] = "../../site/build.py"
                v.pop("text_sha256", None)
                return
validator_says(_escape_path, "text_path escapes registry/texts")

def _break_hash(d):
    for b in d["bills"]:
        for v in b["versions"]:
            if v.get("text_sha256"):
                v["text_sha256"] = "0" * 64
                return
validator_says(_break_hash, "stored text hash does not match file")

# An undocumented vocabulary entry, and a tag used but not in the vocabulary.
validator_says_vocab(
    lambda v: v["provisions"].append({"key": "invents_a_new_category", "label": "x",
                                      "in_matrix": False}),
    "is not documented in SCHEMA.md")
validator_says_vocab(
    lambda v: v.__setitem__("provisions",
                            [p for p in v["provisions"]
                             if p["key"] != "denies_legal_personhood"]),
    "bad provisions")

print(f"{len(fails)} failure(s)")
for f in fails: print("  ✗", f)
if not fails: print("  all regression tests pass")
sys.exit(1 if fails else 0)
