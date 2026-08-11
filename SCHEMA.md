# Registry schema v0.1

Source of truth for the AI Legal Status Tracker. One JSON record per **bill number**.

## Counting unit

A record is a single bill number, not a legislative vehicle. Companion bills (Tennessee
HB 849 / SB 837, Wisconsin AB 959 / SB 932) get **one record each**, linked by
`companion_group`. This reproduces the paper's count of 23 bills across 12 states and lets
the UI group or ungroup as needed.

## Record

| Field | Type | Notes |
|---|---|---|
| `id` | string | `{state}-{billnum}-{year}`, lowercase, e.g. `id-hb720-2022` |
| `jurisdiction` | object | `{country, state, level}` |
| `bill_number` | string | As cited by the legislature |
| `chamber` | enum | `house` · `senate` · `joint` |
| `session` | object | `{legislature, session, year_introduced}` |
| `companion_group` | string¦null | Shared key across companion bills |
| `status` | object | `{stage, as_of, source_url}` |
| `codified_at` | string¦null | Statutory citation once enacted |
| `family` | enum | `A` · `B` · `C` · `other` |
| `derived_from` | string¦null | `id` of the template parent → genealogy graph |
| `derived_from_changes` | array | What mutated between parent and child; becomes the genealogy edge label. Required whenever `derived_from` is set |
| `watch_dates` | array | `{date, event, kind}` — dated future events. `kind`: `effective` · `expiry` · `report` · `ballot` · `deadline` |
| `technique` | enum | see below |
| `provisions` | array | flat multi-select, see below |
| `definitional_anchor` | enum | `taxonomic` · `enumerated_only` · `none` · `unknown` |
| `augmented_human_exposure` | enum | `anchored` · `unanchored` · `unclear` |
| `affects_algorithmic_entity_formation` | enum | `bars` · `does_not_bar` · `untested` · `not_analysed` |
| `corporate_carve_out` | enum | `express_saving_clause` · `prospective_only` · `none` · `unknown` |
| `constitutional_exposure` | array | `{amendments[], claimed_by}` — claims recorded, never our own conclusion |
| `sponsors` | array | `{name, party, role}`; empty if not established |
| `versions` | array | `{version_id?, label, date, source_url, text_path}` — introduced → substitute → enacted. `version_id` is an immutable identifier for versions addressed by provenance/diffs; it is unique repository-wide. During incremental migration it may be absent from versions not yet addressable by structured provenance. `text_path` points at the stored text under `registry/texts/` |
| `key_clause` | object¦null | `{text, source}` verbatim |
| `evidence_refs` | array | `ref_key`s into the Evidence sheet |
| `sources` | object | `{primary[], tracker[]}` |
| `provenance` | string | Where the record came from |
| `verification_status` | enum | How the **status** was established: `verified_primary` · `verified_secondary` · `seeded_unverified`. It has never meant that every version was read |
| `verification` | object | Per-dimension provenance: `{status, operative_text, operative_text_note, sponsors, codified_at_source, versions_with_text, last_verified}`. `operative_text`: `read_in_full` · `partial` · `not_read` — a note is required unless `read_in_full` |
| `last_verified` | date¦null | Null until someone reads the primary source |
| `notes` | string | |

## Controlled vocabularies

**`status.stage`** — `introduced` · `in_committee` · `passed_one_chamber` · `enacted` ·
`failed` · `dead`

**`technique`** — `standalone_provision` · `amends_general_person_definition` ·
`amends_specific_statutes` · `constitutional_amendment` · `hybrid`

**`provisions`** — `denies_legal_personhood` · `declares_non_sentient` ·
`assigns_liability_to_humans` · `restricts_ai_speech_rights` · `restricts_chatbot_claims` ·
`restricts_person_like_training` · `covers_non_ai_entities` · `study_only` ·
`bars_marriage_or_union` · `bars_property_ownership` · `bars_corporate_office` ·
`imposes_safety_duties` · `incident_reporting_duty` · `addresses_corporate_veil` ·
`bars_ai_liability` · `provides_compliance_safe_harbor` · `defines_human_to_include_unborn` ·
`creates_criminal_offence` · `creates_private_right_of_action`

Operational tests, with negative examples, are in `PROVISIONS.md`. A tag may not be added
without an entry there in the same commit.

**These are authoritative.** `registry/validate.py` must accept exactly this set and no other;
a drift check belongs in CI.

## Rules

1. **Flat and descriptive.** No scoring, ranking, or index. Every tag must be checkable
   against bill text by two people reaching the same answer.
2. **Never invent.** Unknown is `null` or `unknown`, never a guess. An empty `sponsors`
   array means not established, not that there are none.
3. **`constitutional_exposure` records claims, with attribution.** We never assert that a
   bill is unconstitutional.
4. **Versions are records, not a field.** The diff between introduced and enacted is where
   the story lives — Tennessee's dropped fetal clause, Missouri's committee substitute.
5. **`verification_status` is honest.** `seeded_unverified` until a human has opened the
   primary source. Do not publish unverified records without labelling them.

## Files

```
registry/bills.json      the registry
registry/validate.py     schema + vocabulary + referential checks
registry/texts/          stored bill texts, {bill_id}--{version}.txt
registry/incoming/       source documents as retrieved (PDFs)
```

Stored texts are **normalised**: line numbers, page furniture and running headers removed,
wording untouched. They exist so versions can be diffed; the authoritative document is always
the `source_url`.

## Changelog

**v0.2.0 provenance migration (2026-08-11).** `versions[].version_id` is now a first-class immutable identifier for version objects addressed by claim-level provenance. Four audited IDs were promoted from the temporary sidecar map; the core validator enforces syntax and repository-wide uniqueness for IDs as they are added. The sidecar mapping has been removed.

**v0.1.4 → v0.2.0 (2026-08-10, after external red-team review).** Added the `verification`
object. `verification_status` alone was carrying far more epistemic weight than the evidence
model supported — it described how a *status* was established, but the site read it as "every
record read against its bill text", which was false for seven records. Verification is now
recorded per dimension. Also: `bars_ai_liability` and `provides_compliance_safe_harbor` were
live in the validator but missing from the vocabulary above; `as_of` renamed to
`baseline_snapshot` to stop it being read as the registry's currency date.

**Codification rule.** For an enacted law, `codified_at` must be verified against the **code**,
not the bill. Utah HB 249's enrolled text says it enacts §§ 63G-31-101/102; the published Code
renumbered it to §§ 63G-32-101/102. The bill states intent, the code states the result.

**v0.1.3 → v0.1.4 (2026-08-10).** Added `versions[].text_path`, `derived_from_changes` and
`watch_dates`. All three exist to make Phase 3 views derivable from the registry alone rather
than from prose in `notes`. The validator now requires a label on every lineage edge, checks
watch-date shape, and confirms every `text_path` resolves on disk.

**v0.1.2 → v0.1.3 (2026-08-10).** Six provision tags added after reading Ohio HB 469 in full:
`bars_marriage_or_union`, `bars_property_ownership`, `bars_corporate_office`,
`imposes_safety_duties`, `incident_reporting_duty`, `addresses_corporate_veil`. The Family C
bills do considerably more than deny personhood and declare non-sentience, and three tags on a
twelve-section bill was losing most of what it actually does. Family C records other than Ohio
still carry the old three tags and must be re-tagged as each is verified.

**v0.1.1 → v0.1.2 (2026-08-10).** Added `verified_secondary` to `verification_status`. Some
legislature hosts are unreachable, and a tracker record (LegiScan) can establish session-law
chapter, effective date, sponsors and vote counts even when the enrolled text cannot be read.
That is a real and distinct state: better than seeded, weaker than primary. It must never be
silently promoted to `verified_primary`.

**v0.1 → v0.1.1 (2026-08-10).** Added `effective_date` (string¦null). Discovered during
verification of Utah HB 249: the enrolled text carries an effective date (1 May 2024) that
appears nowhere in the bill status page or the paper, and a legal registry needs it.

**Known limitation (2026-08-10).** `provisions` describes the record's *operative* text only.
Missouri HB 1769 carried `addresses_corporate_veil` as introduced and lost it in committee, and
that is currently captured in prose rather than structurally. Per-version provision tags are the
obvious fix and should be considered at the checkpoint — the diff is the product.

**Verification note.** The primary URLs in the paper point at bill *status* pages, not bill
*text*. Version records need document-level URLs (e.g. Utah's enrolled PDF at
`le.utah.gov/~2024/bills/hbillenr/HB0249.pdf`). Capture both: `sources.primary` for the
landing page, `versions[].source_url` for the actual document.
