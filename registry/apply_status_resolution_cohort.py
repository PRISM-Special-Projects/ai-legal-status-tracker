#!/usr/bin/env python3
"""One-time gated migration for MO SB 1012 and CA SB 1119 status provenance."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BILLS = ROOT / "bills.json"
SOURCES = ROOT / "source_catalog.json"
CLAIMS = ROOT / "claim_evidence.json"
DOC = ROOT.parent / "CLAIM_EVIDENCE.md"
TODAY = "2026-08-11"

bdata = json.loads(BILLS.read_text())
sdata = json.loads(SOURCES.read_text())
cdata = json.loads(CLAIMS.read_text())
by_id = {b["id"]: b for b in bdata["bills"]}

mo = by_id["mo-sb1012-2026"]
assert mo["status"]["stage"] == "passed_one_chamber", mo["status"]
assert mo["status"]["basis"] == "secondary_source", mo["status"]
mo["status"] = {
    "stage": "failed",
    "as_of": TODAY,
    "source_url": "https://www.senate.mo.gov/BillTracking/Bills/BillInformation?billid=469&year=2026",
    "evidence": {
        "action": "Voted Do Not Pass H Emerging Issues on 05/12/2026 after Senate passage; 2026 regular session ended without House passage",
        "date": "2026-05-12"
    },
    "basis": "session_rule"
}
mo["last_verified"] = TODAY
mo["verification"]["last_verified"] = TODAY
mo["notes"] = mo["notes"].replace(
    "STATUS AMBIGUOUS: the House Emerging Issues committee returned a Do Not Pass. Whether the Senate passed it first needs a human read of the action history - stage left at passed_one_chamber pending that.",
    "STATUS RESOLVED 2026-08-11: the official Senate history shows Senate third reading and passage on 6 May 2026, followed by a House Emerging Issues hearing and Do Not Pass vote on 12 May. The 2026 regular session then ended without House passage, so the current stage is failed; the historical fact that it passed the Senate is preserved in the action history."
)

ca = by_id["ca-sb1119-2026"]
assert ca["status"]["stage"] == "in_committee", ca["status"]
assert ca["status"]["basis"] == "secondary_source", ca["status"]
ca["status"] = {
    "stage": "in_committee",
    "as_of": TODAY,
    "source_url": "https://www.senate.ca.gov/system/files/2026-07/sds-7-2-2026.pdf",
    "evidence": {
        "action": "From committee: Do pass and re-refer to Com. on APPR. (Ayes 12. Noes 2.) (July 1). Re-referred to Com. on APPR.",
        "date": "2026-07-02"
    },
    "basis": "explicit_action"
}
ca["last_verified"] = TODAY
ca["verification"]["last_verified"] = TODAY
ca["notes"] += " STATUS RE-CONFIRMED 2026-08-11 from the official California Senate Daily Summary for 2 July 2026: Assembly committee do-pass, 12-2, and re-referral to Appropriations."

new_sources = [
    {
        "id": "mo-sb1012-actions",
        "label": "Missouri Senate — SB 1012 bill information and actions",
        "kind": "action_history",
        "url": "https://www.senate.mo.gov/BillTracking/Bills/BillInformation?billid=469&year=2026",
        "jurisdiction": "MO",
        "note": "Official bill page showing Senate passage and House Emerging Issues Do Not Pass action."
    },
    {
        "id": "mo-2026-session-end",
        "label": "Missouri Senate — 2026 regular-session end report",
        "kind": "session_record",
        "url": "https://www.senate.mo.gov/Media/NewsDetails?id=2349",
        "jurisdiction": "MO",
        "note": "Official Senate report stating the 2026 session is over and bills that did not pass must be refiled."
    },
    {
        "id": "ca-sb1119-july2-summary",
        "label": "California Senate — Daily Summary for July 2, 2026",
        "kind": "action_history",
        "url": "https://www.senate.ca.gov/system/files/2026-07/sds-7-2-2026.pdf",
        "jurisdiction": "CA",
        "note": "Official Daily Summary recording SB 1119's Assembly do-pass vote and re-referral to Appropriations."
    }
]
existing_sources = {s["id"] for s in sdata["sources"]}
for source in new_sources:
    if source["id"] not in existing_sources:
        sdata["sources"].append(source)

records = {r["record_id"]: r for r in cdata["records"]}
assert "mo-sb1012-2026" not in records
assert "ca-sb1119-2026" not in records
cdata["records"].extend([
    {
        "record_id": "mo-sb1012-2026",
        "claims": [{
            "claim": {"field": "status.stage"},
            "value": "failed",
            "mode": "derived",
            "supports": [
                {"source_ref": "mo-sb1012-actions", "locator": "2026-05-06 Senate third read and passed; 2026-05-12 House Emerging Issues voted Do Not Pass"},
                {"source_ref": "mo-2026-session-end", "locator": "2026 regular session ended; unpassed bills must be refiled"}
            ],
            "derivation": "SB 1012 passed the Senate but did not pass the House before the 2026 regular session ended; it therefore failed while retaining passed-one-chamber as a historical event, not the current stage."
        }]
    },
    {
        "record_id": "ca-sb1119-2026",
        "claims": [{
            "claim": {"field": "status.stage"},
            "value": "in_committee",
            "mode": "direct",
            "supports": [{
                "source_ref": "ca-sb1119-july2-summary",
                "locator": "SB 1119 — Assembly Jul 2: do pass 12-2 and re-refer to Appropriations"
            }]
        }]
    }
])

text = DOC.read_text()
text = text.replace("Eight records currently have structured claim-level evidence.", "Ten records currently have structured claim-level evidence.")
old = "`mo-sb1012-2026` was deliberately excluded from that cohort because its House Do Not Pass action\nand completed session require a separate terminal-stage classification review. `ca-sb1119-2026`\nwas also excluded because the retrievable live LegInfo status surface was stale relative to the\nlater amendment history already documented in the audit."
new = "A third bounded status-resolution cohort, promoted on 2026-08-11, closes the two exclusions from that screen:\n\n- `mo-sb1012-2026` — corrected from historical `passed_one_chamber` to current `failed`, using Senate passage, the House Do Not Pass action, and session-end evidence;\n- `ca-sb1119-2026` — retained `in_committee` but replaced secondary status basis with the official 2 July Senate Daily Summary recording re-referral to Assembly Appropriations."
assert old in text
text = text.replace(old, new)

BILLS.write_text(json.dumps(bdata, indent=2, ensure_ascii=False) + "\n")
SOURCES.write_text(json.dumps(sdata, indent=2, ensure_ascii=False) + "\n")
CLAIMS.write_text(json.dumps(cdata, indent=2, ensure_ascii=False) + "\n")
DOC.write_text(text)
print("remaining secondary-status cohort applied")
