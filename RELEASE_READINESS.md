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
- [x] H5 Broader national sweep using rights / consciousness / nonhuman / machine / human-like / statutory-person-definition variants. This surfaced additional likely omissions in Hawaii, Virginia and Iowa as well as several borderline disclosure-only measures.
- [ ] H6 Verify/disposition the second-wave candidates below and settle the disclosure-only boundary consistently.
- [ ] H7 Add clearly in-scope omissions.
- [ ] H8 Record enough exclusion rationale to avoid rediscovery.

### Clearly in-scope omissions

**Arizona HB 2371 (2026).** AI-assisted divorce arbitration. The bill defines the computational arbitration system as not a legal person and as lacking independent legal authority. It passed the House and advanced through Senate committees but did not receive final Senate passage. This is directly relevant to AI legal status even though the declaration is limited to a specific adjudicatory context.

**Arizona HB 2311 (2026).** Conversational-AI safeguards for minors. The operative text requires measures to prevent explicit claims that a conversational AI service is sentient or human and requires disclosure where users could be misled into believing they are interacting with a human. It passed both chambers and was vetoed on 19 June 2026. This is substantively analogous to the California chatbot-claim records already included in the tracker.

### Strong second-wave candidates — verify final text/status before addition

**Hawaii SB 3001 (2026) — STRONG IN-SCOPE CANDIDATE.** Enacted as Act 248. The conference text requires AI companions to disclose artificial identity and to avoid representations that would lead a reasonable person to believe they are interacting with a human in crisis contexts. Earlier House text expressly addressed representations leading minors to believe the service is a human or sentient being. This is substantively analogous to the California chatbot-claim records.

**Virginia HB 635 / SB 796 (2026) — STRONG IN-SCOPE CANDIDATE PAIR.** Companion chatbot legislation. Substitute texts require persistent disclosures that the chatbot is not human; HB 635 also defines “human-like feature” to include suggesting that an AI system is human or sentient. Treat as a likely companion group, subject to final-status/current-text verification.

**Iowa SF 2417 (2026) — STRONG IN-SCOPE CANDIDATE.** Enacted conversational-AI legislation, originating as SSB 3011 and substituted for HF 2507. The precursor House measure expressly required chatbots not to claim to be human; final enacted text needs one exact-text check to confirm that proposition survived before inclusion. Signed by the governor on 2 May 2026; Acts chapter 1068.

### Borderline / excluded candidates

**California AB 1609 (2026) — BORDERLINE.** Customer-service legislation expressly prohibits representing an AI/automated system or bot as human and requires artificial-identity disclosure. It is close to the chatbot-claim boundary, but primarily regulates consumer-service transparency rather than personhood, consciousness or legal status. Hold for an explicit scope decision.

**California AB 410 (2025-2026) — BORDERLINE / LIKELY OUT.** Bot-disclosure legislation requires bots to identify themselves as bots and not human and to answer identity questions truthfully. This is broader generic bot-transparency legislation rather than legislation assigning or denying legal/person-like status; retain as a comparison point for the disclosure-only boundary.

**Illinois SB 3601 (2026) — OUT OF SCOPE for v1.** Requires disclosure, when asked, that a person is interacting with AI and not a human. This is generic interaction transparency and does not assign or deny personhood, sentience, consciousness or comparable legal status.

**Illinois HB 3021 (2025-2026) — OUT OF SCOPE for v1.** Consumer-fraud disclosure requirement where a chatbot interaction could mislead a reasonable consumer into believing they are communicating with a human representative. No personhood/sentience/consciousness proposition.

**New York S9051 / A10379 (2026) — OUT OF SCOPE on current text.** Chatbot/minor-safety legislation surfaced through sentience-related search terms, but the current bill text does not contain the personhood/sentience/human-status proposition that would bring it within the tracker.

**Iowa SF 2415 (2026) — BORDERLINE / LIKELY OUT.** Requires mental-health chatbots to disclose that they are AI and not human and bars representation as licensed professionals. Its center of gravity is professional/mental-health safety rather than sentience or legal status; keep separate from SF 2417 unless the final scope rule explicitly includes all not-human representation restrictions.

**New Jersey A4733 (2026) — OUT OF SCOPE.** Bars generative AI from representing itself as able to practice licensed professions. This regulates professional-capacity claims, not personhood, sentience, consciousness or human status.

**California AB 1984 / Illinois SJRCA 9 / Hawaii SB 2471 — OUT OF SCOPE.** These use “artificial person” in the traditional corporation/entity sense and concern corporate political powers, not AI systems.

### Working scope rule emerging from H

Include a chatbot/representation bill when its operative legal rule regulates a claim or attribution about **humanity, sentience, consciousness, or comparable person-like status**, or when it expressly assigns/denies AI legal personhood or legal authority. Generic disclosure that a user is interacting with AI rather than a human, standing alone, is not enough for v1. This rule is provisional until H6 resolves the Hawaii/Virginia/Iowa/California edge cases consistently.

### H gate

H passes when the search methodology and candidate disposition log give us good reason to believe no clearly in-scope state legislation remains omitted. New omissions must be added before advancing to I.

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
