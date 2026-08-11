# Release readiness — tracker-focused plan

## Definition of done

The tracker is ready for v1 when we have good reason to believe the corpus is materially complete, every included bill's current status and relevant legal effect are accurately described from adequate evidence, material changes are represented, and another researcher can reproduce the important conclusions.

## Priority order

- **P0 Corpus completeness** — are relevant bills missing?
- **P1 Legislative accuracy** — bill/session/status/dates are correct.
- **P2 Substantive accuracy** — relevant operative text has been read and described correctly.
- **P3 Material legislative history** — changes that alter the tracker's description/tags/legal-effect account are represented.
- **P4 Reproducibility** — important conclusions can be followed back to adequate sources.
- **P5 Technical/provenance perfection** — exhaustive version graphs, perfect PDF normalisation and zero parser warnings. Useful, but not a release requirement unless it blocks P0–P4.

A **material version** is one whose change would alter the tracker's substantive description, classification, provision tags, or account of legal effect.

## G — Finish substantive bill verification — COMPLETE

- [x] G1 North Dakota HB 1361 — substantive history verified.
- [x] G2 Missouri HB 1746 — substantive history verified.
- [x] G3 Missouri SB 1012 — substantive history verified. Remaining structural-parser work is backlog, not a release blocker.
- [x] G4 Tennessee HB 1455 / SB 1493 — material history reconciled: introduced criminal/civil regime → SA1113 Advisory Council study → HA1260/final TACIR study.
- [x] G5 California SB 1159 — operative June 25 text verified; tracker correctly captures exclusion of AI/nonhuman entities from specified government-participation/person terminology.
- [x] G6 California AB 2023 — material intent-only → child-safety regime transition verified.
- [x] G7 California SB 1119 — material intent-only → child-safety regime transition verified.
- [x] G8 Remaining records — quick seven-question screen completed; stale Oklahoma and South Carolina terminal statuses corrected and remaining operative-text flags closed.

### G gate — PASS

For every record:
1. genuinely in scope;
2. current status correct;
3. relevant/operative text read;
4. AI-personhood/legal-status description accurate;
5. important provision tags defensible;
6. material earlier changes represented where relevant;
7. important conclusions traceable to adequate sources.

## H — Fresh corpus-completeness search — COMPLETE

- [x] H1 National keyword sweep: artificial intelligence + personhood / legal person / legal status / sentient / human / chatbot terminology.
- [x] H2 Compare candidates against the original 23-record corpus.
- [x] H3 Verify/disposition Arizona HB 2371.
- [x] H4 Verify/disposition Arizona HB 2311.
- [x] H5 Broader sweep using rights / consciousness / nonhuman / machine / human-like / statutory-person-definition variants.
- [x] H6 Resolve second-wave candidates and settle the disclosure-only boundary.
- [x] H7 Add all six clearly in-scope omissions.
- [x] H8 Final negative sweep and exclusion log.

### H7 additions — corpus expanded from 23 to 29 records

**Arizona HB 2371 (2026).** AI-assisted divorce arbitration; expressly states that the computational arbitration system is not a legal person and lacks independent legal authority. Failed after House passage and Senate advancement without final Senate passage.

**Arizona HB 2311 (2026).** Conversational-AI safeguards for minors; expressly targets claims that the service is sentient or human. Passed both chambers and was vetoed 19 June 2026.

**Hawaii SB 3001 (2026).** Enacted as Act 248. Final conference text restricts AI-companion representations that could lead users in crisis services to believe they are interacting with a human; preceding House text expressly addressed human or sentient-being representations.

**Iowa SF 2417 (2026).** Enacted as Acts chapter 1068. Requires safeguards against statements leading a reasonable person to believe the conversational AI service is sentient or human. Signed 2 May 2026; effective 1 July 2026; applicability begins 1 July 2027.

**Virginia HB 635 / SB 796 (2026 carryover to 2027).** Live companion group regulating chatbot human-identity representations. HB 635 remains in House Communications, Technology and Innovation; SB 796 passed the Senate and remains before the House committee after continuation into 2027.

All six were added at the tracker-focused standard: current status, directly reviewed operative text, provision tags, primary sources and companion grouping where applicable. Core validation, claim-evidence validation and site build passed before the additions were committed.

### H6 scope rule — settled

Include a bill when its operative rule either:

1. expressly assigns or denies AI **legal personhood, legal authority, legal capacity, or inclusion in a statutory person category**; or
2. regulates an AI system’s claim or attribution of **sentience, consciousness, humanity, or comparable person-like status** in a way that is more substantive than a generic disclosure that the user is interacting with software rather than a human.

Generic bot/AI identity disclosure alone is not enough for v1. This keeps the tracker focused on legal/person-like status rather than becoming a general chatbot-transparency database.

### H8 exclusion / rediscovery log

**California AB 1609 (2026) — OUT.** Customer-service identity transparency; no sentience/consciousness/personhood proposition.

**California AB 410 (2025-2026) — OUT.** General bot disclosure/truthful-identity requirement only.

**Illinois SB 3601 / HB 3021 — OUT.** Generic not-human/consumer-disclosure rules.

**New York S9051 / A10379 — OUT on current text.** Minor-safety chatbot rules without the personhood/sentience/human-status proposition used by this tracker.

**New York A6767 (2025-2026) — OUT.** AI-companion crisis protocols and notice of the companion's non-human nature; still a generic identity disclosure rather than a sentience/consciousness/legal-status rule under the settled boundary.

**Iowa SF 2415 — OUT.** Mental-health/professional-capacity restrictions plus generic not-human disclosure; no comparable sentience/legal-status rule.

**New Jersey A4733 — OUT.** Licensed-profession capacity, not person-like status.

**Washington ESHB 2225 / SB 5984 — OUT under final scope rule.** Companion-chatbot safety and AI/not-human disclosure measures; no independent personhood, sentience, consciousness or legal-capacity proposition found in the final negative sweep.

**California AB 1984 / Illinois SJRCA 9 / Hawaii SB 2471 — OUT.** “Artificial person” means corporations/entities, not AI systems.

The final national negative sweep repeated combinations of legal person/personhood, sentient/conscious, human/nonhuman, AI rights/legal authority and chatbot identity terms. It surfaced the exclusions above but no additional clearly in-scope state bill beyond the six added in H7.

### H gate — PASS

The current working corpus is **29 records across 16 states**. The search and exclusion log provide a reproducible reason for the major inclusion boundary, and no clearly in-scope omission remains from the final sweep. Future discoveries can still be added, but corpus completeness no longer blocks v1.

## I — publication audit — COMPLETE

- [x] Correct bill/session/state.
- [x] Correct current status and latest action/date at the audit date.
- [x] Relevant text read — 29/29 records are `read_in_full`.
- [x] AI-personhood/legal-status descriptions checked under the G/H substantive standard.
- [x] Provision tags validated against the controlled vocabulary and reviewed text.
- [x] Material amendments represented where they affect tracker-facing conclusions.
- [x] Enacted law/effective date present and reconciled for all nine enacted records.
- [x] Primary source present for every record; no status remains secondary-source based.
- [x] Known limitations disclosed, including bill-sourced codification where code-level verification is not yet established.
- [x] Cross-record checks: companion groups, terminal statuses, enacted/live/failed groups and publication-facing verification state.
- [x] Full registry validation, publication audit, regression suite, audit tests, site build, post-build assertions and lint pass on the clean repository state.

### I findings

The tracker-focused publication audit was added as a permanent release check. On the 29-record corpus it found no blocking contradictions. It did surface four small publication-quality issues: stale review wording in Washington HB 2029 and Minnesota SF 4114, plus missing explicit `CODIFIED_AT PROVENANCE` caveats for newly added Hawaii SB 3001 and Iowa SF 2417. Those were corrected without changing substantive classifications.

Current audit summary: **29 records / 16 states; 29/29 status established from primary/citable records; 29/29 operative texts read in full; 9 enacted laws; 18/18 terminal statuses carry evidence.**

### I gate — PASS

No material data inconsistency remains from the publication audit.

## J — Documentation and handoff — COMPLETE

- [x] Scope and inclusion/exclusion criteria — `METHODOLOGY.md`.
- [x] Search methodology — `METHODOLOGY.md` plus H8 exclusion log above.
- [x] Provision-tag methodology — `PROVISIONS.md`, controlled vocabulary and methodology cross-reference.
- [x] Material-version rule — documented in `METHODOLOGY.md`.
- [x] Legislative-status methodology — explicit-action versus session-rule derivation documented.
- [x] Evidence policy and known access limitations — `METHODOLOGY.md` and refreshed `VERIFICATION.md`.
- [x] Opus/future-maintainer handoff — `RESEARCH_HANDOFF.md`, including source recovery and failure modes.
- [x] Obsolete one-shot migration helpers removed; parser/differ work clearly separated as non-blocking technical backlog.
- [x] README corrected to the 29-record/16-state state; generated site counts remain data-driven.
- [x] Final CI after documentation/handoff changes — PASS.

### J findings

The README and verification narrative had still described the original 23-record pre-publication state. They were rewritten to reflect the post-H/I corpus and to avoid implying exhaustive field-level provenance where the claim-evidence sidecar is selective. A dedicated methodology and research-handoff document were added.

**Non-code metadata action:** the GitHub repository description returned by the API still says “23 bills, 12 states.” The available connector does not expose repository-metadata editing, so this should be changed manually to 29 bills / 16 states. The README and generated tracker itself are current; this does not block the data/site release.

### J gate — PASS WITH ONE DOCUMENTED ACTION

The repository contents and CI are release-ready; only the GitHub repository description needs a manual metadata update.

## Final release gate — COMPLETE

A six-case **source-first reconstruction** was completed and recorded in `FINAL_RELEASE_AUDIT.md` before comparing conclusions with the registry. The sample covered:

- Utah HB 249 — enacted personhood prohibition and enactment/current-code numbering;
- Washington HB 2029 — session-rule-derived failure;
- Tennessee HB 1455 / SB 1493 — material amendment sequence and effective date;
- North Dakota HB 1361 — current-code renumbering;
- Iowa SF 2417 — chatbot sentience/human-status scope boundary;
- Idaho HB 720 — enacted personhood law plus the known official-code access limitation.

No sample produced a material contradiction. Utah, Washington, Tennessee, North Dakota and Iowa were directly reconstructed from accessible official public sources. Idaho reproduced the already documented limitation: the live Idaho Legislature/code portal was blocked to the audit retrieval environment, so direct live-code inspection could not be newly repeated; the registry correctly retains bill/session-law-level codification provenance rather than overstating verification.

### Final gate — PASS WITH DOCUMENTED LIMITATIONS

**v1 COMPLETE.** The tracker has passed the substantive verification, corpus-completeness, publication, documentation/handoff and independent source-first reconstruction gates. The remaining items below are maintenance or technical backlog, not release blockers.

## Non-blocking post-v1 actions / backlog

- Manually update the GitHub repository description from `23 bills / 12 states` to `29 bills / 16 states`.
- Missouri SB 1012 structural-differ perfection for source-specific PDF formatting.
- Exhaustive intermediate-version graphs where they do not alter tracker-facing conclusions.
- Further parser and normalisation hardening not needed for P0–P4.
- Repeat corpus-completeness/status sweeps as new state legislation is introduced, amended or carried into later sessions.
