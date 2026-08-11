# AI Legal Status Tracker — Project Plan

> **Planning record, superseded.** This is the design document as written before the build, kept
> for the decision trail. Where it disagrees with the artefact, the artefact governs — see
> `README.md`, `IMPLEMENTATION-REPORT.md` and `DIFF-REPORT.md`. Two decisions recorded here were
> reversed after external review: the state tiles no longer say "no legislation identified" (it
> claims more than the inclusion methodology can support, and now reads "no bills in this
> registry"), and the version differ is structural rather than sentence-level. A third was
> reversed on 2026-08-11: the equal-area tile grid is gone, replaced by an actual map of the
> United States. The argument here — that a choropleth encodes a quantity it cannot support —
> holds against a colour ramp and was wrongly extended to geography itself; orientation is the
> map's assigned job and recognition is the whole of that job. Fill is categorical and counts
> are numerals, so no ramp returns. Last checked
> against the artefact 2026-08-11.

**Status:** draft for review · **Date:** 2026-08-09 · **Owner:** Mitchel (PRISM)

## What we are building

A free, public registry of legislation addressing the **legal status, personhood, and
asserted mental properties of AI systems**, with map / timeline / lineage / provision
views and a downloadable dataset — plus a literature layer mapping the research
landscape around the same question.

**Not** a general AI-legislation tracker. That space is covered (MultiState, IAPP,
Brennan Center, ailawsbystate — 2,000+ bills). Our slice is narrow; our differentiator
is the structural layer on top of it: template families, bill-to-bill lineage, provision
tagging, and **amendment diffs** (introduced → substitute → enacted), which generic
trackers structurally discard.

**Seed dataset:** Appendix A of Smith, Caviola & Alexander (2026), *Denying Personhood
to AI* — 23 bills across 12 states, 2022–May 2026. Austin and Lucius are on the team, so
this is in-house data; Heather Alexander (Laboratory for the Future of Citizenship) is
external and should be credited and kept in the loop.

## Explicitly out of scope for MVP

International law · courts and litigation · federal bills · corporate/lab internal
policies · any scoring, ranking, index, or normative rating of jurisdictions.

Descriptive-first, per the Observatory principle: flat categories, neutral zeros
("no legislation identified", not "behind"), no ordered indicators until credibility
is established.

---

## Phase 1 — Literature grounding · DONE, descoped 2026-08-10

**Scope decision (Mitchel, 2026-08-10):** this project is a policy tracker, not a
literature review. The comprehensive-survey standard applies to **the bills**, not to the
scholarship. Steps 1–2 are done and give us enough grounding; **step 3, the second
snowball round, is cancelled.** A literature layer may return later as an additional
dashboard feature, not as a core output.

Delivered: `literature/reference-register.xlsx` (110 works), `FINDINGS.md`, `TOP20.md`,
`PRIOR-SURVEYS.md`, and — the part that actually feeds Phase 2 — `SCHEMA-NOTES.md`.

*Original plan, retained for reference:*

1. **Extract the scholarly subset** of the paper's ~150 references. Exclude news,
   testimony, tweets, advocacy pages — those are *evidence* about the bills, not
   literature. Expect ~40–60 genuine scholarly works.
2. **Dedupe against the existing DM corpus** (1,280 works, already classified) before
   collecting anything new. The law/philosophy slice likely overlaps substantially —
   check first, don't rebuild.
3. **Snowball, two rounds.** Backward from the anchor legal works (Solum 1992; Chopra &
   White 2011; Salib & Goldstein 2024a/b; Alexander et al. 2026; Arbel et al. 2026);
   forward via citations to those same anchors.
4. **Classify** on a small flat scheme: question addressed (juridical personhood ·
   natural personhood · moral status · liability · rights-of-nature lineage), discipline,
   year, stance-neutral.
5. **Deliverable:** `literature/` — a CSV registry + a 3–5pp written synthesis of what
   the field has and has not addressed, and where the open questions sit.

**Gate:** synthesis reviewed before it informs the provision taxonomy in Phase 2.

## Phase 2 — Schema and seed registry · ~2 days

1. Define the record schema (see below) and write it down as `SCHEMA.md`.
2. Normalise all 23 bills from Appendix A into `registry/bills.json` — hand-verified
   against primary sources (legislature sites), not transcribed on trust.
3. Capture bill **text versions** as separate records: introduced / substitute / enacted,
   each with date and source URL.
4. Registry lives in git as the single source of truth — auditable, diffable, forkable,
   citable. Every future change is a dated commit, which is where trend data comes from.

Schema fields: identity (jurisdiction, bill numbers + companions, session, sponsors,
party) · status + `status_as_of` + `last_verified` · technique (standalone · amends
general "person" definition · amends specific statutes · constitutional amendment ·
hybrid) · provisions (multi-select, flat) · lineage (`family`, `derived_from`) ·
evidence (verbatim clause + citation) · versions.

**Gate:** every record traceable to a primary source URL.

## Phase 3 — Static site and views · ~2–3 days

**Design settled 2026-08-10 — see `PRESENTATION-DESIGN.md`.** Matrix-first landing view,
map demoted to a filter control, version diffs as the signature feature, argument split out
into separate signed commentary, corrections held pending the authors' response.

Built from the registry at build time. No database, no backend.

1. **Per-bill pages first** — these carry the citations and make the resource findable
   and quotable. They matter more than the map.
2. Map (the hook), timeline, provision matrix (state × provision), genealogy graph.
3. Method page: what we track, what we exclude, how classification is decided,
   how to file a correction.
4. Downloadable CSV/JSON — a reusable dataset is a contribution independent of the site.

End of Phase 3 **is** the MVP: a working, populated, reviewable thing.

## Checkpoint — share MVP internally, align on vision · ~1 week elapsed

Share the built MVP with Austin and Lucius (and Heather, as courtesy + credit). Aligning
on a real artefact beats aligning on a proposal — they can see the schema decisions and
push back on taxonomy, framing and scope while it's still cheap to change.

Questions to settle here, not before:

1. Is the provision taxonomy right, and does the lineage/family model hold up?
2. Scope for v1: stay US-state-only, or open a courts or federal track sooner?
3. Who owns ongoing classification review once bills start moving?

**Gate:** do not build the ingestion loop until the schema survives this review.
Automating collection into a schema that's about to change is wasted work.

## Phase 4 — Ingestion loop · ~3–4 days

The part that makes this maintainable rather than a snapshot that rots.

1. LegiScan API (free key, 30k queries/month, full-text search designed for automated
   keyword monitoring). Keyword set: `"legal personhood"` + `"artificial intelligence"`,
   `sentient`, `non-sentient`, `self-aware`, `personhood`.
2. Nightly GitHub Action: sweep → diff against registry → Claude drafts a
   classification → **opens a PR**. Nothing auto-publishes.
3. **Acceptance test:** backtest the sweep against the paper's 23 bills. If it doesn't
   rediscover them, the keyword set is wrong. This is the gate.
4. Document the weekly review ritual (~1–3 hrs/wk Jan–May, near zero off-season).

## Phase 5 — Publish · ~2 days

Deploy alongside the Observatory. Surface `last_verified` dates prominently. Announce
to CDM/PRISM network and the paper's authors. Commit publicly only to the update cadence
we can actually hold.

---

## Sequence summary

```
Phase 1  Lit review ──► synthesis ──► informs taxonomy ──► gate
                                            │
Phase 2  Schema + seed registry ────────────┴───────────► gate
                                            │
Phase 3  Site + views  ═══► MVP ════════════┤
                                            │
CHECKPOINT  share with Austin + Lucius, align on vision ─► gate
                                            │
Phase 4  Ingestion loop (backtest vs 23) ───┴───────────► gate
                                            │
Phase 5  Publish
```

Phases 1 and 2 can overlap; the lit review only needs to land before the provision
taxonomy is frozen.

**To MVP:** ~7–9 working days. **Total build:** ~12–15 working days.
**Ongoing:** ~1–3 hrs/week in session, near zero out of session.

## Decisions needed from Mitchel

1. Is this a PRISM property or a CDM/Observatory track? (Affects where it deploys and
   whose brand carries the accuracy risk.)
2. Who owns the weekly review when we're mid-session and 40 bills are live? Austin is
   the obvious candidate — is that his time to give?
3. Do we commit publicly to a cadence, or ship it "updated when updated"?
4. Name. Working title is descriptive; avoid superlatives.
