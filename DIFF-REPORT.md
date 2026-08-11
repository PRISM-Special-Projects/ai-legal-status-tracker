# The structural differ and the hardening pass — implementation report

**Written after the code, against a pushed commit.** Verify it by checking out the SHA below and
running the three commands in §8; every number here comes from that run.

```
Repository      https://github.com/PRISM-Special-Projects/ai-legal-status-tracker
Commit          see git log — this report describes the tree containing site/legdiff.py
Differ          site/legdiff.py (531 lines, standard library only)
Differ tests    site/test_diff.py (37 tests)
Registry tests  registry/test_regressions.py (includes 10 negative validator cases)
Validator       registry/validate.py
Vocabulary      registry/vocabulary.json
CI              .github/workflows/validate.yml — two jobs: check, lint
```

## 0. A process failure that wasted a reviewer's time

The previous review was conducted against `origin/main`, which was **two commits behind** the
work the report described. `site/legdiff.py` was not public. The reviewer therefore read the
superseded inline differ and reported, correctly and in detail, that the report did not describe
HEAD and that the differ collapsed duplicate paths via `dict(A), dict(Z)`.

That was my fault, not a defect in the review. I handed over a report naming a commit I had not
pushed. The commits are pushed now, and this report is written against the pushed tree.

For the record, the reviewer's reconstruction was exact. Running the old differ from `d667623`
reproduces Tennessee **7 / 3 / 1 / 1** and Missouri **7 / 3 / 12 / 6** — the numbers they derived
by reading the code, and also the numbers the original specification had quoted as "expected".
Their method was sound; only their copy of the artefact was stale.

## 1. What the differ does

Aligns two normalised bill texts by the statutory designators they carry, and reports
`unchanged`, `modified`, `added`, `removed`, `renumbered` and `ambiguous` provisions. Where
structure cannot be identified it says so on the page and falls back to block-level comparison.

- **Identity is the full path.** `("1.2045", "2", "(1)")`, parent context included. `(1)` under
  one subsection is never aligned with `(1)` under another.
- **Nesting from a local stack**, not a fixed precedence. Tennessee runs
  `SECTION → (19) → (A)`; Missouri runs `1.2045. → 2. → (1)`.
- **Citations are masked before designators are sought** — `Section 1-3-105(a)`,
  `N.D. Cent. Code § 1-01-49(8)`, `subdivision (b)(1)`, `January 1.`, and by context
  `15 U.S.C. 9401(3)`.
- **Duplicates are never collapsed.** Nodes are a list, not a dict. A path repeating on both
  sides is reported `ambiguous`; nothing is paired positionally.
- **Section markers are line-start only**, so `SECTION` inside prose or a title is not structure.

## 2. What was withdrawn after review — the substantive change

The previous version carried three inferential rules. I measured what each was worth by disabling
it and re-running the corpus, then withdrew two. The reviewer had recommended rejecting all three;
the evidence supported them on two and not on the third.

| Rule | Measured effect | Disposition |
|---|---|---|
| **Ancestor-inherited redesignation** — a child whose text is identical moved with its redesignated parent | Changed **one** provision pair in the entire corpus | **Withdrawn.** A trivial return on the most inferential mechanism in the codebase, and it made this project's most-quoted diff read more cleanly |
| **Blank `( )` designators keyed by their defined term** | Changed **no counts at all** | **Withdrawn.** My previous report overstated its role. Replaced with a positional ordinal, which keeps provisions distinguishable for a reader without claiming the drafter's identity |
| **Definitions matched by the term they define** | Without it Missouri reports 12 modifications, including *"Emergent properties"* amended into *"Developer"* | **Kept.** Load-bearing, and its trigger is already the narrow one the reviewer said would be acceptable: same parent, all siblings definitions, terms unique on both sides |

Consequences, stated plainly:

- Tennessee SB 837 now reports **9 removed / 1 added / 1 modified / 3 same-text-new-designator**,
  where the withdrawn rule gave 8 / 0 / 1 / 4. The extra removal and addition are the recurring
  boilerplate sentence, which cannot be paired on text alone. **This overstates the change**, and
  is preferred to inferring a correspondence the documents do not state.
- A blank designator can now be paired on exact text and on nothing else. Where blanks repeat on
  both sides the result is *identity not established*.
- The secondary-key separator for repeated designators is gone entirely. Duplicates on both sides
  are always ambiguous.

`renumbered` survives as a category but now rests solely on exact text occurring once in each
version — observable, not inferred — and is labelled *same text, new designator* in the interface.
**Whether it belongs as a primary category at all is still open**: demoting it to metadata would
send Tennessee's headline back to 12 removed / 4 added, which overstates change in the opposite
direction. I kept it and renamed it; argue with that if you think the ontology should be five
categories.

## 3. What else the review produced

Every item below was a real finding against the current tree, not the stale one.

| Fix | What it was |
|---|---|
| Validator is shape-safe | `b["status"]["stage"]` after checking only top-level presence meant a malformed record produced a `KeyError` and hid every other finding. All nested access now reports a shape error instead |
| **Hashes are verified** | `source_manifest.json` and `versions[].text_sha256` were never compared to the files. They were decoration; now the validator recomputes them |
| `text_path` is constrained | Must resolve to a file beneath `registry/texts/`. A record pointing at `../../site/build.py` was previously accepted, and the differ would have parsed Python as statutory text |
| Source URLs are shape-checked | http(s) only, no network request |
| One vocabulary | `registry/vocabulary.json`. The controlled provision vocabulary was in four places — `validate.py`, `build.py` twice, and prose in `SCHEMA.md`/`PROVISIONS.md`. The validator now checks it **both ways**: every key documented, and every documented tag accepted |
| Callout deduplication | Deduplicated on `(removed, added)`, so two unrelated bills with identical counts would silently collapse into one. Now keyed on companion group, falling back to bill id |
| "No legislation identified" | Overclaimed. Now "no bills in this registry — which is not the same as none existing, since the inclusion methodology is not yet established" |
| Regression tests in CI | The suite existed but CI never ran it |
| Ruff in CI | A separate job, so the main job stays `pip`-free and keeps proving the build needs nothing. `--select F,E9` only. It immediately found an unused `os` import, an unused `cls`, a dead `_KIND_CLASS` map, and **a whole dead card-list HTML block computed and thrown away** |
| Roman-numeral warning | `(i)` is both the ninth letter and roman one; the stack treats it as a letter sibling. It now says so rather than hiding it |

## 4. Tests

37 differ tests, and 10 negative validator cases.

- **Adversarial fixtures the reviewer specified**: U.S.C. citations, `SECTION` in prose, decimals
  opening a sentence, duplicate identical provisions under one parent, duplicates on both sides,
  roman numerals, `subdivision (b)(1)` cross-references.
- **Six mutation properties**: editing one provision leaves others unchanged; appending does not
  cascade; removal does not alter another body; duplicating a label never reduces the parsed node
  count; punctuation-only change does not alter structural identity; renumbering leaves unrelated
  provisions alone.
- **Conservation**: `|A| + |Z| == 2·paired + removed + added + ambiguous`, anchored on `parse()`
  node counts so a parser that collapsed duplicates could not satisfy it trivially.
- **Negative validator cases** break one thing each in a throwaway copy of the registry and assert
  the message: non-dict `status`, non-list `watch_dates`, non-list `versions`, a
  `javascript:` URL, an escaping `text_path`, a wrong hash, an undocumented vocabulary entry, a
  vocabulary entry removed while still in use. Writing these found two crash sites in the audit
  summary that my own hardening pass had missed.

Two tests that encoded the withdrawn rules were rewritten to assert the opposite, **and shown
failing before the code changed**.

## 5. Current corpus output

| Pair | provisions earlier / later | unchanged | modified | same text, new designator | removed | added | ambiguous |
|---|---|---|---|---|---|---|---|
| MO HB 1462 → HCS 1746 | 26 / 22 | 7 | 11 | 0 | 8 | 4 | 0 |
| TN SB 837 introduced → Pub. Ch. 781 | 13 / 5 | 0 | 1 | 3 | 9 | 1 | 0 |
| TN SB 1493 introduced → Pub. Ch. 1066 | 39 / 10 | 0 | 1 | 0 | 38 | 9 | 0 |

Tennessee SB 837 is checkable by hand in about ten minutes: 13 provisions in, 5 out; the 9
removals are SECTION 2's heading, its seven subdivisions, and the `(19)(B)` clause whose identical
text recurs. **Please check whether those are the right nine.** Conservation proves nothing was
dropped or double-counted; it proves nothing about whether a pairing is right.

## 6. Where this is weakest now

- **The fallback path has never run on real data.** All five corpus pairs parse structurally, so
  the one code path designed to say "I could not do this reliably" exists only under synthetic
  fixtures. Unchanged since the last report, and still the thing I would attack first.
- **`renumbered` as a primary category** — see §2. Genuinely unresolved.
- **Arbitrary constants**: structural mode requires ≥3 markers and ≥50% body coverage. Both are
  guesses. The reviewer's better test — "did every recognised marker form a coherent hierarchy?" —
  is **not implemented**; the coverage threshold and the warning list are what stand in for it.
- **`_OPENERS = ".;:)—"`** decides whether a parenthesis opens a provision. Including `)` is what
  let `subdivision (b)(1)` through before citations were masked. There may be more of that class.
- **Endpoint comparison.** The differ still compares `versions[0]` to `versions[-1]`. The
  intermediate version is labelled as the mechanism and is not itself diffed. The reviewer's
  minimum — say explicitly that this is an endpoint comparison — is **not yet done**.
- **Roman numerals** mis-nest where a bill uses both `(i)` as roman and as the ninth letter. Now
  warned about, not fixed.
- **No second coder** on the diff output. I read Missouri and Tennessee and judged them right.

## 7. Not in scope, still open

From the second review's eighteen findings: **2, 3, 5, 9, 10, 12, 15, 17, 18 remain open** —
notably per-field provenance (R3), the claims layer (R4), the ontology inclusion rule for the
three new provision tags, `PROVISIONS.md`'s two-reader claim, Washington's rule provenance,
inter-coder reliability for the 19 version-provision assignments, and the discovery ledger.
Triage is in `REVISIONS.md`; the review is verbatim in `RED-TEAM-2-FINDINGS.md`.

Publication blockers, unchanged: the status audit for six `secondary_source` records, a written
`METHODOLOGY.md`, and verification/provenance semantics — the README still says "every claim cites
something", which outruns a data model with no field-level source links.

## 8. What would be most useful back

```bash
python3 registry/validate.py && python3 registry/test_regressions.py \
  && python3 site/test_diff.py && python3 site/build.py
```

1. **Are the nine Tennessee removals the right nine?** Check against the primary documents.
2. **Should `renumbered` be demoted to metadata?** It moves provisions out of the two columns a
   reader treats as evidence of change. Both answers overstate something; say which is worse.
3. **What breaks the parser?** Give a text, not a hypothesis. The fixtures were written by the
   person who wrote the parser and test the failures I could imagine.
4. **Is the abstention real?** Ambiguity is surfaced in a collapsed `<details>` and the
   comparison-method statement is prose most readers skip. Is the honesty apparatus load-bearing
   or decorative?
5. **Did withdrawing the two rules go far enough, or too far?** Tennessee now overstates the
   change by two provisions. That was a deliberate choice for a conservative false negative.

Distinguish what you verified against a source from what you inferred. And check the SHA — if the
tree you are reading has no `site/legdiff.py`, stop and say so, because you are reading a stale
copy and that has already happened once.
