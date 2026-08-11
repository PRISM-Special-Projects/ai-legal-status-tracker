# Fifth red-team prompt — the whole project

You are reviewing a pre-publication registry and static site: **US state legislation on the legal
status and personhood of AI systems**, 23 bills across 12 states. Read `DESIGN-REPORT.md` first for
what the thing is and why it is built the way it is. This prompt tells you what to attack.

Four previous rounds have been about the architecture. This round is about the whole project,
including the parts that have never been reviewed by anyone.

## 0. Before anything else: check you are reading the right tree

```
Repository   https://github.com/PRISM-Special-Projects/ai-legal-status-tracker  (public)
Commit       e086a51 — every claim in DESIGN-REPORT.md describes this commit
```

A previous round was wasted because a report named a commit that had not been pushed, and the
reviewer audited a superseded differ. So verify before you invest:

```bash
git log --oneline -3          # e086a51 should be at or near the top
ls site/geo/                  # states-albers-10m.json, LICENSE-us-atlas
grep -c spanel site/build.py  # non-zero: the state panel exists
```

If the tree lacks `site/geo/` or `audit/`, you are reading a stale copy — say so and stop rather
than reviewing something we have already replaced.

Everything must pass before you start, so that anything you break is your finding and not a
pre-existing failure:

```bash
python3 registry/validate.py && python3 registry/test_regressions.py \
  && python3 site/test_diff.py && python3 audit/test_audit.py && python3 site/build.py
```

The site is not deployed anywhere, deliberately: the project's own publication gate is not
satisfied. Serve `site/dist/` locally to review the presentation.

## 1. The instruction that matters most

**Attack the rejections harder than the implementations.** Where we decided *not* to do something,
that decision ships with an argument, and a wrong argument suppresses the next person who raises the
question. Round 2 overturned six of nine rejections, almost always because the rejection rested on
an alternative that had never been built. The most recent instance: the map was rejected for two
months on an argument that was sound about colour ramps and silently extended to geography itself.
`DESIGN-REPORT.md` §2, §6, §7 and §12 are where the live rejections are.

Second instruction: **distinguish what you verified against a source from what you inferred.** This
project has shipped one confident inference that turned out to be a false correction of another
researcher's published work, and has withdrawn two more inferences from the differ. If you report
something as established, say what you checked it against.

## 2. Specific things to test

### A. The data, which has never had an independent read

Three rounds have reviewed code. Every field in `registry/bills.json` was compiled with AI
assistance and checked by the party that compiled it.

1. **Run the blind audit instrument** — `audit/PROTOCOL.md`, `audit/AUDITOR-BRIEF.md`. Sheets for the
   six `secondary_source` records are in `audit/sheets/`. **Do not read `registry/bills.json` for a
   record before you fill in its sheet.** Fill them from the sources, then run
   `python3 audit/check_sheet.py --all`. This is publication blocker one, and an honest
   `NOT STATED` is more valuable than a confirmation.
2. **Is the blind design real or theatre?** The heading prints the recorded `bill_number` and the
   status question prints the whole controlled vocabulary. Both are argued for in `PROTOCOL.md`.
   Are there other leaks, and does the instrument in fact produce reconstruction rather than
   confirmation?
3. **Missouri SB 859 and SB 1012 both record an effective date of 2026-08-28**, which is Missouri's
   default. Is either stated in the text, or were they computed? The audit conventions forbid
   computing one; the records predate that rule.
4. **Attack a record we are confident about.** Pick any of the seven enacted laws and check
   `codified_at` against the code itself, not the bill. Two of seven are flagged as bill-sourced
   rather than code-verified. One wrong citation has already been found this way.

### B. The five claimed corrections to the source paper

The registry was seeded from Smith, Caviola & Alexander (2026), SSRN 6829981. Five corrections to
that paper stand; a sixth was claimed and retracted. Two of the authors are colleagues of the
project lead, which raises rather than lowers the bar.

`VERIFICATION.md` §"Corrections to the paper" lists them. **Try to retract a second one.** For each,
ask: is the paper actually wrong, or does it use a defensible different convention, or is the
disagreement about a snapshot date? A correction that survives your attempt is worth more than the
four that were never tested.

### C. The differ

`site/legdiff.py`, 548 lines, standard library. `DIFF-REPORT.md` describes it — note that the
report was written at an earlier commit and gives the file as 531 lines, which is itself an
instance of §E.2.

1. **Break the parser with a real document.** Not a hypothesis — a bill text from a state the corpus
   does not contain. The fixtures were written by the person who wrote the parser and test only the
   failures they could imagine. Two provision-losing bugs were found this way by an out-of-corpus
   South Carolina bill.
2. **The fallback path has never run on real data.** The one code path designed to say "I could not
   do this reliably" is exercised only by synthetic fixtures — true for four reports now. Find a real
   text that triggers it, or show why none can.
3. **Are Tennessee SB 837's nine removals the right nine?** Hand-checkable against the two documents
   in about ten minutes: 13 provisions in, 5 out. A conservation test proves nothing was dropped or
   double-counted; it proves nothing about whether any pairing is correct.
4. **`renumbered` as a primary category** is unresolved, not deferred. Keeping it overstates change
   one way, demoting it overstates the other. Which is less wrong, and why?
5. **Endpoint comparison.** Only the first and last versions are compared; intermediate versions are
   labelled and never diffed. Is that defensible for Missouri SB 1012, which has a second senate
   committee substitute?

### D. The presentation, and the map in particular

New this round, never reviewed.

1. **Does the map imply a ranking anyway?** The design bets that a numeral cannot be misread as
   intensity the way a shade can, so `MO 6` beside `WA 1` is safe. Test the bet. If it fails, the
   fix is not a smaller number.
2. **Accessibility of the twelve interactive states.** They are SVG `<g role="button" tabindex="0">`
   with hand-wired Enter and Space. Attribute checks pass, but in one accessibility-tree read they
   did not surface as buttons while the HTML list buttons did. Test with a real screen reader if you
   can. If the SVG controls are not exposed, is the correct fix to make the shapes presentational and
   promote the list, rather than to patch the roles?
3. **`family` A / B / C / other is a filter, a matrix column and a CSV field, and is defined
   nowhere** — not on the method page, not in `SCHEMA.md` beyond the enum. It is inherited from the
   paper's taxonomy. How bad is that, and is the right fix to define it or to remove it from the
   interface until it is defined?
4. **Is the absence caveat doing its job?** "No bills in this registry — which is not the same as
   none existing" appears once, under the map. A screenshot travels without it. What would a
   journalist conclude from the image alone?
5. **The state panel** lists a state's bills on click. Does it duplicate the matrix badly, or does it
   answer the right question? Would a policymaker get what they need from the landing page?

### E. Documentation against artefact

1. **Find a claim in any document that the code does not support.** `DESIGN-REPORT.md` is the primary
   target because it is new and was written by the builder. Its figures were checked
   programmatically against the registry, so look for the claims that *cannot* be checked that way —
   the reasoning, the characterisations, the "why".
2. **Document-code consistency is a convention, not a mechanism.** Reports name the commit they
   describe and nothing enforces it. Propose a mechanism, or argue that the convention is adequate.
3. **`MAP-SPEC.md` §10 and §11 record every departure of the built map from its own spec.** Are they
   complete? An undeclared departure is a worse finding than any of the declared ones.

### F. The publication gate

Three blockers are listed: the six-record status audit, the missing `METHODOLOGY.md`, and
claim-level provenance. **Which is the real blocker?** If it is the completeness methodology — the
registry's scope is still inherited from one paper's May 2026 snapshot — then the other two are
displacement activity, and we would rather know that now.

Related: is a 23-bill registry seeded from one appendix publishable at all without an independent
inclusion rule? What would you require before you would cite it?

## 3. Do not spend time on these

- Style, formatting, naming, type annotations, or the absence of a framework. The
  no-dependency, no-network property is deliberate and is not up for review.
- Suggesting a JavaScript charting library, a database, a CSS framework, or a client-side map
  renderer. All are excluded by design; the constraint is not the interesting part.
- The tile grid, which no longer exists.
- Asking for tests to be added in the abstract. Name the bug the test would have caught.
- The `renumbered` naming. Its *status as a category* is in scope; its label is not.

## 4. What to hand back

For each finding: what you checked, what you found, how you verified it, and how confident you are.
Order by severity, and put anything that would require a public correction first.

Separate these three explicitly, because they are not the same:

1. **The registry is wrong** — a fact does not match its source.
2. **The registry is unsourced** — the fact may be right, but nothing cited establishes it.
3. **The presentation misleads** — the data is right and a reader will still draw a false conclusion.

And state plainly which of our rejections you think are wrong. That is the part we are least able to
check ourselves.
