# Second red-team review — verbatim findings

**Received 2026-08-10 23:16 BST**, in response to `RED-TEAM-PROMPT-2.md`. Reviewer: GPT with
browsing. Recovered from the session transcript and stored here so the worklist is durable and
citable rather than living in a chat log.

Recovery lost the original markdown formatting; headings and label emphasis were reconstructed
mechanically. **No wording has been changed.** Where the reviewer cited a URL it is preserved
inline.

Triage — what has been actioned since — is in `REVISIONS.md`, not here. This file stays as
received.

---

The second pass finds that the implementation report is more honest than the underlying implementation is robust. The biggest pattern is exactly the one the prompt asked to test: several rejected alternatives have been replaced by abstractions that are either incomplete or not actually enforced, while the report sometimes treats the existence of an abstraction as if it solved the failure mode.
## 1. R1 should be overturned: the shipped diff is knowingly indefensible
**Target** — R1, regex differ
**Problem**
The report explicitly concedes:
“section-aware parsing is still unbuilt — so today we have neither.”
That is not a defensible reason to reject the proposed spaCy remedy for the current release.
More importantly, inspection of `site/build.py` shows the shipped differ is substantially weaker than the report's description suggests. `_sents()` does:

```python
re.split(r"(?<=[.;:])\s+(?=[A-Z(0-9\"])")

```

and `render_diff()` compares the resulting pseudo-sentences using `difflib.SequenceMatcher`.
It also strips everything through an `ENACT_RE` match before doing so. There is no statutory section parser in the current code.
That means the current "version diff" is not a section-aware legislative diff. It is a heuristic punctuation diff.
A particularly important failure is that the regex does not split ordinary full stops at all. A sequence such as:
`SECTION 1. ... SECTION 2. ...`
can remain one comparison unit unless another `;` or `:` triggers a split.
So the report's proposed dichotomy—
spaCy = wrong unit; section parser = right unit
—is technically reasonable as a future design preference, but it does not justify shipping the existing implementation.
**Evidence**
The implementation itself shows the regex and the `SequenceMatcher` approach.
**Confidence** — verified against source
**Fix**
Two defensible options:

## 1. Build the section-aware differ now, as the report proposes; or
2. temporarily remove/label the current diffs as experimental textual similarity, rather than presenting them as the project's differentiating legislative comparison.

I would not ship the current implementation as a substantive legislative diff.
## 2. R2 should be overturned in its present form: the project has created a review aid, not a stale-status safeguard
**Target** — R2, rejection of computed status
**Problem**
The report says:
“The rules registry exists so a human can see when a non-terminal status has become implausible.”
But nothing forces that human review.
Worse, `session_rules.json` explicitly says:
“Status must never be COMPUTED from these rules.”
and the validator does not compare a bill's status against the rules.
So the architecture is:

```text
legislative event
       ↓
human enters status
       ↓
rules registry sits beside it
       ↓
human may notice inconsistency

```

That is precisely the stale-data failure mode R2 was supposed to address.
The Washington correction illustrates the problem. The official Washington page still shows:
“By resolution, reintroduced and retained in present status”
and then no terminal action. ([Washington State Legislative Information](https://app.leg.wa.gov/billsummary?BillNumber=2029&Initiative=false&Year=2025&utm_source=chatgpt.com))
The legislature separately adjourned sine die on March 12, 2026.
Thus “failed” is a derived procedural conclusion, not an explicit legislative action. The registry is right to distinguish that. But refusing to compute or at least mechanically flag the consequence leaves the status manually maintained.
There is also a provenance problem: the WA rule's `source` is the bill summary page, which documents the bill history but does not itself state the expiration rule.
**Confidence** — verified against source / strong inference
**Fix**
Don't use the simplistic proposed:

```python
if date > session_end:
    failed

```

Instead implement:

```text
observed legislative events
        +
state session rule
        ↓
derived procedural status

```

and retain:

```text
status.type = derived
status.basis = session_rule
status.rule_source = ...

```

A human should be able to override the derived result only with a cited contradictory event.
That is not the same failure as the original Washington mistake.
## 3. R3 should be overturned: `verification` is not actually provenance
**Target** — R3, rejection of per-field provenance
**Problem**
The report says the existing per-dimension object makes wrappers premature.
It doesn't.
The current object looks like:

```json
"verification": {
  "status": "verified_primary",
  "operative_text": "read_in_full",
  "sponsors": "established",
  "codified_at_source": "code",
  "versions_with_text": 1,
  "last_verified": "2026-08-10"
}

```

That records verification state, not provenance.
It does not tell the reader:
Which source established the sponsor?
Which code page established `codified_at`?
Which document was read for the operative text?
The repository's `sources.primary` array is just a bag of URLs. There is no field-level relationship between a claim and a source.
That directly fails the README's stronger assertion:
“Every claim cites something.”
The README also calls this:
“per-dimension provenance”
but the data model doesn't actually contain per-dimension source identifiers.
This is not a size argument. At 23 records, now is the easiest point to introduce the model.
**Confidence** — verified against source
**Fix**
Don't wrap literally every scalar. Use a compact provenance structure:

```json
"verification": {
  "status": {
    "level": "primary",
    "source": "source-id"
  },
  "operative_text": {
    "level": "full",
    "source": "source-id"
  },
  "sponsors": {
    "level": "primary",
    "source": "source-id"
  },
  "codification": {
    "level": "code",
    "source": "source-id"
  }
}

```

The source manifest can then contain the actual URLs.
## 4. The verification abstraction contains an internal contradiction that the validator does not catch
**Target** — dimensional verification
**Problem**
There are now three verification concepts:

```text
verification_status
verification.status
verification.operative_text

```

But `validate.py` validates only the latter two partially.
It validates:

```python
v.get("operative_text")
v.get("sponsors")

```

but never validates:

```python
v.get("status")

```

and never checks it against top-level `verification_status`.
Therefore this malformed state can pass:

```json
"verification_status": "verified_primary",

"verification": {
    "status": "seeded_unverified",
    "operative_text": "not_read"
}

```

Nothing in the validator establishes that those fields agree.
This is exactly the kind of abstraction drift the project is supposed to prevent.
**Confidence** — verified against source
**Fix**
Remove the duplicated global status, or derive it.
I'd make `verification` authoritative and have any aggregate status computed from it.
## 5. R4 should be overturned: “notes → analysis” is not implemented, and the current `notes` field remains epistemically overloaded
**Target** — R4, claims-layer rejection
**Problem**
The report's rationale is:
“the planned `notes` → `analysis` split achieves most of it more cheaply.”
But there is no `METHODOLOGY.md`, no `analysis` field, and no claims layer. The README explicitly lists:
`METHODOLOGY.md ... TODO`
So R4 is currently justified by an alternative that doesn't exist.
More importantly, a claims layer would solve something a simple notes/analysis split does not:

```text
fact
inference
interpretation

```

are epistemic categories, whereas:

```text
notes
analysis

```

are merely locations.
Moving an unsupported inference from `notes` to `analysis` doesn't make it more auditable.
**Confidence** — verified against source
**Fix**
Either implement the claims layer, or define an actual schema for `analysis` that requires:

```text
claim type
claim text
source(s)
attribution

```

At minimum, don't claim the problem has been architecturally solved.
## 6. R8 should be overturned: the vocabulary still has two sources of truth
**Target** — R8, controlled vocabulary
**Problem**
This is almost a textbook case of deferral.
The report says:
“the vocabulary still lives in two places.”
Those places are visibly:

* `PROVISIONS.md`
* the `PROV={...}` set inside `validate.py`.

The mitigation is one-directional:
every validator tag must be documented.
But that does not catch the reverse failure:
a documented tag exists but the validator doesn't accept it.
Nor does it prevent the two definitions from diverging semantically.
And parsing Markdown is not the only alternative. A tiny:

```json
registry/provisions.json

```

would eliminate the problem cleanly while allowing `PROVISIONS.md` to remain human-readable documentation.
**Confidence** — verified against source
**Fix**
Use:

```text
provisions.json
      ↓
validator
      ↓
site

```

and generate/check `PROVISIONS.md` from it.
This is one of the rejections I would most clearly reverse.
## 7. The audit summary is itself overclaiming
**Target** — audit summary / publication gate
**Problem**
The report correctly recognised that:
`ERRORS (0)`
was too reassuring.
But the replacement has a new problem.
`validate.py` says:
`WARNINGS ... (publishable, but each needs a caveat on the record)`
Yet terminal statuses without evidence are only warnings, not errors.
The code literally says:

```python
if stage in ("enacted","failed","dead") and not evidence:
    warn.append(...)

```

So the claimed publication gate does not enforce its own evidentiary requirement.
The comment calls terminal status:
“a claim like any other”
but then doesn't make evidence mandatory.
That's a serious mismatch between rhetoric and enforcement.
**Confidence** — verified against source
**Fix**
Make these errors:

```text
terminal status without evidence
status.basis without basis source
enacted codification without adequate source

```

Warnings should be for things genuinely compatible with publication.
## 8. The regression tests test instances, not the underlying failure classes
**Target** — `test_regressions.py`
**Problem**
The report says:
“one test per bug actually found.”
That sounds robust but isn't.
The Utah test is:

```python
check("63G-32-101" in ...)
check("63G-32-102" in ...)

```

That catches wrong Utah citation #1, not wrong statutory citation generally.
The Washington test requires:

```python
stage == "failed"

```

It therefore protects the corrected answer, but does not test whether another state's carryover rule is being misread.
The evaluative-language test checks only:

```python
derived_from_changes

```

It does not inspect `notes`, despite the report explicitly acknowledging that the language purge may be cosmetic.
The vocabulary test checks:
validator → documented
but not:
documented → validator.
So the test suite is regression-specific, not failure-mode-specific.
**Confidence** — verified against source
**Fix**
Replace tests like:

```python
assert Utah == X

```

with properties such as:

```text
every enacted statutory citation has source_type == code
every status derived from a session rule cites that rule
every documented provision is validator-recognised
no evaluative language occurs in factual fields

```

Then retain the specific Utah/Washington tests as regression fixtures.
## 9. The three new provision tags are currently under-justified
**Target** — `defines_human_to_include_unborn`, `creates_criminal_offence`, `creates_private_right_of_action`
**Problem**
The report is right to flag this as the weakest area.
The underlying textual facts are real. Tennessee HB 849's introduced text explicitly defines “human being” to include the unborn. ([Tennessee General Assembly](https://www.capitol.tn.gov/Bills/114/Bill/HB0849.pdf?utm_source=chatgpt.com))
Tennessee HB 1455's introduced proposal really did create an offence relating to AI training and a cause of action. The Tennessee Fiscal Review Committee describes both a Class A felony and a cause of action. ([Tennessee General Assembly](https://www.capitol.tn.gov/Bills/114/Fiscal/HB1455.pdf?utm_source=chatgpt.com))
So the problem isn't factuality.
The problem is selection bias.
Why do these collateral provisions become structured tags when the registry does not have a general rule saying which non-personhood provisions deserve tagging?
The ontology appears to have been expanded because these provisions make a particularly interesting Tennessee version diff visible.
That is precisely the motivated-reasoning concern the report acknowledges.
There is an especially awkward asymmetry:
`creates_criminal_offence`
is not specifically about AI legal status. It could describe thousands of unrelated provisions in an AI bill.
**Confidence** — strong inference
**Fix**
Before retaining these tags, establish a general inclusion rule:
A provision tag belongs in the ontology only if the feature directly concerns AI's legal status, an incident of legal personality, or the allocation of a legal right/duty/liability that follows from that status.
Then test the three tags against that criterion.
`defines_human_to_include_unborn` probably passes because it directly modifies the human/person taxonomy.
The two Tennessee training-conduct tags need a stronger justification. If retained, the project should explain why these collateral legal consequences are in scope while other collateral provisions aren't.
The safest alternative is an explicit `ancillary_legal_consequence` layer rather than continually adding bespoke tags when an interesting diff appears.
## 10. `PROVISIONS.md` is substantially better, but some operational tests are still not genuinely binary
**Target** — `PROVISIONS.md`
**Problem**
The document says:
“Two readers applying these tests to the same text should reach the same answer.”
But several tests require interpretation of legal effect.
For example:
“The text places an affirmative duty of oversight, supervision, risk assessment or safety mechanism on a human or corporate actor.”
Whether a statutory requirement constitutes a “duty” can depend on drafting context.
Likewise:
“bars a category of liability”
in the safe-harbour definition mixes different legal mechanisms.
And:
“may not be granted, or may not be recognised as having, legal personhood”
requires deciding whether particular statutory terminology is equivalent to “legal personhood.”
This doesn't mean the tags are unusable. It means the claim that they are mechanically decidable is too strong.
**Evidence**
`PROVISIONS.md` expressly sets the standard of two-reader agreement and says intent-dependent tags are invalid.
**Confidence** — strong inference
**Fix**
For every tag add:

```text
exclusion test
boundary case
decision rule

```

and replace:
“Two readers should reach the same answer”
with:
“The aim is reproducible classification using these textual decision rules; ambiguous cases must be coded `not_assessed` and recorded.”
That is more honest.
## 11. `session_rules.json` creates an appearance of a general infrastructure that covers only 3/12 states
**Target** — `session_rules.json`
**Problem**
The README calls it:
`how a bill dies in each state, sourced`
but the file contains only:

* Washington
* Wisconsin
* Missouri.

The registry covers 12 states.
This matters because the report explicitly uses the rules registry to support status auditing. It therefore isn't merely an implementation detail; it has epistemic significance.
A reader could reasonably infer:
“The registry knows the procedural death rules relevant to its corpus.”
It doesn't.
**Confidence** — verified against source
**Fix**
Either:

1. document the file as partial, reviewed session rules, with explicit coverage; or
2. add rules for every jurisdiction represented.

I would choose #1 now and build #2 before automated status derivation.
## 12. The Washington correction is more honest, but the current evidence chain is still incomplete
**Target** — Washington HB 2029
**Problem**
The correction itself appears substantially fixed.
The official bill page shows the January 12 carryover event, but no subsequent legislative action. ([Washington State Legislative Information](https://app.leg.wa.gov/billsummary?BillNumber=2029&Initiative=false&Year=2025&utm_source=chatgpt.com))
Washington's official HCR 4409 records adjournment sine die on March 12, 2026.
So the project's conclusion that the earlier “alive” interpretation was wrong is now much more defensible.
But the registry's rule source still points to the bill page rather than a source establishing the legal consequence of sine die.
That's a provenance gap in the exact correction that is supposed to demonstrate improved procedural reasoning.
**Confidence** — verified against source
**Fix**
Make the status evidence explicitly two-part:

```text
Observed event:
    HCR 4409 — session adjourned sine die 12 March 2026

Rule:
    Washington rule establishing disposition of unpassed bills

Conclusion:
    derived status = failed

```

Do not make the bill-history page carry all three evidentiary roles.
## 13. The README still makes a stronger verification claim than the data supports
**Target** — README
It says:
“Every record has since been independently checked”
and:
“Every claim cites something.”
The first sentence is ambiguous but potentially defensible if “checked” means some source was consulted.
The second is not.
The current model has:

* `evidence_refs`;
* `sources.primary`;
* free-text notes;
* verification levels.

It does not have claim-level source linkage.
A researcher cannot reliably map each substantive sentence in `notes` to a source.
**Confidence** — verified against source
**Fix**
Change:
“Every claim cites something”
to:
“Each structured status and verification dimension records its evidentiary basis; narrative notes may contain multiple observations supported by the record's cited sources.”
Or actually implement claim-level provenance.
## 14. The source manifest is not yet the provenance system the report implies
**Target** — `source_manifest.json`
**Problem**
The report says:
“SHA-256 for 10 source documents and 16 normalised texts; 12 versions linked to the exact hashed document they derive from.”
That leaves:

* 13 versions without provision tags;
* fewer source documents than records;
* fewer exact source-to-version links than versions.

Hashes prove identity of a retrieved file. They do not establish that:
`normalised text X` is a faithful transformation of `source Y`.
That is particularly important for the Tennessee provenance issue.
**Confidence** — strong inference
**Fix**
Add a transformation manifest:

```json
{
  "source": "...",
  "source_sha256": "...",
  "normalized_text": "...",
  "normalization_operations": [...],
  "substantive_changes": false,
  "verified_by": "..."
}

```

Then the hash becomes actual provenance rather than just file integrity.
## 15. The report understates the problem with “19 assignments, one pass”
**Target** — version-level provisions
**Problem**
The report calls this a weakness, but I think it is more serious than §5 suggests.
These tags are now being used to produce derived historical claims:
Tennessee had `restricts_person_like_training` in the introduced version and subsequently lost it.
That is exactly the kind of claim for which independent coding matters.
There is no second coder, no blind reclassification, and no disagreement log.
So the new version-level matrix is more sophisticated than before, but the epistemic foundation is actually less tested than the old bill-level coding.
The Tennessee primary text confirms that the relevant introduced provisions really existed, so this particular tag has strong textual support. ([Tennessee General Assembly](https://www.capitol.tn.gov/Bills/114/Bill/HB1455.pdf?utm_source=chatgpt.com))
But that does not validate the other 18 assignments.
**Confidence** — strong inference
**Fix**
Do a blind second-pass sample of at least:

* all three new tags;
* all removed provisions;
* all `retained` classifications;
* a random sample of positive and negative assignments.

Record:

```text
coder A
coder B
agreement
disagreement
resolution

```

For a research artefact, this is considerably more valuable than another layer of code.
## 16. The site-diff architecture has a particularly bad hidden assumption
**Target** — `render_diff()`
The code does:

```python
a, z = vs[0], vs[-1]
mech = vs[1] if len(vs) > 2 else None

```

So when there are more than two stored versions, the second version is simply called the “mechanism.”
That's not a legal concept. It is an array-position assumption.
For:

```text
introduced
committee substitute
engrossed
conference
enrolled

```

the “mechanism” isn't necessarily the committee substitute.
**Confidence** — verified against source
**Fix**
Represent version transitions explicitly:

```json
{
  "from": "introduced",
  "to": "committee_substitute",
  "change_type": "committee_substitute"
}

```

Then render the actual transition.
## 17. R5 is not yet blocking, but the report understates its importance
**Target** — R5, discovery ledger
**Problem**
The report says:
“premature while discovery is manual.”
That is reasonable only if the project does not make a completeness claim.
But the README describes a 23-bill corpus covering 12 states and identifies the source paper as the starting point.
The forthcoming methodology will need to answer:
How do we know there aren't bills outside the inherited paper?
Once that question is asked, a discovery ledger isn't a Phase 4 luxury. It becomes the audit trail for corpus completeness.
**Fix**
You don't need automated discovery yet.
Create a simple manual discovery ledger now:

```text
jurisdiction
search date
search source
search terms
candidates found
included/excluded
reason

```

That would be tiny and would substantially improve the eventual completeness claim.
## 18. The self-assessment understates the central problem: the data model still cannot distinguish “observed fact” from “researcher conclusion”
This is the broadest issue.
The report recognises:
“The language purge may be cosmetic.”
But that is not merely a prose problem.
The architecture currently contains:

* structured classifications;
* free-text notes;
* `derived_from_changes`;
* `status.basis`;
* `provision_changes`;
* `verification`.

There is still no general distinction between:

```text
I observed X in the document

```

and:

```text
I infer Y from X.

```

The Washington error was precisely this transformation:

```text
absence of terminal action
        ↓
bill is alive

```

The correction now makes the opposite inference:

```text
session ended + no enactment
        ↓
bill failed

```

The second may be correct, but the data model needs to make the inference itself inspectable.
That's the deeper lesson from the first red-team.
Which rejections I would overturn
In order of importance:
R1 — overturn
The current diff is not defensible as a published differentiating feature. Build the section-aware parser now.
R3 — overturn
The current “verification” is not field-level provenance. The project is small enough that this is exactly when to implement it.
R4 — overturn
A notes/analysis split is not a substitute for typed claims. At minimum, implement typed evidentiary claims for contentious narrative assertions.
R2 — overturn, but modify the proposal
Don't blindly calculate `failed` from a date. Build derived-status computation with rule provenance and human override.
R8 — overturn
A tiny machine-readable vocabulary is preferable to duplicated Python/Markdown vocabularies.
R5 — partially overturn
A full automated discovery ledger can wait, but a manual discovery/provenance ledger should exist before claiming methodological completeness.
R6 — keep
The rejection of an isolated `role="gridcell"` is technically sensible. The important accessibility problem was the missing textual equivalent.
R7 — keep
No reason to use `!important` when the specificity bug can be fixed structurally.
R9 — keep
Accumulate-and-report is appropriate for a batch validation tool. The problem is not accumulation; it is that some things currently classified as warnings should be hard errors.
Are the two publication blockers the right two?
Not quite.
The six secondary-source status audit is absolutely a blocker.
The methodology is also a blocker if the site is going to be presented as a research registry rather than a seed corpus.
But I would add at least two more publication gates:
## 3. The version-diff implementation
The current diff is explicitly acknowledged as unbuilt in its promised replacement, while the shipped version remains regex-based. The project shouldn't make version diffs a central differentiating feature until the representation is reliable.
## 4. Verification/provenance semantics
The project should not claim:
“Every claim cites something”
or:
“per-dimension provenance”
until the source-to-claim relationship actually exists.
And I would make terminal status evidence a hard validator error, not a warning.
What §5 understates
Three things.
## 1. The new tags are not merely “weak”
The issue isn't whether the three tags happen to be correct. The issue is ontology selection under researcher discretion. The project needs a rule for why some collateral legal features become structured variables and others do not.
## 2. The version classifications need reliability testing
This is more serious than the report presents because these classifications underpin the project's most interesting historical claims.
## 3. The architecture still permits epistemic drift
The project has added more labels describing how confident it is, but it has not yet created a robust mechanism connecting:

```text
claim → source → observation → inference → classification

```

That is the underlying failure mode.
One particularly important positive result from this second audit
The Tennessee additions are not fabricated findings.
The official Tennessee text really does contain the unborn-human definition in HB 849. ([Tennessee General Assembly](https://www.capitol.tn.gov/Bills/114/Bill/HB0849.pdf?utm_source=chatgpt.com)) And HB 1455 really did contain the criminal-training and cause-of-action machinery in its introduced form. ([Tennessee General Assembly](https://www.capitol.tn.gov/Bills/114/Fiscal/HB1455.pdf?utm_source=chatgpt.com))
So I would not tell Opus simply to delete those tags.
I would tell it:
Prove why these tags belong in the ontology, rather than merely proving that the text contains them.
That distinction is the heart of this second red-team.
The project has made substantial progress on catching factual errors. It has not yet fully solved the harder problem: preventing a researcher from turning an interesting textual observation into a structured “finding” simply because the schema has been adjusted to accommodate it.
