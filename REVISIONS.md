# Revision list — from red-team review, 2026-08-10

Source: GPT red-team (23 findings + a 10-item publication gate), with additions from a second
review and from our own follow-up. Ordered by whether it blocks publication.

**Done: 18 · Remaining: 11**

---

## A. Publication blockers

### A1–A8 — DONE 2026-08-10

| # | Finding | Fix applied |
|---|---|---|
| A1 | "23 of 23 read against primary sources" was false, contradicted by our own caveats | Per-record `verification` object. Operative text read in full 16 · partial 1 · not read 6. Site lede and method page corrected |
| A2 | Utah `codified_at` wrong — cited the enrolled bill's proposed sections | Corrected to §§ 63G-32-101/102, ch. 32, 2024 Utah Laws ch. 451, verified against the Code. Rule recorded: verify against the code, not the bill |
| A3 | `as_of: 2026-05-12` contradicted `generated`/`last_verified` of 2026-08-10 | Split into `baseline_snapshot` and `verified_as_of` |
| A4 | `SCHEMA.md` vocabulary had drifted from `validate.py` | Reconciled; `SCHEMA.md` declared authoritative. **Drift check still needed in CI — see D1** |
| A5 | "Action of record behind every status" overclaimed what the validator enforces | Copy now says terminal statuses, which is what is enforced |
| A6 | Evaluative language in `derived_from_changes` and `notes` | 18 edits. "softening", "overbroad", "weakened", "generous in form", "the state has not made up its mind", "remarkable" all removed. Scan returns zero |
| A7 | "Ohio inverted Missouri" was rhetorical | Replaced with the default/exception description; explicit note that practical equivalence is a question for a lawyer and the registry takes no view |
| A8 | "Diffusion by commissioned drafts" asserted a causal chain from drafting metadata | Rewritten to claim only what the metadata shows: same model text used in separate drafting jobs, provenance unknown |

### A9 — Retraction (found in follow-up, not in the original review) — DONE

Our "correction" that **Washington HB 2029 is not Failed** was wrong. Its 12 Jan 2026 carryover
resolution keeps a bill alive *into* the 2026 session, not beyond it; that session adjourned
sine die 12 March 2026 and unpassed bills die at end of biennium. The paper was right.
Corrections to the paper: **six → five.**

### A10 — Audit every remaining status against its session calendar — TODO

The Washington error is a *class*, not an instance: we inferred life from the absence of a
terminal action. Nine records still have no `status.evidence`, and several sit in states whose
sessions have since adjourned. **Until this is done, no status claim should be treated as
settled.** Highest-priority remaining item.

---

## B. Structural — schema and data model

### B1 — Per-version provisions — TODO, the big one

Both reviewers independently identified this as the root fix. `provisions` currently describes
only operative text, so a provision removed in committee vanishes from the structured data —
`restricts_person_like_training` applies to zero records despite being the substance of
Tennessee HB 1455 as introduced.

Move `provisions` onto each version, and derive `added` / `removed` / `retained` between them.
That makes the legislative change queryable rather than only visible in a rendered diff, and
it is what makes the dataset useful to a researcher rather than just a reader.

### B2 — `codified_at` is semantically overloaded — TODO

It holds a real citation for enacted laws and "Would enact Ohio Rev. Code §§ …" for pending
ones. Split into `codified_at` (enacted, code-verified) and `proposed_code_sections`.

### B3 — Machine-readable provenance per source document — TODO

The Tennessee introduced texts came from Internet Archive snapshots of a URL that now serves a
different document. That chain currently lives in prose. Record it structurally:
`{source_type, url_as_retrieved, current_url, retrieved_at, sha256, version}` so the evidence
is independently auditable rather than resting on our note saying we did it.

### B4 — Rename provision tags to literal textual predicates — TODO

`bars_ai_liability` and `assigns_liability_to_humans` are not parallel propositions, and the
first can read as a policy conclusion. Move to predicates that describe text:
`explicitly_excludes_ai_from_liability`, `explicitly_allocates_liability_to_human_actor`,
`attributes_ai_related_assets_to_humans`. Define each precisely in `SCHEMA.md`.

### B5 — Separate `notes` from `analysis` — TODO

`notes` is doing two jobs: evidentiary record and interpretation. Make `notes` strictly
evidentiary; move interpretation into an `analysis` field carrying author and date. The
language purge (A6) treated the symptom; this is the cause.

### B6 — Define scope explicitly, including positive personhood — TODO

Scope was inherited from one paper's May 2026 snapshot, which is provenance, not a completeness
methodology. The corpus is heavily weighted toward bills that *deny* personhood, while the
title implies all legislation on AI legal status. Add
`recognition_direction: denies | permits | creates | modifies | unclear` and state the
inclusion rule. The reviewer flagged Delaware's proposed AI-company framework as the boundary
case that exposes this.

### B7 — Completeness audit — TODO

An independent search of all 50 state systems, rather than inheriting one paper's scope. Needed
before the registry can honestly be called *the* registry rather than *a* registry.

---

## C. Code

### C1 — `validate.py` is a field-presence checker, not a structural validator — TODO

It accesses `b["status"]["stage"]` before establishing that `status` exists or has the right
shape, so a malformed record raises `KeyError` rather than reporting a validation error. No
validation of nested shapes (`jurisdiction`, `session`, sponsors, `constitutional_exposure`,
`versions`), date formats, URL formats, or cross-field coherence.

Add JSON Schema or Pydantic as the structural layer; keep the current checks for domain rules.

### C2 — The diff algorithm is unreliable for legislative text — TODO

Sentence splitting by regex on `[.;:]` breaks on statutory citations (`N.D. Cent. Code
§ 1-01-49(8)`), subsection markers, decimals and quoted definitions. Operative-text extraction
by matching an enacting clause will fail on resolutions, constitutional amendments and
amendment instruments — **silently**, producing a plausible-looking diff rather than an error.

Fix: section/subsection-aware parsing first, paragraph diff as fallback, mark fallback mode
explicitly, and stop describing it as an operative-text comparison when it has fallen back.
A state-by-state table of enacting clauses is cheap and removes the guesswork.

### C3 — "Mechanism" in a diff is an assumption, not a fact — TODO

`render_diff` labels `versions[1]` as the mechanism whenever there are three or more versions.
That is right for introduced → substitute → enrolled and wrong for anything longer. Represent
transitions explicitly: `{from, to, instrument, date, source_url}`.

---

## D. Process and infrastructure

### D1 — CI — TODO

None exists. Should run `validate.py` and `build.py`, then assert: expected page count, no
broken internal links, every `text_path` resolves, generated CSV matches the registry, HTML
parses, **and a rendered check at 375 / 720 / desktop**. The CSS bug that hid every matrix row
proves data validation alone is insufficient.

Add a vocabulary drift test comparing `SCHEMA.md` against `validate.py` (see A4).

### D2 — README — TODO

The repository is public with no front door.

### D3 — Licence — DECISION NEEDED

The data page promises a permissive licence; the repo has none, which by default means all
rights reserved. Suggested: CC BY 4.0 for the data, MIT for the code.

### D4 — Rename the Tennessee text files — TODO

`tn-sb837-2025--introduced.txt` derives from `wb-hb0849.pdf`. Tennessee prints companions on
one document and that PDF carries both headers, so the transcription is sound — but the naming
invites exactly the misreading a reviewer made. Name by source document and record the
companion relationship in the version label.

---

## E. Presentation

### E1 — Lead with findings, not the matrix — TODO

The 23×16 grid signals rigour but does not tell a first-time reader what matters. Lead with
three or four empirical findings — lineage and divergence — and make the matrix the second
layer for readers who already have a question.

### E2 — The tile grid still reads as a map — TODO

The caption says it is not one, which is honest but does not stop the misreading. Retitle it
"Filter by state" or make the geography genuine.

### E3 — Matrix accessibility — TODO

Sixteen vertical column headers are hard for sighted and screen-reader users alike; `title`
attributes are not accessible labels; dots carry meaning without a text equivalent. Note also
that the mobile view is a *different information architecture* (list of chips, not a
comparison grid) — that is defensible but should be deliberate and stated.

### E4 — Binary matrix implies false equivalence — TODO

A 0/1 cell cannot distinguish required from permitted, broad from narrow, or affirmative
allocation from prohibition — which is exactly the Wisconsin distinction. Either encode
strength or state plainly that the matrix records presence of a textual feature, not
comparable policy dimensions.

---

## Suggested order

1. **A10** — status audit. Nothing else matters if the statuses are wrong.
2. **B1** — per-version provisions. Every other data fix is easier afterwards.
3. **C1, D1** — structural validator and CI, so regressions stop shipping.
4. **B2, B3, B4, B5** — schema hygiene.
5. **D2, D3** — README and licence, before any wider sharing.
6. **C2, C3** — diff correctness.
7. **E1–E4** — presentation.
8. **B6, B7** — scope and completeness, which is really a Phase 4 question.

**Do not publish before A10, D2 and D3.**

---

## Appendix — assessment of the proposed implementations

### Adopt

**The enacting-clause table (C2).** A state-by-state dictionary of exact enacting clauses
removes the guesswork from operative-text extraction and is cheap. Adopt directly. Extend it
to cover amendment instruments, whose anchor is "by deleting all language after the enacting
clause and substituting".

**A provenance audit script (B3, D4).** The idea is right: assert that every `text_path`
resolves, that filenames match the document they came from, and that no two records share a
text file without declaring a `companion_group`. It needs writing against our actual schema —
the proposal assumes root-level `bill_id` and `text_file`, whereas we use `id` and
`versions[].text_path`, so it would not run as written.

Note the rule it should encode is *not* "filename must equal bill id". Tennessee prints
companion bills on a single document — the PDF behind `tn-sb837-2025--introduced.txt` carries
both "SENATE BILL 837 By Pody" and "HOUSE BILL 849 By Reneau" in its header. A shared text is
correct there; what must be asserted is that sharing is **declared**, not incidental.

**Session-calendar awareness (A10).** Hard-coding sine die dates per state and biennium is
exactly what we lacked, and its absence caused the Washington error.

### Adopt with a significant change

**Do not let the calendar rule *set* status.** The proposal returns `"Failed"` when the
session end has passed. That replaces a sourced fact with a computed inference — which is the
precise failure that produced the Washington error, where we inferred life from the absence of
a terminal action instead of evidencing it.

Build it as a **flagger, not a mutator**: where a record is non-terminal and its session has
adjourned, raise a warning that a human must verify and supply a `status.evidence` line. The
registry's discipline is that every status cites an action; a derived status cites a
calculation.

Also note the proposed Wisconsin date (15 Apr 2026) is wrong — both Wisconsin bills carry an
explicit action line dated **23 March 2026**. Where a state posts a terminal action, that
action governs and no calendar rule is needed.

### Do not adopt

**spaCy for sentence splitting.** Three reasons:

1. It adds a ~50 MB model and a heavy dependency to a build that is deliberately
   zero-dependency and regenerable by anyone with a Python install. That property is worth
   more than marginally better segmentation.
2. `en_core_web_sm` is trained on general English, not legislative drafting. It will also
   mis-split `N.D. Cent. Code § 1-01-49(8)`. It is not obviously better than a tuned regex —
   it is differently wrong, and harder to inspect when it is.
3. It solves the wrong problem. Legislative text is not prose; it is a **hierarchy** —
   SECTION 1 → subsection (a) → subdivision (1). Parsing that structure is deterministic,
   dependency-free, and yields something better than a sentence diff: a section-by-section
   comparison that can say "§ 1357.11 changed" rather than "sentence 14 changed".

Section-aware parsing is the fix. Sentence splitting is the fallback, and should be labelled
as such when used.

**Parsing `SCHEMA.md` to load the vocabulary.** Extracting controlled terms from markdown
prose is brittle in exactly the way that caused the original drift. Put the vocabulary in a
machine-readable file, have the validator import it, and have CI assert that `SCHEMA.md`
documents the same set.

**Raising on the first invalid tag.** Our validator accumulates and reports every error in one
pass, which is what makes a bulk edit tractable. Fail-fast would make a 23-record fix a
23-run loop.

### Already done, differently

The editorial-neutrality example quotes text that is not ours. Our actual fix removed 18
instances across `notes` and `derived_from_changes` and replaced "inverted" with a
default/exception description that also states the registry takes no view on whether the two
provisions differ in practice.

---

## Implemented from the second review batch (2026-08-10)

**D1 CI — DONE.** `.github/workflows/validate.yml` runs the validator, builds the site, then
asserts: page count, no broken internal links, every `text_path` resolves, CSV rows match the
registry, every provision in use is documented in `SCHEMA.md`, and no evaluative language in
`derived_from_changes`. Dry-run passes locally. **No `pip install` step** — the standard-library-only
property is worth protecting, and the proposed spaCy install would have added ~50 MB per run
for a dependency nothing uses.

**Path bug — DONE.** `validate.py` chdir'd to its own directory. It previously required being
run from `registry/`, so the proposed CI would have failed on its first run. Found by writing
the CI, which is the point of CI.

**E3 partial — DONE.** Every matrix cell now carries a visually-hidden text equivalent. The
filled cells previously relied on `aria-label` on a `<span>`, which is not reliably announced,
so a screen reader could reach a cell and hear nothing. Now `aria-hidden` on the dot plus
`yes`/`no` in the accessible name.

**Not adopted:** `role="gridcell"` on `<td>` — it overrides native table semantics, and without
a full `role="grid"` structure it degrades screen-reader behaviour rather than improving it.
Our table already has `th scope="col"`/`scope="row"`, so headers are announced automatically;
the gap was the missing cell text, now fixed. Also not adopted: `!important` to fix the mobile
collapse — that was a specificity bug and is already fixed by scoping the selectors properly.


---

## Hardening pass — implemented 2026-08-10

Working from the specification's principle: turn each finding into a constraint or a test, so
the *class* of error becomes hard to reproduce.

| Item | Implemented |
|---|---|
| **Regression suite (D)** | `registry/test_regressions.py` — one test per bug actually found: Utah code-not-bill, Washington-carryover-is-not-life, Wisconsin's explicit failure line, verification dimensionality, terminal statuses require evidence, enacted `codified_at` needs code provenance, vocabulary drift, lineage edges resolve, stored texts exist, no evaluative language, no ambiguous `as_of`. All pass |
| **B1 — version-level provisions** | `versions[].provisions` populated for 19 of 32 versions, and `provision_changes` derived as structured added/removed/retained. `restricts_person_like_training` now attaches to Tennessee HB 1455 *as introduced* instead of vanishing |
| **Structured lineage deltas** | Change objects rather than prose, so neutrality is structural rather than policed by regex |
| **`status.basis`** | `explicit_action` (15) · `session_rule` (2) · `secondary_source` (6). The site can now say "Failed — by session rule" rather than implying the legislature recorded it. This is the Washington error turned into a permanent safeguard |
| **Session-rules registry** | `registry/session_rules.json` — carryover and expiration rules for WA, WI and MO, each sourced, each recording whether the state posts a terminal action. **Deliberately not used to compute status** |
| **Source manifest** | `registry/source_manifest.json` — SHA-256 for 10 source documents and 16 normalised texts; 12 versions now link to the exact hashed document they derive from. Answers "is this transcription faithful?" without taking our word |
| **Audit summary** | The validator now reports the evidentiary state — operative text read 16/23, `codified_at` code-verified 5/7, status evidence 14/23 — before the pass/fail line. "ERRORS (0)" was reading as stronger than the evidence warranted |
| **Publication gate** | ERROR = cannot publish · WARNING = publishable with a caveat |
| **`PROVISIONS.md`** | Operational test, positive example, **negative examples** and exclusions for every tag. The Wisconsin `assigns_liability_to_humans` case is written up as the worked negative example. Adding a tag now requires an entry in the same commit |
| **Three new tags** | `defines_human_to_include_unborn`, `creates_criminal_offence`, `creates_private_right_of_action` — added because tagging versions revealed the vocabulary could not express what Tennessee actually removed |

### Deliberately not implemented

**Per-field epistemic wrappers** (`{value, source, source_type, verified}` on every field).
Roughly quadruples record size and adds friction to every edit, for value the per-dimension
`verification` object already delivers at 23 records. Revisit at 200.

**A separate claims layer.** The `notes` → `analysis` split (B5, still open) achieves most of
it at a fraction of the cost.

**A discovery ledger.** Correct for Phase 4; premature while discovery is manual.

**Computing status from session rules.** The rules registry exists so a human can *see* when a
non-terminal status has become implausible. Deriving status from a calendar would replace a
sourced fact with a calculation — the same move that produced the Washington error.

---

## Second red-team round — triage (2026-08-10)

The review is stored verbatim in `RED-TEAM-2-FINDINGS.md`. It overturned six of the nine
rejections. Its central charge is that several rejections rested on alternatives that had not
been built, so "we have a better plan" was doing the work of "we have a better implementation".

| # | Finding | Status |
|---|---|---|
| 1 | **R1 overturn** — shipped differ was a punctuation differ, knowingly indefensible | **DONE.** `site/legdiff.py` + 22 tests. See `IMPLEMENTATION-REPORT.md` §3 R1 |
| 2 | R2 overturn — session rules are a review aid, not a safeguard; nothing forces review | open |
| 3 | R3 overturn — `verification` records state, not provenance; no field-level source links | open |
| 4 | `verification.status` vs top-level `verification_status` can disagree and the validator never checks | open |
| 5 | R4 overturn — `notes`/`analysis` are locations, not epistemic categories | open |
| 6 | R8 overturn — vocabulary still lives in `PROVISIONS.md` and in `validate.py` | open |
| 7 | Terminal status without evidence is a warning, so the publication gate does not enforce its own requirement | open |
| 8 | Regression tests pin instances, not failure classes | partly addressed for the differ: the tests assert properties (citations never become nodes, reused labels never collapse) as well as the Utah/Washington-style fixtures |
| 9 | The three new provision tags need an ontology inclusion rule, not just textual support | open |
| 10 | `PROVISIONS.md` tests are not all genuinely binary; drop the two-reader claim | open |
| 11 | `session_rules.json` covers 3 of 12 states but reads as general infrastructure | open |
| 12 | Washington's rule source is the bill page, which does not state the consequence of sine die | open |
| 13 | README "every claim cites something" outruns the data model | open |
| 14 | Hashes prove file identity, not faithful transcription; needs a transformation manifest | open |
| 15 | 19 version-provision assignments, one coder, no reliability testing | open |
| 16 | `render_diff` called version `vs[1]` the "mechanism" by array position | **DONE** before this round: selected by label match |
| 17 | R5 partial overturn — a manual discovery ledger should precede any completeness claim | open |
| 18 | The data model still cannot separate observed fact from researcher inference | open — the architectural finding, and the one the report understated |

Nothing in this table is closed by having been argued about. Items 2–18 are open.
