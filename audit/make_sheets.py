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

# Conventions carried on every sheet. They tell an auditor how to answer consistently; none
# of them authorises supplying a fact the source does not state.
CONVENTIONS = [
    "## Conventions",
    "",
    "**Which source counts.** Prefer the legislature's own page, the official bill text, or the "
    "enrolled or enacted act. Use a tracker only where the official source is unavailable or "
    "silent on the field. Where sources conflict, answer from the official one and describe the "
    "conflict in `answer.notes`. Name any source you used that is not listed above.",
    "",
    "**`status_stage` is the one field you may classify.** It converts a source history into this "
    "registry's controlled vocabulary, so reading the history and choosing a category is expected "
    "here — and nowhere else. Two cautions. Choose from the latest material action shown: a "
    "committee referral with nothing after it is `in_committee`; one chamber's passage with the "
    "other silent is `passed_one_chamber`; an approval, signature or enacted act is `enacted`; an "
    "expressly recorded defeat, rejection, withdrawal, or veto without override is `failed`. And "
    "**this project has not documented what separates `failed` from `dead`** — so if the only "
    "ground for a terminal status is that the session ended, write `CANNOT TELL` and say so in "
    "`answer.notes` rather than picking one. Same answer for any history you cannot classify "
    "without an added assumption.",
    "",
    "**Do not compute a date the source does not print.** Many states have a default effective "
    "date; deriving one is exactly the kind of inference this audit exists to detect.",
    "",
]

# Questions are phrased so the answer comes from the document, not from judgement.
FIELDS = [
    ("bill_number", "The bill number exactly as the source prints it (e.g. 'H. 3796', 'HB 1462')."),
    ("chamber", "Which chamber introduced it? house / senate / joint."),
    ("year_introduced", "Calendar year of introduction. The year in an explicitly dated "
                        "introduction action counts as stated."),
    ("session", "The session as the source names it (e.g. '126th General Assembly, 1st Reg. Sess.')."),
    ("status_stage", f"Current disposition, one of: {STAGES}. Classify from the history per the "
                     "conventions above, or write CANNOT TELL."),
    ("status_action", "The MOST RECENT action line, copied verbatim from the official legislative "
                      "history. Do not substitute a tracker's prose summary where an official "
                      "history exists."),
    ("status_action_date", "Date of that action, as printed."),
    ("sponsors", "Every person named in the authoritative page's sponsor, author, co-sponsor or "
                 "co-author fields, separated by semicolons and spelled as printed. Do not "
                 "reconstruct sponsorship from history entries. If the page distinguishes primary "
                 "from additional sponsors, record that distinction in `answer.notes`."),
    ("codified_at", "Which code sections the bill or act expressly creates, amends or repeals. Do "
                    "not infer codification from a subject heading or a tracker summary."),
    ("effective_date", "Effective date only where the bill text, the act, or official legislative "
                       "metadata expressly states one — do not calculate a default. If text and "
                       "metadata disagree, record the text's date and note the conflict. If none "
                       "is stated, write NOT STATED."),
    ("operative_quote", "The sentence that denies personhood, declares AI non-sentient, or "
                        "otherwise sets AI's legal status — copied VERBATIM. Where distinct "
                        "legal-status rules need more than one sentence, quote the shortest "
                        "contiguous passage containing them and explain the choice in "
                        "`answer.notes`; never paraphrase. If the source you can reach does not "
                        "contain operative text, write NOT STATED; if the operative text exists "
                        "but you cannot retrieve it, write UNREACHABLE."),
]

# The interpretive part, kept to the tags whose operational test is genuinely textual.
# The test is quoted from PROVISIONS.md so the auditor applies it rather than judging.
PROV_QUESTIONS = ["denies_legal_personhood", "declares_non_sentient",
                  "assigns_liability_to_humans", "bars_ai_liability", "covers_non_ai_entities"]


def provision_tests():
    """Pull each tag's Test line out of PROVISIONS.md rather than restating it here.

    A heading may name several keys where they share one test (PROVISIONS.md rule 5); each
    key then gets that test. Keys whose tests differ have their own heading, because a
    "respectively" list cannot be split back into its keys reliably — that is how
    `covers_non_ai_entities` reached six sheets as "(test not found in PROVISIONS.md)".
    """
    text = (ROOT.parent / "PROVISIONS.md").read_text()
    out = {}
    for m in re.finditer(r"^## (`[a-z_]+`(?: · `[a-z_]+`)*)\n\*\*Tests?\.\*\*\s*(.+?)(?=\n\*\*|\n\n|\Z)",
                         text, re.S | re.M):
        body = " ".join(m.group(2).split())
        for key in re.findall(r"`([a-z_]+)`", m.group(1)):
            out[key] = body
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
        "does not say, `UNREACHABLE` if you cannot retrieve it, `CANNOT TELL` where a "
        "classification or a provision test cannot be applied to what you can read. Do not guess, "
        "do not infer from context beyond the one classification the conventions permit, and do "
        "not consult `registry/bills.json` — the comparison happens afterwards, mechanically.",
        "",
        "## Sources",
        "",
    ]
    lines += [f"- {u}" for u in urls] or ["- (none recorded — note that as a finding)"]
    lines += ["", "If you use a source that is not listed, add its URL here.", ""]
    lines += CONVENTIONS
    lines += ["## Fields", ""]
    for key, question in FIELDS:
        lines += [f"**{key}** — {question}", "", "```", f"answer.{key}: ", "```", ""]

    lines += ["## Provision tests", "",
              "Apply each test to the operative text. Answer `yes`, `no`, or `CANNOT TELL` if you "
              "could not read the operative text. These are textual tests, not judgements about "
              "legal effect.", ""]
    for key in PROV_QUESTIONS:
        lines += [f"**{key}**", f"> {tests[key]}", "", "```", f"answer.provision.{key}: ", "```", ""]

    lines += ["## Notes", "",
              "Anything the sheet did not ask for: a source that contradicts another, a source you "
              "used that was not listed, a sponsorship-role distinction, why you answered CANNOT "
              "TELL, an operative provision that spans several sentences, or a field you think is "
              "unanswerable from any public document.",
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

    tests = provision_tests()
    missing = [k for k in PROV_QUESTIONS if k not in tests]
    if missing:
        # A sheet that asks an auditor to apply a test it does not state collects a guess.
        # Six sheets shipped that way once; failing here is what stops it recurring.
        print("error: PROVISIONS.md states no test for: " + ", ".join(missing))
        print("       give each key its own `## `key`` heading with a **Test.** line (rule 5).")
        sys.exit(1)

    SHEETS.mkdir(parents=True, exist_ok=True)
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


if __name__ == "__main__":
    main()
