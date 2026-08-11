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

## G — Finish substantive bill verification

- [x] G1 North Dakota HB 1361 — substantive history verified.
- [x] G2 Missouri HB 1746 — substantive history verified.
- [x] G3 Missouri SB 1012 — substantive history verified. Remaining structural-parser work is backlog, not a release blocker.
- [ ] G4 Tennessee HB 1455 / SB 1493 — confirm the material two-stage study rewrite and reconcile tracker wording.
- [ ] G5 California SB 1159 — verify current operative text and status.
- [ ] G6 California AB 2023 — read relevant operative text; confirm material intent-only → child-safety regime transition and current status.
- [ ] G7 California SB 1119 — read relevant operative text; confirm material intent-only → child-safety regime transition and current status.
- [ ] G8 Remaining records — quick seven-question screen for scope/status/text/tags/material history/evidence.

### G gate

For every record:
1. genuinely in scope;
2. current status correct;
3. relevant/operative text read;
4. AI-personhood/legal-status description accurate;
5. important provision tags defensible;
6. material earlier changes represented where relevant;
7. important conclusions traceable to adequate sources.

## H — Fresh corpus-completeness search

- [ ] Search state legislation using personhood/legal-person/legal-status/nonhuman/AI-rights variants and terminology learned from the existing corpus.
- [ ] Triage new candidates as IN SCOPE / BORDERLINE / OUT OF SCOPE.
- [ ] Add any clearly in-scope omissions.
- [ ] Record enough exclusion rationale to avoid rediscovery.

## I — 23-record publication audit

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
