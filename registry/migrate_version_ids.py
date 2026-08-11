#!/usr/bin/env python3
"""Attach immutable version IDs from claim_evidence.json to bills.json.

Default mode is a dry run: prove every sidecar mapping resolves to exactly one real
versions[] object and that resulting IDs are unique. Pass --write only when the
version-ID migration gate has explicitly been opened.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write version_id fields to bills.json")
    args = ap.parse_args()

    bills_path = ROOT / "bills.json"
    data = load(bills_path)
    evidence = load(ROOT / "claim_evidence.json")
    by_id = {b["id"]: b for b in data["bills"]}

    errors = []
    assignments = []
    global_ids = {}

    for record_id, mapping in evidence.get("version_ids", {}).items():
        bill = by_id.get(record_id)
        if bill is None:
            errors.append(f"{record_id}: record missing from bills.json")
            continue

        versions = bill.get("versions") or []
        for selector, version_id in mapping.items():
            matches = [v for v in versions if selector.lower() in str(v.get("label", "")).lower()]
            if len(matches) != 1:
                labels = [v.get("label") for v in versions]
                errors.append(
                    f"{record_id}: selector {selector!r} matched {len(matches)} versions; labels={labels!r}"
                )
                continue
            v = matches[0]
            existing = v.get("version_id")
            if existing not in (None, version_id):
                errors.append(
                    f"{record_id}: {v.get('label')!r} already has conflicting version_id {existing!r}"
                )
                continue
            owner = global_ids.get(version_id)
            current = f"{record_id}:{v.get('label')}"
            if owner and owner != current:
                errors.append(f"duplicate version_id {version_id!r}: {owner} and {current}")
                continue
            global_ids[version_id] = current
            assignments.append((record_id, v, version_id))

    if errors:
        print("VERSION ID MIGRATION: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    for record_id, version, version_id in assignments:
        print(f"{record_id}: {version.get('label')} -> {version_id}")
        if args.write:
            version["version_id"] = version_id

    if args.write:
        bills_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"VERSION ID MIGRATION: WROTE {len(assignments)} assignments")
    else:
        print(f"VERSION ID MIGRATION: DRY-RUN PASS ({len(assignments)} assignments)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
