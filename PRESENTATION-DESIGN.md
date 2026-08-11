# Phase 3 — presentation design

> **Planning record, superseded.** This is the design document as written before the build, kept
> for the decision trail. Where it disagrees with the artefact, the artefact governs — see
> `README.md`, `IMPLEMENTATION-REPORT.md` and `DIFF-REPORT.md`. Two decisions recorded here were
> reversed after external review: the state tiles no longer say "no legislation identified" (it
> claims more than the inclusion methodology can support, and now reads "no bills in this
> registry"), and the version differ is structural rather than sentence-level. Last checked
> against the artefact 2026-08-11.

Draft for the checkpoint. 23 verified records, 16 provision tags, 13 lineage edges,
three genuine amendment diffs, five corrections to the source paper (a sixth was
claimed here and later retracted — see `VERIFICATION.md`).

## The central call: the map is not the hero

A choropleth is the obvious hook and the weakest thing we have. It shows 12 of 50 states,
renders Missouri's six bills as one flat colour, cannot show that Missouri simultaneously
runs vehicles with and without the corporate-veil clause, and says nothing about the
amendment diffs that are our actual differentiator.

**Use the map for orientation and navigation. Make the provision matrix the spine and the
version diff the signature.**

## Three depths on one spine

### 1. Orientation — "what is happening"

- Count and scope stated plainly: *23 bills across 12 states since 2022.* No "first",
  no "largest". Let the number do the work.
- **Map**, with a dot cluster per state rather than a flat fill, so Missouri reads as six
  and Idaho as one. States with nothing say **"no legislation identified"** — a neutral
  zero, not "behind".
- **Timeline**, 2022 → 2026, one mark per bill, coloured by status. The acceleration is
  real and needs no commentary.
- **Status triplet** in the header, borrowed from Lee: `Tracker status` · `Published` ·
  `Last verified`. Honest about staleness before anyone has to ask.

### 2. Comparison — the analytical spine

**The provision matrix: 23 bills × 16 provision tags.** Filterable by state, family,
status, provision. This is the workhorse and almost nobody builds one.

It earns its place immediately: it shows at a glance that Family C is *not* homogeneous —
Wisconsin's row is missing `assigns_liability_to_humans`, Ohio's carries
`addresses_corporate_veil` where the Missouri substitute does not. The paper's three-family
taxonomy is a useful simplification; the matrix is what the simplification costs.

**Ordering rule: chronological, never by "strength".** Sorting rows so the pattern looks
like decline is editorial. Sort by date and the reader sees it anyway.

**A definitions panel.** Four AI definitions side by side — Ohio's "rules-based logic",
Missouri's homegrown original, Missouri's substituted federal 15 U.S.C. § 9401(3),
Wisconsin's OECD/EU AI Act formulation. Cheap to build, unusually informative, and it makes
the overbreadth critique legible without us having to assert it.

### 3. Evidence — per-bill pages

The citable unit. Verbatim key clause, statutory citation, effective date, sponsors, votes,
full source links, `last_verified`, and a suggested citation. These are what make it a
resource rather than a dashboard, and what makes it findable.

## The signature feature: version diffs

Three bills changed materially between introduction and enactment, and we hold both texts:

- **TN HB 849 / SB 837** — the fetal-personhood clause removed
- **TN HB 1455 / SB 1493** — Class A felonies converted into a TACIR study agenda
- **MO HCS 1746 & 1769** — corporate-veil clause deleted, NIST safe harbour and
  open-source carve-out added

Render these as an actual inline diff: struck-through removals, marked additions, dated,
with the committee step named. No other tracker in this space does this, and it is the
single most defensible reason for the project to exist.

## The genealogy graph, done better than the paper's

The paper's Figure 2 shows *that* bills descend from one another. Ours can show **what
mutated in transit** — annotate each edge with the factual change:

```
MO HB 1462 ──▶ OH HB 469     veil default inverted · human-liability clause dropped
MO HB 1462 ──▶ MO HCS        veil clause deleted · NIST safe harbour added
MO HB 1462 ──▶ WI AB 959     definition replaced (OECD) · no affirmative human liability
ID HB 720  ──▶ UT HB 249     taxonomic anchor added · saving clause → prospective-only
```

Every label is a checkable fact about text. The gradient emerges from the edges without us
naming it.

**Drafting provenance is worth surfacing here too.** Identical text under different draft
numbers — MO 4626H.01I / 4600S.01I / 6352S.01I, WI LRB-5476/1 / LRB-6000/1 — shows
diffusion by independently commissioned drafts rather than a circulated file. It is a
stronger claim than "copy-and-paste" and it lives entirely in metadata.

## A watch list nobody else has

Forward-looking dated events, pulled straight from the registry:

- **31 Jan 2027** — Tennessee TACIR report due to the governor and both speakers
- **28 Aug 2026** — Missouri applicability date
- **1 Mar 2027** — Missouri compliance grace period ends
- CA AB 2023 on the Senate Appropriations suspense file since 3 Aug 2026

Trackers are almost always retrospective. A short "what happens next" panel is cheap,
genuinely useful, and gives people a reason to return.

## Presenting the corrections

Six corrections, and the framing matters because Austin and Lucius are colleagues.

**Frame it as what it is: a live registry extending a snapshot.** The paper is a May 2026
cross-section; the tracker is continuous. Corrections are the expected product of ongoing
verification, not a critique. Bills genuinely moved after publication — Washington was
reintroduced, two California bills advanced.

**Two placements:**

1. **Inline, on the affected record.** A neutral provenance note: *"Smith, Caviola &
   Alexander (2026) record this bill as Failed. Verified against the Washington
   Legislature bill history, 10 Aug 2026: reintroduced and retained in present status,
   12 Jan 2026."* Source link, verification date, no adjective.
2. **One corrections page**, in a fixed three-column form: **what the source says · what
   the primary source says · link and date verified.** Nothing else. No commentary column
   — the moment there is one, it reads as scorekeeping.

**Separate the substantive extensions from the corrections.** The veil inversion, the
alignment-washing clause, the NIST safe harbour and the drafting-provenance pattern are not
corrections — they are new findings the paper had no reason to cover. Mixing them into a
"corrections" list would overstate the error rate and understate the contribution. Two
distinct pages: *Corrections* and *What the registry adds*.

## Explicitly ruled out

- Any score, index, ranking, or "protectiveness" rating of states or bills
- Ordering that implies a normative direction
- Predicting whether a bill will pass
- Asserting that a bill is unconstitutional — we record claims with attribution only
- Superlatives in the copy: give the count and the scope

## Build shape

Static site generated from `registry/bills.json` at build time. No backend, no database.
Per-bill pages, matrix and graph all derived from the one file, so the registry stays the
single source of truth and every change remains a dated commit. Downloadable CSV and JSON
alongside — the dataset is a contribution independent of the site.

## Decisions (Mitchel, 2026-08-10)

**1. Matrix-first.** The provision matrix is the landing view; the map sits beside it as a
navigation aid, not a hero. We lead with what the data actually supports.

**2. The argument lives in a separate signed piece.** The tracker stays purely descriptive —
matrix, diffs, genealogy, per-bill pages, all factual and checkable. "The Responsibility
half degrades as the template travels" goes in a dated, signed commentary that links back
to individual records. This keeps the registry usable by people who *support* these bills,
which roughly doubles its audience and is the main protection against PRISM being read as
an advocacy shop.

**3. Authors get first refusal on the corrections.** Austin, Lucius and Heather see the six
corrections before launch and can issue an updated SSRN version. The tracker cites the
verified facts either way; only the *corrections page* waits. If the paper is updated
first, the page reframes from "corrections" to "changes since publication", which is better
for everyone.

## What this means for the build

- The landing page is the matrix. It must be legible on a phone, which means the 23×16 grid
  needs a compact mobile form — probably per-bill cards with provision chips below ~700px,
  and the full grid above it.
- The map is demoted to a filter control. Clicking a state filters the matrix. That solves
  the Missouri problem: the state is a filter, the bills are the rows.
- The signed commentary is a separate page with its own byline and date, linking into
  per-bill records. It is not in the site nav's primary position.
- The corrections page is built but unpublished at launch, behind the authors' response.
  Records still carry inline provenance notes from day one, since those are just sourced
  facts.

## Build order

1. Per-bill pages — the citable unit, and everything else links into them
2. Provision matrix + map-as-filter — the landing view
3. Version diffs for the three bills where we hold both texts
4. Genealogy graph with annotated edges
5. Watch list
6. Method page: scope, source hierarchy, inclusion-does-not-imply-endorsement, AI-use
   disclosure, corrections route, suggested citation
7. CSV/JSON download
8. Signed commentary (separate)
9. Corrections page (held)
