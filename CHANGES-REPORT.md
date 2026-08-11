# Changes since the third review — report for red-teaming

**Everything described here is on `origin/main` and CI is green on it.** Check the SHA before you
start: if the tree lacks `site/legdiff.py` and `registry/vocabulary.json`, you are reading a stale
copy, and that has already cost one reviewer their time.

```
Repository   https://github.com/PRISM-Special-Projects/ai-legal-status-tracker  (public)
Differ       site/legdiff.py            531 lines, standard library only
Site         site/build.py              1,225 lines → 58 files in site/dist/
Differ tests site/test_diff.py          37 tests
Registry     registry/test_regressions.py  one check per bug ever found, + 10 negative
             validator cases that each break one thing and assert the message
Vocabulary   registry/vocabulary.json   19 provision keys
CI           .github/workflows/validate.yml — jobs: check, lint (both passing)
```

```bash
python3 registry/validate.py && python3 registry/test_regressions.py \
  && python3 site/test_diff.py && python3 site/build.py
```

The site is **not deployed anywhere** and there is no GitHub Pages configuration. That is
deliberate: the project's own publication gate is not satisfied (§6).

Written by the party that made the changes. Nothing here is independently checked.

---

## 1. The process failure that shaped this round

The third review read `origin/main`, which was two commits behind. The structural differ existed
locally but had not been pushed, so the reviewer audited the superseded inline differ and reported —
accurately, about the tree they could see — that the report described files that did not exist and
that the differ collapsed duplicate paths via `dict(A), dict(Z)`.

That was a failure on this side. A report was handed out naming a commit that was not public.

I verified the reviewer's reconstruction rather than assuming it: checking out `d667623` and running
its differ reproduces Tennessee **7 / 3 / 1 / 1** and Missouri **7 / 3 / 12 / 6**, exactly the
numbers they derived by reading code, and also the numbers the original specification had quoted as
"expected". Their method was sound.

**What changed as a result:** `IMPLEMENTATION-REPORT.md` and `DIFF-REPORT.md` now name the commit
they describe and carry the verification commands. Three pre-build planning documents
(`PROJECT_PLAN.md`, `PRESENTATION-DESIGN.md`, `PHASE3-BUILD.md`) carry a banner marking them as a
superseded decision trail, naming the two decisions in them that were reversed.

**Worth attacking:** naming a SHA is a convention, not a mechanism. Nothing enforces it. A report
can still drift the moment the next commit lands, and no test checks that any document's claims
match the code.

## 2. Inferential rules withdrawn from the differ

The previous version carried three rules that inferred correspondence beyond structural identity.
I measured each by disabling it and re-running the corpus, then withdrew two.

| Rule | Measured effect on the corpus | Disposition |
|---|---|---|
| A child whose text is identical moved with its redesignated parent | **One** provision pair, in one bill | Withdrawn |
| Blank `( )` designators keyed by the term they define | **No change to any count** | Withdrawn; replaced with a positional ordinal used for display only |
| Definitions matched by the term they define | Without it Missouri reports 12 modifications, including *"Emergent properties"* amended into *"Developer"* | Kept |

Consequences, stated rather than smoothed over:

- Tennessee SB 837 now reports **9 removed / 1 added / 1 modified / 3 same-text-new-designator**.
  With the withdrawn rule it was 8 / 0 / 1 / 4. The extra removal and addition are one recurring
  boilerplate sentence which cannot be paired on exact text. **This overstates the change**, and was
  chosen over inferring a correspondence the documents do not state.
- A blank designator can be paired on exact text and nothing else. Blanks repeating on both sides
  produce *identity not established*.
- The secondary-key separator for repeated designators is gone. Duplicates on both sides are always
  ambiguous.

`renumbered` survives as a category, resting only on exact text occurring once in each version, and
is labelled *same text, new designator*. **Whether it should be a primary category at all is
unresolved.** Demoting it to metadata sends Tennessee to 12 removed / 4 added, which overstates
change in the other direction. Both answers overstate something; I picked one and renamed it.

## 3. Parser changes

- **Section markers are line-start only.** The mid-line all-caps `SECTION` rule was inert on every
  corpus pair and would have misfired on Idaho's title line, which recites `A NEW SECTION 5-346,
  IDAHO CODE`. It came from a reviewer fixture (`SECTION` in prose) and was deleted rather than
  patched.
- **Internal cross-references are masked.** `risks identified under subdivision (b)(1)` was being
  parsed as a provision, putting two phantom provisions in Tennessee HB 1455's enacted text. Found
  by reading the rendered page, not by a test.
- **Roman-numeral ambiguity is now warned about.** `(i)` is both the ninth letter and roman one; the
  stack treats it as a letter sibling, which is wrong if the drafter meant a roman child. The parser
  says so. It does not fix it.

## 4. Registry and validator

| Change | What it replaced |
|---|---|
| Validator is shape-safe throughout | `b["status"]["stage"]` after checking only that the key existed. A malformed record raised `KeyError` and **hid every other finding** |
| **Hashes are recomputed and compared** | `source_manifest.json` and `versions[].text_sha256` were never checked against the files. They were decoration |
| `text_path` must resolve beneath `registry/texts/` | A record pointing at `../../site/build.py` was accepted, and the differ would have parsed Python as statutory text |
| Source URLs are shape-checked, no network | Nothing |
| `registry/vocabulary.json` | The provision vocabulary in four places — `validate.py`, `build.py` twice, prose in `SCHEMA.md`/`PROVISIONS.md` — with CI checking one direction only |
| 10 negative validator cases | No test that any validator check actually fires |
| Ruff in a separate CI job (`--select F,E9`) | No linting. It found an unused import, an unused local, a dead label map, and **a dead card-list HTML block being computed and discarded** |
| Regression suite runs in CI | The suite existed and CI never executed it |

The negative cases each break one thing in a throwaway copy and assert the message. **Writing them
found two crash sites in the audit summary that my own hardening pass had just missed**, which is
the argument for them.

## 5. Presentation and copy

- The changed-bills callout deduplicated on `(removed, added)`, so two unrelated bills with equal
  counts would silently drop one. Keyed on companion group now.
- State tiles said **"no legislation identified"**. They now say "no bills in this registry — which
  is not the same as none existing, since the inclusion methodology is not yet established."
- The README said **"Every claim cites something."** It does not. Replaced with what the model
  supports, plus an explicit statement that there is no field-level link from a claim to a source
  and that closing the gap is a blocker.

## 6. Publication gate — still not satisfied

1. **Status audit for six `secondary_source` records.** Untouched this round.
2. **`METHODOLOGY.md` does not exist.** Scope is still inherited from one paper's May 2026 snapshot,
   which is provenance, not a completeness methodology.
3. **Verification/provenance semantics.** The README overclaim is fixed by weakening the claim, not
   by building field-level provenance.

Also open, from the second review: the ontology inclusion rule for the three version-only provision
tags; `PROVISIONS.md`'s two-reader decidability claim; Washington's rule provenance; inter-coder
reliability for the 19 version-provision assignments; the discovery ledger; the
`verification.status` / `verification_status` reconciliation; and terminal-status-without-evidence
being a warning rather than an error. Triage in `REVISIONS.md`.

## 7. Where I think this is weakest — attack here first

- **The fallback path has never run on real data.** All five corpus pairs parse structurally. The
  one code path designed to say "I could not do this reliably" is exercised only by synthetic
  fixtures. This has been true for three reports running and is the thing I would attack first.
- **`renumbered` as a primary category** (§2). Genuinely unresolved, not deferred for convenience.
- **Structural-mode detection is still a threshold, not a coherence test.** ≥3 markers and ≥50% body
  coverage, both guesses. The better test proposed last round — "did every recognised marker form a
  coherent hierarchy?" — is **not implemented**; a warning list stands in for it.
- **Endpoint comparison.** The differ compares `versions[0]` to `versions[-1]`. Intermediate
  versions are labelled as the mechanism and never diffed. The minimum fix — saying on the record
  that this is an endpoint comparison — is **not done**.
- **Document/code consistency is a convention.** §1 fixed the instance. Nothing prevents recurrence.
- **No second coder** on anything: the diff output, the provision tags, or this report.
- **Everything reported as verified here was verified by the person who wrote it.** The one external
  check that has ever caught a factual error in this project was a red team, twice.

## 8. What would be most useful back

1. **Are Tennessee SB 837's nine removals the right nine?** Hand-checkable in ten minutes against
   the two documents: 13 provisions in, 5 out; the removals are SECTION 2's heading, its seven
   subdivisions, and the `(19)(B)` clause whose text recurs. Conservation is asserted by a test, but
   it only proves nothing was dropped or double-counted — not that any pairing is right.
2. **Did withdrawing two rules go far enough, or too far?** Tennessee now overstates the change by
   two provisions. That was deliberate.
3. **Is the abstention real or decorative?** Ambiguity appears in a collapsed `<details>`; the
   comparison-method statement is prose most readers skip.
4. **What breaks the parser?** A text, not a hypothesis. The fixtures were written by the person who
   wrote the parser and test only failures I could imagine.
5. **Is `vocabulary.json` a real single source of truth, or did it just move the duplication?**
   `SCHEMA.md` and `PROVISIONS.md` still describe the tags in prose; CI checks names, not meanings.
6. **Which of the open items in §6 is actually the blocker?** I have listed three. If the real
   blocker is the completeness methodology, the other two are displacement activity.

Distinguish what you verified against a source from what you inferred. This project has shipped one
confident inference that turned out to be a false correction of another researcher's work, and this
round withdrew two more inferences that had shipped.
