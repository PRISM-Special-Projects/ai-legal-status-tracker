#!/usr/bin/env python3
"""Retired one-time status-resolution migration guard.

MO SB 1012 and CA SB 1119 were resolved and promoted on 2026-08-11. The production
registry, source catalogue and claim-evidence sidecar now hold those results directly.
This file remains only to prevent accidental reuse of the completed migration path.
"""

raise SystemExit(
    "status-resolution cohort migration already completed; edit production data through the normal audited workflow"
)
