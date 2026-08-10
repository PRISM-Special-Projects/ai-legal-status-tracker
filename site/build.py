#!/usr/bin/env python3
"""AI Legal Status Tracker — static site build.

Reads ../registry/bills.json and writes ./dist/. No network, no dependencies.
Run: python3 site/build.py
"""
import json, os, shutil, html, pathlib, datetime, re

ROOT = pathlib.Path(__file__).resolve().parent
REG  = ROOT.parent / "registry"
DIST = ROOT / "dist"

SITE = {
    "name": "AI Legal Status Tracker",
    "tagline": "US state legislation on the legal status and personhood of AI systems",
    "base": "/ai-legal-status",          # Observatory subpath
    "publisher": "PRISM",
    "status": "Active / monitoring",
    "published": "2026-08-10",
}

def esc(s): return html.escape(str(s), quote=True) if s is not None else ""

def load():
    d = json.loads((REG / "bills.json").read_text())
    bills = d["bills"]
    bills.sort(key=lambda b: (b["session"]["year_introduced"], b["jurisdiction"]["state"], b["bill_number"]))
    return d, bills

def last_verified(bills):
    ds = [b["last_verified"] for b in bills if b.get("last_verified")]
    return max(ds) if ds else "—"

# ---------------------------------------------------------------- page shell
def page(title, body, *, depth=0, desc="", active=""):
    up = "../" * depth
    nav = [("", "Bills"), ("method/", "Method"), ("data/", "Data")]
    links = "".join(
        f'<a href="{up}{h}"{" aria-current=page" if active==h else ""}>{esc(t)}</a>'
        for h, t in nav)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · {esc(SITE['name'])}</title>
<meta name="description" content="{esc(desc or SITE['tagline'])}">
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="wrap">
    <div class="brand">
      <a class="title" href="{up}">{esc(SITE['name'])}</a>
      <p class="tagline">{esc(SITE['tagline'])}</p>
    </div>
    <nav aria-label="Primary">{links}</nav>
  </div>
</header>
<div class="statusbar"><div class="wrap">
  <span><b>Tracker status</b> {esc(SITE['status'])}</span>
  <span><b>Published</b> <time>{esc(SITE['published'])}</time></span>
  <span><b>Last verified</b> <time>{esc(SITE['_lastver'])}</time></span>
</div></div>
<main id="main" class="wrap">
{body}
</main>
<footer class="site"><div class="wrap">
  <p>{esc(SITE['name'])} — a descriptive registry. Inclusion does not imply endorsement of any
     bill, nor any view about the legal status of AI systems.</p>
  <p class="muted">Published by {esc(SITE['publisher'])}. Every record links to its primary source.</p>
</div></footer>
</body>
</html>
"""

CSS = """
:root{
  --bg:#fbfbf9; --fg:#1a1a18; --muted:#6b6b63; --line:#e2e1db;
  --card:#fff; --accent:#3d5a45; --accent-weak:#eef2ee;
  --add:#1f6f3f; --add-bg:#e9f5ed; --del:#9a2c2c; --del-bg:#fbecec;
  --maxw:1180px; --radius:6px;
}
@media (prefers-color-scheme:dark){
  :root{ --bg:#14150f; --fg:#eceade; --muted:#9a988c; --line:#2e2f27;
         --card:#1b1c15; --accent:#8fb99a; --accent-weak:#1f2a22;
         --add:#7fc79a; --add-bg:#16281d; --del:#e08b8b; --del-bg:#2a1717; }
}
:root[data-theme=dark]{ --bg:#14150f; --fg:#eceade; --muted:#9a988c; --line:#2e2f27;
  --card:#1b1c15; --accent:#8fb99a; --accent-weak:#1f2a22;
  --add:#7fc79a; --add-bg:#16281d; --del:#e08b8b; --del-bg:#2a1717; }
:root[data-theme=light]{ --bg:#fbfbf9; --fg:#1a1a18; --muted:#6b6b63; --line:#e2e1db;
  --card:#fff; --accent:#3d5a45; --accent-weak:#eef2ee;
  --add:#1f6f3f; --add-bg:#e9f5ed; --del:#9a2c2c; --del-bg:#fbecec; }

*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.6 ui-serif,Georgia,"Iowan Old Style","Times New Roman",serif;}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 20px}
a{color:var(--accent);text-underline-offset:2px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:var(--card);padding:8px;z-index:10}

header.site{border-bottom:1px solid var(--line);background:var(--card)}
header.site .wrap{display:flex;flex-wrap:wrap;gap:12px;align-items:baseline;
  justify-content:space-between;padding-top:18px;padding-bottom:14px}
.title{font-size:1.32rem;font-weight:600;text-decoration:none;color:var(--fg);letter-spacing:-.01em}
.tagline{margin:.25rem 0 0;color:var(--muted);font-size:.9rem;max-width:52ch}
header.site nav{display:flex;gap:18px;font-size:.92rem}
header.site nav a[aria-current]{color:var(--fg);font-weight:600}

.statusbar{border-bottom:1px solid var(--line);background:var(--accent-weak);
  font:500 .8rem/1.4 ui-sans-serif,system-ui,sans-serif}
.statusbar .wrap{display:flex;flex-wrap:wrap;gap:8px 26px;padding-top:9px;padding-bottom:9px}
.statusbar b{font-weight:600;color:var(--muted);margin-right:5px;font-weight:500}

main{padding:42px 20px 64px}
h1{font-size:1.9rem;line-height:1.2;letter-spacing:-.02em;margin:0 0 .4em}
h2{font-size:1.28rem;margin:2.2em 0 .6em;letter-spacing:-.01em}
.lede{font-size:1.06rem;color:var(--muted);max-width:64ch;margin:0 0 1.6em}
.muted{color:var(--muted)}
.count{font-variant-numeric:tabular-nums;font-weight:600}

.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  list-style:none;padding:0;margin:0}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px}
.card a{text-decoration:none}
.card h3{margin:0 0 .3em;font-size:1rem}
.card .meta{font:.8rem/1.5 ui-sans-serif,system-ui,sans-serif;color:var(--muted)}

.chip{display:inline-block;font:500 .72rem/1 ui-sans-serif,system-ui,sans-serif;
  padding:4px 7px;border:1px solid var(--line);border-radius:99px;margin:3px 3px 0 0;
  background:var(--accent-weak);color:var(--fg);white-space:nowrap}
.chip.s-enacted{background:var(--add-bg);border-color:transparent;color:var(--add)}
.chip.s-failed{background:var(--del-bg);border-color:transparent;color:var(--del)}

footer.site{border-top:1px solid var(--line);margin-top:40px;padding:22px 0 46px;
  font:.85rem/1.6 ui-sans-serif,system-ui,sans-serif;color:var(--muted);background:var(--card)}
footer.site p{margin:.3em 0;max-width:74ch}

@media (max-width:700px){
  header.site .wrap{flex-direction:column;align-items:flex-start}
  main{padding-top:24px}
  h1{font-size:1.6rem}
}
"""

# ---------------------------------------------------------------- build
def build():
    d, bills = load()
    SITE["_lastver"] = last_verified(bills)
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "style.css").write_text(CSS.strip() + "\n")

    st = {}
    for b in bills: st[b["status"]["stage"]] = st.get(b["status"]["stage"], 0) + 1
    states = sorted({b["jurisdiction"]["state"] for b in bills})

    cards = "".join(
        f'<li class="card"><h3><a href="bills/{esc(b["id"])}/">{esc(b["jurisdiction"]["state"])} '
        f'{esc(b["bill_number"])}</a></h3>'
        f'<p class="meta">{esc(b["session"]["year_introduced"])} · family {esc(b["family"])} · '
        f'{len(b["provisions"])} provision{"" if len(b["provisions"])==1 else "s"}</p>'
        f'<span class="chip s-{esc(b["status"]["stage"])}">{esc(b["status"]["stage"].replace("_"," "))}</span>'
        f'</li>' for b in bills)

    body = f"""
<h1>Legislation on the legal status of AI systems</h1>
<p class="lede"><span class="count">{len(bills)}</span> bills across
<span class="count">{len(states)}</span> US states since 2022, each read against its primary
source. This is a descriptive record of what bills say, not an assessment of them.</p>
<p class="muted" style="font-size:.9rem">Step 2 harness — the provision matrix and map filter
land in step 4. Current disposition:
{" · ".join(f"{v} {k.replace('_',' ')}" for k,v in sorted(st.items(), key=lambda x:-x[1]))}.</p>
<h2>Bills</h2>
<ul class="grid">{cards}</ul>
"""
    (DIST / "index.html").write_text(page("Bills", body, active=""))
    return bills, st

if __name__ == "__main__":
    bills, st = build()
    n = sum(len(list(p.rglob("*"))) for p in [DIST])
    print(f"built dist/ — {len(bills)} bills, {n} files")
    print(f"  disposition: {st}")
