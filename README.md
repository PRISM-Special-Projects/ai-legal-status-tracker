# AI Legal Status Tracker

A registry of **US state legislation on the legal status and personhood of AI systems** —
23 bills across 12 states, 2022 to mid-2026 — and a static site generated from it.

Not a general AI-legislation tracker. That space is well covered (MultiState, IAPP, NCSL,
Brennan Center, all tracking 1,000+ bills a year). This is a narrow slice with a structural
layer on top: what each provision says, how bills descend from one another, and **how their
text changed between introduction and enactment**.

Court decisions on AI personhood, inventorship and standing are tracked by
[Matthew Lee's AI Rights and Legal Personhood Tracker](https://naturalandartificiallaw.com/ai-rights-and-legal-personhood-tracker/),
which we point to rather than duplicate. He tracks the courts; this tracks the legislatures.

## Status

**Pre-publication.** The data is verified and the site builds, but two things are open:
a status audit for six records established from secondary sources, and a written inclusion
methodology. See `REVISIONS.md`.

The version differ is now structural: provisions are aligned on their full section and
subsection path rather than on punctuation, redesignation is distinguished from amendment, and
a comparison that cannot establish structure says so on the record. What it does and does not
establish is set out on the site's method page and in `site/legdiff.py`.

```
Records                                   23 across 12 states
Status established from a citable record  23
  basis: explicit legislative action      15
  basis: session rule (derived)            2
  basis: secondary source                  6
Operative text read in full               16
  partial                                  1
  not read                                 6
Enacted laws                               7  (codified_at code-verified: 5)
```

Run `python3 registry/validate.py` for the current audit summary. It reports the evidentiary
state, not just pass/fail — zero validator errors is not the same as strong evidence.

## What is here

```
registry/bills.json          the registry — single source of truth, 23 records
registry/texts/              16 normalised bill texts, used for diffs
registry/incoming/           source PDFs as retrieved
registry/source_manifest.json SHA-256 for every document and text
registry/session_rules.json  how a bill dies in each state, sourced
registry/validate.py         validation + audit summary
registry/test_regressions.py one test per bug ever found here
site/build.py                builds the site from the registry
site/legdiff.py              structural differ — aligns provisions by statutory path
site/test_diff.py            adversarial + corpus tests for the differ
SCHEMA.md                    record definition and controlled vocabularies
PROVISIONS.md                operational test + negative examples per tag
VERIFICATION.md              what was checked, how, and what we got wrong
METHODOLOGY.md               scope and inclusion rules — TODO
```

## Build it

No dependencies beyond the Python standard library, and no network calls at runtime.

```bash
python3 registry/validate.py        # validate + audit
python3 registry/test_regressions.py # regression tests
python3 site/test_diff.py           # differ tests
python3 site/build.py               # writes site/dist/
```

## Principles

**Descriptive, not evaluative.** The registry records what bills say. It does not rate,
rank, score or predict them, and it takes no position on whether AI systems should have legal
status. Inclusion implies no endorsement. Where a bill is claimed to be unconstitutional we
record *who claimed it*, with attribution.

The intent is that this is equally usable by people who support these bills and people who
oppose them.

**Every claim cites something.** Each record carries per-dimension provenance: how the status
was established, whether the operative text was read, whether the statutory citation was
verified against the code or only the bill. `status.basis` distinguishes a status the
legislature recorded from one derived from a session rule.

**Errors are recorded, not quietly fixed.** `VERIFICATION.md` documents our own mistakes,
including a correction to the source paper that we later retracted.

## AI use

This registry was compiled with substantial AI assistance — retrieving documents, extracting
fields, drafting classifications and generating this site. AI tools misread documents, invent
plausible details and mis-attribute sources. Every record was checked against a source by a
person, and the audit summary records how far that went for each one.

External adversarial review has already found errors here that we missed, including a wrong
statutory citation and an unsound correction to another researcher's work. Expect more.
Please report them.

## Source

Seeded from Appendix A of Smith, A., Caviola, L., & Alexander, H. (2026),
*Denying Personhood to AI: An Analysis of U.S. State Legislation on AI Legal Status*,
SSRN 6829981 — which documented 23 bills across 12 states as of May 2026. Every record has
since been independently checked, and the registry now records statutory citations, effective
dates, sponsors, votes, provision detail and text versions that the paper did not set out to
capture.

## Licence

Code: MIT (`LICENSE`). Data and documentation: CC BY 4.0 (`LICENSE-DATA`).
Underlying legislative text is a US government edict and in the public domain.

Suggested citation for a record:

> AI Legal Status Tracker, Mitch Alexander, CC BY 4.0. Record for [state and bill number],
> last verified [date shown on the record]. Accessed [date].

## Corrections

Errors, stale statuses, broken links, missing bills, mischaracterised provisions — please
open an issue. Corrections are logged with the date and what changed, and the registry is
versioned, so every change is a dated, inspectable diff.
