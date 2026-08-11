# Claim-level provenance

`registry/bills.json` remains the authoritative, bill-centred domain registry. Claim-level
provenance is a sidecar layer that records which source(s) actually support selected structured
claims. It does **not** turn the registry into a generic claim graph.

## Files

- `registry/source_catalog.json` — sources actually used by claim mappings. Each source has a
  stable `id`, a human-readable `label`, a `kind`, and either a URL or a repository reference.
- `registry/claim_evidence.json` — typed claim selectors, asserted values and support edges.
- `registry/validate_claim_evidence.py` — referential, semantic and stale-value checks.

## Semantics

`mode: direct` means the cited source itself states or records the supported proposition.

`mode: derived` means the registry reaches the value by combining cited inputs. A short
`derivation` is mandatory and every evidentiary input actually relied upon must be listed.

`assessment: present` is an explicit positive textual assessment and carries `value: true`.

`assessment: checked_absent` is an explicit negative textual assessment and carries
`value: false`. A missing claim-evidence entry means **unmapped / not assessed**, never absent.

A source being official or relevant to a bill does not mean it supports every claim on that
record. Source identity and claim support are separate.

## Typed selectors

Scalar claims use a field selector such as:

```json
{"field": "effective_date"}
```

Claims on repeated version objects use a stable version identifier plus the property or item
being assessed:

```json
{"field": "provisions", "version_id": "mo-hb1769-4626H.01I",
 "item": "addresses_corporate_veil"}
```

`versions[].version_id` is now a first-class property in `registry/bills.json`. The first four
audited IDs were promoted from the temporary sidecar map on 2026-08-11, and that map has been
removed. The core registry validator checks ID syntax and repository-wide uniqueness; the claim
validator resolves version selectors directly against `bills.json`. During incremental migration,
versions not yet addressed by structured provenance may still lack a `version_id`.

## Current migration boundary

Fifteen records currently have structured claim-level evidence.

The first production cohort contains the four records that passed the Workstream F pilot:

- `wa-hb2029-2025` — derived terminal status;
- `ut-hb249-2024` — current code location versus enactment-time numbering;
- `tn-sb837-2025` — derived effective date, statutory destination and amendment mechanism;
- `mo-hb1769-2026` — version-specific provision presence, checked absence and removal.

The second bounded cohort, promoted on 2026-08-11, replaces secondary-basis status assertions
with direct official action-history support where the displayed stage did not need to change:

- `sc-hb3796-2025` — House Judiciary referral;
- `oh-hb469-2025` — House Technology and Innovation referral;
- `mo-sb859-2026` — Senate General Laws hearing conducted;
- `mn-sf4114-2026` — Senate Judiciary and Public Safety referral.

A third bounded status-resolution cohort, promoted on 2026-08-11, closes the two exclusions from that screen:

- `mo-sb1012-2026` — corrected from historical `passed_one_chamber` to current `failed`, using Senate passage, the House Do Not Pass action, and session-end evidence;
- `ca-sb1119-2026` — retained `in_committee` but replaced secondary status basis with the official 2 July Senate Daily Summary recording re-referral to Assembly Appropriations.


A fourth bounded enacted-law cohort, promoted on 2026-08-11, maps codification and effective-date provenance and corrects two stale citations/dates:

- `id-hb720-2022` — enactment-time § 5-346 destination and 1 July 2022 effective date mapped; direct official live-code inspection remains a documented access limitation, so `codified_at_source` remains `bill`;
- `nd-hb1361-2023` — current official Century Code location corrected from enactment-time § 1-01-49(8) to current § 1-01-49(17), with both states preserved; effective date mapped from the emergency/final-action record;
- `ut-hb249-2024` — 1 May 2024 effective date added to the already mapped code provenance;
- `tn-hb849-2025` — Public Chapter 781 codification and 23 April 2026 effective date mapped using the enacted companion record;
- `tn-hb1455-2025` / `tn-sb1493-2025` — corrected effective date from 23 April (final legislative passage) to 22 May 2026 (governor signature/effective date), with Public Chapter 1066 dated 27 May; uncodified status and enacted-stage provenance mapped.

Corpus-wide mapping remains intentionally incremental. The next expansion should prioritise
high-risk structured facts (`status.stage`, `codified_at`, `effective_date`, and source-observed
version-specific provision assessments) rather than attempting to map every sentence in
`notes`.

## Validation

Run from the repository root:

```bash
python3 registry/validate.py
python3 registry/validate_claim_evidence.py
```

The core validator checks first-class version-ID syntax and repository-wide uniqueness. The
claim validator checks source resolution, source display labels, duplicate claim selectors,
direct/derived semantics, explicit negative assessments, version-ID registration and selected
stale values against `bills.json`.

The migration-preview renderer remains separate from `site/build.py` until the display design
has passed the next gate. This is deliberate: production data can become more precise without
silently changing every public page at the same time.
