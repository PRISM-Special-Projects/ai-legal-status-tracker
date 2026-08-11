# Source-to-record audit protocol

The registry's architecture can now be trusted to report what the registry says. That is not the
same as knowing the registry is right. Every field in it was compiled with AI assistance and
checked by the same party that compiled it, so the corpus has never had an independent read.

This protocol produces one. It is deliberately small: no new tooling beyond two standard-library
scripts, no schema layer, no dashboard.

## The one design decision that matters

**The auditor never sees the recorded value before writing down what the source says.**

A sheet that asks "the registry says the sponsor is Kilmartin — does that match?" reliably produces
agreement, because confirming is easier than reconstructing. So each sheet contains the source URLs
and the questions, and *not* the answers. The auditor reads the source, fills in the blanks, and a
script does the comparison afterwards.

This is the whole methodological content of the protocol. Everything else is bookkeeping.

Two fields escape it, and saying so is better than pretending otherwise. The heading has to name
the record, so it prints the recorded `bill_number` — which is why `bill_number` is one of the five
fields never scored. And the `status_stage` question has to print the controlled vocabulary; it
prints all six values, so it points at none. `audit/test_audit.py` asserts both — that no other
recorded value appears in a generated sheet, and that no sheet prints a subset of the stage
vocabulary.

## Who can run it

Anyone with the source documents: the project lead, an external reviewer with browsing, or a
colleague. It is designed to be readable with a bill page open in the next tab and no knowledge of
this repository's schema.

An auditor who has already read `bills.json` for a given record should not audit that record.

## Procedure

```bash
python3 audit/make_sheets.py              # writes audit/sheets/<record-id>.md
python3 audit/make_sheets.py --batch secondary   # just the priority batch
```

For each sheet:

1. Open the source URLs listed at the top. Prefer the legislature's own page or the enacted act
   over any tracker.
2. Answer every `answer.*` line. Leave the value exactly as the source states it — do not tidy,
   expand abbreviations, or convert formats.
3. Where the source does not state something, write `NOT STATED`. Where you cannot reach the
   source, write `UNREACHABLE`. **Do not guess and do not infer from context.** An honest
   `NOT STATED` is the most valuable answer this instrument can collect, because it distinguishes
   a wrong record from an unsupported one.
4. Save the sheet in place.

Then:

```bash
python3 audit/check_sheet.py audit/sheets/sc-hb3796-2025.md
python3 audit/check_sheet.py --all
```

The checker prints agreements, mismatches and gaps, and writes `audit/results/<record-id>.json`.

## Decision rules

| Checker verdict | Meaning | What happens next |
|---|---|---|
| `match` | Source and record agree | Nothing. Record the audit date. |
| `mismatch` | Source states something different | **The record is wrong until shown otherwise.** Fix the registry, and log it in `VERIFICATION.md` with the date and what changed — never silently. |
| `not_stated` | The source does not support the recorded value | The record is not necessarily wrong, but it is unsourced. Either find a source that states it or downgrade the field's verification level. |
| `unreachable` | Source could not be retrieved | Not a finding about the record. Note it and move on; `registry/NEEDED.md` exists for this. |
| `extra` | Source states something the record omits | Fill the gap. Missing `status.evidence` is the commonest case. |
| `review` | Not scored. The two values differ in a way notation alone explains — one of the five review fields, or a sponsor list naming the same people with different completeness | A human accepts or rejects it. Recording an accepted `review` as agreement is fine; recording it as *verified* is not, unless the values are the same fact. |

A field is only *verified* when an auditor who did not compile it extracted the same value from a
primary source. Agreement with a tracker is weaker and should be recorded as such.

## Order of work

Audit in this order, because it front-loads the standing blockers:

1. **The six `secondary_source` records** — `sc-hb3796-2025`, `oh-hb469-2025`, `mo-sb859-2026`,
   `mo-sb1012-2026`, `mn-sf4114-2026`, `ca-sb1119-2026`. Their status was derived from a summary
   page or tracker rather than a recorded legislative action, and none carries an evidence line.
   This is publication blocker one.
2. **The seven enacted laws** — their `codified_at` and `effective_date` are the fields most likely
   to be cited by someone else, and two of seven have `codified_at` taken from the bill rather than
   verified against the code.
3. **Everything else.**

23 records is small enough that sampling is unnecessary, and auditing all of them avoids arguing
about whether the sample was representative.

## Recording the result

`audit/results/*.json` is the machine record. Discrepancies that change the registry must also be
written into `VERIFICATION.md`, which is the project's standing log of its own errors — including
the ones it corrected wrongly and had to retract.

Do not update a record and its audit result in the same commit as the fix without saying which
came first. The point of the exercise is the trail, not the green tick.
