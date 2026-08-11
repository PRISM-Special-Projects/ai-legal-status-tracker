# Claim-level provenance pilot

This directory implements the **pilot-only** boundary approved at the Workstream F gate. It does not modify the production `registry/bills.json` schema or migrate the corpus.

## Scope

Four records exercise different provenance patterns:

- `wa-hb2029-2025` — a terminal status derived from official action history, the official 2025→2026 carryover resolution, and the official 2026 sine-die record.
- `ut-hb249-2024` — current published-code location distinguished from enactment-time bill numbering.
- `tn-sb837-2025` — an effective date derived from an enactment clause plus governor-signature date, alongside separate codification and amendment-mechanism claims.
- `mo-hb1769-2026` — version-specific provision presence, explicit checked absence, and a derived provision-removal event.

## Files

- `source_catalog.json` identifies sources actually used by pilot claims. It is intentionally separate from `literature/csv/Evidence.csv`: the latter is not a complete catalogue of legislative texts, action histories, codes and session records.
- `claim_evidence.json` contains typed claim selectors and evidence edges. It also contains provisional immutable version IDs for repeated version objects; these are not yet production fields.
- `validate_claim_evidence.py` checks source resolution, direct/derived semantics, explicit negative assessments, registered version selectors, the four-record boundary, duplicate selectors, and stale values for scalar fields already present in `bills.json`.
- `../../site/pilot_claim_evidence.py` is the one-record rendering experiment. It patches only the generated TN SB 837 page **after** a normal build; production `site/build.py` remains unchanged.
- `../../.github/workflows/claim-provenance-pilot.yml` runs the validator, a normal site build, the one-record renderer, and render assertions on push and pull request.

## Semantics

`mode: direct` means the cited source itself records or states the supported proposition.

`mode: derived` means the registry reaches the asserted value by combining cited inputs. A derivation statement is mandatory. In this pilot, derived claims require at least two supports.

`assessment: checked_absent` is an explicit negative textual finding. Missing claim evidence means only **unmapped / not assessed**; it must never be interpreted as absence.

`assessment: present` is an explicit positive textual finding and must carry `value: true`.

Source identity and claim support are separate. A source may be official and relevant to a bill without supporting a particular displayed claim.

## Deliberate limitations

This is not a generic claim graph and does not replace the bill-centred registry. It does not yet add production `version_id` or `sponsor_id` fields. It does not migrate the remaining records. The rendered evidence panel is an experiment on one generated page, not a production-wide UI feature.

Corpus-wide migration remains blocked until the post-pilot review passes.

## Run

From the repository root:

```bash
python registry/pilot/validate_claim_evidence.py
python site/build.py
python site/pilot_claim_evidence.py
```
