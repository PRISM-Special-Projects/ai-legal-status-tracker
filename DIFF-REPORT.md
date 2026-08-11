# The structural differ — implementation report and review brief

**Date:** 2026-08-10 · **Commit:** `75cf95e` · **Repo:** https://github.com/PRISM-Special-Projects/ai-legal-status-tracker

R1 was overturned and the differ rebuilt. This records what was built, what I decided that
nobody asked me to decide, and where I think it is weakest. Everything below §3 is written to be
attacked.

Written by the party that wrote the code. Nothing here has been independently checked.

Copy from the line below into a fresh conversation with browsing enabled.

---

## 1. What was asked

Replace a punctuation-based text differ with a deterministic section-aware one. The specification
set eleven acceptance criteria: no punctuation segmentation as the primary mechanism; provisions
have structural identities including parent context; reused labels cannot silently overwrite one
another; `modified` is first-class; ambiguity surfaced rather than guessed; fallback explicitly
labelled; statutory citations never become structural nodes; synthetic adversarial tests exist;
Missouri and Tennessee corpus fixtures pass; unrelated site functions intact; documentation
honest about limitations.

## 2. What was built

`site/legdiff.py` (553 lines, standard library only). `site/build.py` consumes it and renders.
`site/test_diff.py` holds 24 tests.

- **Identity is the full path.** `("1.2045", "2", "(1)")`, parent context included. `(1)` under
  subsection 2 is never aligned with `(1)` under subsection 3.
- **Nesting from a local stack**, not a fixed precedence. A designator type already on the stack
  unwinds to that level (a sibling); a new type pushes (a child). Tennessee runs
  `SECTION → (19) → (A)`, Missouri runs `1.2045. → 2. → (1)`, and neither is privileged.
- **Citations masked before designators are sought.** `Section 1-3-105(a)`,
  `N.D. Cent. Code § 1-01-49(8)`, `subdivision (b)(1)`, `January 1.` — all masked with a filler
  that preserves offsets.
- **Duplicate paths are kept as a list.** Where a path repeats, a secondary key is tried; failing
  that the provisions are reported `ambiguous` and not compared.
- **Categories:** `unchanged`, `added`, `removed`, `modified`, `renumbered`, `ambiguous`.
- **`DiffResult`** carries counts and `parser_warnings`, so tests inspect the result rather than
  scraping HTML. The site shows the warnings in a collapsed `<details>`.
- **Fallback** is block-level, labelled on the page, and claims no block is the same provision
  amended.

### What the parser found

Masking cross-references exposed a live false positive the old differ had hidden. Tennessee
HB 1455's `risks identified under subdivision (b)(1)` was being parsed as a provision, putting
two phantom provisions in the enacted text (`total` fell 50 → 48). Now a regression test.

## 3. Decisions nobody asked me to make — **attack these first**

The specification asked for path-based alignment. I added two further passes because path-only
alignment produced output I judged misleading. **Both are my inventions, and both make the
project's headline finding more legible, which is precisely the pattern the second review
condemned elsewhere in this project** (the three new provision tags: ontology adjusted until a
favoured finding became visible). Treat them as suspect on those grounds alone.

### D1 — Redesignation as a category, with two routes in

Path identity alone reports a renumbering as a removal plus an addition. Tennessee SB 837 read
**9 removed, 3 added, 0 unchanged** under the specified design. It now reads **8 removed,
0 added, 1 modified, 4 redesignated**, and the deleted fetal-personhood section is unmistakable.

Two routes qualify, both requiring exact normalised text:

1. text occurring exactly once in each version (`diff_nodes`, the text-identity pass);
2. **a provision whose ancestor has already been shown to have moved** (`diff_nodes`, the
   "inherit an established redesignation" block).

Route 2 is the one to attack. It exists because boilerplate recurs — *"Does not include
artificial intelligence, a computer algorithm, a software program, computer hardware, or any type
of machine"* appears three times in Tennessee SB 837 as introduced and once in the enacted text,
so route 1 refuses to pair it. Without route 2, `(19)(B)` and `(20)(B)` rendered as the same
sentence in red and then again in green. Route 2 pairs them by inheriting the already-established
`(19) → (20)` move.

Questions worth pressing: is "the parent moved and my text is identical, so I moved with it"
sound, or does it smuggle in a transitive assumption? Route 2 fires only when the destination
path is unique among unmatched additions — is that sufficient? Would a disinterested implementer
have written route 2, or accepted the noisier honest output? And note the direction of the
benefit: route 2 makes the diff the project most wants to show read more cleanly.

### D2 — Definitions aligned by the term they define

Where every sibling under a parent opens with a quoted term and the terms are unique on both
sides, alignment uses the term rather than the designator (`_align_definitions`). Without it,
Missouri's re-alphabetised definitions reported *"Emergent properties"* as **amended into**
*"Developer"* — juxtaposing two unrelated definitions under one label and calling it a
modification.

Questions: is "all siblings open with a quoted term" a decidable trigger, or does it fire on
non-definitional lists? Is the defined term genuinely the drafting identity, or is that a
convenient rationalisation? What happens to a definition that is renamed while keeping its
substance — does this pass hide it?

### D3 — Blank designators keyed by their defined term

Tennessee writes `( ) "Human being" means…` for subdivisions the code reviser will number later.
All such nodes collapse onto one path, and their `(A)`/`(B)` children then collapse too. I key a
blank designator by its leading quoted term, so `("Human being")` becomes the path element.

This is inference presented as structure. The document does not say these are different
provisions; I decided the defined term supplies the identity that the drafter left blank. If that
is wrong, the honest output was three `ambiguous` provisions, not three identified ones.

## 4. Deviations from the specification — check each

| Spec | What I did | Why |
|---|---|---|
| `python -m pytest` | `unittest`, run as `python3 site/test_diff.py` | pytest is not installed and the project is deliberately dependency-free. Tests still run under pytest if present. |
| "Missouri: 7 removed, 3 added, 12 modified, 6 unchanged" | Recorded **8 / 4 / 11 / 0 renumbered / 7 unchanged** | The spec's numbers came from the superseded differ. **I changed the fixture to match my code**, which is the move that always deserves scrutiny — see §5. |
| "Tennessee HB 849: 7 removed, 3 added, 1 modified, 1 unchanged" | Recorded **8 / 0 / 1 / 4 renumbered / 0 unchanged** | Same. |
| "the fallback should be the existing text differ" | Block-level (paragraph) matching | The existing differ *was* the punctuation splitter being removed. Reinstating it as the fallback would have kept the defect on the same pages. |
| `LegislativeNode` dataclass as sketched | Implemented as given, with `confidence` ∈ {`labelled`, `blank_label`} | — |
| Categories `added/removed/modified/unchanged/ambiguous` | Added a sixth, `renumbered` | See D1. |

## 5. How to check the corpus numbers without trusting me

There is one internal check and it is not a correctness proof. Every provision on both sides is
accounted for exactly once — a paired slot consumes one from each side, an unpaired one consumes
one — asserted by `test_every_provision_is_accounted_for_exactly_once`:

| Pair | provisions earlier / later | unchanged | modified | renumbered | removed | added |
|---|---|---|---|---|---|---|
| MO HB 1462 → HCS 1746 | 26 / 22 | 7 | 11 | 0 | 8 | 4 |
| TN SB 837 introduced → Pub. Ch. 781 | 13 / 5 | 0 | 1 | 4 | 8 | 0 |
| TN SB 1493 introduced → Pub. Ch. 1066 | 39 / 10 | 0 | 1 | 0 | 38 | 9 |

For Tennessee SB 837 the accounting is checkable by hand against the two documents: 13 provisions
in, 5 out; the 5 outputs are 1 modified + 4 redesignated; the 8 removals are SECTION 2's heading
and its seven subdivisions. **Do that by hand and tell me if the 8 removals are the right 8.**
Conservation proves nothing was dropped or double-counted. It does not prove any pairing is right.

## 6. Where I think this is weakest

- **Route 2 of D1**, for the reasons in §3. It is the change most likely to be motivated
  reasoning, and it improves the project's most-quoted diff.
- **The fallback path has never run on real data.** All five corpus pairs parse structurally, so
  the labelled-fallback rendering exists only under synthetic fixtures. The one path designed to
  say "I could not do this reliably" is the one never exercised in production.
- **Arbitrary constants.** Structural mode requires ≥3 markers and ≥50% body coverage. Both
  numbers are guesses. Nothing establishes that 50% is where a parse stops being trustworthy.
- **`_OPENERS = ".;:)—"`** decides whether a parenthesis opens a provision. Including `)` is what
  let `subdivision (b)(1)` through until citations were masked. There may be more of that class.
- **Roman numerals are treated as lowercase letters.** `(i)`, `(ii)` work in this corpus only
  because they never collide with `(i)` as the ninth letter designator. A bill with both breaks it.
- **The depth warning is noise on the one text that triggers it.** Tennessee HB 1455 warns three
  times about designator types at multiple depths, and its parse is nevertheless correct. So the
  warning does not indicate an error — and a real mis-nesting may not warn at all.
- **No second coder.** I read the Missouri and Tennessee diffs and judged them right. That is one
  person checking their own output, which is the standing criticism of this whole project.
- **`_secondary`'s fallback key** is the first six words of a provision. Where duplicates differ
  only later in the text, it will call them ambiguous — that is safe — but the key is arbitrary.

## 7. What is not in scope this round

The second review produced eighteen findings; this closes one (R1) and a pre-existing
array-position bug (its finding 16). **Findings 2–18 remain open** and are triaged in
`REVISIONS.md`, with the review stored verbatim in `RED-TEAM-2-FINDINGS.md`. Do not re-report
them. Publication blockers are unchanged: the status audit for six `secondary_source` records, a
written `METHODOLOGY.md`, and verification/provenance semantics.

## 8. What would be most useful back

Read `site/legdiff.py` in full — it is the artefact. Then:

1. **Should D1 route 2, D2 or D3 be reverted?** Rank them. For each, say whether the honest
   alternative (noisier output, or `ambiguous`) is better than the inference.
2. **Is any pairing in the three corpus pairs wrong?** Check against the primary documents. The
   Tennessee removals are hand-checkable in ten minutes.
3. **What breaks the parser?** Give a text, not a hypothesis. Adversarial fixtures are cheap to
   add and the existing set was written by the person who wrote the parser, so it tests the
   failures I could imagine.
4. **Is `renumbered` a legitimate category or a flattering one?** It moves provisions out of
   "removed" and "added" — the two columns a reader treats as evidence of change.
5. Whether the honesty apparatus is load-bearing or decorative: parser warnings are in a
   collapsed `<details>`, and the comparison-method statement is prose most readers will skip.

Distinguish what you verified against a source from what you inferred. This project has already
shipped one confident inference that turned out to be a false correction of someone else's work.

Commands, no dependencies required:

```bash
python3 site/test_diff.py && python3 registry/validate.py && python3 site/build.py
```
