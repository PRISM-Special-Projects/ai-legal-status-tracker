# Research handoff — continuing the AI Legal Status Tracker

This document is for a researcher or AI system taking over maintenance of the tracker. It describes **how the evidence was found and checked**, not just the finished answers.

Read first:

1. `METHODOLOGY.md` — scope and inclusion rule.
2. `RELEASE_READINESS.md` — current gate state, completeness search and exclusion log.
3. `VERIFICATION.md` — errors already found and lessons from them.
4. `PROVISIONS.md` — operational tests for provision tags.
5. `registry/bills.json` — current bill-centred source of truth.

## 1. Start from the tracker question, not from keywords alone

The tracker is narrow. A new bill belongs here when its operative text either:

- assigns/denies AI legal personhood, legal authority, legal capacity or statutory-person status; or
- substantively regulates claims/attributions that AI is sentient, conscious, human or comparably person-like.

A generic requirement to say “this is AI, not a human” is not sufficient by itself for v1. Before adding a candidate, write down the exact operative proposition that crosses the scope boundary.

## 2. Discovery workflow

For a fresh state/session sweep, use multiple formulations. Useful search concepts include:

- `artificial intelligence` + `personhood`
- `artificial intelligence` + `legal person`
- `artificial intelligence` + `person` / statutory definition
- `artificial intelligence` + `legal authority` / `legal capacity`
- `AI` + `sentient` / `sentience`
- `AI` + `conscious` / `consciousness`
- `chatbot` / `AI companion` + `human` / `sentient`
- `machine` / `algorithm` / `software` + `person`

Do not assume a bill title will advertise the relevant clause. Arizona HB 2371 was an arbitration bill; the relevant proposition was a context-specific statement that the AI-assisted system was not a legal person and had no independent legal authority.

When a candidate appears, compare its state/bill/session against `registry/bills.json` and then inspect the operative text before deciding it is new.

## 3. Source hierarchy

Prefer sources in this order for the proposition they actually establish:

1. **Official bill text / amendment / substitute / enrolled act** for what the legislation says.
2. **Official legislative action history/journal** for what happened to the bill.
3. **Official session law / secretary of state publication** for enacted text and chapter number.
4. **Official published code** for current codification.
5. **Official session calendar/rule/journal** when terminal status must be derived from adjournment.
6. Secondary trackers (for example LegiScan) as discovery/navigation aids or corroboration, not as a replacement for accessible primary evidence.

An official URL on a bill record is not automatically evidence for every field. Identify the source actually used for the claim.

## 4. Recovering bill texts

### A. Use the official bill/document page before guessing URLs

Many legislature sites expose multiple text states from a single bill page. Record the source-native drafting/version identifier when available. Examples from this project include Missouri `3891H.01I`, `3891H.04C`, `5687S.02C` and North Dakota `23.0346.04000`.

The identifier is often more reliable than a human label such as “latest” because labels can change as a bill advances.

### B. Follow amendment history, not document chronology alone

A published substitute is not necessarily part of the operative chain. Check whether it was **adopted, withdrawn, superseded or rejected**.

Missouri SB 1012 is the key example: one floor substitute was withdrawn. It is useful historical evidence but must not be represented as an ancestor of the perfected bill.

### C. If an official page looks dead, test access assumptions

Do not conclude that a primary URL is dead solely because one retrieval tool cannot fetch it. During this project Missouri House pages were initially recorded as 404/dead when the actual issue was tool/user-agent blocking. A normal browser/curl-style request returned HTTP 200 and the official histories were intact.

Record “access limitation” separately from “source does not exist.”

### D. Archives are a recovery route, not a source upgrade

If a current portal no longer exposes an older text, use the official drafting identifier, filename or source URL to look for archived copies. Preserve the original source identity/URL where known and document that the bytes were recovered through an archive.

If the archive is the only retrievable copy, do not describe the document as directly fetched from the live official portal.

### E. Read the relevant text directly

PDF extraction is a convenience. It can collapse hierarchy, split cross-references or lose subsection markers. When the proposition matters to the tracker, inspect the source text itself rather than relying on a structural parser outcome.

The Missouri SB 1012 parser investigation is intentionally technical backlog because the substantive text was already established. Do not reopen that work unless a parser issue changes a tracker-facing factual conclusion.

## 5. Determining current legislative status

### Explicit action

Use the legislature's recorded action when it directly establishes the current state: introduced, committee referral, chamber passage, veto, governor signature, etc.

### Session-rule derivation

Some legislatures do not post a terminal `failed` action for bills left unfinished. In that case:

1. establish the last official bill action;
2. establish the relevant session/biennium end from an official source;
3. establish the carryover/expiration rule if needed;
4. record the resulting stage as derived (`status.basis = session_rule`).

Do not keep `passed_one_chamber` as the current stage after the session has ended without final passage. It remains a historical fact, not the current status.

Washington HB 2029 is the canonical warning: “reintroduced and retained in present status” kept the bill alive **into** the second year of the biennium, not after the biennium ended.

## 6. Enacted laws: bill text versus code

For an enacted law, distinguish three things:

- what the enrolled/session-law text says it enacts;
- the act's effective date;
- where the provision appears in the current published code.

Do not assume enactment-time numbering equals current code numbering. Utah HB 249 and North Dakota HB 1361 both demonstrated why.

If the code cannot be directly inspected, keep `verification.codified_at_source = "bill"` and state the limitation. Do not promote a secondary reproduction to official-code verification.

## 7. Effective dates

Read the effective-date clause rather than using the last legislative action by default.

If an act says it takes effect “upon becoming a law,” pair that clause with the official governor-signature/becoming-law date. Tennessee HB 1455/SB 1493 was initially assigned the final concurrence date rather than the later governor-signature date; that was corrected during audit.

Distinguish an **effective date** from a later **applicability/compliance date**. Iowa SF 2417, for example, has an effective date and a later applicability date.

## 8. Material version review

Do not build an exhaustive version graph unless it serves the tracker.

Ask: **would this version change the tracker's summary, classification, provision tags or account of legal effect?**

If yes, preserve the material state/change. If not, ordinary amendment metadata is enough.

Typical material changes found here:

- personhood prohibition added or removed;
- corporate-veil provision removed;
- substantive prohibition replaced with a study;
- person-definition mechanism replaced by a different statutory mechanism;
- sentience/human-status chatbot rule added in amendment.

## 9. Provision tagging

Use `PROVISIONS.md`, not intuition. A tag should correspond to an observable textual rule.

For absence:

- no evidence entry = not mapped/not assessed;
- `checked_absent` = the relevant text was actually reviewed for that proposition and it was absent.

Never infer absence merely because a tag is missing.

## 10. Claim provenance

`registry/claim_evidence.json` is a sidecar for selected high-risk claims. It does not replace `bills.json` and is not exhaustive.

Use it when a claim particularly benefits from explicit evidence edges, especially:

- session-rule-derived status;
- effective dates derived from more than one source;
- current code versus enactment-time destination;
- version-specific provision presence/absence;
- material provision transitions.

Keep direct facts and derived conclusions distinct. A sourced interpretation does not become a direct legislative fact simply because a URL is attached.

## 11. Corpus-completeness maintenance

The H-gate search produced an exclusion log in `RELEASE_READINESS.md`. Check it before reopening near-miss bills.

If a previously excluded bill is amended so that it now contains a sentience/consciousness/human-status or legal-personhood rule, reconsider it. Scope decisions are based on operative text, so a bill can cross the boundary during its lifecycle.

When doing a fresh sweep:

1. run the established term families;
2. add terminology learned from new bills;
3. compare results with existing records and the exclusion log;
4. investigate only candidates that could cross the scope rule;
5. record representative exclusions to prevent rediscovery.

## 12. Validation and release checks

For an ordinary factual update, run:

```bash
python3 registry/validate.py
python3 registry/publication_audit.py
python3 registry/test_regressions.py
python3 registry/validate_claim_evidence.py
python3 site/build.py
```

The GitHub workflows run the publication-facing checks automatically. The structural differ also runs as a technical-quality check but is intentionally non-blocking unless it affects a substantive tracker conclusion.

## 13. Known failure modes from this project

- Confusing a carryover resolution with continued life after sine die.
- Treating a chamber-passage milestone as the current status after later failure.
- Using an enrolled bill's proposed section number as the current code citation.
- Using final legislative concurrence as the effective date when the act takes effect on governor signature.
- Treating a withdrawn substitute as part of the operative version chain.
- Calling an official page dead when the retrieval tool was actually blocked.
- Inferring a provision from a summary instead of reading the operative text.
- Inferring absence from lack of a citation/tag.
- Treating document hashes as proof of semantic correctness.
- Allowing parser/normalisation work to displace the tracker’s substantive research goal.

## 14. Handoff standard

A future maintainer should be able to explain every material tracker update in this form:

> **Claim/change → why it matters to scope or current status → primary source used → exact operative/action basis → registry field(s) changed → validation result.**

If that chain is clear, the research is at the standard used for v1.
