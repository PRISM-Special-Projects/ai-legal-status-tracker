# Fourth red-team prompt

**Lineage.** Round 1: `RED-TEAM-PROMPT.md`. Round 2: `RED-TEAM-PROMPT-2.md`, findings verbatim in
`RED-TEAM-2-FINDINGS.md`. Round 3 had no standalone prompt — its brief was §8 of `DIFF-REPORT.md`,
and it produced the review that caused most of the changes now under test. This is round 4.

Copy everything below the line into a fresh conversation with browsing enabled.

---

## 0. Before anything else: check you are reading the right tree

Round 3 was conducted against a repository state two commits behind the work being described,
because the author had written a report naming an unpushed commit. **Most of that review's effort
went into auditing code that had already been replaced.** It is the most expensive mistake this
project has made with a reviewer's time, and it was the author's fault, not the reviewer's.

So, first:

```
https://github.com/PRISM-Special-Projects/ai-legal-status-tracker
```

Confirm that `site/legdiff.py` and `registry/vocabulary.json` **both exist on `main`**. If either is
missing, stop and say so — you have a stale copy and nothing else in this prompt applies.

Then note the SHA of `main` and state it in your output. Every claim you test should be tested
against that SHA. `CHANGES-REPORT.md` names the commit whose code it
describes. If `main` has moved past it in a way that touches `registry/` or `site/`, treat the
report as stale and say which claims you could not attribute to a specific commit.

## 1. The artefact

A registry of US state legislation on the legal status and personhood of AI systems — 23 bills,
12 states — plus a static site generated from it. Standard library only, no runtime dependencies,
no network at build time. Nothing is deployed: there is no GitHub Pages site, deliberately, because
the project's own publication gate is unsatisfied.

Read in this order:

1. **`CHANGES-REPORT.md`** — what changed since round 3 and where the author thinks it is weakest.
2. **`site/legdiff.py`** — the differ. 531 lines. This is the artefact with real algorithmic risk.
3. **`registry/validate.py`** — validation, hash verification, path constraints.
4. **`REVISIONS.md`** — triage of all three previous rounds. **Do not re-report anything marked
   DONE without checking it; do not re-report anything marked open at all.**

Run it:

```bash
python3 registry/validate.py && python3 registry/test_regressions.py \
  && python3 site/test_diff.py && python3 site/build.py
```

## 2. The instruction that matters most this round

Previous rounds were told to attack the *rejections* hardest, because a rejection ships with an
argument that suppresses the next person to raise it. That produced results: six of nine rejections
were overturned, and round 3 killed two inferential rules in the differ.

**This round, attack the withdrawals and the measurements.**

The author withdrew two mechanisms after round 3 and kept a third, and justified each decision by
disabling the rule and re-running the corpus. That is better than arguing. It is also a rhetorical
form that can conceal three things:

- **Withdrawal as a cheap concession.** The two withdrawn rules were the two that changed almost
  nothing (one provision pair; zero counts). The one that survived is the one doing real work. Test
  whether the author conceded what was cheap and kept what was load-bearing but equally
  inferential. `_align_definitions` in `site/legdiff.py` is the survivor — is matching definitions
  by their quoted term genuinely more observable than the two rules that were dropped, or merely
  more useful?
- **The measuring instrument is five pairs.** "Changed one provision pair in the entire corpus"
  sounds decisive, but the corpus has **five** comparable version pairs, and two of them are
  companion bills sharing the identical stored text with two of the others — so the sample is
  **three independent documents**, one from Missouri and two from Tennessee. Does that support any
  conclusion about a rule's general value? Construct a case where a withdrawn rule would have
  mattered, and say whether you think it is realistic drafting or a contrivance.
- **Measurement chosen by the person being measured.** The author measured the three rules that had
  been challenged. Nothing was measured that had not already been named. What else in the differ
  would fail a disable-and-compare test if someone thought to run it?

## 3. Specific things to test

Ranked by where I would expect a real finding.

1. **Force the fallback path.** It has never run on real data — all five corpus pairs parse
   structurally — so the one code path designed to say "I could not do this reliably" is exercised
   only by synthetic fixtures, and has been for three reports running. Feed it a real bill whose
   text this corpus does not hold — note that 9 of the 23 records hold no text at all, so there is
   no shortage of candidates. Does it fall back when it should? Is the labelling honest, or does a
   fallback comparison read like a structural one once rendered?

   For the record, this was attempted with South Carolina H. 3796 and did **not** trigger the
   fallback — legislative text is self-marking, so it parsed structurally. It broke the parser in
   a different way instead, which is how the two masking bugs were found. The fallback remains
   unexercised by real data.

2. **Break the citation masking.** `CITE_RE` masks statutory citations before designators are
   sought. One false negative was already found by eye, not by a test: `subdivision (b)(1)` was
   being parsed as a provision, putting two phantom provisions into a Tennessee record. That
   suggests a class, not an instance. Sweep for others — `Art. I, § 8`, `Pub. L. 117-263`,
   `Rule 12(b)(6)`, `Chapter 1, RSMo`, `(a) through (c)`, `Sec. 2(b)`, parenthetical clauses in
   ordinary prose. Give a text that produces a phantom provision.

3. **Is `renumbered` defensible as a primary category?** It rests on exact text occurring once in
   each version, and is labelled "same text, new designator". It moves provisions out of `removed`
   and `added` — the two columns a reader treats as evidence of change. The author says demoting it
   to metadata would send Tennessee from 9/1 to 12/4, overstating change in the other direction,
   and picked one. Which error is worse for a legal researcher, and is there a third option?

4. **Check the Tennessee arithmetic against the documents.** SB 837: 13 provisions in the introduced
   text, 5 in the enacted; reported as 9 removed, 1 added, 1 modified, 3 same-text-new-designator.
   The claim is that the removals are SECTION 2's heading, its seven subdivisions, and the `(19)(B)`
   clause. **Verify that against the two primary documents.** A conservation test asserts nothing
   was dropped or double-counted; it asserts nothing about whether a pairing is right.

5. **Is the abstention real or decorative?** Ambiguity is surfaced in a collapsed `<details>`
   element; the comparison-method statement is a paragraph of prose above the diff. Build the site
   and look at a bill page. Would a reader who skims come away with a false impression of certainty?

6. **Is `registry/vocabulary.json` a single source of truth, or did it move the duplication?**
   The validator now checks that every vocabulary key is documented in `SCHEMA.md` and
   `PROVISIONS.md` and that every documented tag is accepted. But it checks **names, not meanings**.
   `PROVISIONS.md` still carries the operational test for each tag in prose. Can the name agree and
   the definition diverge?

7. **Structural-mode detection.** Round 3 proposed asking "did every recognised marker form a
   coherent hierarchy?" That was **not implemented**. What stands in its place is ≥3 markers and
   ≥50% body coverage, both admittedly arbitrary, plus a warning list. Construct a document that
   passes the threshold with an incoherent hierarchy.

8. **Documents versus code.** The author swept every document against the artefact this round and
   found stale claims in five files, including a README principle that was simply false and a
   design document claiming six corrections to the source paper when one had been retracted. The sweep
   fixed instances; **nothing prevents recurrence** — no test checks any document's claims against
   the code. Pick any numeric or factual claim in any markdown file and verify it. If you find one
   that is wrong, the class is unfixed.

9. **The negative-test pattern, applied where it is missing.** The validator now has ten cases that
   each break one thing and assert the message — writing them found two crash sites the author's own
   hardening pass had missed. The differ has no equivalent: no test proves the fallback label
   actually renders, or that a parser warning reaches the page. What else is asserted only by the
   code that produces it?

## 4. Do not spend time on these

Documented, triaged, open, and re-reporting them costs you output for no gain. They are in
`REVISIONS.md` with status.

- Field-level provenance (no claim→source link). Known; the README claim was weakened to match.
- No `METHODOLOGY.md`; scope inherited from one paper's snapshot; no discovery ledger.
- Six `secondary_source` statuses unaudited.
- The three version-only provision tags lack an ontology inclusion rule.
- `PROVISIONS.md`'s two-reader decidability claim is too strong.
- `verification.status` and `verification_status` are not reconciled.
- Terminal status without evidence is a warning, not an error.
- Endpoint-only comparison; intermediate versions are not diffed.
- Roman numerals `(i)` mis-nest; warned about, not fixed.
- No transformation manifest proving normalised text is a faithful transform of its source.

If you think one of these is misclassified as "open" when it is really a publication blocker, say
so — that is a finding. Restating it is not.

## 5. Output

Ranked, most serious first. For each:

- **Target** — file, function, or claim
- **Problem** — what is wrong, unsupported, or only apparently fixed
- **Evidence** — what you ran or read, with source URL where the claim is factual, and what it
  actually showed
- **Confidence** — `verified against source` / `strong inference` / `suspicion worth checking`
- **Fix** — the smallest change that would make it defensible

Then, separately:

1. Which of the two withdrawals you would **reverse**, if any, and which surviving mechanism you
   would withdraw instead.
2. Whether the three stated publication blockers are the right three, and whether anything now
   closed should be reopened.
3. One thing this project is doing that you would tell a similar project to copy — brief, and only
   if it is genuinely load-bearing rather than presentational.

Do not open with praise. Do not restate the reports. If a section yields nothing, write "no
findings" — that is useful information and padding is not. Distinguish throughout what you verified
from what you inferred: this project has shipped one confident inference that turned out to be a
false correction of another researcher's published work, and withdrew two more last round.
