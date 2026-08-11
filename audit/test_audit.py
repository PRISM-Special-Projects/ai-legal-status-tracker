#!/usr/bin/env python3
"""One test per bug actually found in the audit instrument, plus the two properties
the instrument would be worthless without: every question it asks is defined, and no
sheet carries the answer.

Run: python3 audit/test_audit.py
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import check_sheet as c          # noqa: E402
import make_sheets as m          # noqa: E402

BILLS = {b["id"]: b for b in json.loads((ROOT.parent / "registry" / "bills.json").read_text())["bills"]}
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def verdict(rid, field, answer):
    b = BILLS[rid]
    rows = c.compare({field: answer}, c.recorded(b), b)
    return next(v for k, v, _, _ in rows if k == field)


# --- Found 2026-08-11 while reviewing a proposed sheet revision: the sponsors branch ran
# --- ahead of the sentinel check, so an honest abstention scored as a contradiction.
check(verdict("sc-hb3796-2025", "sponsors", "NOT STATED") == "not_stated",
      "a sentinel answer for sponsors must not be compared as a name list")
check(verdict("sc-hb3796-2025", "sponsors", "UNREACHABLE") == "unreachable",
      "UNREACHABLE for sponsors must report unreachable, not mismatch")

# --- Same review: the sponsors branch also ran ahead of the empty-record check, so the
# --- one record in the priority batch with no sponsors recorded (mn-sf4114-2026) would
# --- have reported the registry as wrong about a field it says nothing about.
check(BILLS["mn-sf4114-2026"]["sponsors"] == [],
      "mn-sf4114-2026 no longer has an empty sponsor list; this test's premise is stale")
check(verdict("mn-sf4114-2026", "sponsors", "Maye Quade") == "extra",
      "a sponsor the record omits entirely is an 'extra' gap to fill, not a mismatch")

# --- Same review: notation that varies legitimately between a legislature's page and a
# --- registry record was scored. A false mismatch teaches an auditor to discount real ones.
check(verdict("mo-sb859-2026", "sponsors", "Sen. Moon") == "match",
      "an honorific must not turn a matching sponsor into a discrepancy")
check(verdict("sc-hb3796-2025", "sponsors", "Rep. Beach; Rep. Kilmartin") == "match",
      "sponsor order and honorifics must not affect the verdict")
check(verdict("oh-hb469-2025", "sponsors", "Claggett") == "review",
      "a surname against a full name is a completeness difference for a human, not a mismatch")

# --- ...but the check must still fire. A comparison that cannot fail is decoration.
check(verdict("sc-hb3796-2025", "sponsors", "Smith; Jones") == "mismatch",
      "wholly different sponsor names must still report mismatch")
check(verdict("sc-hb3796-2025", "sponsors", "Kilmartin") == "partial",
      "a sponsor list missing a recorded name must report partial")

# --- Found 2026-08-11: the sheets permit CANNOT TELL for status_stage, which is only
# --- honest if the checker treats it as an abstention rather than a contradiction.
check(verdict("mn-sf4114-2026", "status_stage", "CANNOT TELL") == "not_stated",
      "CANNOT TELL for status_stage must record an unsourced field, not a mismatch")
check(verdict("mn-sf4114-2026", "status_stage", "enacted") == "mismatch",
      "a wrong status_stage must still report mismatch")

# --- Found 2026-08-11: six sheets shipped asking the auditor to apply
# --- covers_non_ai_entities, whose test PROVISIONS.md stated under a shared
# --- "Respectively:" heading the extractor could not read. It printed a placeholder and
# --- warned only when NO test extracted at all.
tests = m.provision_tests()
for key in m.PROV_QUESTIONS:
    check(key in tests and len(tests[key]) > 20,
          f"no usable test extracted from PROVISIONS.md for '{key}'")
for key in ("bars_marriage_or_union", "bars_property_ownership", "bars_corporate_office"):
    check(tests.get(key), f"shared-heading key '{key}' lost its test")

r = subprocess.run([sys.executable, str(ROOT / "make_sheets.py"), "--batch", "secondary"],
                   capture_output=True, text=True, timeout=120)
check(r.returncode == 0, f"make_sheets.py failed on the priority batch:\n{r.stdout}{r.stderr}")

_missing = subprocess.run(
    [sys.executable, "-c",
     "import sys; sys.path.insert(0, %r);"
     "import make_sheets as m; m.PROV_QUESTIONS = m.PROV_QUESTIONS + ['no_such_tag'];"
     "sys.argv = ['x', '--batch', 'secondary']; m.main()" % str(ROOT)],
    capture_output=True, text=True, timeout=120)
check(_missing.returncode == 1,
      "make_sheets.py must refuse to write a sheet asking a test PROVISIONS.md does not state")
check("no_such_tag" in _missing.stdout + _missing.stderr,
      "the refusal must name the undefined test")

# --- The instrument's one design property: a sheet carries the questions, not the answers.
# --- Two fields are exempt, for different reasons. bill_number: the heading has to identify
# --- the record to be usable at all, and that limit is recorded in PROTOCOL.md rather than
# --- tested away. status_stage: the question has to print the controlled vocabulary, and
# --- printing every value privileges none — a property asserted below rather than assumed.
BLIND = ("status_action", "status_action_date", "sponsors",
         "effective_date", "codified_at", "operative_quote")
STAGE_VALUES = [s.strip() for s in m.STAGES.split("·")]
for path in sorted((ROOT / "sheets").glob("*.md")):
    b = BILLS.get(path.stem)
    if b is None:
        continue
    text = path.read_text()
    for field in BLIND:
        rec = c.recorded(b).get(field)
        if rec in (None, "", []) or len(str(rec)) < 4:
            continue
        check(str(rec) not in text,
              f"{path.name} leaks the recorded {field} to the auditor: {str(rec)[:60]!r}")
    check("test not found" not in text,
          f"{path.name} asks a provision test it does not state")
    absent = [s for s in STAGE_VALUES if s not in text]
    check(not absent,
          f"{path.name} omits stage value(s) {absent} — printing a subset points at an answer")

for f in fails:
    print("  ✗", f)
print(f"{len(fails)} failure(s)" if fails else f"  all audit-instrument tests pass "
      f"({len(list((ROOT / 'sheets').glob('*.md')))} sheets checked)")
sys.exit(1 if fails else 0)
