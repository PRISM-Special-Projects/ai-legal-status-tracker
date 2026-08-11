# Claim-level provenance pilot

This directory implements the **pilot-only** boundary approved at the Workstream F gate. It does not modify the production `registry/bills.json` schema or migrate the corpus.

## Scope

Four records exercise different provenance patterns:

- `wa-hb2029-2025` — a terminal status derived from an official action history plus a sourced session rule.
- `ut-hb249-2024` — current published-code location distinguished from enactment-time bill numbering.
- `tn-sb837-2025` — an effective date derived from an enactment clause plus governor-signature date, alongside separate codification and amendment-mechanism claims.
- `mo-hb1769-2026` — version-specific provision presence, explicit checked absence, and a derived provision-removal event.

## Files

- `source_catalog.json` identifies sources actually used by pilot claims. It is intentionally separate from `literature/csv/Evidence.csv`: the latter is not a complete catalogue of legislative texts, action histories, codes and session rules.
- `claim_evidence.json` contains typed claim selectors and evidence edges. It also contains provisional immutable version IDs for repeated version objects; these are not yet production fields.
- `validate_claim_evidence.py` checks source resolution, direct/derived semantics, explicit negative assessments, required version selectors, the four-record boundary, and stale values for scalar fields already present in `bills.json`.

## Semantics

`mode: direct` means the cited source itself records or states the supported proposition.

`mode: derived` means the registry reaches the asserted value by combining cited inputs. A derivation statement is mandatory. In this pilot, derived claims require at least two supports.

`assessment: checked_absent` is an explicit negative textual finding. Missing claim evidence means only **unmapped / not assessed**; it must never be interpreted as absence.

Source identity and claim support are separate. A source may be official and relevant to a bill without supporting a particular displayed claim.

## Deliberate limitations

This is not a generic claim graph and does not replace the bill-centred registry. It does not yet change site rendering. It does not yet add production `version_id` or `sponsor_id` fields. It does not migrate the remaining records.

The next gate is a post-pilot review after validation and one bill-detail rendering experiment. Corpus-wide migration remains blocked until that review passes.

## Run

From the repository root:

```bash
python registry/pilot/validate_claim_evidence.py
```
