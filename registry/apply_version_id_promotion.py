#!/usr/bin/env python3
"""One-time gated promotion of tested version IDs into the production registry."""
from __future__ import annotations

import json
from pathlib import Path

REG = Path(__file__).resolve().parent
ROOT = REG.parent


def load(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"promotion patch failed: {label} anchor not found")
    if text.count(old) != 1:
        raise SystemExit(f"promotion patch failed: {label} anchor occurs {text.count(old)} times")
    return text.replace(old, new, 1)


def main():
    bills_path = REG / "bills.json"
    evidence_path = REG / "claim_evidence.json"
    bills = load(bills_path)
    evidence = load(evidence_path)
    mappings = evidence.get("version_ids")

    if mappings:
        by_id = {b["id"]: b for b in bills["bills"]}
        seen = set()
        assignments = []
        for record_id, mapping in mappings.items():
            bill = by_id.get(record_id)
            if bill is None:
                raise SystemExit(f"promotion failed: missing bill {record_id}")
            for selector, version_id in mapping.items():
                matches = [v for v in bill.get("versions", []) if selector.lower() in str(v.get("label", "")).lower()]
                if len(matches) != 1:
                    raise SystemExit(f"promotion failed: {record_id} selector {selector!r} matched {len(matches)} versions")
                version = matches[0]
                existing = version.get("version_id")
                if existing not in (None, version_id):
                    raise SystemExit(f"promotion failed: {record_id} conflicting version_id {existing!r}")
                if version_id in seen:
                    raise SystemExit(f"promotion failed: duplicate version_id {version_id}")
                seen.add(version_id)
                version["version_id"] = version_id
                assignments.append((record_id, version.get("label"), version_id))
        evidence.pop("version_ids", None)
        write_json(bills_path, bills)
        write_json(evidence_path, evidence)
        for record_id, label, version_id in assignments:
            print(f"PROMOTED {record_id}: {label} -> {version_id}")
    else:
        print("version_ids sidecar map already removed; promotion is idempotent")

    # Make version_id a first-class nested schema property in the core validator.
    validate_path = REG / "validate.py"
    text = validate_path.read_text(encoding="utf-8")
    if "version_ids_seen={}" not in text:
        text = replace_once(text, "seen=set()\nfor b in bills:", "seen=set()\nversion_ids_seen={}\nfor b in bills:", "global version-id set")
        text = replace_once(
            text,
            '    for v in shape(b, i, "versions", list, "a list"):\n        if not isinstance(v, dict):\n            err.append(f"{i}: version entry is {type(v).__name__}, not an object"); continue\n',
            '    record_version_ids=set()\n    for v in shape(b, i, "versions", list, "a list"):\n        if not isinstance(v, dict):\n            err.append(f"{i}: version entry is {type(v).__name__}, not an object"); continue\n        version_id=v.get("version_id")\n        if version_id is not None:\n            chk(isinstance(version_id, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]+", version_id)),\n                f"{i}: bad version_id {version_id!r}")\n            chk(version_id not in record_version_ids, f"{i}: duplicate version_id within record {version_id!r}")\n            owner=version_ids_seen.get(version_id)\n            chk(owner in (None, i), f"{i}: version_id {version_id!r} already used by {owner}")\n            if isinstance(version_id, str):\n                record_version_ids.add(version_id)\n                version_ids_seen.setdefault(version_id, i)\n',
            "version loop",
        )
        validate_path.write_text(text, encoding="utf-8")
        print("patched registry/validate.py for first-class version_id validation")

    # Make claim provenance resolve version IDs from bills.json, not a sidecar mapping.
    cv_path = REG / "validate_claim_evidence.py"
    cv = cv_path.read_text(encoding="utf-8")
    if 'version_maps = evidence.get("version_ids", {})' in cv:
        cv = replace_once(
            cv,
            '    seen_records = set()\n    version_maps = evidence.get("version_ids", {})\n\n    unexpected_maps = set(version_maps) - MIGRATED_RECORDS\n    if unexpected_maps:\n        fail(errors, f"version_ids contains unexpected records: {sorted(unexpected_maps)}")\n',
            '    seen_records = set()\n    if "version_ids" in evidence:\n        fail(errors, "legacy sidecar version_ids map must be removed after promotion")\n',
            "claim validator legacy map",
        )
        cv = replace_once(
            cv,
            '        version_map = version_maps.get(rid) or {}\n        registered_version_ids = set(version_map.values())\n        if len(registered_version_ids) != len(version_map):\n            fail(errors, f"{rid}: duplicate immutable version_id values")\n',
            '        bill_versions = (bill_by_id.get(rid) or {}).get("versions") or []\n        version_id_list = [v.get("version_id") for v in bill_versions if isinstance(v, dict) and v.get("version_id")]\n        registered_version_ids = set(version_id_list)\n        if len(registered_version_ids) != len(version_id_list):\n            fail(errors, f"{rid}: duplicate immutable version_id values in bills.json")\n',
            "claim validator version source",
        )
        cv_path.write_text(cv, encoding="utf-8")
        print("patched claim validator to resolve version IDs from bills.json")

    # Update schema prose conservatively: version_id is first-class but incremental.
    schema_path = ROOT / "SCHEMA.md"
    schema = schema_path.read_text(encoding="utf-8")
    old_row = '| `versions` | array | `{label, date, source_url, text_path}` — introduced → substitute → enacted; `text_path` points at the stored text under `registry/texts/` |'
    new_row = '| `versions` | array | `{version_id?, label, date, source_url, text_path}` — introduced → substitute → enacted. `version_id` is an immutable identifier for versions addressed by provenance/diffs; it is unique repository-wide. During incremental migration it may be absent from versions not yet addressable by structured provenance. `text_path` points at the stored text under `registry/texts/` |'
    if old_row in schema:
        schema = schema.replace(old_row, new_row, 1)
    elif new_row not in schema:
        raise SystemExit("promotion patch failed: SCHEMA versions row not found")
    marker = "## Changelog\n"
    entry = "\n**v0.2.0 provenance migration (2026-08-11).** `versions[].version_id` is now a first-class immutable identifier for version objects addressed by claim-level provenance. Four audited IDs were promoted from the temporary sidecar map; the core validator enforces syntax and repository-wide uniqueness for IDs as they are added. The sidecar mapping has been removed.\n"
    if "v0.2.0 provenance migration (2026-08-11)" not in schema:
        schema = schema.replace(marker, marker + entry, 1)
    schema_path.write_text(schema, encoding="utf-8")
    print("updated SCHEMA.md")


if __name__ == "__main__":
    main()
