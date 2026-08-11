#!/usr/bin/env python3
"""AI Legal Status Tracker — static site build.

Reads ../registry/bills.json and writes ./dist/. No network, no dependencies.
Run: python3 site/build.py
"""
import json, shutil, html, pathlib, re

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
    nav = [("", "Bills"), ("lineage/", "Lineage"), ("method/", "Method"), ("data/", "Data")]
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


/* ---- lineage graph ---- */
figure.tree{margin:1.8em 0;border:1px solid var(--line);border-radius:var(--radius);
  background:var(--card);overflow:hidden}
figure.tree figcaption{padding:11px 16px;border-bottom:1px solid var(--line);
  font:600 .86rem/1.4 ui-sans-serif,system-ui,sans-serif}
.svgscroll{overflow-x:auto;padding:8px 12px}
.svgscroll svg{max-width:none;display:block}
path.edge{fill:none;stroke:var(--line);stroke-width:1.6}
circle.ebadge{fill:var(--bg);stroke:var(--accent);stroke-width:1.4}
text.ebadget{font:600 10px ui-sans-serif,system-ui,sans-serif;fill:var(--accent);text-anchor:middle}
a.gnode rect.nbox{fill:var(--bg);stroke:var(--line);stroke-width:1.4}
a.gnode:hover rect.nbox{stroke:var(--accent);stroke-width:2}
rect.nbox.s-enacted{fill:var(--add-bg);stroke:var(--add)}
rect.nbox.s-failed{fill:var(--del-bg);stroke:var(--del)}
text.nt{font:600 12.5px ui-sans-serif,system-ui,sans-serif;fill:var(--fg)}
text.nm{font:10.5px ui-sans-serif,system-ui,sans-serif;fill:var(--muted)}
.edgedef{border-top:1px solid var(--line);padding:12px 0}
.edgedef h3{margin:0 0 .3em;font-size:.92rem;text-transform:none;letter-spacing:0;
  color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
.edgedef h3 .arrow{color:var(--muted)}
.edgedef ul{margin:0;padding-left:1.15em;font-size:.9rem}
.edgedef ul li{margin:.25em 0;max-width:78ch}
.edgedef:target{background:var(--accent-weak);border-radius:var(--radius);
  padding-left:12px;padding-right:12px}
ul.orphans{columns:2;column-gap:28px;list-style:none;padding-left:0;font-size:.92rem}
ul.orphans li{margin:.25em 0;break-inside:avoid}
@media (max-width:700px){ ul.orphans{columns:1} }

p.pending{background:var(--del-bg);border-left:3px solid var(--del);padding:11px 14px;
  border-radius:0 var(--radius) var(--radius) 0;font-size:.92rem}
table.deftable{width:100%;border-collapse:collapse;margin:1em 0;background:var(--card);
  border:1px solid var(--line);border-radius:var(--radius);
  font:.87rem/1.5 ui-sans-serif,system-ui,sans-serif}
table.deftable th,table.deftable td{padding:8px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
table.deftable thead th{font:600 .74rem/1.3 ui-sans-serif,system-ui,sans-serif;text-transform:uppercase;
  letter-spacing:.06em;color:var(--muted);background:var(--accent-weak)}
table.deftable tbody tr:last-child td{border-bottom:0}
table.deftable td:first-child{white-space:nowrap}
table.deftable .n{text-align:right;font-variant-numeric:tabular-nums;color:var(--muted);white-space:nowrap}
code{font:.86em ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--accent-weak);
  padding:1px 4px;border-radius:3px}
main ol{max-width:74ch}
main ol li{margin:.4em 0}
main>p{max-width:74ch}

/* ---- watch list ---- */
aside.watch{margin:2.2em 0}
aside.watch h2{margin:0 0 .35em}
aside.watch>p{margin:0 0 .9em;font-size:.9rem;color:var(--muted);max-width:70ch}
table.watchtable{width:100%;border-collapse:collapse;background:var(--card);
  border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;
  font:.88rem/1.5 ui-sans-serif,system-ui,sans-serif}
table.watchtable th,table.watchtable td{padding:9px 12px;text-align:left;
  border-bottom:1px solid var(--line);vertical-align:top}
table.watchtable thead th{font:600 .74rem/1.3 ui-sans-serif,system-ui,sans-serif;
  text-transform:uppercase;letter-spacing:.06em;color:var(--muted);background:var(--accent-weak)}
table.watchtable tbody tr:last-child td{border-bottom:0}
td.wd{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:600}
td.wk{white-space:nowrap;color:var(--accent);font-weight:500}
td.we{max-width:44ch}
td.wb{font-size:.84rem}
table.watchtable tr.past{opacity:.5}
table.watchtable tr.past td.wd::after{content:" (passed)";font-weight:400;color:var(--muted);font-size:.78rem}
@media (max-width:700px){
  table.watchtable thead{display:none}
  table.watchtable,table.watchtable tbody,table.watchtable tr,table.watchtable td{display:block;width:100%}
  table.watchtable tr{border-bottom:1px solid var(--line);padding:10px 12px}
  table.watchtable td{border:0;padding:1px 0}
  td.we{max-width:none}
}

aside.callout{border:1px solid var(--accent);border-left-width:3px;border-radius:var(--radius);
  background:var(--accent-weak);padding:14px 18px;margin:1.8em 0}
aside.callout h2{margin:0 0 .35em;font-size:1.05rem}
aside.callout p{margin:0 0 .6em;font-size:.9rem;color:var(--muted);max-width:70ch}
ul.changed{margin:0;padding-left:1.15em;font:.9rem/1.7 ui-sans-serif,system-ui,sans-serif}
ul.changed .k{font-weight:600}
ul.changed .k.del{color:var(--del)}
ul.changed .k.add{color:var(--add)}

/* ---- version diff ---- */
.diff{border:1px solid var(--line);border-radius:var(--radius);background:var(--card);
  margin:1.2em 0;overflow:hidden}
.diffhead{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0;
  padding:12px 16px;border-bottom:1px solid var(--line);
  font:600 .84rem/1.4 ui-sans-serif,system-ui,sans-serif}
.diffhead .v{max-width:44ch}
.diffhead .from{color:var(--del)}
.diffhead .to{color:var(--add)}
.diffhead .arrow{color:var(--muted);font-weight:400}
.mech{margin:0;padding:10px 16px;border-bottom:1px solid var(--line);
  font:.84rem/1.5 ui-sans-serif,system-ui,sans-serif;background:var(--accent-weak)}
.mech .lbl{color:var(--muted);text-transform:uppercase;font-size:.7rem;
  letter-spacing:.06em;margin-right:6px}
.diffstat{margin:0;padding:9px 16px;border-bottom:1px solid var(--line);
  font:.8rem/1.4 ui-sans-serif,system-ui,sans-serif;display:flex;gap:14px;flex-wrap:wrap}
.diffstat .k{font-weight:600}
.diffstat .k.del{color:var(--del)}
.diffstat .k.add{color:var(--add)}
.diffstat .k.mod{color:var(--accent)}
.diffstat .k.renum,.diffstat .k.amb{color:var(--muted)}
.ulab{display:inline-block;min-width:9.5em;margin-right:9px;font:600 .72rem/1.5 ui-monospace,
  SFMono-Regular,Menlo,monospace;color:var(--muted);vertical-align:top}
.modtag{display:inline-block;font:600 .64rem ui-sans-serif,system-ui,sans-serif;color:var(--accent);
  background:var(--accent-weak);padding:1px 5px;border-radius:99px;margin-right:6px;vertical-align:top}
.difftext{padding:6px 0;max-height:34em;overflow-y:auto}
.difftext p{margin:0;padding:5px 16px;font-size:.9rem;line-height:1.55}
.difftext .same{color:var(--muted)}
.difftext .del{background:var(--del-bg)}
.difftext .del del{color:var(--del);text-decoration-thickness:1px}
.difftext .add{background:var(--add-bg)}
.difftext .add ins{color:var(--add);text-decoration:none;font-weight:500}
.difftext .elide{color:var(--muted);font-size:.78rem;font-style:italic;
  text-align:center;padding:7px 16px;background:var(--bg)}
/* Redesignated and not-aligned provisions are neither a change nor a certainty,
   so they read as neutral rather than borrowing the add/remove colours. */
.difftext .renum,.difftext .amb{color:var(--fg);border-left:3px solid var(--line)}
.renumtag,.ambtag{display:inline-block;font:600 .64rem ui-sans-serif,system-ui,sans-serif;
  color:var(--muted);background:var(--bg);border:1px solid var(--line);padding:0 5px;
  border-radius:99px;margin-right:6px;vertical-align:top}
.diffwarn{margin:0;padding:0 16px 9px;border-bottom:1px solid var(--line);
  font:.78rem/1.5 ui-sans-serif,system-ui,sans-serif;color:var(--muted)}
.diffwarn summary{cursor:pointer;padding:6px 0}
.diffwarn ul{margin:0 0 4px;padding-left:20px}

/* ---- visually hidden ---- */
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

/* ---- state map (filter control) ----
   Two fills only, and they are categorical: holds bills / holds none. No ramp, no
   graded shade — a count is printed as a numeral instead, because a numeral cannot be
   misread as intensity and this registry does not rank states. Selection is marked by
   stroke weight as well as fill, so it survives greyscale and colour-blind viewing. */
.mapwrap{margin:1.8em 0 1.4em;max-width:720px}
.usmap{display:block;width:100%;height:auto}
/* --line is the token for subtle borders and disappears against --card at map scale in
   both themes (they differ by a couple of steps). --muted held back with stroke-opacity
   gives an outline that reads as a country without competing with the filled states. */
.usmap .st path{fill:var(--card);stroke:var(--muted);stroke-opacity:.45;stroke-width:1;
  vector-effect:non-scaling-stroke}
.usmap .st.has path{fill:var(--accent-weak);stroke:var(--accent);stroke-width:1.75}
.usmap .st.has{cursor:pointer}
.usmap .ab{font:600 11px/1 ui-sans-serif,system-ui,sans-serif;fill:var(--fg);
  text-anchor:middle;pointer-events:none}
.usmap .n{font:700 11px/1 ui-sans-serif,system-ui,sans-serif;fill:var(--accent);
  text-anchor:middle;pointer-events:none;font-variant-numeric:tabular-nums}
.usmap .lead{stroke:var(--accent);stroke-width:.75;fill:none}
.usmap .st.has:hover path{fill:var(--accent)}
.usmap .st.has:hover .ab,.usmap .st.has:hover .n{fill:var(--bg)}
.usmap .st.has[aria-pressed=true] path{fill:var(--accent);stroke:var(--fg);stroke-width:2.5}
.usmap .st.has[aria-pressed=true] .ab,.usmap .st.has[aria-pressed=true] .n{fill:var(--bg)}
.usmap .st.has:focus-visible{outline:none}
.usmap .st.has:focus-visible path{stroke:var(--fg);stroke-width:3;stroke-dasharray:4 2}
.usmap .inset{stroke:var(--line);stroke-width:1;fill:none;stroke-dasharray:3 3}
.usmap .insetlab{font:500 9px/1 ui-sans-serif,system-ui,sans-serif;fill:var(--muted)}
.maplegend{font-size:.78rem;margin:.7em 0 0;max-width:60ch}
.maplist{font:.82rem/1.5 ui-sans-serif,system-ui,sans-serif;margin:.5em 0 0}
.maplist summary{color:var(--accent);cursor:pointer}
.maplist table{border-collapse:collapse;margin:.6em 0 0;font-size:.98em}
.maplist td{border-bottom:1px solid var(--line);padding:2px 14px 2px 0}
.maplist td.c{font-variant-numeric:tabular-nums;text-align:right}
.maplist button.mrow{font:inherit;color:var(--accent);background:none;border:0;padding:4px 0;
  min-height:32px;cursor:pointer;text-align:left;text-decoration:underline;
  text-underline-offset:2px}
.maplist button.mrow[aria-pressed=true]{color:var(--fg);font-weight:600;text-decoration:none}
.maplist button.mrow:focus-visible{outline:2px solid var(--fg);outline-offset:2px}

/* ---- filter controls ---- */
.controls{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;margin:1.4em 0 1em;
  padding:12px 14px;border:1px solid var(--line);border-radius:var(--radius);background:var(--card);
  font:.85rem/1.4 ui-sans-serif,system-ui,sans-serif}
.controls label{display:flex;gap:6px;align-items:center;color:var(--muted)}
.controls select{font:inherit;padding:4px 6px;border:1px solid var(--line);border-radius:4px;
  background:var(--bg);color:var(--fg);max-width:210px}
.controls button{font:inherit;padding:5px 10px;border:1px solid var(--line);border-radius:4px;
  background:var(--bg);color:var(--fg);cursor:pointer}
.rowcount{margin-left:auto;font-weight:600;color:var(--fg);font-variant-numeric:tabular-nums}

/* ---- provision matrix ---- */
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--card)}
table.matrix{border-collapse:collapse;width:100%;font:.85rem/1.4 ui-sans-serif,system-ui,sans-serif}
table.matrix th,table.matrix td{border-bottom:1px solid var(--line);padding:7px 6px;text-align:center}
table.matrix thead th{position:sticky;top:0;background:var(--card);z-index:1;
  border-bottom:2px solid var(--line);vertical-align:bottom}
th.pv{height:150px;padding:6px 2px;font-weight:500}
th.pv>span{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;
  font-size:.72rem;color:var(--muted)}
td.pv{width:26px;min-width:26px}
td.pv.on{background:var(--accent-weak)}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--accent)}
th.bill{text-align:left;white-space:nowrap;padding-left:12px}
th.bill a{font-weight:600;text-decoration:none}
th.bill a:hover{text-decoration:underline}
.rowmeta{display:none}
td.yr{font-variant-numeric:tabular-nums;color:var(--muted)}
td.fam{color:var(--muted)}
td.chipsum{display:none}
table.matrix tbody tr:hover td.pv.on{background:var(--accent)}
table.matrix tbody tr:hover .dot{background:var(--bg)}

@media (max-width:760px){
  .usmap .ab{font-size:13px}
  .usmap .n{font-size:13px}
  .tablewrap{overflow:visible;border:0;background:transparent}
  table.matrix,table.matrix tbody,table.matrix tr{display:block;width:100%}
  table.matrix thead{display:none}
  table.matrix tr{border:1px solid var(--line);border-radius:var(--radius);
    background:var(--card);margin-bottom:10px;padding:12px 14px}
  table.matrix th,table.matrix td{border:0;padding:0;text-align:left;display:none}
  /* These two must out-specify the rule above (0,1,2), hence the table.matrix prefix. */
  table.matrix th.bill{display:block;white-space:normal;padding-left:0}
  table.matrix th.bill a{font-size:1.02rem}
  table.matrix th.bill .rowmeta{display:block;color:var(--muted);font-size:.8rem;margin-top:2px}
  table.matrix td.chipsum{display:block;margin-top:8px}
  .rowcount{margin-left:0;width:100%}
}

.crumb{font:.85rem/1 ui-sans-serif,system-ui,sans-serif;margin:0 0 1.2em}
h1+.lede{margin-top:-.2em}
.statusblock{border:1px solid var(--line);background:var(--card);border-radius:var(--radius);
  padding:14px 16px;margin:1.4em 0 1.8em}
.chip.big{font-size:.85rem;padding:5px 11px}
.evidence{margin:.7em 0 0;font:.88rem/1.55 ui-sans-serif,system-ui,sans-serif;color:var(--fg)}
.evidence .lbl{display:block;color:var(--muted);font-size:.76rem;text-transform:uppercase;
  letter-spacing:.06em;margin-bottom:2px}
blockquote.clause{margin:1.6em 0;padding:16px 20px;border-left:3px solid var(--accent);
  background:var(--accent-weak);border-radius:0 var(--radius) var(--radius) 0}
blockquote.clause p{margin:0 0 .6em;font-size:1.02rem}
blockquote.clause cite{font:.8rem/1.4 ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-style:normal}
dl.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px 24px;margin:1.4em 0}
dl.facts>div{border-top:1px solid var(--line);padding-top:8px}
dl.facts dt{font:.74rem/1.3 ui-sans-serif,system-ui,sans-serif;text-transform:uppercase;
  letter-spacing:.06em;color:var(--muted);margin-bottom:3px}
dl.facts dd{margin:0;font-size:.94rem}
.chips{margin:.4em 0 0}
ul.changes,ul.sponsors,ul.versions,ul.watch,ul.urls{margin:.5em 0 0;padding-left:1.15em}
ul.changes li,ul.watch li{margin:.35em 0}
ul.sponsors{list-style:none;padding-left:0;columns:2;column-gap:26px}
ul.sponsors li{margin:.2em 0;font-size:.94rem;break-inside:avoid}
.party{font:600 .74rem ui-sans-serif,system-ui,sans-serif;color:var(--muted)}
ul.versions li{margin:.35em 0;font-size:.94rem}
.has-text{font:600 .68rem ui-sans-serif,system-ui,sans-serif;color:var(--add);
  background:var(--add-bg);padding:2px 6px;border-radius:99px;margin-left:4px}
ul.urls{list-style:none;padding-left:0}
ul.urls li{margin:.3em 0}
ul.urls a{font:.8rem/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;word-break:break-all}
.notes p{font-size:.95rem;margin:.8em 0;max-width:74ch}
.cite{font:.86rem/1.6 ui-sans-serif,system-ui,sans-serif;background:var(--card);
  border:1px solid var(--line);border-radius:var(--radius);padding:12px 14px;max-width:74ch}
.small{font-size:.85rem}
h3{font-size:.95rem;margin:1.4em 0 .3em;color:var(--muted);
  font-family:ui-sans-serif,system-ui,sans-serif;text-transform:uppercase;letter-spacing:.06em}
time{font-variant-numeric:tabular-nums}
@media (max-width:700px){ ul.sponsors{columns:1} }

@media (max-width:700px){
  header.site .wrap{flex-direction:column;align-items:flex-start}
  main{padding-top:24px}
  h1{font-size:1.6rem}
}
"""

# ---------------------------------------------------------------- version diffs
import legdiff

_STRUCTURAL_NOTE = (
    "<strong>Comparison method: structural.</strong> Provisions are matched by their full "
    "section and subsection path, parent context included, so a change is reported against the "
    "provision it affects and a designator such as <code>(1)</code> under one subsection is "
    "never aligned with <code>(1)</code> under another. Text that survives under a new number "
    "is reported as redesignated rather than as a removal and an addition. This is textual and "
    "structural comparison, not legal interpretation — always read the linked source.")

_FALLBACK_NOTE = (
    "<strong>Comparison method: text fallback.</strong> This comparison could not establish "
    "reliable legislative structure. Changes are shown at text level and may contain alignment "
    "artefacts; blocks carry no identity, so nothing here is claimed to be the same provision "
    "amended.")

_AMB_NOTE = ("Some provisions had repeated structural labels and could not be uniquely aligned. "
             "They are listed without a comparison.")


def render_diff(b):
    vs = [v for v in b["versions"] if v.get("text_path")]
    if len(vs) < 2: return "", None
    a, z = vs[0], vs[-1]
    mech = next((v for v in vs[1:-1]
                 if re.search(r"amendment|substitute|SA\d|HA\d|HCS", v["label"], re.I)), None)
    r = legdiff.diff_texts((REG / a["text_path"]).read_text(),
                           (REG / z["text_path"]).read_text())

    def line(cls, lab, body, tag="", el="span"):
        inner = {"del": f"<del>{esc(body)}</del>", "add": f"<ins>{esc(body)}</ins>"}.get(
            cls, esc(body))
        lb = f'<span class="ulab">{esc(lab)}</span>' if lab else ""
        return f'<p class="{cls}">{lb}{tag}{inner}</p>'

    parts, run = [], []
    def flush():
        nonlocal run
        if len(run) > 4:
            parts.extend([run[0],
                          f'<p class="elide">… {len(run)-2} provisions unchanged …</p>',
                          run[-1]])
        else:
            parts.extend(run)
        run = []

    for e in r.entries:
        if e.kind == "unchanged":
            run.append(line("same", e.label, e.old or e.new)); continue
        flush()
        if e.kind == "modified":
            tag = '<span class="modtag">modified</span>'
            parts.append(line("del", e.label, e.old, tag))
            parts.append(line("add", "", e.new))
        elif e.kind == "renumbered":
            parts.append(line("renum", e.label, e.new or e.old,
                              '<span class="renumtag">same text, new designator</span>'))
        elif e.kind == "ambiguous":
            parts.append(line("amb", e.label, e.old,
                              '<span class="ambtag">not aligned</span>'))
        elif e.kind == "removed":
            parts.append(line("del", e.label, e.old))
        else:
            parts.append(line("add", e.label, e.new))
    flush()

    total = r.nodes_total or 1
    retained = r.unchanged + r.renumbered
    mechhtml = (f'<p class="mech"><span class="lbl">Mechanism</span> '
                f'<a href="{esc(mech["source_url"])}">{esc(mech["label"])}</a></p>') if mech else ""

    counts = [f'<span class="k del">{r.removed} removed</span>',
              f'<span class="k add">{r.added} added</span>',
              f'<span class="k mod">{r.modified} modified</span>']
    if r.renumbered:
        counts.append(f'<span class="k renum">{r.renumbered} same text, '
                      f'new designator</span>')
    if r.ambiguous:
        counts.append(f'<span class="k amb">{r.ambiguous} identity not '
                      f'established</span>')
    counts.append(f'<span class="muted">{r.unchanged} of {total} provisions unchanged</span>')

    note = _STRUCTURAL_NOTE if r.mode == "structural" else _FALLBACK_NOTE
    if r.ambiguous:
        note += f' {_AMB_NOTE}'
    warn = ""
    if r.parser_warnings:
        warn = ('<details class="diffwarn"><summary>Parser notes '
                f'({len(r.parser_warnings)})</summary><ul>'
                + "".join(f"<li>{esc(w)}</li>" for w in r.parser_warnings) + "</ul></details>")

    stat = (f'<p class="diffstat">{" ".join(counts)}</p>'
            f'<p class="diffmode muted">{note}</p>{warn}')
    html_ = (f'<div class="diff"><p class="diffhead">'
             f'<span class="v from">{esc(a["label"])}</span>'
             f'<span class="arrow" aria-hidden="true">→</span>'
             f'<span class="v to">{esc(z["label"])}</span></p>'
             f'{mechhtml}{stat}<div class="difftext">{"".join(parts)}</div></div>')
    return html_, {"id": b["id"], "removed": r.removed, "added": r.added, "modified": r.modified,
                   "unchanged": r.unchanged, "renumbered": r.renumbered,
                   "ambiguous": r.ambiguous, "total": total, "from": a["label"],
                   "to": z["label"], "retained": retained / total, "mode": r.mode,
                   "warnings": len(r.parser_warnings)}

def changed_callout(bills):
    seen=set(); items=[]
    for b in bills:
        _,d = render_diff(b)
        if not d: continue
        # Companion bills share a text and should appear once. Key on the companion
        # group, never on the diff counts: two unrelated bills with the same number
        # of removals and additions would silently collapse into one.
        key=b.get("companion_group") or b["id"]
        if key in seen: continue
        seen.add(key)
        items.append(f'<li><a href="bills/{esc(b["id"])}/#main">'
                     f'{esc(b["jurisdiction"]["state"])} {esc(b["bill_number"])}</a> — '
                     f'<span class="k del">{d["removed"]} provisions removed</span>, '
                     f'<span class="k add">{d["added"]} added</span>, '
                     f'<span class="k mod">{d["modified"]} amended</span>, '
                     f'{d["retained"]:.0%} carried over verbatim</li>')
    if not items: return ""
    return (f'<aside class="callout"><h2>Bills whose text changed materially</h2>'
            f'<p>Where we hold both the introduced and the final text, the registry shows the '
            f'change itself rather than describing it. Companion bills share a text and appear once.</p>'
            f'<ul class="changed">{"".join(items)}</ul></aside>')

# ---------------------------------------------------------------- data page + downloads
import csv as _csv, io, json as _json

FLAT_COLS=["id","state","bill_number","chamber","year_introduced","session","legislature",
  "status","status_as_of","status_evidence_action","status_evidence_date","codified_at",
  "effective_date","family","derived_from","technique","definitional_anchor",
  "augmented_human_exposure","affects_algorithmic_entity_formation","corporate_carve_out",
  "provisions","sponsors","companion_group","verification_status","last_verified",
  "key_clause","primary_sources","versions_held"]

def flat_rows(bills):
    for b in bills:
        ev=b["status"].get("evidence") or {}
        yield {
          "id":b["id"],"state":b["jurisdiction"]["state"],"bill_number":b["bill_number"],
          "chamber":b["chamber"],"year_introduced":b["session"]["year_introduced"],
          "session":b["session"]["session"],"legislature":b["session"].get("legislature") or "",
          "status":b["status"]["stage"],"status_as_of":b["status"]["as_of"],
          "status_evidence_action":ev.get("action",""),"status_evidence_date":ev.get("date",""),
          "codified_at":b["codified_at"] or "","effective_date":b["effective_date"] or "",
          "family":b["family"],"derived_from":b["derived_from"] or "","technique":b["technique"],
          "definitional_anchor":b["definitional_anchor"],
          "augmented_human_exposure":b["augmented_human_exposure"],
          "affects_algorithmic_entity_formation":b["affects_algorithmic_entity_formation"],
          "corporate_carve_out":b["corporate_carve_out"],
          "provisions":"; ".join(b["provisions"]),
          "sponsors":"; ".join(f'{x["name"]}'+(f' [{x["party"]}]' if x.get("party") else "") for x in b["sponsors"]),
          "companion_group":b["companion_group"] or "",
          "verification_status":b["verification_status"],"last_verified":b["last_verified"] or "",
          "key_clause":(b["key_clause"] or {}).get("text",""),
          "primary_sources":" | ".join(b["sources"].get("primary",[])),
          "versions_held":sum(1 for v in b["versions"] if v.get("text_path")),
        }

def write_data(d, bills, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir/"bills.json").write_text(_json.dumps(d, indent=2, ensure_ascii=False))
    buf=io.StringIO(); w=_csv.DictWriter(buf, fieldnames=FLAT_COLS); w.writeheader()
    for r in flat_rows(bills): w.writerow(r)
    (outdir/"bills.csv").write_text(buf.getvalue())
    buf=io.StringIO(); w=_csv.writer(buf)
    w.writerow(["id","state","bill_number","year","family","status"]+PROV_ORDER)
    for b in bills:
        w.writerow([b["id"],b["jurisdiction"]["state"],b["bill_number"],
                    b["session"]["year_introduced"],b["family"],b["status"]["stage"]]
                   +[1 if p in b["provisions"] else 0 for p in PROV_ORDER])
    (outdir/"matrix.csv").write_text(buf.getvalue())
    return {"bills.json":(outdir/"bills.json").stat().st_size,
            "bills.csv":(outdir/"bills.csv").stat().st_size,
            "matrix.csv":(outdir/"matrix.csv").stat().st_size}

def data_page(d, bills, sizes):
    kb=lambda n: f"{n/1024:.0f} KB"
    texts=sum(1 for b in bills for v in b["versions"] if v.get("text_path"))
    body=f"""
<h1>Data</h1>
<p class="lede">The registry is the dataset. Everything on this site is generated from one
file, so the download is not an export — it is the source.</p>

<h2>Downloads</h2>
<table class="deftable"><thead><tr><th scope="col">File</th><th scope="col">Contents</th>
<th scope="col" class="n">Size</th></tr></thead><tbody>
<tr><td><a href="bills.json">bills.json</a></td><td>The full registry: {len(bills)} records with
every field, including notes, version histories, source lists and verification metadata.
This is the authoritative form.</td><td class="n">{kb(sizes["bills.json"])}</td></tr>
<tr><td><a href="bills.csv">bills.csv</a></td><td>One row per bill, {len(FLAT_COLS)} columns.
Nested fields are flattened with semicolons. Convenient; lossy.</td>
<td class="n">{kb(sizes["bills.csv"])}</td></tr>
<tr><td><a href="matrix.csv">matrix.csv</a></td><td>The provision matrix as 1/0 columns —
{len(bills)} rows by {len(PROV_ORDER)} provisions. For counting and cross-tabulation.</td>
<td class="n">{kb(sizes["matrix.csv"])}</td></tr>
</tbody></table>

<h2>What the data contains</h2>
<ul>
<li><strong>One record per bill number</strong>, not per legislative vehicle. Companion bills
each get a record, linked by <code>companion_group</code>. This is what preserves cases where
identical text diverges — different committees, different sponsors, different fates.</li>
<li><strong>Statutory citations and effective dates</strong> for enacted laws.</li>
<li><strong>An action of record</strong> behind every status, so no status is an unsourced
assertion.</li>
<li><strong>{len(PROV_ORDER)} flat provision tags</strong>, checkable against bill text.</li>
<li><strong>Descent relationships</strong> with an explicit list of what changed between parent
and child.</li>
<li><strong>{texts} stored bill texts</strong> referenced by <code>versions[].text_path</code>,
which is what makes the diffs reproducible.</li>
</ul>

<h2>Reproducing this site</h2>
<p>The site is built by a single script with no dependencies beyond the Python standard
library, and makes no network requests at runtime. Given the registry and the stored texts,
every page here — including the matrix, the lineage graph and the diffs — is regenerable.</p>

<h2>Licence</h2>
<p>Data and documentation: <strong>CC BY 4.0</strong>. Code: MIT. Reuse and adapt it, including
commercially — give credit, link the licence, and say if you changed anything.</p>
<p class="muted small">The underlying legislative texts are US government edicts and are in the
public domain. The CC BY licence covers this registry's structuring, classification and
verification metadata, not the statutes themselves.</p>

<h2>Known gaps</h2>
<ul>
<li>Operative text has not been read line by line for every record. Where verification rested
on a status page or official summary, the record's notes say so.</li>
<li>Some sponsor lists are incomplete, and party affiliation is recorded only where a source
stated it. An empty sponsor field means not established, not none.</li>
<li>Coverage is US state legislatures only. See <a href="../method/">Method</a>.</li>
</ul>
"""
    return page("Data", body, depth=1, active="data/",
                desc="Download the registry as JSON or CSV, and what the dataset contains.")

# ---------------------------------------------------------------- method page
def method_page(d, bills):
    vs={}; 
    for b in bills: vs[b["verification_status"]]=vs.get(b["verification_status"],0)+1
    provrows="".join(
      f'<tr><td><code>{esc(k)}</code></td><td>{esc(v)}</td>'
      f'<td class="n">{sum(1 for b in bills if k in b["provisions"])}</td></tr>'
      for k,v in PROVISION_LABEL.items())
    body=f"""
<h1>Method</h1>
<p class="lede">What this registry contains, how each record is established, and what it
deliberately does not do.</p>

<h2>Scope</h2>
<p><strong>In scope.</strong> Bills and enacted laws of US state legislatures that address the
legal status, legal personhood, or asserted mental properties of AI systems — including
provisions that deny personhood, declare AI non-sentient, allocate liability, restrict what a
chatbot may claim about itself, or restrict AI speech rights.</p>
<p><strong>Out of scope, for now.</strong> Courts and litigation; federal legislation;
non-US jurisdictions; corporate and laboratory internal policies. Court decisions on AI
personhood, inventorship and standing are tracked by
<a href="https://naturalandartificiallaw.com/ai-rights-and-legal-personhood-tracker/">Matthew
Lee's AI Rights and Legal Personhood Tracker</a>, which we recommend rather than duplicate.</p>
<p>General AI-legislation trackers covering all AI topics at volume include MultiState, IAPP,
NCSL and Orrick. This registry is narrower and structured differently: it records what
individual provisions say, how bills descend from one another, and how their text changed.</p>

<h2>Inclusion does not imply endorsement</h2>
<p>Listing a bill here does not mean we support it, oppose it, or hold any view about whether
AI systems should have legal status. Records describe what bills say. Where a bill is claimed
to be unconstitutional, we record <em>who made the claim</em> and attribute it; we never assert
it ourselves.</p>
<p>This registry is intended to be equally usable by people who support these bills and people
who oppose them.</p>

<h2>Source hierarchy</h2>
<ol>
<li><strong>Primary sources preferred.</strong> Enacted acts, published chapters, enrolled and
introduced bill text, official action histories.</li>
<li><strong>Legislative trackers</strong> (e.g. LegiScan) where a primary host is unreachable
and the tracker establishes a citable fact such as a session-law chapter or a vote count.</li>
<li><strong>Archived copies</strong> (Internet Archive) where a primary document has been
overwritten or the host is unreachable. Several introduced texts here exist only as archived
snapshots, because the legislature's "bill text" URL serves the current version and is
overwritten on amendment.</li>
</ol>
<p>Every record names its sources and carries the date it was last checked.</p>

<h2>Verification status</h2>
<table class="deftable"><tbody>
<tr><td><code>verified_primary</code></td><td>A person has read the primary document.</td>
<td class="n">{vs.get("verified_primary",0)}</td></tr>
<tr><td><code>verified_secondary</code></td><td>Established from a tracker record because the
primary host could not be reached. Better than unverified, weaker than primary. Never silently
promoted.</td><td class="n">{vs.get("verified_secondary",0)}</td></tr>
<tr><td><code>seeded_unverified</code></td><td>Transcribed from a secondary account and not yet
checked. Labelled as such wherever it appears.</td><td class="n">{vs.get("seeded_unverified",0)}</td></tr>
</tbody></table>
<p class="muted small">A bill's <em>status</em> is a claim like any other, so each carries an
<em>action of record</em> — the verbatim legislative action establishing it — for every
<strong>terminal</strong> status (enacted, failed, dead), which the validator enforces.
Non-terminal statuses carry one where the source supplied it. States record
death differently: Wisconsin posts an explicit "failed to pass" line, Missouri posts nothing
and a bill simply dies at adjournment, and Washington carries bills across a biennium so they
do not die at all. The action line makes which of these applies visible.</p>

<h2>Provision tags</h2>
<p>Flat and descriptive. Every tag must be checkable against bill text such that two readers
would reach the same answer. There is no score, index, ranking or rating, and rows are ordered
chronologically — sorting by anything implying a hierarchy would be an editorial act.</p>
<p class="muted small">Tags describe a record's <strong>operative</strong> text. Where a
provision was present as introduced and removed later, the change appears in that bill's diff
rather than in its tags.</p>
<table class="deftable"><thead><tr><th scope="col">Tag</th><th scope="col">Meaning</th>
<th scope="col" class="n">Bills</th></tr></thead><tbody>{provrows}</tbody></table>
<p class="muted small"><code>restricts_person_like_training</code> currently applies to no
record. It is not a mistake: it described Tennessee HB 1455 as introduced, which would have
made training AI for companionship a felony, and that text was replaced in committee. Because
tags describe operative text, the tag is retained in the vocabulary but attaches to nothing —
the provision survives only in that bill's <a href="../bills/tn-hb1455-2025/">diff</a>. This
is the clearest illustration of the limitation noted above.</p>

<h2 id="diff">How version comparisons are produced</h2>
<p>Where two texts of the same bill are held, the registry compares them provision by
provision rather than describing the change in prose. The comparison is mechanical and its
assumptions are worth stating, because a diff that looks authoritative is easy to over-read.</p>
<ul>
<li><strong>Structure, where it can be identified.</strong> Legislative text marks its own
hierarchy — <code>SECTION 1.</code>, <code>2.</code>, <code>(a)</code>, <code>(1)</code> — and
the comparison uses those designators. Nesting is inferred from the order the designators
appear in each document, because conventions differ: Tennessee runs
<code>SECTION</code> → <code>(19)</code> → <code>(A)</code>, Missouri runs
<code>1.2045.</code> → <code>2.</code> → <code>(1)</code>. No fixed precedence is assumed.</li>
<li><strong>Identity is the whole path, not the label.</strong> <code>(1)</code> under one
subsection is a different provision from <code>(1)</code> under another, and the two are never
aligned. A statutory citation such as <code>Section 1-3-105(a)</code> or
<code>N.D. Cent. Code § 1-01-49(8)</code> is not structure, and stays inside the sentence that
cites it.</li>
<li><strong>Identical text under a new designator is reported as such.</strong> Inserting one
subdivision renumbers every later one, and treating that as deletion-plus-insertion overstates
the change. The test is exact text occurring once in each version — nothing weaker. A provision
that was both renumbered <em>and</em> amended is therefore reported as a removal and an addition,
and so is boilerplate that recurs verbatim, because neither can be matched on text alone.</li>
<li><strong>A parent's move says nothing about its children.</strong> An earlier version of this
differ inferred that a child whose text was identical had moved with its redesignated parent.
That inference was withdrawn after external review: it is not observable in the documents, and it
made this project's most-quoted comparison read more cleanly, which is the wrong reason to keep
a rule.</li>
<li><strong>Definitions are matched by the term they define.</strong> In a list where every
sibling opens with a quoted term and the terms are unique on both sides, the term is the
identity, so re-alphabetising a definitions subsection does not report each definition as having
been rewritten into the next one. Where that condition does not hold, the rule does not fire.</li>
<li><strong>Ambiguity is shown, not resolved.</strong> Where the same designator repeats on both
sides, the provisions are listed as <em>identity not established</em> rather than compared —
pairing them would require a positional guess. The same applies to a blank
<code>( )</code> designator, which Tennessee uses for subdivisions the code reviser will number
later: it can be matched on exact text and on nothing else. Such provisions are kept distinct
from one another by position, which is a reading aid and not a claim about identity.</li>
<li><strong>Fallback is labelled.</strong> If structure cannot be identified reliably, the
comparison falls back to block-level text matching and says so on the record. A fallback
comparison makes no claim that any block is the same provision amended.</li>
</ul>
<p><code>modified</code> means the same structural provision exists in both versions and its
text differs. It does not mean the legal effect changed, and the comparison makes no judgement
about legal effect. This is textual and structural comparison, not legal interpretation, not
semantic comparison, and not a complete parse of legislative drafting. Counts are a reading
aid; the linked source is the evidence.</p>
<p class="muted small">The implementation is <code>site/legdiff.py</code>, with adversarial
tests in <code>site/test_diff.py</code> covering citations that look like designators, reused
labels, insertions that must not cascade, and text with no usable structure. It replaced a
punctuation-based comparison that split <code>N.D. Cent. Code</code> into fragments and severed
<code>SECTION 1.</code> from the text it introduced; that failure was found by external review,
not by us.</p>

<h2>Use of AI in compiling this registry</h2>
<p>This registry was compiled with substantial assistance from AI tools, which were used to
retrieve documents, extract fields, draft classifications and generate this site. AI tools
make mistakes: they misread documents, invent plausible details, and mis-attribute sources.
Every record was checked against its source by a person before publication, and the
verification status above records how far that went for each one. Errors will remain. Please
report them.</p>

<h2>Corrections</h2>
<p>If you find an error, a stale status, a broken link, a missing bill or a
mischaracterised provision, please tell us. Corrections are logged with the date and what
changed. The registry is versioned, so every change is a dated, inspectable record.</p>

<h2>Citing this registry</h2>
<p class="cite">{esc(SITE["name"])}, {esc(SITE["publisher"])}. Record for [state and bill
number], last verified [date shown on the record]. Accessed [date].
&lt;{esc(SITE["base"])}/bills/[record-id]/&gt;</p>
<p class="muted small">Cite individual records rather than the site as a whole where you can:
each carries its own verification date, and the registry changes.</p>

<h2>Update cadence</h2>
<p>State legislatures are seasonal. Most activity falls between January and May, and the
registry is checked most often in that window. The header states when it was last verified;
treat that date, not the publication date, as the currency of the data. We would rather show
an honest last-verified date than imply continuous coverage we cannot hold.</p>

<h2>Source dataset</h2>
<p>The registry began from Appendix A of Smith, Caviola &amp; Alexander (2026),
<em>Denying Personhood to AI: An Analysis of U.S. State Legislation on AI Legal Status</em>
(SSRN 6829981), which documented {len(bills)} bills across
{len({b["jurisdiction"]["state"] for b in bills})} states as of May 2026. Every record has
since been checked against a primary or citable source and carries a per-record account of what was verified. The registry now records statutory citations,
effective dates, sponsors, vote counts, provision detail and text versions that the paper did
not set out to capture. The underlying data is available on the <a href="../data/">data</a>
page.</p>
"""
    return page("Method", body, depth=1, active="method/",
                desc="Scope, source hierarchy, verification status, provision definitions, AI-use disclosure and citation guidance.")

# ---------------------------------------------------------------- watch list
KIND_LABEL={"effective":"Takes effect","expiry":"Deadline passes","report":"Report due",
            "ballot":"Goes to voters","deadline":"Deadline"}

def watch_panel(bills, today):
    grouped={}
    for b in bills:
        for w in b["watch_dates"]:
            grouped.setdefault((w["date"],w["event"],w["kind"]),[]).append(b)
    if not grouped: return ""
    rows=[]
    for (date,event,kind) in sorted(grouped):
        bs=grouped[(date,event,kind)]
        refs=", ".join(f'<a href="bills/{esc(x["id"])}/">{esc(x["jurisdiction"]["state"])} '
                       f'{esc(x["bill_number"])}</a>' for x in bs)
        past = date < today
        rows.append(f'<tr{" class=past" if past else ""}>'
                    f'<td class="wd"><time datetime="{esc(date)}">{esc(date)}</time></td>'
                    f'<td class="wk">{esc(KIND_LABEL.get(kind,kind))}</td>'
                    f'<td class="we">{esc(event)}</td>'
                    f'<td class="wb">{refs}</td></tr>')
    return (f'<aside class="watch"><h2>What happens next</h2>'
            f'<p>Dated events the registry is holding, soonest first. Trackers are usually '
            f'retrospective; these are commitments already written into bill text.</p>'
            f'<table class="watchtable"><thead><tr><th scope="col">Date</th>'
            f'<th scope="col">Event</th><th scope="col">Detail</th>'
            f'<th scope="col">Bills</th></tr></thead><tbody>{"".join(rows)}</tbody></table></aside>')

# ---------------------------------------------------------------- lineage graph
STAGE_SHORT={"passed_one_chamber":"passed 1 chamber","in_committee":"in committee"}

def lineage(bills):
    byid={b["id"]:b for b in bills}
    kids={}
    for b in bills:
        if b["derived_from"]: kids.setdefault(b["derived_from"],[]).append(b["id"])
    linked={i for i in kids} | {c for v in kids.values() for c in v}
    roots=[i for i in kids if not byid[i]["derived_from"]]
    orphans=[b for b in bills if b["id"] not in linked]

    NW,NH,GX,GY,PAD = 200,44,88,16,14
    trees=[]; edgedefs=[]
    for root in sorted(roots, key=lambda i:byid[i]["session"]["year_introduced"]):
        # depth-first layout: x = generation, y = running row
        pos={}; row=[0]
        def place(nid, depth):
            ch=sorted(kids.get(nid,[]), key=lambda i:(byid[i]["jurisdiction"]["state"],byid[i]["bill_number"]))
            if not ch:
                pos[nid]=(depth,row[0]); row[0]+=1; return pos[nid][1]
            ys=[place(c,depth+1) for c in ch]
            y=(min(ys)+max(ys))/2; pos[nid]=(depth,y); return y
        place(root,0)
        maxd=max(d for d,_ in pos.values()); maxr=max(y for _,y in pos.values())
        W=PAD*2+(maxd+1)*NW+maxd*GX; H=PAD*2+(maxr+1)*(NH+GY)
        X=lambda d: PAD+d*(NW+GX); Y=lambda y: PAD+y*(NH+GY)
        paths=[];nodes=[]
        for nid,(d,y) in pos.items():
            b=byid[nid]; x0,y0=X(d),Y(y)
            for c in kids.get(nid,[]):
                cd,cy=pos[c]; x1,y1=X(cd),Y(cy)
                mx=(x0+NW+x1)/2
                paths.append(f'<path d="M{x0+NW} {y0+NH/2} C{mx} {y0+NH/2} {mx} {y1+NH/2} {x1} {y1+NH/2}" '
                             f'class="edge"/>')
                n=len(byid[c]["derived_from_changes"])
                paths.append(f'<a href="#e-{esc(c)}"><circle cx="{mx}" cy="{(y0+y1)/2+NH/2}" r="9" class="ebadge"/>'
                             f'<text x="{mx}" y="{(y0+y1)/2+NH/2+3.5}" class="ebadget">{n}</text></a>')
                edgedefs.append((nid,c))
            st=b["status"]["stage"]
            nodes.append(
              f'<a href="../bills/{esc(nid)}/" class="gnode"><rect x="{x0}" y="{y0}" width="{NW}" height="{NH}" '
              f'rx="5" class="nbox s-{esc(st)}"/>'
              f'<text x="{x0+11}" y="{y0+18}" class="nt">{esc(b["jurisdiction"]["state"])} {esc(b["bill_number"])}</text>'
              f'<text x="{x0+11}" y="{y0+34}" class="nm">{esc(b["session"]["year_introduced"])} · fam {esc(b["family"])} · '
              f'{esc(STAGE_SHORT.get(st, st.replace("_"," ")))}</text></a>')
        trees.append(f'<figure class="tree"><figcaption>Template family rooted in '
                     f'{esc(byid[root]["jurisdiction"]["state"])} {esc(byid[root]["bill_number"])}</figcaption>'
                     f'<div class="svgscroll"><svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
                     f'role="img" aria-label="Lineage diagram">{"".join(paths)}{"".join(nodes)}</svg></div></figure>')

    defs=[]
    for par,ch in edgedefs:
        c=byid[ch]; pb=byid[par]
        items="".join(f"<li>{esc(x)}</li>" for x in c["derived_from_changes"])
        defs.append(f'<div class="edgedef" id="e-{esc(ch)}">'
                    f'<h3><a href="../bills/{esc(par)}/">{esc(pb["jurisdiction"]["state"])} {esc(pb["bill_number"])}</a>'
                    f' <span class="arrow">→</span> '
                    f'<a href="../bills/{esc(ch)}/">{esc(c["jurisdiction"]["state"])} {esc(c["bill_number"])}</a></h3>'
                    f'<ul>{items}</ul></div>')

    orph="".join(f'<li><a href="../bills/{esc(b["id"])}/">{esc(b["jurisdiction"]["state"])} '
                 f'{esc(b["bill_number"])}</a> <span class="muted">({esc(b["session"]["year_introduced"])})</span></li>'
                 for b in orphans)
    body=f"""
<h1>Template lineage</h1>
<p class="lede">Most of these bills are not independently drafted. {len(edgedefs)} documented
descent relationships link {len(linked)} of the {len(bills)} bills into
{len(roots)} template families. Numbers on the connectors count the differences between
parent and child; each links to the detail below.</p>
{"".join(trees)}
<h2>What changed in transit</h2>
<p class="muted small">Every line is a checkable statement about bill text, drawn from the
verified records. Nothing here characterises a bill as better or worse than its parent.</p>
{"".join(defs)}
<h2>No documented template lineage</h2>
<p class="muted small">{len(orphans)} bills we have not traced to a parent text. That means we
found no evidence of descent, not that none exists.</p>
<ul class="orphans">{orph}</ul>
"""
    return page("Template lineage", body, depth=1, active="lineage/",
                desc="How AI legal-status bills descend from one another, and what changed at each step.")

# ---------------------------------------------------------------- landing: map + matrix
# State boundaries come from us-atlas 3.0.1, vendored at site/geo/ and hashed in
# registry/source_manifest.json. The publisher has already applied the projection —
# d3.geoAlbersUsa fitted to 975x610, Alaska and Hawaii placed bottom-left — so nothing
# here projects anything; it decodes TopoJSON arcs into SVG paths and stops.
GEO = ROOT / "geo" / "states-albers-10m.json"

# FIPS is what the geometry carries; postal codes are what the registry keys on. Derived
# from the Census reference file https://www2.census.gov/geo/docs/reference/state.txt and
# cross-checked both ways against the vendored geometry: 51 codes, 51 geometries, every
# STATE_NAME identical. _load_geometry re-asserts the coverage at build time.
FIPS_USPS = {
 "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE","11":"DC",
 "12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN","19":"IA","20":"KS","21":"KY",
 "22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN","28":"MS","29":"MO","30":"MT",
 "31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC","38":"ND","39":"OH",
 "40":"OK","41":"OR","42":"PA","44":"RI","45":"SC","46":"SD","47":"TN","48":"TX","49":"UT",
 "50":"VT","51":"VA","53":"WA","54":"WV","55":"WI","56":"WY",
}

# The north-eastern seaboard cannot hold a label inside its own outline at this scale —
# Maryland's centroid and DC's are four units apart. These states get the label pushed
# clear with a leader line back to the shape. Present now though none of them yet holds a
# bill, because discovering the collision after the registry gains Delaware is worse.
LABEL_OFFSET = {
 "DC":(74,26), "MD":(80,-2), "DE":(66,10), "NJ":(60,-14), "RI":(46,10),
 "CT":(52,-6), "MA":(58,-20), "NH":(40,-26), "VT":(-34,-24),
}
# Labels and column order come from registry/vocabulary.json, the same file the
# validator reads its allowed keys from.
_VOCAB = json.loads((REG / "vocabulary.json").read_text())
PROVISION_LABEL = {p["key"]: p["label"] for p in _VOCAB["provisions"]}
PROV_ORDER = [p["key"] for p in _VOCAB["provisions"] if p.get("in_matrix")]

def _decode_topology(topo):
    """TopoJSON -> {usps: (name, path_d, label_point)}. Standard library only.

    Coordinates are rounded to whole units: the map renders about 720 CSS px wide against
    a 975-unit viewBox, so sub-unit precision is 39 KB of path data nobody can see.
    """
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:                       # delta-encoded and quantized
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx; y += dy
            p = (round(x * sx + tx), round(y * sy + ty))
            if not pts or p != pts[-1]:
                pts.append(p)
        arcs.append(pts)

    def ring(idxs):
        out = []
        for i in idxs:                             # negative index = arc reversed
            seg = arcs[~i][::-1] if i < 0 else arcs[i]
            out.extend(seg if not out else seg[1:])
        return out

    def centroid(pts):
        """Area-weighted centroid of one ring, or None if it is degenerate."""
        a = cx = cy = 0.0
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            cr = x0 * y1 - x1 * y0
            a += cr; cx += (x0 + x1) * cr; cy += (y0 + y1) * cr
        if abs(a) < 1e-9:
            return None
        a *= 0.5
        return (cx / (6 * a), cy / (6 * a), abs(a))

    out = {}
    for g in topo["objects"]["states"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        d = "".join("M" + "L".join(f"{x},{y}" for x, y in ring(r)) + "Z"
                    for poly in polys for r in poly)
        # Label the largest polygon, not the bounding box: a bbox centre falls in Lake
        # Michigan for Michigan and in the Gulf for Louisiana.
        best = None
        for poly in polys:
            c = centroid(ring(poly[0]))
            if c and (best is None or c[2] > best[2]):
                best = c
        out[FIPS_USPS[g["id"]]] = (g["properties"]["name"], d,
                                   (round(best[0]), round(best[1])))
    return out


def _load_geometry():
    topo = json.loads(GEO.read_text())
    geo = _decode_topology(topo)
    # The FIPS table and the geometry must agree, or a state silently vanishes from the
    # map while every count elsewhere on the page keeps including its bills.
    missing = [g["id"] for g in topo["objects"]["states"]["geometries"]
               if g["id"] not in FIPS_USPS]
    if missing:
        raise SystemExit(f"build: geometry has FIPS codes absent from FIPS_USPS: {missing}")
    for g in topo["objects"]["states"]["geometries"]:
        name = geo[FIPS_USPS[g["id"]]][0]
        if name != g["properties"]["name"]:
            raise SystemExit(f"build: FIPS {g['id']} name mismatch: {name!r}")
    # The file's own bbox, not 0 0 975 610 — Aleutian geometry sits left of zero and a
    # 975-wide box clips it.
    x0, y0, x1, y1 = topo["bbox"]
    view = f"{int(x0) - 2} {int(y0) - 2} {int(x1 - x0) + 4} {int(y1 - y0) + 4}"
    return geo, view


GEOMETRY, VIEWBOX = _load_geometry()


def state_map(bills):
    """The landing page's state filter, as a map.

    Fill is categorical and two-valued; the count is a numeral. Only states that hold
    bills are labelled or reachable by keyboard — labelling all fifty at this size is
    noise, and announcing thirty-nine "no bills" nodes to a screen reader is worse than
    the list that follows the map, which carries every state.
    """
    counts = {}
    for b in bills:
        st = b["jurisdiction"]["state"]
        counts[st] = counts.get(st, 0) + 1
    unknown = sorted(set(counts) - set(GEOMETRY))
    if unknown:
        raise SystemExit(f"build: registry states absent from the geometry: {unknown}")

    shapes, labels = [], []
    for usps, (name, d, (lx, ly)) in sorted(GEOMETRY.items()):
        n = counts.get(usps, 0)
        if not n:
            shapes.append(f'<g class="st" aria-hidden="true"><path d="{d}"/></g>')
            continue
        dx, dy = LABEL_OFFSET.get(usps, (0, 0))
        tx_, ty_ = lx + dx, ly + dy
        lead = (f'<path class="lead" d="M{lx},{ly}L{tx_},{ty_}"/>' if (dx or dy) else "")
        labels.append(
            f'<g class="st has" role="button" tabindex="0" data-state="{esc(usps)}" '
            f'aria-pressed="false" '
            f'aria-label="{esc(name)}, {n} bill{"" if n == 1 else "s"}. Filter.">'
            f'<path d="{d}"/>{lead}'
            f'<text class="ab" x="{tx_}" y="{ty_ - 2}">{esc(usps)}</text>'
            f'<text class="n" x="{tx_}" y="{ty_ + 10}">{n}</text></g>')

    # Insets are the projection's doing, not geography. Say so on the face of the map.
    insets = ('<rect class="inset" x="-60" y="438" width="268" height="170" rx="3"/>'
              '<text class="insetlab" x="-56" y="452">Alaska (inset, not to scale)</text>'
              '<rect class="inset" x="232" y="536" width="150" height="70" rx="3"/>'
              '<text class="insetlab" x="234" y="531">Hawaii (inset)</text>')

    # The list is the text alternative to the map, and also the reliable way to filter:
    # South Carolina's outline is about 15px across on a phone, well under a usable tap
    # target, and a keyboard user should not have to hunt a shape either.
    rows = "".join(
        f'<tr><td><button type="button" class="mrow" data-state="{esc(s)}" '
        f'aria-pressed="false">{esc(GEOMETRY[s][0])}</button></td>'
        f'<td class="c">{counts[s]}</td></tr>'
        for s in sorted(counts, key=lambda s: (-counts[s], GEOMETRY[s][0])))
    none = ", ".join(sorted(GEOMETRY[s][0] for s in GEOMETRY if s not in counts))

    return ('<div class="mapwrap">'
            f'<svg class="usmap" viewBox="{VIEWBOX}" role="group" '
            f'aria-label="Filter by state" xmlns="http://www.w3.org/2000/svg">'
            f'{"".join(shapes)}{insets}{"".join(labels)}</svg>'
            '<p class="maplegend muted">Numbers are bills held. '
            'States without a number: no bills in this registry — which is not the same as '
            'none existing, since the inclusion methodology is not yet established.</p>'
            '<details class="maplist"><summary>States and bill counts as a list</summary>'
            f'<table><tbody>{rows}</tbody></table>'
            f'<p class="muted">No bills in this registry: {esc(none)}.</p>'
            '</details></div>')

def matrix(bills):
    heads="".join(f'<th scope="col" class="pv"><span>{esc(PROVISION_LABEL[p])}</span></th>'
                  for p in PROV_ORDER)
    rows=[]
    for b in bills:
        st=b["jurisdiction"]["state"]; pset=set(b["provisions"])
        tds="".join(
          f'<td class="pv{" on" if p in pset else ""}" '
          f'title="{esc(PROVISION_LABEL[p])}">'
          f'{"<span class=dot aria-hidden=true></span><span class=vh>yes</span>" if p in pset else "<span class=vh>no</span>"}</td>'
          for p in PROV_ORDER)
        chipsum=" ".join(f'<span class="chip">{esc(PROVISION_LABEL[p])}</span>' for p in b["provisions"])
        rows.append(
          f'<tr data-state="{esc(st)}" data-family="{esc(b["family"])}" '
          f'data-status="{esc(b["status"]["stage"])}" '
          f'data-prov="{esc(" ".join(b["provisions"]))}">'
          f'<th scope="row" class="bill"><a href="bills/{esc(b["id"])}/">{esc(st)} {esc(b["bill_number"])}</a>'
          f'<span class="rowmeta">{esc(b["session"]["year_introduced"])} · fam {esc(b["family"])} · '
          f'{esc(b["status"]["stage"].replace("_"," "))}</span></th>'
          f'<td class="yr">{esc(b["session"]["year_introduced"])}</td>'
          f'<td class="fam">{esc(b["family"])}</td>'
          f'<td class="stt"><span class="chip s-{esc(b["status"]["stage"])}">'
          f'{esc(b["status"]["stage"].replace("_"," "))}</span></td>'
          f'{tds}<td class="chipsum">{chipsum}</td></tr>')
    return (f'<div class="tablewrap"><table class="matrix" id="matrix">'
            f'<caption class="vh">Bills by provision</caption><thead><tr>'
            f'<th scope="col" class="bill">Bill</th><th scope="col" class="yr">Year</th>'
            f'<th scope="col" class="fam">Family</th><th scope="col" class="stt">Status</th>'
            f'{heads}<th scope="col" class="chipsum vh">Provisions</th>'
            f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')

FILTER_JS = """
(function(){
  // The map shapes and the fallback list are the same control; a real <button> in the
  // list needs no key handling, an SVG <g role="button"> does. Matrix rows also carry
  // data-state, so the selector must not be attribute-only.
  var STATEBTN='.usmap .st.has, .maplist button[data-state]';
  var t=document.getElementById('matrix'); if(!t) return;
  var rows=[].slice.call(t.tBodies[0].rows);
  var sel={state:'',family:'',status:'',prov:''};
  var count=document.getElementById('rowcount');
  function apply(){
    var n=0;
    rows.forEach(function(r){
      var ok=(!sel.state||r.dataset.state===sel.state)
          && (!sel.family||r.dataset.family===sel.family)
          && (!sel.status||r.dataset.status===sel.status)
          && (!sel.prov||r.dataset.prov.split(' ').indexOf(sel.prov)>=0);
      r.hidden=!ok; if(ok) n++;
    });
    count.textContent=n+(n===1?' bill':' bills')+(sel.state?' in '+sel.state:'');
    document.querySelectorAll(STATEBTN).forEach(function(b){
      b.setAttribute('aria-pressed', b.dataset.state===sel.state ? 'true':'false');
    });
    document.getElementById('clear').hidden = !(sel.state||sel.family||sel.status||sel.prov);
  }
  // An SVG <g role="button"> is not a real button: it gets no keyboard activation for
  // free, so Enter and Space are wired by hand.
  document.querySelectorAll(STATEBTN).forEach(function(b){
    function toggle(){
      sel.state = (sel.state===b.dataset.state) ? '' : b.dataset.state; apply();
    }
    b.addEventListener('click',toggle);
    b.addEventListener('keydown',function(e){
      if(e.key==='Enter'||e.key===' '||e.key==='Spacebar'){ e.preventDefault(); toggle(); }
    });
  });
  ['family','status','prov'].forEach(function(k){
    var el=document.getElementById('f-'+k);
    if(el) el.addEventListener('change',function(){ sel[k]=el.value; apply(); });
  });
  document.getElementById('clear').addEventListener('click',function(){
    sel={state:'',family:'',status:'',prov:''};
    ['family','status','prov'].forEach(function(k){var e=document.getElementById('f-'+k); if(e) e.value='';});
    apply();
  });
  apply();
})();
"""

# ---------------------------------------------------------------- bill pages
STAGE_LABEL={"introduced":"Introduced","in_committee":"In committee",
  "passed_one_chamber":"Passed one chamber","enacted":"Enacted","failed":"Failed","dead":"Dead"}
FIELD_LABEL={"technique":"Legislative technique","definitional_anchor":"Definitional anchor",
  "augmented_human_exposure":"Augmented-human exposure",
  "affects_algorithmic_entity_formation":"Effect on algorithmic entity formation",
  "corporate_carve_out":"Corporate carve-out"}

def dl(pairs):
    rows="".join(f"<div><dt>{esc(k)}</dt><dd>{v}</dd></div>" for k,v in pairs if v)
    return f"<dl class=facts>{rows}</dl>" if rows else ""

def paras(t):
    if not t: return ""
    out=[]
    for chunk in re.split(r"(?<=\.)\s+(?=[A-Z*\*])", t):
        c=chunk.strip()
        if not c: continue
        c=esc(c)
        c=re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", c)
        out.append(c)
    # regroup into readable paragraphs of ~2 sentences
    ps=["".join(out[i:i+2]) if False else " ".join(out[i:i+3]) for i in range(0,len(out),3)]
    return "".join(f"<p>{x}</p>" for x in ps)

def bill_page(b, byid):
    st=b["status"]; j=b["jurisdiction"]
    head=f'{esc(j["state"])} {esc(b["bill_number"])}'
    ev=st.get("evidence")
    evhtml=(f'<p class="evidence"><span class="lbl">Action of record</span> '
            f'{esc(ev["action"])} <span class="muted">&middot;</span> '
            f'<time>{esc(ev["date"])}</time></p>') if ev else ""
    chips=" ".join(f'<span class="chip">{esc(PROVISION_LABEL.get(p,p.replace("_"," ")))}</span>'
                   for p in b["provisions"])

    lineage=""
    if b["derived_from"]:
        par=byid[b["derived_from"]]
        items="".join(f"<li>{esc(c)}</li>" for c in b["derived_from_changes"])
        lineage=(f'<h2>Lineage</h2><p>Follows the template of '
                 f'<a href="../{esc(par["id"])}/">{esc(par["jurisdiction"]["state"])} '
                 f'{esc(par["bill_number"])}</a>. Differences:</p><ul class="changes">{items}</ul>')

    comps=[x for x in byid.values() if b["companion_group"] and
           x["companion_group"]==b["companion_group"] and x["id"]!=b["id"]]
    comphtml=("<h2>Companion bills</h2><ul>"+"".join(
        f'<li><a href="../{esc(c["id"])}/">{esc(c["jurisdiction"]["state"])} {esc(c["bill_number"])}</a></li>'
        for c in comps)+"</ul>") if comps else ""

    def _sp(s):
        party = f' <span class="party">[{esc(s["party"])}]</span>' if s.get("party") else ""
        return f'<li>{esc(s["name"])}{party} <span class="muted">— {esc(s["role"])}</span></li>'
    sp="".join(_sp(s) for s in b["sponsors"])
    sphtml=f"<h2>Sponsors</h2><ul class=sponsors>{sp}</ul>" if sp else \
           '<h2>Sponsors</h2><p class="muted">Not established.</p>'

    def _v(v):
        dt = f' <time>{esc(v["date"])}</time>' if v.get("date") else ""
        th = ' <span class="has-text">text held</span>' if v.get("text_path") else ""
        return f'<li><a href="{esc(v["source_url"])}">{esc(v["label"])}</a>{dt}{th}</li>'
    vs="".join(_v(v) for v in b["versions"])
    vshtml=f"<h2>Versions</h2><ul class=versions>{vs}</ul>" if vs else ""

    wd="".join(f'<li><time>{esc(w["date"])}</time> — {esc(w["event"])} '
               f'<span class="muted">({esc(w["kind"])})</span></li>' for w in b["watch_dates"])
    wdhtml=f"<h2>Dates ahead</h2><ul class=watch>{wd}</ul>" if wd else ""

    ce="".join(f'<li>{esc(", ".join(c["amendments"]))} — claimed by <code>{esc(c["claimed_by"])}</code></li>'
               for c in b["constitutional_exposure"])
    cehtml=(f'<h2>Constitutional exposure claimed</h2><ul>{ce}</ul>'
            f'<p class="muted small">Claims recorded with attribution. The tracker takes no view '
            f'on whether any bill is constitutional.</p>') if ce else ""

    src="".join(f'<li><a href="{esc(u)}">{esc(u)}</a></li>' for u in b["sources"].get("primary",[]))
    trk="".join(f'<li><a href="{esc(u)}">{esc(u)}</a></li>' for u in b["sources"].get("tracker",[]))
    srch=f"<h2>Sources</h2><h3>Primary</h3><ul class=urls>{src}</ul>"+ \
         (f"<h3>Tracker</h3><ul class=urls>{trk}</ul>" if trk else "")

    kc=""
    if b["key_clause"]:
        kc=(f'<blockquote class="clause"><p>{esc(b["key_clause"]["text"])}</p>'
            f'<cite>{esc(b["key_clause"]["source"])}</cite></blockquote>')

    dh,_ds = render_diff(b)
    diffsection = (f'<h2>How the text changed</h2>'
                   f'<p class="muted small">A provision-by-provision comparison of the stored '
                   f'texts, aligned on statutory structure where that can be identified. '
                   f'Every version links to its source; the '
                   f'<a href="{"../" * 2}method/#diff">method note</a> sets out what the '
                   f'comparison does and does not establish.</p>{dh}') if dh else ""
    cite=(f'{SITE["name"]}, “{j["state"]} {b["bill_number"]}”, {SITE["publisher"]}, '
          f'record verified {b["last_verified"] or "—"}, accessed [date].')

    body=f"""
<p class="crumb"><a href="../../">All bills</a></p>
<h1>{head}</h1>
<p class="lede">{esc(b["session"].get("legislature") or "")} {esc(b["session"]["session"])},
  introduced {esc(b["session"]["year_introduced"])} · {esc(b["chamber"])}</p>

<div class="statusblock">
  <span class="chip s-{esc(st["stage"])} big">{esc(STAGE_LABEL.get(st["stage"],st["stage"]))}</span>
  <span class="muted">as of <time>{esc(st["as_of"])}</time></span>
  {evhtml}
</div>

{kc}

{dl([("Codified at", esc(b["codified_at"])),
     ("Effective", esc(b["effective_date"])),
     ("Family", esc(b["family"])),
     *[(FIELD_LABEL[k], esc(str(b[k]).replace("_"," "))) for k in FIELD_LABEL if b.get(k) not in (None,"","unknown")]])}

<h2>Provisions</h2>
<div class="chips">{chips}</div>

{lineage}
{comphtml}
{sphtml}
{vshtml}
{wdhtml}
{cehtml}

{diffsection}

<h2>Notes</h2>
<div class="notes">{paras(b["notes"])}</div>

{srch}

<h2>Record</h2>
{dl([("Verification", esc(b["verification_status"].replace("_"," "))),
     ("Last verified", esc(b["last_verified"])),
     ("Provenance", esc(b["provenance"]))])}
<h3>Cite this record</h3>
<p class="cite">{esc(cite)}</p>
"""
    return page(head, body, depth=2, desc=f'{head}: status, provisions, sponsors and primary sources.')

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

    fam=sorted({b["family"] for b in bills})
    sts=sorted({b["status"]["stage"] for b in bills})
    provs=sorted({p for b in bills for p in b["provisions"]}, key=lambda x: PROV_ORDER.index(x))
    opt=lambda vs,lab: "".join(f'<option value="{esc(v)}">{esc(lab(v))}</option>' for v in vs)

    body = f"""
<h1>Legislation on the legal status of AI systems</h1>
<p class="lede"><span class="count">{len(bills)}</span> bills across
<span class="count">{len(states)}</span> US states since 2022. Every record's status is
established from a primary or citable source; operative text has been read in full for
<span class="count">{sum(1 for x in bills if x["verification"]["operative_text"]=="read_in_full")}</span>
of them, and each record states what was checked. A descriptive record of what these bills
say — not an assessment of them.</p>

{state_map(bills)}

{changed_callout(bills)}

{watch_panel(bills, SITE['published'])}

<div class="controls">
  <label>Family <select id="f-family"><option value="">any</option>{opt(fam, lambda v: v)}</select></label>
  <label>Status <select id="f-status"><option value="">any</option>{opt(sts, lambda v: v.replace("_"," "))}</select></label>
  <label>Provision <select id="f-prov"><option value="">any</option>{opt(provs, lambda v: PROVISION_LABEL[v])}</select></label>
  <button type="button" id="clear" hidden>Clear filters</button>
  <span class="rowcount" id="rowcount">{len(bills)} bills</span>
</div>

{matrix(bills)}

<p class="muted small">Sorted by year introduced, then state. Order is chronological by
design: sorting by anything that implies a ranking would be an editorial act, and this
registry does not rank bills.</p>
<script>{FILTER_JS}</script>
"""
    (DIST / "index.html").write_text(page("Bills", body, active=""))

    sizes = write_data(d, bills, DIST / "data")
    (DIST / "data" / "index.html").write_text(data_page(d, bills, sizes))

    (DIST / "method").mkdir(parents=True, exist_ok=True)
    (DIST / "method" / "index.html").write_text(method_page(d, bills))

    (DIST / "lineage").mkdir(parents=True, exist_ok=True)
    (DIST / "lineage" / "index.html").write_text(lineage(bills))

    byid={b["id"]:b for b in bills}
    for b in bills:
        outdir = DIST / "bills" / b["id"]
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "index.html").write_text(bill_page(b, byid))
    return bills, st

if __name__ == "__main__":
    bills, st = build()
    n = sum(len(list(p.rglob("*"))) for p in [DIST])
    print(f"built dist/ — {len(bills)} bills, {n} files")
    print(f"  disposition: {st}")
