# Methodology

## Research question

The tracker asks a narrow descriptive question: **what US state legislation assigns, denies or otherwise regulates the legal or person-like status of AI systems, and what is the current legislative/legal state of that proposal?**

It is not intended to catalogue general AI regulation.

## Inclusion rule

A bill is in scope when its operative rule does at least one of the following:

1. expressly assigns or denies AI **legal personhood, legal authority, legal capacity, or inclusion in a statutory person category**; or
2. regulates an AI system's claim or attribution of **sentience, consciousness, humanity, or comparable person-like status** in a way that is more substantive than a generic disclosure that the user is interacting with software rather than a human.

The second branch captures legislation such as child-safety or companion-chatbot provisions that specifically regulate claims that an AI is sentient, conscious or human. Generic bot/AI identity disclosure by itself is outside v1 scope.

The boundary is functional rather than title-based. A bill need not use the word `personhood` if its operative text directly governs one of the status propositions above.

## Discovery

The corpus began with the 23 state bills identified in Smith, Caviola & Alexander (2026), *Denying Personhood to AI*.

A fresh 2026 completeness sweep then searched combinations of terms including:

- artificial intelligence + personhood / legal person / person / legal status;
- legal authority / legal capacity / rights;
- sentient / sentience / conscious / consciousness;
- human / nonhuman / machine;
- chatbot / AI companion + human / sentient / conscious;
- statutory definitions of `person` combined with AI terminology.

Candidates were compared against the existing registry and classified as **in scope**, **borderline**, or **out of scope** using the rule above. The exclusion/rediscovery log in `RELEASE_READINESS.md` records representative near-misses so subsequent researchers do not repeatedly reopen the same generic-disclosure bills.

The sweep added six records: Arizona HB 2371 and HB 2311; Hawaii SB 3001; Iowa SF 2417; and Virginia HB 635 / SB 796. The working v1 corpus is therefore 29 records across 16 states.

Completeness is necessarily provisional: legislative databases change, terminology evolves and new bills can be introduced. The claim is not that no other arguably related bill exists, but that the documented search found no additional **clearly in-scope** state bill as of the verification date.

## Verification standard for each record

A record is publication-ready when the following tracker-facing questions have been answered:

1. Is the bill genuinely within scope?
2. Are state, bill number, chamber and session correct?
3. Is the current legislative status correct at the verification date?
4. Has the relevant/operative text been read directly?
5. Does the summary/key clause accurately describe the AI legal-status proposition?
6. Are the provision tags defensible under `PROVISIONS.md`?
7. If an earlier version materially changed the tracker's account, is that change represented?
8. Are enacted-law destinations/effective dates stated with the correct evidentiary qualification?
9. Can another researcher reach the important source material from the record?

Technical perfection of every historical PDF or intermediate amendment is not required if it does not change one of those answers.

## Material versions

A **material version** is a version whose change would alter the tracker's substantive description, classification, provision tags, or account of legal effect.

Examples of material changes include:

- adding or removing an AI-personhood prohibition;
- replacing a substantive prohibition with a study requirement;
- adding/removing liability, corporate-veil or chatbot-status provisions that appear in the tracker;
- changing the operative statutory mechanism in a way that changes how the bill is classified.

Formatting changes, technical redesignations and unrelated amendments are not material merely because a legislative system publishes a new document. A withdrawn substitute may be retained as historical evidence when it explains the legislative path, but it is not treated as an ancestor of the enacted/perfected text unless it was actually adopted.

## Legislative status

`status.stage` is a current tracker classification, not necessarily a phrase printed by the legislature.

- When an official action explicitly establishes the state (for example, signed, vetoed, passed a chamber or referred to committee), `status.basis` is `explicit_action`.
- When a bill has no terminal action line but the relevant session/biennium has ended, the terminal classification can be derived from the last official action plus a sourced session rule/calendar. That is recorded as `session_rule`.
- A historical achievement such as passing one chamber is not kept as the current stage after the bill later fails at session end.

This distinction is important in states such as Washington and Missouri, where an unpassed bill can die without a bill-history entry saying `failed`.

## Legislative text and provision tags

The operative text is read directly for every record. `registry/verification.operative_text` records that state.

Provision tags are descriptive and controlled by `registry/vocabulary.json`, with operational tests and negative examples in `PROVISIONS.md`. A tag records an observable legislative feature; it is not a score or normative judgement.

A missing tag is not inferred to mean textual absence unless the relevant version was actually assessed for that provision. Where the structured claim-evidence layer records an absence, it uses an explicit `checked_absent` assessment.

## Evidence hierarchy and provenance

Primary legislative sources are preferred for bill text, action history, amendments, votes, enacted acts and published code.

The registry distinguishes several evidentiary questions that should not be collapsed:

- an official URL can identify a source without proving every claim on the record;
- a document hash establishes integrity of the stored file, not correctness of an extraction or interpretation;
- `verified_primary` describes the verification state of the record/status and is not shorthand for exhaustive field-level citation;
- `registry/claim_evidence.json` supplies claim-specific evidence for selected high-risk claims, including derived statuses and version-specific findings, but is not an exhaustive graph of every sentence in `notes`.

Derived claims list the evidentiary inputs actually relied upon. Directly recorded legislative facts and researcher inferences remain distinct.

## Enacted law and codification

The bill text states what the legislature proposes or directs; the published code states the codified result. Those can differ because of renumbering or later code changes.

For enacted records, `verification.codified_at_source` distinguishes:

- `code` — current/published code inspected directly; and
- `bill` — the destination is established from the enrolled bill/session law but direct code-level incorporation was not independently verified.

The registry preserves enactment-time numbering where useful rather than silently replacing it with current numbering. Known access limitations are disclosed instead of being converted into stronger verification claims.

## Descriptive presentation

The project does not advocate for or against the legislation it tracks. Categories are kept as close as possible to observable textual mechanisms. Outside constitutional, policy or political claims are attributed to the source making them rather than presented as findings of the tracker.

## AI assistance and checking

AI tools were used extensively for discovery, document retrieval, text extraction, comparison, structured-data editing and code generation. Because those tools can misread legislative pages, confuse current and historical versions, or attach plausible but wrong sources, the project uses direct source review, regression tests and adversarial rechecking.

Material errors found during that process are retained in `VERIFICATION.md` so later researchers can see the failure modes rather than only the cleaned final dataset.
