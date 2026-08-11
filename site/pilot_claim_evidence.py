#!/usr/bin/env python3
"""Render the claim-level provenance pilot on one built bill page.

This is intentionally NOT part of site/build.py. It patches only the generated
TN SB 837 page after a normal build so the F-gate presentation can be reviewed
without making claim-level provenance a production-wide site feature.
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
    pilot = load(REG / "pilot" / "claim_evidence.json")
    catalog = load(REG / "pilot" / "source_catalog.json")
    sources = {s["id"]: s for s in catalog["sources"]}
    rec = next((r for r in pilot["records"] if r["record_id"] == TARGET), None)
    if rec is None:
        raise SystemExit(f"pilot renderer: no claims for {TARGET}")

    items = []
    for entry in rec["claims"]:
        mode = entry["mode"]
        support_items = []
        for support in entry["supports"]:
            src = sources[support["source_ref"]]
            label = src["id"]
            if src.get("url"):
                label = f'<a href="{esc(src["url"])}">{esc(label)}</a>'
            elif src.get("registry_ref"):
                label = f'<code>{esc(src["registry_ref"])}</code>'
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
        '<h2>Claim evidence <span class="muted">(pilot)</span></h2>'
        '<p class="muted small">Experimental claim-level provenance for this one record. '
        'It shows the evidence actually attached to individual claims; it is not yet a '
        'corpus-wide site feature.</p>'
        + "".join(items)
    )

    page = DIST / "bills" / TARGET / "index.html"
    text = page.read_text(encoding="utf-8")
    marker = "<h2>Sources</h2>"
    if marker not in text:
        raise SystemExit("pilot renderer: Sources marker not found")
    page.write_text(text.replace(marker, panel + "\n" + marker, 1), encoding="utf-8")
    print(f"pilot claim evidence rendered: {page}")


if __name__ == "__main__":
    main()
