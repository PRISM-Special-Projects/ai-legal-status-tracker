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
- [x] G5 California SB 1159 — operative June 25 text verified; tracker correctly captures exclusion of AI/nonhuman entities from specified government-participation/person terminology. Bill remains alive after Senate passage and Assembly committee action; stale LegInfo indexing is not treated as a substantive blocker.
- [x] G6 California AB 2023 — material intent-only → child-safety regime transition verified. Amended text expressly treats chatbot claims of being sentient, conscious, or human as covered/prohibited conduct; bill remains alive in Senate committee process.
- [x] G7 California SB 1119 — material intent-only → child-safety regime transition verified. Operative text and July 2 Assembly committee re-referral to Appropriations already supported in the registry.
- [x] G8 Remaining records — quick seven-question screen completed. It caught and corrected stale terminal statuses for Oklahoma HB 3546 and South Carolina HB 3796, and closed the remaining operative-text verification flags for Washington HB 2029 and California AB 2023.

### G gate — PASS

For every record:
1. genuinely in scope;
2. current status correct;
3. relevant/operative text read;
4. AI-personhood/legal-status description accurate;
5. important provision tags defensible;
6. material earlier changes represented where relevant;
7. important conclusions traceable to adequate sources.

## H — Fresh corpus-completeness search — IN PROGRESS

- [x] H1 First national keyword sweep: artificial intelligence + personhood / legal person / legal status / sentient / human / chatbot terminology.
- [x] H2 Compare first-wave candidates against repository — Arizona HB 2371 and HB 2311 are absent from the current 23-record corpus.
- [x] H3 Verify and disposition Arizona HB 2371 — clearly in scope; final status failed after House passage and Senate committee advancement without final Senate passage.
- [x] H4 Verify and disposition Arizona HB 2311 — clearly in scope; passed both chambers and vetoed 19 June 2026.
- [x] H5 Broader national sweep using rights / consciousness / nonhuman / machine / human-like / statutory-person-definition variants.
- [x] H6 Resolve second-wave candidates and disclosure-only boundary.
- [ ] H7 Add clearly in-scope omissions.
- [ ] H8 Record enough exclusion rationale to avoid rediscovery and run one final negative sweep.

### Clearly in-scope omissions to add in H7

**Arizona HB 2371 (2026).** AI-assisted divorce arbitration. Defines the computational arbitration system as not a legal person and as lacking independent legal authority. Passed the House and advanced through Senate committees but did not receive final Senate passage.

**Arizona HB 2311 (2026).** Conversational-AI safeguards for minors. Requires measures to prevent explicit claims that a conversational AI service is sentient or human. Passed both chambers and was vetoed on 19 June 2026.

**Hawaii SB 3001 (2026).** Enacted as Act 248. The enacted conference text regulates representations that could lead users to believe an AI companion is human, and the House-stage operative text expressly addressed belief that the system was a human or sentient being. This falls on the same side of the scope boundary as the California child-safety chatbot records.

**Iowa SF 2417 (2026).** Enacted as Acts chapter 1068. The final act requires reasonable measures to prevent statements leading a reasonable individual to believe they are interacting with a human, expressly including claims that the conversational AI service is “sentient or human.” Signed 2 May 2026; effective 1 July 2026; applies 1 July 2027.

**Virginia HB 635 / SB 796 (2026 carryover to 2027) — in-scope live companion group.** Both regulate AI-chatbot human identity representations. HB 635’s substitute defines human-like features to include suggesting that an AI system is human or sentient. HB 635 was continued from 2026 into the 2027 House Communications, Technology and Innovation Committee. SB 796 passed the Senate and was continued into the 2027 House committee. Treat as live carryover rather than failed 2026 legislation.

### Borderline / excluded candidates

**California AB 1609 (2026) — OUT OF SCOPE for v1 under final H6 boundary.** Prohibits a customer-service chatbot from being represented as human, but functions as general consumer-service identity transparency without a sentience/consciousness/personhood proposition.

**California AB 410 (2025-2026) — OUT OF SCOPE for v1.** General bot-identity disclosure and truthful-answering requirement; no AI legal-status or sentience/consciousness proposition.

**Illinois SB 3601 (2026) — OUT OF SCOPE for v1.** Generic disclosure that an interaction is with AI rather than a human.

**Illinois HB 3021 (2025-2026) — OUT OF SCOPE for v1.** Consumer-fraud notification where chatbot interaction could be mistaken for a human representative.

**New York S9051 / A10379 (2026) — OUT OF SCOPE on current text.** Current text lacks the personhood/sentience/human-status proposition.

**Iowa SF 2415 (2026) — OUT OF SCOPE for v1.** Mental-health/professional-capacity restrictions plus generic not-human disclosure; no sentience/consciousness/legal-status rule comparable to SF 2417.

**New Jersey A4733 (2026) — OUT OF SCOPE.** Regulates claims that generative AI can practice a licensed profession, not human/sentient/person-like status.

**California AB 1984 / Illinois SJRCA 9 / Hawaii SB 2471 — OUT OF SCOPE.** “Artificial person” is used in the traditional corporation/entity sense, not to regulate AI systems.

### H6 scope rule — settled

Include a bill when its operative rule either:

1. expressly assigns or denies AI **legal personhood, legal authority, legal capacity, or inclusion in a statutory person category**; or
2. regulates an AI system’s claim or attribution of **sentience, consciousness, humanity, or comparable person-like status** in a way that is more substantive than a generic disclosure that the user is interacting with software rather than a human.

Generic bot/AI identity disclosure alone is not enough for v1. This keeps the tracker focused on legal/person-like status rather than becoming a general chatbot-transparency database.

### H gate

H passes when H7 adds the clearly in-scope omissions, H8 records the exclusion rationale, and a final negative sweep finds no additional clearly in-scope state legislation.

## I — publication audit

- [ ] Correct bill/session/state.
- [ ] Correct current status and latest action/date.
- [ ] Relevant text read.
- [ ] AI-personhood description accurate.
- [ ] Provision tags defensible.
- [ ] Material amendments represented.
- [ ] Enacted law/effective date correct where applicable.
- [ ] Primary source available where reasonably accessible.
- [ ] Known limitations disclosed.
- [ ] Cross-record checks: companions, shared language, status families, enacted/live/failed groups.
- [ ] Full registry validation and site build.

## J — Documentation and handoff

- [ ] Scope and inclusion/exclusion criteria.
- [ ] Search methodology.
- [ ] Provision-tag methodology.
- [ ] Material-version rule.
- [ ] Legislative-status methodology.
- [ ] Evidence policy and known access limitations.
- [ ] Opus handoff: how sources were found and verified.
- [ ] Remove or clearly label obsolete migration/pilot machinery.
- [ ] Final CI.

## Final release gate

Independently reconstruct a deliberately difficult sample from tracker claim → source → exact text/action → same substantive conclusion.

## Non-blocking technical backlog

- Missouri SB 1012 structural-differ perfection for source-specific PDF formatting.
- Exhaustive intermediate-version graphs where they do not alter tracker-facing conclusions.
- Further parser and normalisation hardening not needed for P0–P4.
