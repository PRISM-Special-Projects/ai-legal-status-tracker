#!/usr/bin/env python3
"""Validate production claim-level provenance sidecars.

The bill-centred registry remains authoritative for domain facts. claim_evidence.json
records which sources support selected high-risk claims and whether support is direct
or derived. Missing claim evidence means unmapped/not assessed, never false.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALLOWED_MODES = {"direct", "derived"}
ALLOWED_ASSESSMENTS = {"present", "checked_absent"}
MIGRATED_RECORDS = {
    "wa-hb2029-2025",
    "ut-hb249-2024",
    "tn-sb837-2025",
    "mo-hb1769-2026",
    "mn-sf4114-2026",
    "mo-sb859-2026",
    "oh-hb469-2025",
    "sc-hb3796-2025",
    "mo-sb1012-2026",
    "ca-sb1119-2026",
}


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fail(errors, message):
    errors.append(message)


def selector_key(claim):
    return json.dumps(claim, sort_keys=True, ensure_ascii=False)


def main() -> int:
    catalog = load(ROOT / "source_catalog.json")
    evidence = load(ROOT / "claim_evidence.json")
    bills = load(ROOT / "bills.json")

    errors = []
    source_ids = [s.get("id") for s in catalog.get("sources", [])]
    if len(source_ids) != len(set(source_ids)):
        fail(errors, "source_catalog contains duplicate source ids")
    source_ids = set(source_ids)

    for i, src in enumerate(catalog.get("sources", [])):
        sid = src.get("id")
        if not sid or not src.get("label") or not src.get("kind"):
            fail(errors, f"source_catalog source[{i}] requires id, label and kind")
        has_url = bool(src.get("url"))
        has_ref = bool(src.get("registry_ref"))
        if not (has_url or has_ref):
            fail(errors, f"source_catalog {sid!r} needs url or registry_ref")
        if has_url and not str(src["url"]).startswith(("http://", "https://")):
            fail(errors, f"source_catalog {sid!r} has invalid url {src['url']!r}")

    bill_by_id = {b.get("id"): b for b in bills.get("bills", [])}
    seen_records = set()
    if "version_ids" in evidence:
        fail(errors, "legacy sidecar version_ids map must be removed after promotion")

    for rec in evidence.get("records", []):
        rid = rec.get("record_id")
        if rid in seen_records:
            fail(errors, f"duplicate evidence record: {rid}")
        seen_records.add(rid)
        if rid not in MIGRATED_RECORDS:
            fail(errors, f"unexpected migrated record: {rid}")
        if rid not in bill_by_id:
            fail(errors, f"claim-evidence record not found in bills.json: {rid}")

        bill_versions = (bill_by_id.get(rid) or {}).get("versions") or []
        version_id_list = [v.get("version_id") for v in bill_versions if isinstance(v, dict) and v.get("version_id")]
        registered_version_ids = set(version_id_list)
        if len(registered_version_ids) != len(version_id_list):
            fail(errors, f"{rid}: duplicate immutable version_id values in bills.json")

        seen_claims = set()
        for i, entry in enumerate(rec.get("claims", [])):
            prefix = f"{rid} claim[{i}]"
            claim = entry.get("claim")
            if not isinstance(claim, dict) or not claim.get("field"):
                fail(errors, f"{prefix}: typed claim selector with field is required")
                continue

            skey = selector_key(claim)
            if skey in seen_claims:
                fail(errors, f"{prefix}: duplicate claim selector {claim!r}")
            seen_claims.add(skey)

            mode = entry.get("mode")
            if mode not in ALLOWED_MODES:
                fail(errors, f"{prefix}: invalid mode {mode!r}")

            supports = entry.get("supports")
            if not isinstance(supports, list) or not supports:
                fail(errors, f"{prefix}: at least one support is required")
            else:
                for j, support in enumerate(supports):
                    ref = support.get("source_ref") if isinstance(support, dict) else None
                    if ref not in source_ids:
                        fail(errors, f"{prefix} support[{j}]: unresolved source_ref {ref!r}")

            if mode == "derived":
                if not entry.get("derivation"):
                    fail(errors, f"{prefix}: derived claim requires derivation")
                if not isinstance(supports, list) or len(supports) < 2:
                    fail(errors, f"{prefix}: derived claim requires at least two supports")

            assessment = entry.get("assessment")
            if assessment is not None and assessment not in ALLOWED_ASSESSMENTS:
                fail(errors, f"{prefix}: invalid assessment {assessment!r}")
            if assessment == "present" and entry.get("value") is not True:
                fail(errors, f"{prefix}: assessment=present must carry value=true")
            if entry.get("value") is False and assessment != "checked_absent":
                fail(errors, f"{prefix}: false textual claim must be explicit checked_absent")
            if assessment == "checked_absent" and entry.get("value") is not False:
                fail(errors, f"{prefix}: checked_absent must carry value=false")

            vid = claim.get("version_id")
            if vid and vid not in registered_version_ids:
                fail(errors, f"{prefix}: unregistered version_id {vid!r} for {rid}")
            if claim.get("field") == "provisions" and not vid:
                fail(errors, f"{prefix}: provision claim requires version_id")
            if claim.get("field") == "provision_change":
                fvid = claim.get("from_version_id")
                tvid = claim.get("to_version_id")
                if not fvid or not tvid:
                    fail(errors, f"{prefix}: provision_change requires from/to version ids")
                else:
                    if fvid not in registered_version_ids:
                        fail(errors, f"{prefix}: unregistered from_version_id {fvid!r}")
                    if tvid not in registered_version_ids:
                        fail(errors, f"{prefix}: unregistered to_version_id {tvid!r}")
                    if fvid == tvid:
                        fail(errors, f"{prefix}: provision_change from/to ids must differ")

            # Stale-value checks for high-risk scalar claims already in bills.json.
            if rid in bill_by_id and claim.get("field") in {"codified_at", "effective_date"}:
                actual = bill_by_id[rid].get(claim["field"])
                if actual != entry.get("value"):
                    fail(errors, f"{prefix}: stale value; bills.json has {actual!r}, evidence has {entry.get('value')!r}")
            if rid in bill_by_id and claim.get("field") == "status.stage":
                actual = (bill_by_id[rid].get("status") or {}).get("stage")
                if actual != entry.get("value"):
                    fail(errors, f"{prefix}: stale status.stage; bills.json has {actual!r}, evidence has {entry.get('value')!r}")

    if seen_records != MIGRATED_RECORDS:
        missing = sorted(MIGRATED_RECORDS - seen_records)
        fail(errors, f"migrated record set incomplete; missing {missing}")

    if errors:
        print("CLAIM PROVENANCE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CLAIM PROVENANCE: PASS")
    print(f"records={len(seen_records)} sources={len(source_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
