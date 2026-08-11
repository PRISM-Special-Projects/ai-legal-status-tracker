#!/usr/bin/env python3
"""Retired compatibility check for the completed 2026-08-11 version-ID migration.

Immutable version IDs now live directly on registry/bills.json version objects.
The temporary claim_evidence.json `version_ids` map must not reappear.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    evidence = json.loads((ROOT / "claim_evidence.json").read_text(encoding="utf-8"))
    if "version_ids" in evidence:
        print("VERSION ID MIGRATION: FAIL — legacy sidecar version_ids map has reappeared")
        return 1
    print("VERSION ID MIGRATION: RETIRED — IDs are first-class in bills.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
