# Design report — AI Legal Status Tracker

Written to orient a reviewer who has not seen this project. It explains what the thing is, the
decisions that shaped it, and why each was made, so that a critique can engage with the reasoning
rather than reconstruct it. It is not a defence: §12 lists what is weakest, and the companion
red-team prompt asks you to attack all of it.

Repository: `https://github.com/PRISM-Special-Projects/ai-legal-status-tracker` (public).
Describes commit `e086a51`. Nothing here is independently verified; it is written by the party that
built it.

```
Registry   registry/bills.json — 23 records, 12 states, 2022 to mid-2026
Site       site/build.py → 58 files in site/dist/ (landing, 23 bill pages, lineage, method, data)
Language   Python 3.12, standard library only. No dependency, at build time or run time
Gates      registry/validate.py · registry/test_regressions.py · site/test_diff.py
           audit/test_audit.py · site/build.py · CI post-build assertions · ruff (F,E9)
```

## 1. What this is, and what it deliberately is not

A registry of US state legislation on the **legal status and personhood of AI systems**, plus a
static site generated from it. Not a general AI-legislation tracker: that space is well served by
MultiState, IAPP, NCSL and the Brennan Center, all tracking a thousand-plus bills a year. This is a
narrow slice — 23 bills — with a structural layer on top: what each provision says, how bills
descend from one another, and how their text changed between introduction and enactment.

Court decisions are out of scope and are pointed at rather than duplicated: Matthew Lee's AI Rights
and Legal Personhood Tracker covers the courts, this covers the legislatures.

The registry was **seeded from Appendix A of Smith, Caviola & Alexander (2026)**, SSRN 6829981,
which documented these 23 bills as of a May 2026 snapshot. Two of the three authors are colleagues.
That has a consequence worth stating up front: **any claimed correction to that paper is the
highest-stakes output this project produces**, and one such correction was made confidently, then
retracted after review. Five stand.

## 2. The governing principle: descriptive, not evaluative

Everything else follows from this. The registry records what bills say. It does not rate, rank,
score or predict them, and it takes no position on whether AI systems should have legal status. The
intended test is that it is equally usable by someone who supports these bills and someone who
opposes them.

Concretely, this forbids things that would otherwise be natural design choices:

- **No graded visual encoding.** The state map's fill is categorical and two-valued — holds bills in
  this registry, or does not — and counts are printed as numerals. A shade ramp from 1 to 6 bills
  would read as intensity; `MO 6` cannot. CI asserts no gradient, no per-shape fill, at most two
  fills.
- **No ordering that implies a ranking.** The matrix sorts chronologically. Sorting so the pattern
  looks like a trend is an editorial act; sort by date and a reader draws their own conclusion.
- **Constitutional claims are attributed, never adopted.** `constitutional_exposure` records *who*
  claimed a bill is unconstitutional. Three records carry such claims. The registry never concludes
  it.
- **Absence is never a finding.** A state with no bill shows no number, and the caption says
  explicitly that this is not the same as none existing, because the inclusion methodology is not
  yet written (§11).
- **Copy is audited for it.** CI greps the structured fields for evaluative language — `soften`,
  `degrad`, `overbroad`, `weaken` and similar — because that vocabulary crept in once already.

## 3. Counting unit

One record per **bill number**, not per legislative vehicle. Companion bills (Tennessee HB 849 /
SB 837, Wisconsin AB 959 / SB 932) get one record each, linked by `companion_group`. This
reproduces the source paper's count of 23 and lets the interface group or ungroup as needed. It also
means "23 bills" is not "23 distinct texts" — six companion groups exist, and the changed-text
callout deduplicates on the group so a shared text is not reported twice.

## 4. The evidentiary architecture

The design assumption is that a registry's value is not its rows but its account of how it knows
each row. So provenance is a first-class field, not a footnote.

- **`status.basis`** records what kind of thing the disposition rests on: `explicit_action` (15
  records — a dated action in the legislature's own history), `session_rule` (2 — derived from the
  rule by which a bill dies at adjournment, sourced in `registry/session_rules.json`),
  `secondary_source` (6 — a summary page or tracker that asserts a status without citing the action
  that produced it). Those six are publication blocker one.
- **`verification`** is per-dimension, not a single flag: whether the operative text was read
  (`read_in_full` 16, `partial` 1, `not_read` 6), whether the statutory citation was checked against
  the code or only the bill, how many versions have stored text, when it was last checked. A note is
  required unless the text was read in full.
- **`verification_status`** describes how the *status* was established and has never meant the text
  was read. Those two were conflated once; a regression test now asserts they cannot be.
- **What "verified" does not mean.** There is **no field-level link from an individual claim to an
  individual source**. The narrative `notes` may carry several observations supported collectively by
  the record's sources, and a reader cannot map one sentence to one source. The README said "every
  claim cites something" until 2026-08-11; that claim was withdrawn rather than papered over, and
  closing the gap is a blocker, not a refinement.
- **`validate.py` prints an audit summary, not a pass/fail.** Zero validator errors is not the same
  as strong evidence, so the tool reports the evidentiary state — how many texts read, how many
  statuses on secondary sources — where a green tick would otherwise hide it.

## 5. Provenance of files

`registry/source_manifest.json` carries a SHA-256 and byte count for every source document (10),
every normalised text (16), and the vendored map geometry. The hashes are **recomputed and compared**
by the validator: they were decoration until external review pointed out that nothing checked them.
`text_path` must resolve beneath `registry/texts/`, after a record pointing at `../../site/build.py`
was accepted and would have had the differ parse Python as statutory text.

Normalisation of stored texts removes line numbers and page furniture only; wording is untouched,
and each text records which normalisations were applied and whether substantive text changed.

Licensing is split deliberately: code MIT, data and documentation CC BY 4.0, underlying legislative
text public domain as a government edict, and the vendored `us-atlas` geometry ISC with its notice
carried beside the file as that licence requires.

## 6. The version differ

The distinguishing feature is that the registry holds bill texts and shows *the change itself*
rather than describing it. Five records hold two or more stored texts and render a comparison;
because companion bills share a text, those five pages carry **three distinct comparisons**, which
is also why the changed-text callout lists three and not five.

`site/legdiff.py` aligns provisions on their **full statutory path** — section and subsection — not
on punctuation or sentence order. Design commitments:

- **Structural or nothing.** If the comparison cannot establish a hierarchy, it says so on the record
  rather than degrading silently into a text diff. Every rendered diff carries a
  comparison-method statement, and CI fails a diff rendered without one.
- **Inference was withdrawn, twice.** Three rules once inferred correspondence beyond structural
  identity. Each was measured by disabling it and re-running the corpus; two were withdrawn. One
  withdrawal makes Tennessee SB 837 report an extra removal and addition — the same boilerplate
  sentence, unpairable on exact text. That **overstates the change**, and was chosen over asserting
  a correspondence the documents do not state.
- **`renumbered` is labelled "same text, new designator"** and rests only on exact text occurring
  once on each side. Whether it should be a primary category at all is genuinely unresolved:
  demoting it sends Tennessee to 12 removed / 4 added, which overstates in the other direction.
- **Ambiguity is named, not resolved.** Roman-numeral `(i)` is treated as a letter sibling and the
  parser warns that this is wrong if the drafter meant a roman child. It does not guess.

## 7. Presentation architecture

Three depths on one spine, from the pre-build design document: the **matrix is the spine**, the
**version diff is the signature**, and the **map is for orientation and navigation only**.

- **The matrix** is 23 bills × 16 provision columns (the vocabulary holds 19; three apply only to
  superseded versions and are excluded from the matrix). It earns its place by showing that the
  paper's three-family taxonomy is a simplification: Wisconsin lacks `assigns_liability_to_humans`,
  Ohio carries `addresses_corporate_veil` where the Missouri substitute does not.
- **The map** was an equal-area tile grid until 2026-08-11, on the reasoning that a choropleth
  encodes a quantity it cannot support. That argument is correct about a colour ramp and says
  nothing about geography; it was wrongly extended into rejecting any real map. Orientation is the
  map's job and recognition is the whole of that job, so it is now an actual US map — categorical
  fill, numeral counts, `us-atlas` geometry with the projection already applied.
- **Feedback is local.** Clicking a state filters the matrix, but the matrix begins a full viewport
  below the map, so the click looked inert. A panel under the map now lists that state's bills with
  year, status and family, ordered by year then number.
- **Two controls, one state.** The map shapes and a list of real `<button>`s share one selector and
  stay in sync, because South Carolina's outline is about 15px on a phone and a keyboard user should
  not have to hunt a shape. Only the 12 states holding bills are interactive; the other 39 are
  `aria-hidden`, with the list as the text alternative.

## 8. One vocabulary, one source of truth

`registry/vocabulary.json` is the single machine-readable provision vocabulary. It previously lived
in four places — the validator, the builder twice, and prose — with CI checking one direction only,
which is how it drifted. `PROVISIONS.md` gives each tag an operational test with negative examples,
and `audit/make_sheets.py` quotes those tests into audit sheets rather than restating them. CI
checks both directions: every vocabulary key documented, every documented key accepted.

## 9. Quality architecture

Five gates run locally and in CI, plus lint:

- `validate.py` — schema, vocabulary, shape-safety, hashes, cross-field consistency, audit summary.
- `test_regressions.py` — **one test per bug ever found here**, plus 10 negative cases that each
  break one thing in a throwaway copy and assert the validator's message. Writing those found two
  crash sites in the audit summary.
- `test_diff.py` — 44 tests, adversarial and corpus, including a conservation test.
- `test_audit.py` — one test per bug in the audit instrument, plus its blindness property.
- CI post-build assertions — page count, every relative link resolves, provisions documented, no
  evaluative language, every diff declares its method, and the map and panel invariants.

The pattern throughout is that **an assertion which cannot fail is decoration**. Every new
assertion is verified by breaking it, and that discipline has repaid itself: it caught a greedy
regex that would have let a real colour ramp through the descriptive-first check.

## 10. The source-to-record audit

Three review rounds have been about architecture, which can now be trusted to report faithfully
what the registry says — a different claim from the registry being right. Every field was compiled
with AI assistance and checked by the party that compiled it, so the data has never had an
independent read.

`audit/` is a blind instrument for one. Sheets carry the source URLs and the questions and
deliberately not the recorded answers, because a sheet that asks "the registry says Kilmartin —
does that match?" produces agreement: confirming is cheaper than reconstructing. `NOT STATED`,
`UNREACHABLE` and `CANNOT TELL` are first-class answers that separate a wrong record from an
unsourced one. Five fields where legal notation varies legitimately are printed side by side for a
human verdict and never scored, because a false mismatch teaches an auditor to wave real ones away.
The six `secondary_source` records are the priority batch. **No independent auditor has run it yet.**

## 11. Publication gate

Not satisfied, and the site is deliberately not deployed anywhere:

1. **Status audit for the six `secondary_source` records** — the instrument exists, unrun.
2. **`METHODOLOGY.md` does not exist.** Scope is still inherited from one paper's May 2026
   snapshot, which is provenance, not a completeness methodology.
3. **Verification and provenance semantics** — no field-level claim-to-source link (§4).

## 12. Where this is weakest

Stated because a reviewer will find them anyway, and because a list of weaknesses written by the
author is checkable:

- **No second coder on anything** — the diff output, the provision tags, the reports.
- **The differ's fallback path has never run on real data.** All corpus pairs parse structurally;
  the one path designed to say "I could not do this reliably" is exercised only by synthetic
  fixtures. True for four reports running.
- **Endpoint comparison only.** The differ compares the first and last version; intermediate
  versions are labelled and never diffed, and the site does not say so plainly enough.
- **`family` A / B / C / other is exposed in the matrix, the filter and the CSV exports, and is
  defined nowhere** — not in `SCHEMA.md` beyond the enum, not on the method page. It is inherited
  from the source paper's taxonomy. A reader can filter by a category the site never explains.
- **Structural-mode detection is a threshold, not a coherence test** — ≥3 markers and ≥50% body
  coverage, both guesses.
- **Document-code consistency is a convention.** Reports name the commit they describe; nothing
  enforces it, and a report went out naming an unpushed SHA once, costing a reviewer their round.
- **The map's twelve interactive states are SVG `<g role="button">` with hand-wired Enter/Space.**
  In one accessibility-tree read they did not surface as buttons while the HTML list buttons did.
  Attribute-level checks pass; the exposure is unconfirmed.
- **Everything reported as verified here was verified by the person who wrote it.** The only
  external checks that have ever caught a factual error in this project were red teams — three
  times.

## 13. How error is handled

`VERIFICATION.md` is a standing log of this project's own mistakes, including corrections it made
wrongly and had to retract. Errors are recorded, not quietly fixed. Superseded planning documents
carry a banner naming which of their decisions were reversed and why, so the trail stays readable
rather than tidy.

The standing instruction for review is: **attack the rejections harder than the implementations.** A
wrong rejection ships with an argument that suppresses the next person who raises it. Round 2
overturned six of nine rejections, mostly because the rejection rested on an alternative that had
never been built — and the map in §7 is the most recent instance of the same failure.
