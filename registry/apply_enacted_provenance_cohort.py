#!/usr/bin/env python3
"""One-time gated migration for enacted-law codification/effective-date provenance."""
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
records = {r["record_id"]: r for r in cdata["records"]}

# --- Registry corrections discovered by the enacted-law audit ---
nd = by_id["nd-hb1361-2023"]
assert nd["codified_at"] == "N.D. Cent. Code § 1-01-49(8) (definition of 'person')"
assert nd["verification"]["codified_at_source"] == "bill"
nd["codified_at"] = "N.D. Cent. Code § 1-01-49(17) (current published-code numbering; enacted in 2023 as subsection 8)"
nd["verification"]["codified_at_source"] = "code"
nd["last_verified"] = TODAY
nd["verification"]["last_verified"] = TODAY
nd["notes"] += " CODIFICATION RECHECK 2026-08-11: the current official Century Code now places the definition of 'Person' at § 1-01-49(17), where it excludes environmental elements, artificial intelligence, an animal, or an inanimate object. HB 1361 enacted the provision in 2023 as subsection 8; later code restructuring renumbered it. `codified_at` now cites the current published-code location while preserving the enactment-time numbering in this note."

for rid in ("tn-hb1455-2025", "tn-sb1493-2025"):
    b = by_id[rid]
    assert b["effective_date"] == "2026-04-23", (rid, b["effective_date"])
    b["effective_date"] = "2026-05-22"
    b["last_verified"] = TODAY
    b["verification"]["last_verified"] = TODAY
    for v in b.get("versions", []):
        if v.get("label") == "enacted (Pub. Ch. 1066)" and v.get("date") == "2026-04-23":
            v["date"] = "2026-05-27"
    if rid == "tn-sb1493-2025":
        b["status"] = {
            "stage": "enacted",
            "as_of": TODAY,
            "source_url": "https://wapp.capitol.tn.gov/apps/BillInfo/Default?BillNumber=SB1493&ga=114",
            "evidence": {"action": "Signed by Governor; effective date 05/22/2026; Pub. Ch. 1066", "date": "2026-05-22"},
            "basis": "explicit_action"
        }
    else:
        b["status"] = {
            "stage": "enacted",
            "as_of": TODAY,
            "source_url": "https://wapp.capitol.tn.gov/apps/BillInfo/Default?BillNumber=SB1493&ga=114",
            "evidence": {"action": "Companion SB 1493 became Pub. Ch. 1066", "date": "2026-05-27"},
            "basis": "explicit_action"
        }
    b["notes"] += " DATE CORRECTION 2026-08-11: 23 April 2026 was final legislative passage/concurrence, not the effective date. The official Tennessee history records governor signature and effective date on 22 May 2026, with Public Chapter 1066 assigned 27 May 2026."

# --- Source catalogue ---
new_sources = [
    {
        "id": "id-hb720-bill",
        "label": "Idaho Legislature — HB 720 official bill text/page",
        "kind": "enrolled_bill",
        "url": "https://legislature.idaho.gov/sessioninfo/2022/legislation/H0720/",
        "jurisdiction": "ID",
        "note": "Official Idaho legislative source; supports enactment-time § 5-346 destination and 1 July 2022 effective date. Direct live-code inspection remained inaccessible to the audit tooling."
    },
    {
        "id": "nd-hb1361-code",
        "label": "North Dakota Century Code — Chapter 1-01, current § 1-01-49",
        "kind": "code",
        "url": "https://ndlegis.gov/cencode/t01c01.pdf",
        "jurisdiction": "ND",
        "note": "Official current Century Code; Person is now subsection 17."
    },
    {
        "id": "nd-hb1361-actions",
        "label": "North Dakota Legislature — HB 1361 actions",
        "kind": "action_history",
        "url": "https://ndlegis.gov/assembly/68-2023/regular/bill-actions/ba1361.html",
        "jurisdiction": "ND",
        "note": "Official action history showing emergency clause carried and filing with Secretary of State on 12 April 2023."
    },
    {
        "id": "nd-effective-date-rule",
        "label": "North Dakota Legislative Branch — general effective-date rules",
        "kind": "session_rule",
        "url": "https://ndlegis.gov/general-information",
        "jurisdiction": "ND",
        "note": "Official explanation that emergency measures may take effect earlier than the ordinary August 1 date when the emergency receives the required vote."
    },
    {
        "id": "tn-pc1066",
        "label": "Tennessee Secretary of State — Public Chapter 1066",
        "kind": "session_law",
        "url": "https://publications.tnsosfiles.com/acts/114/pub/pc1066.pdf",
        "jurisdiction": "TN",
        "note": "Official Public Chapter 1066; uncodified TACIR study directive and effective-upon-becoming-law clause."
    },
    {
        "id": "tn-sb1493-actions",
        "label": "Tennessee General Assembly — SB 1493 / HB 1455 bill history",
        "kind": "action_history",
        "url": "https://wapp.capitol.tn.gov/apps/BillInfo/Default?BillNumber=SB1493&ga=114",
        "jurisdiction": "TN",
        "note": "Official history showing 23 April final legislative action, 22 May governor signature/effective date, and 27 May Public Chapter 1066."
    }
]
existing = {s["id"] for s in sdata["sources"]}
for s in new_sources:
    if s["id"] not in existing:
        sdata["sources"].append(s)


def add_claim(rid, entry):
    rec = records.get(rid)
    if rec is None:
        rec = {"record_id": rid, "claims": []}
        cdata["records"].append(rec)
        records[rid] = rec
    key = json.dumps(entry["claim"], sort_keys=True)
    assert all(json.dumps(x["claim"], sort_keys=True) != key for x in rec["claims"]), (rid, entry["claim"])
    rec["claims"].append(entry)

# Idaho: map what is directly established, while preserving code-access limitation.
idb = by_id["id-hb720-2022"]
add_claim("id-hb720-2022", {
    "claim": {"field": "codified_at"},
    "value": idb["codified_at"],
    "mode": "direct",
    "supports": [{"source_ref": "id-hb720-bill", "locator": "Section 1 — NEW SECTION, Idaho Code § 5-346; Session Law ch. 322"}],
    "note": "Bill/session-law destination; official live-code page was inaccessible to audit tooling, so verification.codified_at_source remains bill."
})
add_claim("id-hb720-2022", {
    "claim": {"field": "effective_date"},
    "value": "2022-07-01",
    "mode": "direct",
    "supports": [{"source_ref": "id-hb720-bill", "locator": "emergency/effective-date clause — July 1, 2022"}]
})

# North Dakota: current code location plus emergency effective date.
add_claim("nd-hb1361-2023", {
    "claim": {"field": "codified_at"},
    "value": nd["codified_at"],
    "mode": "direct",
    "supports": [{"source_ref": "nd-hb1361-code", "locator": "§ 1-01-49(17) — Person; excludes artificial intelligence"}],
    "note": "Current code numbering; HB 1361's enactment-time subsection number was 8."
})
add_claim("nd-hb1361-2023", {
    "claim": {"field": "effective_date"},
    "value": "2023-04-12",
    "mode": "derived",
    "supports": [
        {"source_ref": "nd-hb1361-actions", "locator": "emergency clause carried; filed with Secretary of State 04/12/2023"},
        {"source_ref": "nd-effective-date-rule", "locator": "emergency measures may take effect earlier than ordinary August 1 effective date"}
    ],
    "derivation": "HB 1361 carried its emergency clause through final passage and was filed with the Secretary of State on 12 April 2023; the registry therefore records that filing date as the emergency effective date."
})

# Utah already has codification provenance; add the enacted effective date.
add_claim("ut-hb249-2024", {
    "claim": {"field": "effective_date"},
    "value": "2024-05-01",
    "mode": "direct",
    "supports": [{"source_ref": "ut-hb249-enrolled", "locator": "Section 3 — Effective date: May 1, 2024"}]
})

# Tennessee Pub. Ch. 781 companion: reuse the same enacted source/history as SB 837.
hb849 = by_id["tn-hb849-2025"]
add_claim("tn-hb849-2025", {
    "claim": {"field": "codified_at"},
    "value": hb849["codified_at"],
    "mode": "direct",
    "supports": [{"source_ref": "tn-pc0781", "locator": "Section 1 — amendment to Tenn. Code Ann. § 1-3-105(a)(20)"}]
})
add_claim("tn-hb849-2025", {
    "claim": {"field": "effective_date"},
    "value": "2026-04-23",
    "mode": "derived",
    "supports": [
        {"source_ref": "tn-pc0781", "locator": "Section 2 — act takes effect upon becoming a law"},
        {"source_ref": "tn-sb0837-actions", "locator": "2026-04-23 — Signed by Governor"}
    ],
    "derivation": "HB 849's companion SB 837 became Public Chapter 781; the act takes effect upon becoming law and was signed on 23 April 2026."
})

# Tennessee Pub. Ch. 1066 pair: correct and map status, effective date, and uncodified destination.
for rid in ("tn-hb1455-2025", "tn-sb1493-2025"):
    b = by_id[rid]
    add_claim(rid, {
        "claim": {"field": "status.stage"},
        "value": "enacted",
        "mode": "direct",
        "supports": [{"source_ref": "tn-sb1493-actions", "locator": "Signed by Governor 05/22/2026; Pub. Ch. 1066 05/27/2026"}]
    })
    add_claim(rid, {
        "claim": {"field": "codified_at"},
        "value": b["codified_at"],
        "mode": "direct",
        "supports": [{"source_ref": "tn-pc1066", "locator": "full enacted text — freestanding TACIR study directive; no Tennessee Code section amended"}],
        "note": "The public chapter is uncodified despite the residual caption referencing Titles 29, 33, 39 and 47."
    })
    add_claim(rid, {
        "claim": {"field": "effective_date"},
        "value": "2026-05-22",
        "mode": "derived",
        "supports": [
            {"source_ref": "tn-pc1066", "locator": "effective-upon-becoming-law clause"},
            {"source_ref": "tn-sb1493-actions", "locator": "Signed by Governor / Effective date(s) 05/22/2026"}
        ],
        "derivation": "Public Chapter 1066 takes effect upon becoming law; the official bill history records governor signature and effective date on 22 May 2026."
    })

text = DOC.read_text()
text = text.replace("Ten records currently have structured claim-level evidence.", "Fifteen records currently have structured claim-level evidence.")
insert = """

A fourth bounded enacted-law cohort, promoted on 2026-08-11, maps codification and effective-date provenance and corrects two stale citations/dates:

- `id-hb720-2022` — enactment-time § 5-346 destination and 1 July 2022 effective date mapped; direct official live-code inspection remains a documented access limitation, so `codified_at_source` remains `bill`;
- `nd-hb1361-2023` — current official Century Code location corrected from enactment-time § 1-01-49(8) to current § 1-01-49(17), with both states preserved; effective date mapped from the emergency/final-action record;
- `ut-hb249-2024` — 1 May 2024 effective date added to the already mapped code provenance;
- `tn-hb849-2025` — Public Chapter 781 codification and 23 April 2026 effective date mapped using the enacted companion record;
- `tn-hb1455-2025` / `tn-sb1493-2025` — corrected effective date from 23 April (final legislative passage) to 22 May 2026 (governor signature/effective date), with Public Chapter 1066 dated 27 May; uncodified status and enacted-stage provenance mapped.
"""
marker = "\nCorpus-wide mapping remains intentionally incremental."
assert marker in text
text = text.replace(marker, insert + marker)

BILLS.write_text(json.dumps(bdata, indent=2, ensure_ascii=False) + "\n")
SOURCES.write_text(json.dumps(sdata, indent=2, ensure_ascii=False) + "\n")
CLAIMS.write_text(json.dumps(cdata, indent=2, ensure_ascii=False) + "\n")
DOC.write_text(text)
print("enacted-law provenance cohort applied")
