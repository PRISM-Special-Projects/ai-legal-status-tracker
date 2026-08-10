# Second red-team prompt — reviewing the response to the first

Copy everything below the line into a fresh conversation with browsing enabled.

---

You previously red-teamed a research artefact and found substantive problems. They have now
been worked through. **Your job this round is to test whether the response actually fixed the
underlying failure modes, or merely the specific instances you named.**

## The artefact

**https://github.com/PRISM-Special-Projects/ai-legal-status-tracker** (public)

Start with **`IMPLEMENTATION-REPORT.md`**. It lists what was implemented, what was rejected
with reasons, what still blocks publication, and a self-assessment of where the work is
weakest. `VERIFICATION.md` records the data-level corrections, including a retraction.

## The instruction that matters most

**Attack the rejections harder than the implementations.**

Nine proposals were declined, each with a confident-sounding rationale. A wrong implementation
is visible and gets fixed. **A wrong rejection is worse: it comes with an argument that will
suppress the next person who raises the same concern.** If any of R1–R9 in the report is
reasoning backwards from "we did not want to build this", that is the most valuable thing you
can find.

Test each rejection on its merits, not on whether the argument sounds coherent. Specifically:

- **R1 (spaCy declined in favour of section-aware parsing).** The alternative *has not been
  built*. So the current state is a brittle regex differ plus a promise. Is "the better fix is
  X" a legitimate reason to decline Y when X does not exist? Read `render_diff` in
  `site/build.py` and judge whether the shipped code is defensible today.
- **R2 (declined to compute status from session rules).** The stated reason is that deriving
  status from a calendar caused the original Washington error. Is that the same thing, or is
  it a rhetorically convenient equivalence? A flag-only design leaves stale statuses in place
  when nobody reviews.
- **R3 (declined per-field provenance wrappers).** Justified as premature at 23 records. Is
  retrofitting at 200 actually harder, and does that make the decision wrong now?
- **R4 (declined a claims layer).** The stated substitute — a `notes`/`analysis` split — is
  also unbuilt. Two rejections now rest on unbuilt alternatives. Is that a pattern?
- **R8 (declined markdown-parsed vocabulary).** The report admits the vocabulary still lives
  in two places. Is the mitigation adequate or is this the same drift, deferred?

## Then verify the fixes

**Do not take the report's word for anything.** For each claimed fix, check the artefact:

1. **Utah.** Does `codified_at` now cite 63G-32-101/102? Verify against the Utah Code itself.
2. **Washington.** Is the record now `failed`, with an evidence line naming sine die? Is the
   retraction recorded honestly, or softened?
3. **Verification dimensionality.** Does `verification.operative_text` reflect what was
   actually checked? Sample three records and test the claim against their notes and sources.
4. **The evaluative-language purge.** This is the one most likely to be cosmetic. The words
   were removed. **Read the notes and decide whether they still argue a position in neutral
   vocabulary.** Removing "softening" while retaining a sentence structure that frames one
   version as a retreat from another is not neutrality.
5. **Version-level provisions.** 19 assignments were made in one pass, by judgement, without a
   second coder. Re-derive several from `registry/texts/` against `PROVISIONS.md` and report
   disagreements. This is inter-coder reliability testing and the project has none.

## Attack the new abstractions

Fixes create new surfaces. Assess whether these introduce problems of their own:

- **The three new provision tags** — `defines_human_to_include_unborn`,
  `creates_criminal_offence`, `creates_private_right_of_action`. The report flags these as its
  own weakest point: they were added after tagging revealed a gap, which is legitimate, but is
  indistinguishable from inventing categories to make a favoured finding legible. The first
  applies to exactly one bill's introduced text — the diff the project most wants to show. Is
  this motivated reasoning? Would a disinterested coder have created these tags?
- **`status.basis`.** Does it improve honesty, or manufacture an impression of rigour that the
  six `secondary_source` records do not support?
- **The audit summary.** It replaced "ERRORS (0)" because that read as stronger than the
  evidence. Does the new output overclaim in some new way?
- **`PROVISIONS.md`.** Are the operational tests actually decidable, or do any require reading
  legislative intent? Try applying them blind to a text you have not seen classified.
- **`session_rules.json`.** Three states documented, twelve in the registry. Does a partial
  rules registry create a false impression of systematic coverage?

## Structural questions

- The project declined to build several things on the grounds that a better alternative exists.
  **How many of those alternatives are actually built?** If the answer is "few", the pattern
  is deferral dressed as architecture.
- Regression tests were written by the same party that wrote the bugs. Do they test the
  underlying failure mode, or only the specific instance? Would `test_regressions.py` catch a
  *different* wrong statutory citation, or only a wrong Utah one?
- Is anything in the report's self-assessment (§5) understated?

## Output

Ranked, most serious first. For each:

- **Target** — which rejection, fix, or new abstraction
- **Problem** — what is wrong, unsupported, or merely deferred
- **Evidence** — what you checked, with source URL, and what it actually shows
- **Confidence** — `verified against source` / `strong inference` / `suspicion worth checking`
- **Fix** — the smallest change that would make it defensible

Then, separately:

1. Which of the nine rejections you would **overturn**, in priority order.
2. Whether the two stated publication blockers are the right two, or whether something else
   should be blocking.
3. Anything the report's self-assessment understates.

Do not open with praise. Do not restate the report. If a section yields nothing, say "no
findings". Distinguish what you verified from what you inferred — the project has already
shipped one confident inference that turned out to be a false correction of someone else's
work, and that is the failure mode under test.
