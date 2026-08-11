#!/usr/bin/env python3
"""Compare a filled audit sheet against the registry.

The comparison happens here, after extraction, so the auditor is never shown the
recorded value while answering. Verdicts follow audit/PROTOCOL.md.

    python3 audit/check_sheet.py audit/sheets/sc-hb3796-2025.md
    python3 audit/check_sheet.py --all
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
REG = ROOT.parent / "registry"
RESULTS = ROOT / "results"

SENTINELS = {"NOT STATED", "UNREACHABLE", "CANNOT TELL"}

# Fields a script cannot adjudicate. Legal notation varies legitimately — "H. 3796"
# against "HB 3796", "art. 29 to ch. 1, tit. 1" against "article 29 to chapter 1,
# title 1" — and an automated verdict here produces false mismatches, which teach an
# auditor to wave real ones away as formatting. These are printed side by side for a
# human to accept or reject, and never scored.
REVIEW_FIELDS = {"bill_number", "session", "codified_at", "status_action", "operative_quote"}


def parse_sheet(path):
    out = {}
    for m in re.finditer(r"^answer\.([\w\.]+):[ \t]*(.*)$", path.read_text(), re.M):
        key, val = m.group(1), m.group(2).strip()
        if val:
            out[key] = val
    return out


def norm(s):
    """Compare on substance: case, punctuation and spacing vary between sources."""
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


def recorded(b):
    st = b["status"]
    ev = st.get("evidence") or {}
    return {
        "bill_number": b["bill_number"],
        "chamber": b["chamber"],
        "year_introduced": b["session"]["year_introduced"],
        "session": f"{b['session'].get('legislature') or ''} {b['session']['session']}".strip(),
        "status_stage": st["stage"],
        "status_action": ev.get("action"),
        "status_action_date": ev.get("date"),
        "sponsors": "; ".join(s["name"] for s in b["sponsors"]),
        "codified_at": b["codified_at"],
        "effective_date": b["effective_date"],
        "operative_quote": (b.get("key_clause") or {}).get("text"),
    }


def compare(answers, rec, b):
    rows = []
    for key, recval in rec.items():
        got = answers.get(key)
        if got is None:
            rows.append((key, "unanswered", got, recval)); continue
        if key in REVIEW_FIELDS and got.upper() not in SENTINELS:
            rows.append((key, "extra" if recval in (None, "", []) else "review", got, recval))
            continue
        if key == "sponsors":
            # Compare as a set of surnames: order and punctuation vary by source.
            a = {norm(x) for x in re.split(r"[;,]", got) if norm(x)}
            r = {norm(x) for x in re.split(r"[;,]", str(recval)) if norm(x)}
            rows.append((key, "match" if a == r else ("partial" if a & r else "mismatch"),
                         got, recval))
            continue
        if got.upper() in SENTINELS:
            verdict = "unreachable" if got.upper() == "UNREACHABLE" else (
                "extra" if not recval else "not_stated")
            rows.append((key, verdict, got, recval)); continue
        if recval in (None, "", []):
            rows.append((key, "extra", got, recval)); continue
        if norm(got) == norm(recval):
            rows.append((key, "match", got, recval))
        elif norm(got) in norm(recval) or norm(recval) in norm(got):
            rows.append((key, "partial", got, recval))
        else:
            rows.append((key, "mismatch", got, recval))

    held = set(b["provisions"])
    for key, got in answers.items():
        if not key.startswith("provision."):
            continue
        tag = key.split(".", 1)[1]
        if got.upper() in SENTINELS:
            rows.append((key, "unreachable" if got.upper() == "UNREACHABLE" else "not_stated",
                         got, tag in held)); continue
        said = got.strip().lower() in ("yes", "y", "true")
        if said == (tag in held):
            rows.append((key, "match", got, tag in held))
        else:
            rows.append((key, "mismatch", got, tag in held))
    return rows


ORDER = ["mismatch", "review", "not_stated", "extra", "partial", "unreachable",
         "unanswered", "match"]
MARK = {"match": "  ok", "partial": "  ~", "mismatch": "  ✗", "not_stated": "  ?",
        "extra": "  +", "unreachable": "  -", "unanswered": "  .", "review": "  »"}


def run(path, bills):
    rid = path.stem
    b = next((x for x in bills if x["id"] == rid), None)
    if b is None:
        print(f"{rid}: no such record in bills.json"); return None
    answers = parse_sheet(path)
    if not answers:
        print(f"{rid}: sheet is empty — nothing to check"); return None
    rows = sorted(compare(answers, recorded(b), b), key=lambda r: ORDER.index(r[1]))

    counts = {}
    for _, v, _, _ in rows:
        counts[v] = counts.get(v, 0) + 1
    print(f"\n=== {rid} ===")
    for key, verdict, got, recval in rows:
        if verdict == "match":
            continue                       # only the exceptions need reading
        print(f"{MARK[verdict]} {verdict:<11} {key}")
        print(f"        source says : {got!r}")
        print(f"        record says : {recval!r}")
    print(f"  -- {counts.get('match',0)} match · "
          + " · ".join(f"{v} {k}" for k, v in sorted(counts.items()) if k != "match"))
    if counts.get("review"):
        print("     » = needs a human verdict; notation differs legitimately between sources")

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{rid}.json").write_text(json.dumps({
        "record": rid,
        "auditor_sheet": (str(path.relative_to(ROOT.parent))
                          if ROOT.parent in path.resolve().parents else str(path)),
        "counts": counts,
        "rows": [{"field": k, "verdict": v, "source": g, "record": r} for k, v, g, r in rows],
    }, indent=2, default=str) + "\n")
    return counts


def main():
    bills = json.loads((REG / "bills.json").read_text())["bills"]
    if "--all" in sys.argv:
        paths = sorted((ROOT / "sheets").glob("*.md"))
    else:
        paths = [pathlib.Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    if not paths:
        print(__doc__); sys.exit(2)

    total = {}
    checked = 0
    for p in paths:
        c = run(p, bills)
        if c is None:
            continue
        checked += 1
        for k, v in c.items():
            total[k] = total.get(k, 0) + v
    if checked > 1:
        print(f"\n=== {checked} sheets ===")
        for k in ORDER:
            if total.get(k):
                print(f"  {k:<12} {total[k]}")
    # A mismatch means the registry is wrong until shown otherwise.
    sys.exit(1 if total.get("mismatch") else 0)


if __name__ == "__main__":
    main()
