#!/usr/bin/env python3
"""One-time gated migration for four primary-supported status claims.

Updates bills.json status evidence/basis, appends source-catalog entries and claim-evidence
records, and expands the claim validator's mapped-record set. Idempotent by record/source id.
"""
from __future__ import annotations

import json
from pathlib import Path

REG = Path(__file__).resolve().parent

COHORT = {
    "sc-hb3796-2025": {
        "source": {
            "id": "sc-hb3796-actions",
            "label": "South Carolina Legislature — H. 3796 status and action history",
            "kind": "action_history",
            "url": "https://www.scstatehouse.gov/sess126_2025-2026/bills/3796.htm",
            "jurisdiction": "SC",
            "note": "Official bill page showing referral to House Judiciary on 28 January 2025 and no later action."
        },
        "stage": "in_committee",
        "action": "Referred to Committee on Judiciary",
        "date": "2025-01-28",
        "locator": "2025-01-28 — Referred to Committee on Judiciary"
    },
    "oh-hb469-2025": {
        "source": {
            "id": "oh-hb469-status",
            "label": "Ohio Legislature — HB 469 status",
            "kind": "action_history",
            "url": "https://www.legislature.ohio.gov/legislation/136/hb469/status",
            "jurisdiction": "OH",
            "note": "Official status page showing referral to House Technology and Innovation on 1 October 2025."
        },
        "stage": "in_committee",
        "action": "Referred to committee — Technology and Innovation",
        "date": "2025-10-01",
        "locator": "2025-10-01 — Referred to committee — Technology and Innovation"
    },
    "mo-sb859-2026": {
        "source": {
            "id": "mo-sb859-actions",
            "label": "Missouri Senate — SB 859 bill information and actions",
            "kind": "action_history",
            "url": "https://www.senate.mo.gov/BillTracking/Bills/BillInformation?billid=378&year=2026",
            "jurisdiction": "MO",
            "note": "Official bill page; daily action record shows hearing conducted in Senate General Laws on 4 March 2026."
        },
        "stage": "in_committee",
        "action": "Hearing Conducted S General Laws Committee",
        "date": "2026-03-04",
        "locator": "2026-03-04 — Hearing Conducted S General Laws Committee"
    },
    "mn-sf4114-2026": {
        "source": {
            "id": "mn-sf4114-status",
            "label": "Minnesota Revisor — SF 4114 Senate status",
            "kind": "action_history",
            "url": "https://www.revisor.mn.gov/bills/94/2026/0/SF/4114?body=Senate&view=chrono",
            "jurisdiction": "MN",
            "note": "Official Revisor status page showing introduction and referral to Judiciary and Public Safety on 4 March 2026."
        },
        "stage": "in_committee",
        "action": "Referred to Judiciary and Public Safety",
        "date": "2026-03-04",
        "locator": "2026-03-04 — Introduction and first reading; referred to Judiciary and Public Safety"
    },
}


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    bills_path = REG / "bills.json"
    cat_path = REG / "source_catalog.json"
    ev_path = REG / "claim_evidence.json"
    val_path = REG / "validate_claim_evidence.py"

    bills = load(bills_path)
    catalog = load(cat_path)
    evidence = load(ev_path)
    bill_by_id = {b["id"]: b for b in bills["bills"]}

    for rid, cfg in COHORT.items():
        bill = bill_by_id.get(rid)
        if bill is None:
            raise SystemExit(f"missing cohort record {rid}")
        if bill["status"]["stage"] != cfg["stage"]:
            raise SystemExit(f"{rid}: stage changed unexpectedly: {bill['status']['stage']!r}")
        bill["status"]["evidence"] = {"action": cfg["action"], "date": cfg["date"]}
        bill["status"]["basis"] = "explicit_action"
        bill["status"]["as_of"] = "2026-08-11"
        bill["last_verified"] = "2026-08-11"
        if isinstance(bill.get("verification"), dict):
            bill["verification"]["status"] = "verified_primary"
            bill["verification"]["last_verified"] = "2026-08-11"

    # Remove the now-stale Ohio caveat while preserving the rest of the research note.
    ohio = bill_by_id["oh-hb469-2025"]
    old = "STATUS NOT RE-CONFIRMED: this is the introduced text only; stage remains as the paper recorded it."
    new = "STATUS RE-CONFIRMED 2026-08-11: the official Ohio status page records referral to House Technology and Innovation on 1 October 2025; no later action is shown."
    if old in ohio.get("notes", ""):
        ohio["notes"] = ohio["notes"].replace(old, new, 1)
    elif new not in ohio.get("notes", ""):
        raise SystemExit("Ohio status-note anchor not found")

    source_by_id = {s["id"]: s for s in catalog.get("sources", [])}
    for cfg in COHORT.values():
        src = cfg["source"]
        if src["id"] in source_by_id:
            if source_by_id[src["id"]] != src:
                raise SystemExit(f"conflicting existing source {src['id']}")
        else:
            catalog.setdefault("sources", []).append(src)

    rec_by_id = {r["record_id"]: r for r in evidence.get("records", [])}
    for rid, cfg in COHORT.items():
        claim = {
            "claim": {"field": "status.stage"},
            "value": cfg["stage"],
            "mode": "direct",
            "supports": [{"source_ref": cfg["source"]["id"], "locator": cfg["locator"]}],
        }
        if rid in rec_by_id:
            claims = rec_by_id[rid].setdefault("claims", [])
            existing = [c for c in claims if c.get("claim") == {"field": "status.stage"}]
            if existing:
                if existing[0] != claim:
                    raise SystemExit(f"conflicting existing status claim for {rid}")
            else:
                claims.append(claim)
        else:
            rec = {"record_id": rid, "claims": [claim]}
            evidence.setdefault("records", []).append(rec)
            rec_by_id[rid] = rec

    write(bills_path, bills)
    write(cat_path, catalog)
    write(ev_path, evidence)

    # Expand the validator's intentionally bounded mapped-record set.
    text = val_path.read_text(encoding="utf-8")
    for rid in COHORT:
        quoted = f'    "{rid}",\n'
        if quoted not in text:
            anchor = '    "mo-hb1769-2026",\n'
            if anchor not in text:
                raise SystemExit("validator mapped-record anchor not found")
            text = text.replace(anchor, anchor + quoted, 1)
    val_path.write_text(text, encoding="utf-8")

    print("STATUS PROVENANCE COHORT: APPLIED")
    for rid, cfg in COHORT.items():
        print(f"- {rid}: {cfg['stage']} <- {cfg['source']['id']} ({cfg['date']})")


if __name__ == "__main__":
    main()
