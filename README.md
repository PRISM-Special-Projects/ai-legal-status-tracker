# AI Legal Status Tracker

A registry of **US state legislation on the legal status and person-like status of AI systems** —
**29 bills across 16 states**, 2022–2026 — and a static site generated from it.

This is deliberately not a general AI-legislation tracker. It focuses on legislation that either
assigns or denies AI legal personhood/legal authority/legal capacity, or regulates claims and
attributions of sentience, consciousness, humanity or comparable person-like status.

Court decisions on AI personhood, inventorship and standing are tracked by
[Matthew Lee's AI Rights and Legal Personhood Tracker](https://naturalandartificiallaw.com/ai-rights-and-legal-personhood-tracker/),
which we point to rather than duplicate. He tracks the courts; this project tracks state legislatures.

## Status

**Release candidate.** Substantive verification, the corpus-completeness sweep and the 29-record
publication audit are complete. Remaining release work is documentation/handoff cleanup and an
independent reconstruction sample. See `RELEASE_READINESS.md`.

Current audit state (2026-08-11):

```
Records                                   29 across 16 states
Status established from a citable record  29
  basis: explicit legislative action      23
  basis: session rule (derived)             6
  basis: secondary source                   0
Operative text read in full               29 of 29
Enacted laws                                9
  codified_at verified against the code     6
  codified_at established from bill/act     3
Terminal statuses with evidence            18 of 18
```

Run `python3 registry/validate.py` and `python3 registry/publication_audit.py` for the current
machine checks.

## Scope

A bill is included when its operative rule either:

1. expressly assigns or denies AI **legal personhood, legal authority, legal capacity, or
   inclusion in a statutory person category**; or
2. regulates an AI system's claim or attribution of **sentience, consciousness, humanity, or
   comparable person-like status** in a way that is more substantive than a generic disclosure
   that the user is interacting with software rather than a human.

Generic bot/AI identity disclosure alone is outside the v1 scope. `METHODOLOGY.md` documents the
search, inclusion/exclusion rule and verification process; `RELEASE_READINESS.md` records the final
completeness sweep and important exclusions.

## What is here

```
registry/bills.json             registry — single bill-centred source of truth, 29 records
registry/claim_evidence.json    claim-specific evidence for selected high-risk claims
registry/source_catalog.json    structured source catalogue used by claim evidence
registry/texts/                 normalized legislative texts used where useful for comparison
registry/incoming/              source documents as retrieved
registry/source_manifest.json   SHA-256 integrity metadata for stored documents/texts
registry/session_rules.json     sourced rules used for session-end status derivations
registry/vocabulary.json        controlled provision vocabulary
registry/validate.py            schema, vocabulary, reference and audit-summary checks
registry/publication_audit.py   tracker-focused publication checks
registry/test_regressions.py    regression tests for errors previously found
site/build.py                   static-site builder
site/legdiff.py                 structural legislative-text differ (technical aid, not release gate)
SCHEMA.md                       record definition
PROVISIONS.md                   operational tests for provision tags
METHODOLOGY.md                  scope, search and verification method
VERIFICATION.md                 audit history, corrections and known limitations
RELEASE_READINESS.md            gated release plan and completion record
```

## Build it

No runtime network calls are required.

```bash
python3 registry/validate.py
python3 registry/publication_audit.py
python3 registry/test_regressions.py
python3 site/build.py
```

The structural differ has its own tests (`python3 site/test_diff.py`). Differ/parser perfection is
useful research infrastructure but is not a v1 blocker unless it changes a tracker-facing factual
conclusion.

## Principles

**Descriptive, not evaluative.** The registry records what bills say and what happened to them. It
does not rate, rank, score or predict legislation, and it takes no position on whether AI systems
should have legal status. Where an outside source makes a constitutional or policy claim, the
registry preserves the attribution rather than adopting the claim as its own.

**Primary evidence for material claims.** Every record identifies primary legislative sources and
records how its status was established. `status.basis` distinguishes an explicit legislative action
from a status derived from a sourced session rule. The operative text has been read for every record.
Selected high-risk claims also have field-level evidence in `registry/claim_evidence.json`; the
sidecar is intentionally not presented as an exhaustive citation for every sentence in `notes`.

**Known limits are disclosed.** A bill's proposed codification and the final published code are not
the same evidentiary object. For enacted laws the registry distinguishes code-verified
`codified_at` from bill/session-law-sourced destinations and records access limitations where direct
code inspection was not available.

**Errors are recorded, not silently erased.** `VERIFICATION.md` documents material corrections to
the registry and to claims inherited from the source paper.

## AI use

This registry was compiled with substantial AI assistance for retrieval, extraction, comparison,
classification and code generation. AI tools can misread documents, infer beyond the evidence or
attach the wrong source. The release process therefore requires direct source review for operative
texts, primary/citable status evidence, validation, and adversarial spot checking.

## Source

The project was seeded from Appendix A of Smith, A., Caviola, L., & Alexander, H. (2026),
*Denying Personhood to AI: An Analysis of U.S. State Legislation on AI Legal Status*, SSRN 6829981,
which documented 23 bills across 12 states as of its May 2026 snapshot. The registry was then
independently re-verified and a fresh national completeness sweep added six further in-scope bills,
producing the current 29-record corpus.

## Licence

Code: MIT (`LICENSE`). Data and documentation: CC BY 4.0 (`LICENSE-DATA`).
Underlying legislative text is a government edict and is reproduced for research/audit purposes.

Suggested citation for a record:

> AI Legal Status Tracker, Mitch Alexander, CC BY 4.0. Record for [state and bill number],
> last verified [date shown on the record]. Accessed [date].

## Corrections

Errors, stale statuses, broken links, missing bills or mischaracterised provisions are welcome as
issues. The registry is versioned so corrections remain inspectable in Git history.
