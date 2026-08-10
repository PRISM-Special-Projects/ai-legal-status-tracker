# Implementation report — response to red-team review

**Date:** 2026-08-10 · **Repo:** https://github.com/PRISM-Special-Projects/ai-legal-status-tracker

Two external reviews produced ~29 findings. This records what was implemented, what was
rejected and why, and what still blocks publication. **The rejections matter more than the
implementations** — each carries a rationale that will suppress future scrutiny if it is wrong.

Written by the same party that did the implementation, so nothing here has been independently
checked.

---

## 1. Implemented — data corrections

| Finding | Fix | Verifiable by |
|---|---|---|
| Utah `codified_at` cited the enrolled bill's proposed sections | Corrected to **§§ 63G-32-101/102**, ch. 32, 2024 Utah Laws ch. 451 | `le.utah.gov/xcode/Title63G/Chapter32/` |
| **Our own correction to the paper was wrong** — Washington HB 2029 | Retracted. It died at sine die 12 Mar 2026; a January carryover resolution is not evidence of life. Corrections to the paper: 6 → 5 | WA bill history + 2026 session calendar |
| Consequent error: we claimed WA and WI differ in *outcome* | They do not. Both died at end of biennium; they differ only in whether the state posts a terminal action | `session_rules.json` |
| "23 of 23 read against primary sources" — false, contradicted by our own caveats | Per-record `verification`: operative text **read in full 16 · partial 1 · not read 6** | `registry/validate.py` audit output |
| `as_of` ambiguous against `generated` / `last_verified` | Split into `baseline_snapshot` / `verified_as_of` | `bills.json` header |
| Evaluative language in machine-facing fields | 18 edits removing "softening", "overbroad", "weakened", "generous in form", "the state has not made up its mind", "remarkable" | regression test asserts absence |
| "Ohio inverted Missouri" | Replaced with the default/exception description, plus an explicit statement that whether they differ in practice is a question for a lawyer | `oh-hb469-2025` notes |
| "Diffusion by commissioned drafts" asserted causation from metadata | Narrowed to what the metadata shows: same model text, separate drafting jobs, provenance unknown | `mo-sb859-2026` notes |

## 2. Implemented — architecture

- **`status.basis`** — `explicit_action` 15 · `session_rule` 2 · `secondary_source` 6.
  Distinguishes a status the legislature recorded from one we derived.
- **`session_rules.json`** — sourced carryover and expiration rules for WA, WI, MO, each
  recording whether that state posts a terminal action at all.
- **Version-level `provisions`** on 19 of 32 versions, plus derived `provision_changes`
  (added / removed / retained). `restricts_person_like_training` now attaches to Tennessee
  HB 1455 *as introduced* rather than applying to zero records.
- **Three new tags** — `defines_human_to_include_unborn`, `creates_criminal_offence`,
  `creates_private_right_of_action`. Added because tagging versions revealed the vocabulary
  could not express what Tennessee removed. **See §5: this is the change most at risk of
  motivated reasoning.**
- **`source_manifest.json`** — SHA-256 for 10 source documents and 16 normalised texts;
  12 versions linked to the exact hashed document they derive from.
- **`PROVISIONS.md`** — operational test, positive example, **negative examples** and
  exclusions per tag. Wisconsin's `assigns_liability_to_humans` is the worked negative case.
- **Audit summary** replaces bare pass/fail; **publication gate** separates ERROR (cannot
  publish) from WARNING (publishable with a caveat).
- **`test_regressions.py`** — one test per bug ever found here.
- **CI** — validate, build, then assert page count, link integrity, `text_path` resolution,
  CSV/registry agreement, vocabulary coverage, and absence of evaluative language.
- Fixed: mobile CSS specificity bug hiding every matrix row; matrix cells lacking a text
  equivalent for screen readers; `validate.py` requiring a specific working directory.
- **README, MIT (code) and CC BY 4.0 (data)** licences, noting that the underlying statutes
  are US government edicts in the public domain.

---

## 3. Rejected, with reasons — attack these first

### R1 — spaCy for sentence segmentation
**Proposed:** replace regex sentence splitting with spaCy `en_core_web_sm`.
**Rejected because:** the diagnosis (regex breaks on `N.D. Cent. Code § 1-01-49(8)`) is right,
but the remedy targets the wrong unit. Legislative text is a self-marking hierarchy —
`SECTION 1.` → `(a)` → `(1)` — so section-aware parsing is deterministic and yields
"§ 1357.11(A) changed" rather than "sentence 14 changed". `en_core_web_sm` is trained on web
and news English and would also mis-split statutory citations; it is differently wrong and
harder to inspect. It also adds ~50 MB to a deliberately dependency-free build.
**Risk if wrong:** we keep a brittle differ. Mitigated only by the fact that section-aware
parsing is still unbuilt — so today we have *neither*.

### R2 — Computing status from session rules
**Proposed:** `if current_date > session_end and status != enacted: return "Failed"`.
**Rejected because:** it replaces a sourced fact with a calculation, which is the exact move
that produced the Washington error. The rules registry exists so a human can *see* when a
non-terminal status has become implausible.
**Risk if wrong:** stale statuses persist because nothing forces review. Partially mitigated
by `status.basis`, not fully.

### R3 — Per-field epistemic wrappers
**Proposed:** `{value, source, source_type, verified}` around every legally consequential field.
**Rejected because:** roughly quadruples record size and adds friction to every edit, for
value the per-dimension `verification` object already delivers at 23 records.
**Risk if wrong:** field-level provenance is exactly what a legal academic asks for, and
retrofitting at 200 records is far harder than doing it at 23.

### R4 — Separate claims layer
**Proposed:** a `claims[]` array typed fact / inference / interpretation.
**Rejected because:** the planned `notes` → `analysis` split achieves most of it more cheaply.
**Risk if wrong:** that split is still unbuilt, so `notes` continues to mix evidence and
interpretation. The language purge removed the vocabulary of evaluation, **not necessarily the
evaluation**.

### R5 — Discovery ledger
**Rejected because:** correct for Phase 4, premature while discovery is manual.
**Risk if wrong:** absence from the registry still cannot be distinguished from "not looked
for". This is a real gap today.

### R6 — `role="gridcell"` on matrix cells
**Rejected because:** it overrides native table semantics; without a full `role="grid"`
structure it degrades screen-reader behaviour. The actual gap — filled cells having no
accessible text — is fixed.

### R7 — `!important` to fix the mobile collapse
**Rejected because:** it was a specificity bug, fixed properly by scoping selectors.

### R8 — Parsing `SCHEMA.md` to load the controlled vocabulary
**Rejected because:** extracting terms from markdown prose is brittle in the way that caused
the original drift. **Note this is only partly mitigated** — CI checks that every tag in use
is documented, but the vocabulary still lives in two places.

### R9 — Fail-fast validation
**Rejected because:** accumulate-and-report makes a bulk fix tractable; fail-fast turns a
23-record correction into 23 runs.

---

## 4. Still blocking publication

1. **Status audit for the 6 `secondary_source` records.** The Washington error was a class,
   not an instance. Until each is checked against its session calendar, no status is settled.
2. **`METHODOLOGY.md`** — a deterministic inclusion test. Scope was inherited from one paper's
   May 2026 snapshot, which is provenance, not a completeness methodology. Also unresolved:
   whether legislation *creating* AI legal personality is in scope. The title implies yes; the
   corpus is almost entirely denial bills.

Not blocking, but open: section-aware differ (R1's unbuilt alternative), `notes` → `analysis`
split, `codified_at` vs `proposed_code_sections`, completeness audit, per-version provisions
for the 13 untagged versions.

---

## 5. Where we think this is weakest

**The three new tags.** They were added *after* tagging versions showed the vocabulary could
not express the Tennessee change — which is the correct reason, but it is also indistinguishable
from inventing categories to make a favoured finding legible. `defines_human_to_include_unborn`
applies to exactly one bill's introduced text, which is the diff we most want to show.

**Version provision tags were assigned by judgement**, not by re-reading each text against
`PROVISIONS.md`. 19 assignments, one pass, no second coder.

**The language purge may be cosmetic.** We removed evaluative words. Whether the underlying
notes still *argue* a position in neutral vocabulary has not been independently assessed.

**`status.basis` could create false confidence.** Six records are `secondary_source`, which is
honest, but the field's existence may read as rigour that the underlying checking does not yet
support.

**No independent check.** The same party produced the errors, the fixes, and this report.
