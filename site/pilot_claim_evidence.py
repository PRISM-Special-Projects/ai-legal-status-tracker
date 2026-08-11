#!/usr/bin/env python3
"""Render production claim-level provenance on one built bill page.

This remains intentionally outside site/build.py. It patches only the generated
TN SB 837 page after a normal build so presentation can be reviewed before the
claim-evidence renderer becomes a corpus-wide site feature.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REG = ROOT.parent / "registry"
DIST = ROOT / "dist"
TARGET = "tn-sb837-2025"


def esc(value):
    return html.escape(str(value), quote=True)


def load(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def claim_name(selector):
    field = selector.get("field", "claim")
    vid = selector.get("version_id")
    item = selector.get("item")
    bits = [field]
    if vid:
        bits.append(f"version {vid}")
    if item:
        bits.append(str(item))
    return " · ".join(bits)


def main():
    evidence = load(REG / "claim_evidence.json")
    catalog = load(REG / "source_catalog.json")
    sources = {s["id"]: s for s in catalog["sources"]}
    rec = next((r for r in evidence["records"] if r["record_id"] == TARGET), None)
    if rec is None:
        raise SystemExit(f"claim renderer: no claims for {TARGET}")

    items = []
    for entry in rec["claims"]:
        mode = entry["mode"]
        support_items = []
        for support in entry["supports"]:
            src = sources[support["source_ref"]]
            label = src["label"]
            if src.get("url"):
                label = f'<a href="{esc(src["url"])}">{esc(label)}</a>'
            elif src.get("registry_ref"):
                label = f'{esc(label)} <code>{esc(src["registry_ref"])}</code>'
            locator = support.get("locator")
            suffix = f' — {esc(locator)}' if locator else ""
            support_items.append(f"<li>{label}{suffix}</li>")

        deriv = ""
        if entry.get("derivation"):
            deriv = (f'<p class="muted small"><strong>Derivation:</strong> '
                     f'{esc(entry["derivation"])}</p>')
        note = ""
        if entry.get("note"):
            note = f'<p class="muted small">{esc(entry["note"])}</p>'
        items.append(
            '<div class="cite">'
            f'<p><code>{esc(claim_name(entry["claim"]))}</code><br>'
            f'<strong>{esc(entry.get("value"))}</strong> '
            f'<span class="muted">({esc(mode)})</span></p>'
            f'<ul class="urls">{"".join(support_items)}</ul>{deriv}{note}</div>'
        )

    panel = (
        '<h2>Claim evidence <span class="muted">(migration preview)</span></h2>'
        '<p class="muted small">Claim-level provenance for this migrated record. '
        'It shows the evidence actually attached to individual claims; corpus-wide '
        'rendering remains gated on the next migration review.</p>'
        + "".join(items)
    )

    page = DIST / "bills" / TARGET / "index.html"
    text = page.read_text(encoding="utf-8")
    marker = "<h2>Sources</h2>"
    if marker not in text:
        raise SystemExit("claim renderer: Sources marker not found")
    page.write_text(text.replace(marker, panel + "\n" + marker, 1), encoding="utf-8")
    print(f"claim evidence rendered: {page}")


if __name__ == "__main__":
    main()
