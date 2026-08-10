# Phase 3 — concrete build steps

## Progress

- [x] **Step 0** — decisions: Observatory subpath · "AI Legal Status Tracker"
- [x] **Step 1a** — 12 bill texts persisted to `registry/texts/`, `text_path` on 15 version records, diff renderer proven
- [ ] **Step 1b** — TN HB 849 and HB 1455 *introduced* texts (blocked: needs Mitchel)
- [x] **Step 1c** — `derived_from_changes` (13/13 edges labelled) and `watch_dates` (10 events) added and validated
- [x] **Step 2** — build harness: `site/build.py` → `site/dist/`, theme-aware CSS, status triplet, launch config `ai-legal-status` on :5201
- [x] **Step 3** — per-bill pages: 23 pages at `/bills/{id}/`, every field rendered, readable provision labels, citation block; internal link check clean apart from `method/` and `data/` (steps 8–9)
- [ ] **Step 4** — matrix + map filter
- [ ] **Step 5** — version diffs
- [ ] **Step 6** — genealogy graph
- [ ] **Step 7** — watch list
- [ ] **Step 8** — method page
- [ ] **Step 9** — downloads
- [ ] **Step 10** — signed commentary
- [ ] **Step 11** — corrections page (held)
- [ ] **Step 12** — QA


Design settled in `PRESENTATION-DESIGN.md`. This is the work list.

**Shape:** one Python build script reads `registry/bills.json` and writes static HTML into
`site/dist/`. No framework, no npm, no backend, no external requests at runtime. Consistent
with the rest of the repo and with how the Observatory publishes.

---

## Step 0 — Two decisions that block layout

1. **Where it deploys.** A path under the Observatory, or its own domain? This fixes URL
   structure and the canonical citation string, both of which get baked into every page.
2. **The name.** Working title is descriptive. Needed for the header and the citation block.

---

## Step 1 — Data gaps to close first

Three of these are prerequisites for the signature feature, not nice-to-haves.

**1a. Persist the bill texts we already have.** We hold 31 version records but only three
text files on disk (`incoming/`). The rest were pasted into conversation and exist nowhere.
Write them to `registry/texts/{bill_id}--{version}.txt` and add a `text_path` to each
version record. Without this the diff view has nothing to diff.

Texts we can persist now: Idaho HB 720, Utah HB 249 (enrolled), Tennessee Pub. Ch. 781 and
1066, Ohio HB 469, Wisconsin AB 959 and SB 932, Missouri HB 1462, HB 1769 introduced,
HCS 1746 & 1769, SB 859, SB 1474.

**1b. Two texts we do not have, and they are the headline diffs.**

- **TN HB 849 / SB 837 as introduced** — the version containing the fetal-personhood clause
- **TN HB 1455 / SB 1493 as introduced** — the version containing the Class A felony
  training provisions

Both are on `capitol.tn.gov`, which is blocked here. The enacted halves we already hold.
Without the introduced texts, the two best stories in the registry cannot be rendered as
diffs — only described in prose.

**1c. Three new fields.** Small schema additions the views need:

- `derived_from_changes: []` — what mutated between parent and child, for genealogy edge
  labels. The content already exists in the verification notes; it needs lifting into data.
- `watch_dates: [{date, event}]` — dated future events for the watch list.
- `versions[].text_path` — see 1a.

---

## Step 2 — Build harness

`site/build.py`: read registry → render templates → write `site/dist/`.
One stylesheet, theme-aware (light/dark), no web fonts.
Shared header carrying the status triplet: tracker status · published · last verified.

**Done when:** `python3 site/build.py` produces a complete `dist/` with no network calls.

## Step 3 — Per-bill pages (23)

Built first, because everything else links into them. URL `/bills/{id}/`.

Each renders: bill number, state, session, chamber · status with its evidence action line ·
`codified_at` · effective date · the verbatim key clause as a pull-quote · sponsors with
party · provision chips · family and a link to its parent · every version with source link ·
primary and tracker sources · verification status and date · notes · **a suggested citation
block**.

**Done when:** no non-null field is silently dropped, and every page is citable standalone.

## Step 4 — The matrix, and the map as a filter

The landing view. 23 rows × 16 provision columns, plus state, family, status, technique.

- Renders fully as a plain table **without JavaScript**; JS only adds filtering and sort.
- Default order chronological. No "strength" sort — that would be editorial.
- Below ~700px it becomes per-bill cards with provision chips.
- An inline SVG US map beside it acts as a filter control: click a state, filter the rows.
  States with nothing read "no legislation identified".

**Done when:** clicking Missouri shows six rows, including SB 859 with
`addresses_corporate_veil` and the HCS without it, side by side.

## Step 5 — Version diffs — the signature feature

Three bills where we hold both texts (after 1b):

- TN HB 849 / SB 837 — fetal-personhood clause removed
- TN HB 1455 / SB 1493 — felonies converted to a TACIR study agenda
- MO HCS 1746 & 1769 — veil clause deleted, NIST safe harbour and open-source carve-out added

Render with Python's `difflib` at sentence granularity: removals struck through, additions
marked, each labelled with the date and the committee step that produced it.

**Done when:** a reader can see the fetal-personhood clause disappear without reading prose.

## Step 6 — Genealogy graph

13 edges from `derived_from`, grouped into families. Inline SVG, hand-laid — the graph is
small and static, so a layout library is not worth the weight.

Each edge carries its `derived_from_changes` label: *"veil default inverted · human-liability
clause dropped"*. Nodes link to bill pages.

**Done when:** every edge is labelled and each label traces to a verified record.

## Step 7 — Watch list

Ascending dated events from `watch_dates` and `effective_date`: Missouri applicability
28 Aug 2026, Missouri grace period 1 Mar 2027, TACIR report 31 Jan 2027, CA AB 2023 on the
Senate suspense file. Past events greyed, not removed.

## Step 8 — Method page

Scope in and out · source hierarchy · what each provision tag means · what the verification
statuses mean · **inclusion does not imply endorsement** · AI-use disclosure · how to file a
correction · suggested citation · the update cadence we will actually hold.

Mostly assembled from `SCHEMA.md` and `VERIFICATION.md`.

## Step 9 — Downloads

`bills.json` served as-is, plus a generated flat `bills.csv` and a `matrix.csv`.

**Done when:** CSV row counts match the registry and the validator still passes.

## Step 10 — Signed commentary (separate page)

The "Responsibility half degrades as the template travels" argument. Own byline, own date,
linking into records. Not in the primary nav.

## Step 11 — Corrections page (built, held)

Generate from a new `registry/corrections.json` so it is data, not prose. Three columns:
what the source says · what the primary source says · link and date verified. Nothing else.

Held until Austin, Lucius and Heather have responded. Inline provenance notes on affected
records ship from day one regardless — those are just sourced facts.

## Step 12 — QA before anyone sees it

- Link check: every `sources.primary` and `versions[].source_url` resolves, or is flagged
- 375px mobile pass
- Light and dark
- No external requests
- Table semantics and contrast

---

## Sequencing

```
Step 0 decisions ─┐
Step 1 data gaps ─┴─► Step 2 harness ─► Step 3 bill pages ─► Step 4 matrix  ═══► reviewable
                                                                  │
                          Steps 5-7 diffs · genealogy · watch list┤
                                                                  │
                          Steps 8-9 method · downloads ───────────┤
                                                                  │
                          Steps 10-11 commentary · corrections ───┤
                                                                  │
                                                       Step 12 QA ─► checkpoint
```

Steps 2–4 are the reviewable core. Everything after is additive, so the MVP can go to
Austin and Lucius after Step 4 if you would rather get feedback early than ship complete.

**Estimate:** steps 2–4 about a day. Steps 5–9 another day and a half. Steps 10–12 half a
day. Step 1b depends on you getting the two Tennessee introduced texts.
