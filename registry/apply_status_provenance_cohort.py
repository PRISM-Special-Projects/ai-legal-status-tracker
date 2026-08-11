#!/usr/bin/env python3
"""Retired one-time status-provenance migration guard.

The SC HB 3796, OH HB 469, MO SB 859 and MN SF 4114 status claims were promoted on
2026-08-11. The production registry, source catalogue and claim-evidence sidecar now hold
those results directly. This file remains only to prevent accidental reuse of the completed
migration path.
"""

raise SystemExit(
    "status provenance cohort migration already completed; edit production data through the normal audited workflow"
)
