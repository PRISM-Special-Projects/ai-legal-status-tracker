#!/usr/bin/env python3
"""Generate blind extraction sheets for the source-to-record audit.

A sheet carries the source URLs and the questions. It deliberately does NOT carry
the recorded values: an auditor shown the answer confirms it, an auditor shown only
the question reconstructs it, and only the second is evidence. See audit/PROTOCOL.md.

    python3 audit/make_sheets.py                    # all records
    python3 audit/make_sheets.py --batch secondary  # the six secondary_source ones
    python3 audit/make_sheets.py --batch enacted
    python3 audit/make_sheets.py sc-hb3796-2025     # named records
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
REG = ROOT.parent / "registry"
SHEETS = ROOT / "sheets"

STAGES = "introduced · in_committee · passed_one_chamber · enacted · failed · dead"

# Questions are phrased so the answer comes from the document, not from judgement.
FIELDS = [
    ("bill_number", "The bill number exactly as the source prints it (e.g. 'H. 3796', 'HB 1462')."),
    ("chamber", "Which chamber introduced it? house / senate / joint."),
    ("year_introduced", "Calendar year of introduction, as stated."),
    ("session", "The session as the source names it (e.g. '126th General Assembly, 1st Reg. Sess.')."),
    ("status_stage", f"Current disposition, one of: {STAGES}."),
    ("status_action", "The MOST RECENT action line, copied verbatim from the history."),
    ("status_action_date", "Date of that action, as printed."),
    ("sponsors", "Every sponsor named, separated by semicolons, spelled as printed."),
    ("codified_at", "Which code sections it creates or amends, as the bill or act states."),
    ("effective_date", "Effective date if the text states one, else NOT STATED."),
    ("operative_quote", "The single sentence that denies personhood, declares AI non-sentient, or "
                        "otherwise sets AI's legal status — copied VERBATIM. If the source you can "
                        "reach does not contain operative text, write NOT STATED."),
]

# The interpretive part, kept to the tags whose operational test is genuinely textual.
# The test is quoted from PROVISIONS.md so the auditor applies it rather than judging.
PROV_QUESTIONS = ["denies_legal_personhood", "declares_non_sentient",
                  "assigns_liability_to_humans", "bars_ai_liability", "covers_non_ai_entities"]


def provision_tests():
    """Pull each tag's Test line out of PROVISIONS.md rather than restating it here."""
    text = (ROOT.parent / "PROVISIONS.md").read_text()
    out = {}
    for key in PROV_QUESTIONS:
        m = re.search(rf"^## `{re.escape(key)}`\n\*\*Tests?\.\*\*\s*(.+?)(?=\n\*\*)",
                      text, re.S | re.M)
        if m:
            out[key] = " ".join(m.group(1).split())
    return out


def sheet(b, tests):
    j, s = b["jurisdiction"], b["sources"]
    urls = (s.get("primary") or []) + (s.get("tracker") or [])
    lines = [
        f"# Audit sheet — {j['state']} {b['bill_number']}",
        "",
        f"**Record id:** `{b['id']}`  ",
        "**Auditor:** _______________  **Date:** __________",
        "",
        "Read the sources below and fill in every `answer.` line. Write `NOT STATED` if the source "
        "does not say, `UNREACHABLE` if you cannot retrieve it. Do not guess, do not infer from "
        "context, and do not consult `registry/bills.json` — the comparison happens afterwards, "
        "mechanically.",
        "",
        "## Sources",
        "",
    ]
    lines += [f"- {u}" for u in urls] or ["- (none recorded — note that as a finding)"]
    lines += ["",
              "Prefer the legislature's own page, or the enacted act, over any tracker. If you use "
              "a different source, add its URL here.",
              "",
              "## Fields", ""]
    for key, question in FIELDS:
        lines += [f"**{key}** — {question}", "", "```", f"answer.{key}: ", "```", ""]

    lines += ["## Provision tests", "",
              "Apply each test to the operative text. Answer `yes`, `no`, or `CANNOT TELL` if you "
              "could not read the operative text. These are textual tests, not judgements about "
              "legal effect.", ""]
    for key in PROV_QUESTIONS:
        t = tests.get(key, "(test not found in PROVISIONS.md)")
        lines += [f"**{key}**", f"> {t}", "", "```", f"answer.provision.{key}: ", "```", ""]

    lines += ["## Notes", "",
              "Anything the sheet did not ask for: a discrepancy you noticed, a source that "
              "contradicts another, a field you think is unanswerable from any public document.",
              "", "```", "answer.notes: ", "```", ""]
    return "\n".join(lines)


def main():
    bills = json.loads((REG / "bills.json").read_text())["bills"]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    batch = None
    if "--batch" in sys.argv:
        batch = sys.argv[sys.argv.index("--batch") + 1]

    if batch == "secondary":
        sel = [b for b in bills if b["status"].get("basis") == "secondary_source"]
    elif batch == "enacted":
        sel = [b for b in bills if b["status"]["stage"] == "enacted"]
    elif args:
        sel = [b for b in bills if b["id"] in args]
    else:
        sel = bills

    SHEETS.mkdir(parents=True, exist_ok=True)
    tests = provision_tests()
    written, skipped = 0, 0
    for b in sel:
        p = SHEETS / f"{b['id']}.md"
        if p.exists() and "answer." in p.read_text() and re.search(r"answer\.\w+: \S", p.read_text()):
            skipped += 1        # a partly-filled sheet is never overwritten
            continue
        p.write_text(sheet(b, tests))
        written += 1
    print(f"wrote {written} sheet(s) to {SHEETS.relative_to(ROOT.parent)}/"
          + (f", skipped {skipped} already containing answers" if skipped else ""))
    if not tests:
        print("  warning: no provision tests were extracted from PROVISIONS.md")


if __name__ == "__main__":
    main()
