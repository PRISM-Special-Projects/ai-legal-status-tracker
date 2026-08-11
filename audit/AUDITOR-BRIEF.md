# Brief for an auditor

You are being asked to check whether this registry's records match their sources. You are **not**
being asked to review the code, the architecture, or the reports. Those have had three rounds of
review; the data has had none.

## The rule that makes this worth doing

**Do not open `registry/bills.json`, and do not read any record before answering.**

Each sheet in `audit/sheets/` gives you the source URLs and a list of questions. Read the sources,
write down what they say, and stop. A script compares your answers to the registry afterwards.

If you look first, you will confirm rather than reconstruct, and the exercise produces a number
instead of evidence. This project has been caught twice by external review precisely because
internal checks were performed by the party that produced the thing being checked.

## What to do

1. Take the sheets in `audit/sheets/`. The six there now are the priority batch: their status was
   derived from a summary page or a tracker rather than a recorded legislative action, and none
   carries an evidence line.
2. Fill in every `answer.` line from the sources. Copy values as printed — do not tidy or convert.
   Each sheet carries a short **Conventions** section: which source wins, the one field you are
   asked to classify rather than copy, and the dates you must not calculate. Read it once.
3. Write `NOT STATED` where the source is silent, `UNREACHABLE` where you cannot retrieve it,
   `CANNOT TELL` for a provision test you could not apply. **These are the most valuable answers
   you can give**: they separate a wrong record from an unsourced one.
4. Send the filled sheets back as text. They will be committed with your name on them.

Then `python3 audit/check_sheet.py --all` produces the comparison. Verdicts and what happens next
are in `audit/PROTOCOL.md`.

## What the script will and will not decide

It compares mechanically where that is meaningful — disposition, dates, sponsor surnames, the
provision tests — and refuses to for five fields where legal notation varies legitimately
(`bill_number`, `session`, `codified_at`, `status_action`, `operative_quote`). Those are printed
side by side and marked `» review` for a human verdict. An automated equality test on those
produces false mismatches, which would teach you to wave real ones away as formatting.

## If you find something

A `mismatch` means **the record is wrong until shown otherwise**. It gets fixed in the registry and
logged in `VERIFICATION.md` with the date and what changed — this project logs its own errors,
including one correction it made to another researcher's published work and then had to retract.

If a field cannot be established from any public document, that is a finding about the field, not
about you. Say so.
