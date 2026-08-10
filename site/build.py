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
.difftext{padding:6px 0;max-height:34em;overflow-y:auto}
.difftext p{margin:0;padding:5px 16px;font-size:.9rem;line-height:1.55}
.difftext .same{color:var(--muted)}
.difftext .del{background:var(--del-bg)}
.difftext .del del{color:var(--del);text-decoration-thickness:1px}
.difftext .add{background:var(--add-bg)}
.difftext .add ins{color:var(--add);text-decoration:none;font-weight:500}
.difftext .elide{color:var(--muted);font-size:.78rem;font-style:italic;
  text-align:center;padding:7px 16px;background:var(--bg)}

/* ---- visually hidden ---- */
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

/* ---- state tile grid (filter control, not a map) ---- */
.mapwrap{margin:1.8em 0 1.4em}
.tilegrid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:3px;max-width:620px}
.tile{aspect-ratio:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
  border:1px solid var(--line);border-radius:3px;background:transparent;color:var(--muted);
  font:600 .62rem/1 ui-sans-serif,system-ui,sans-serif;padding:0;min-height:26px}
.tile .n{font-size:.7rem;font-weight:700;color:var(--accent);margin-top:1px}
.tile.has{background:var(--accent-weak);border-color:var(--accent);color:var(--fg);cursor:pointer}
.tile.has:hover{background:var(--accent);color:var(--bg)}
.tile.has:hover .n{color:var(--bg)}
.tile.has[aria-pressed=true]{background:var(--accent);color:var(--bg);box-shadow:0 0 0 2px var(--accent)}
.tile.has[aria-pressed=true] .n{color:var(--bg)}
.tile.has:focus-visible{outline:2px solid var(--fg);outline-offset:2px}
.maplegend{font-size:.78rem;margin:.7em 0 0;max-width:56ch}

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
  .tilegrid{max-width:100%}
  .tablewrap{overflow:visible;border:0;background:transparent}
  table.matrix,table.matrix tbody,table.matrix tr{display:block;width:100%}
  table.matrix thead{display:none}
  table.matrix tr{border:1px solid var(--line);border-radius:var(--radius);
    background:var(--card);margin-bottom:10px;padding:12px 14px}
  table.matrix th,table.matrix td{border:0;padding:0;text-align:left;display:none}
  th.bill{display:block;white-space:normal;padding-left:0}
  th.bill a{font-size:1.02rem}
  .rowmeta{display:block;color:var(--muted);font-size:.8rem;margin-top:2px}
  td.chipsum{display:block;margin-top:8px}
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
import difflib

ENACT_RE = re.compile(r"(BE IT ENACTED[^\n]*\n|Be it enacted[^\n]*\n|by deleting all language after the enacting clause and substituting:)", re.I)

def _sents(path):
    """Operative text only. Bill letterheads, chapter numbers and sponsor lists are
    metadata; diffing them buries the substantive change under boilerplate."""
    raw = (REG / path).read_text()
    m = ENACT_RE.search(raw)
    if m: raw = raw[m.end():]
    t = re.sub(r"\s+", " ", raw)
    return [x.strip() for x in re.split(r"(?<=[.;:])\s+(?=[A-Z(0-9\"])", t) if x.strip()]

def render_diff(b):
    vs = [v for v in b["versions"] if v.get("text_path")]
    if len(vs) < 2: return "", None
    a, z = vs[0], vs[-1]
    mech = vs[1] if len(vs) > 2 else None
    A, Z = _sents(a["text_path"]), _sents(z["text_path"])
    sm = difflib.SequenceMatcher(None, A, Z)
    parts, rem, add = [], 0, 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            keep = A[i1:i2]
            if len(keep) > 4:
                parts.append(f'<p class="same">{esc(keep[0])}</p>'
                             f'<p class="elide">… {len(keep)-2} unchanged passages …</p>'
                             f'<p class="same">{esc(keep[-1])}</p>')
            else:
                parts += [f'<p class="same">{esc(x)}</p>' for x in keep]
        else:
            for x in A[i1:i2]:
                rem += 1; parts.append(f'<p class="del"><del>{esc(x)}</del></p>')
            for x in Z[j1:j2]:
                add += 1; parts.append(f'<p class="add"><ins>{esc(x)}</ins></p>')
    mechhtml = ""
    if mech:
        mechhtml = (f'<p class="mech"><span class="lbl">Mechanism</span> '
                    f'<a href="{esc(mech["source_url"])}">{esc(mech["label"])}</a></p>')
    stat = (f'<p class="diffstat"><span class="k del">{rem} removed</span> '
            f'<span class="k add">{add} added</span> '
            f'<span class="muted">{sm.ratio():.0%} of the text unchanged</span></p>')
    html_ = (f'<div class="diff"><p class="diffhead">'
             f'<span class="v from">{esc(a["label"])}</span>'
             f'<span class="arrow" aria-hidden="true">→</span>'
             f'<span class="v to">{esc(z["label"])}</span></p>'
             f'{mechhtml}{stat}<div class="difftext">{"".join(parts)}</div></div>')
    return html_, {"id": b["id"], "removed": rem, "added": add,
                   "from": a["label"], "to": z["label"], "ratio": sm.ratio()}

def changed_callout(bills):
    seen=set(); items=[]
    for b in bills:
        _,d = render_diff(b)
        if not d: continue
        key=(d["removed"],d["added"])
        if key in seen: continue      # companion pairs share a text; show once
        seen.add(key)
        items.append(f'<li><a href="bills/{esc(b["id"])}/#main">'
                     f'{esc(b["jurisdiction"]["state"])} {esc(b["bill_number"])}</a> — '
                     f'<span class="k del">{d["removed"]} passages removed</span>, '
                     f'<span class="k add">{d["added"]} added</span>, '
                     f'{d["ratio"]:.0%} unchanged</li>')
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
<p class="pending"><strong>To be confirmed before launch.</strong> Our intention is to release
the registry under a permissive licence so it can be reused, corrected and built on. Until that
is settled, please contact us before redistributing, and cite the registry if you use it.</p>

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
<em>action of record</em> — the verbatim legislative action establishing it. States record
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
since been checked against primary sources, and the registry now records statutory citations,
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
# Standard US tile grid: (row, col) on a 12-col lattice. Geography approximate by design —
# this is a filter control, not a map. Equal-area tiles stop small states vanishing.
TILES = {
 "AK":(1,1),"ME":(1,12),
 "VT":(2,11),"NH":(2,12),
 "WA":(3,2),"ID":(3,3),"MT":(3,4),"ND":(3,5),"MN":(3,6),"IL":(3,7),"WI":(3,8),"MI":(3,9),
 "NY":(3,10),"MA":(3,11),"RI":(3,12),
 "OR":(4,2),"NV":(4,3),"WY":(4,4),"SD":(4,5),"IA":(4,6),"IN":(4,7),"OH":(4,8),"PA":(4,9),
 "NJ":(4,10),"CT":(4,11),
 "CA":(5,2),"UT":(5,3),"CO":(5,4),"NE":(5,5),"MO":(5,6),"KY":(5,7),"WV":(5,8),"VA":(5,9),
 "MD":(5,10),"DE":(5,11),
 "AZ":(6,3),"NM":(6,4),"KS":(6,5),"AR":(6,6),"TN":(6,7),"NC":(6,8),"SC":(6,9),"DC":(6,10),
 "OK":(7,4),"LA":(7,5),"MS":(7,6),"AL":(7,7),"GA":(7,8),
 "HI":(8,1),"TX":(8,2),"FL":(8,10),
}
PROV_ORDER = ["denies_legal_personhood","declares_non_sentient","covers_non_ai_entities",
  "assigns_liability_to_humans","bars_ai_liability","addresses_corporate_veil",
  "bars_marriage_or_union","bars_property_ownership","bars_corporate_office",
  "imposes_safety_duties","incident_reporting_duty","provides_compliance_safe_harbor",
  "restricts_chatbot_claims","restricts_ai_speech_rights","restricts_person_like_training",
  "study_only"]

def tile_map(bills):
    counts={}
    for b in bills: counts[b["jurisdiction"]["state"]]=counts.get(b["jurisdiction"]["state"],0)+1
    cells=[]
    for st,(r,c) in sorted(TILES.items(), key=lambda kv:(kv[1][0],kv[1][1])):
        n=counts.get(st,0)
        if n:
            cells.append(f'<button type="button" class="tile has" data-state="{esc(st)}" '
                         f'style="grid-row:{r};grid-column:{c}" '
                         f'aria-label="{esc(st)}, {n} bill{"" if n==1 else "s"}. Filter.">'
                         f'<span class="ab">{esc(st)}</span><span class="n">{n}</span></button>')
        else:
            cells.append(f'<div class="tile" style="grid-row:{r};grid-column:{c}" '
                         f'aria-label="{esc(st)}, no legislation identified">'
                         f'<span class="ab">{esc(st)}</span></div>')
    return ('<div class="mapwrap"><div class="tilegrid" role="group" '
            'aria-label="Filter by state">' + "".join(cells) + '</div>'
            '<p class="maplegend muted">Tiles are positioned approximately, sized equally. '
            'Numbers are bills held. States without a number: no legislation identified.</p></div>')

def matrix(bills):
    heads="".join(f'<th scope="col" class="pv"><span>{esc(PROVISION_LABEL[p])}</span></th>'
                  for p in PROV_ORDER)
    rows=[]
    for b in bills:
        st=b["jurisdiction"]["state"]; pset=set(b["provisions"])
        tds="".join(
          f'<td class="pv{" on" if p in pset else ""}" '
          f'title="{esc(PROVISION_LABEL[p])}">'
          f'{"<span class=dot aria-label=yes></span>" if p in pset else "<span class=vh>no</span>"}</td>'
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
    document.querySelectorAll('.tile.has').forEach(function(b){
      b.setAttribute('aria-pressed', b.dataset.state===sel.state ? 'true':'false');
    });
    document.getElementById('clear').hidden = !(sel.state||sel.family||sel.status||sel.prov);
  }
  document.querySelectorAll('.tile.has').forEach(function(b){
    b.addEventListener('click',function(){
      sel.state = (sel.state===b.dataset.state) ? '' : b.dataset.state; apply();
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
PROVISION_LABEL={
  "denies_legal_personhood":"Denies legal personhood",
  "declares_non_sentient":"Declares non-sentient",
  "assigns_liability_to_humans":"Assigns liability to humans",
  "bars_ai_liability":"Bars AI liability",
  "restricts_ai_speech_rights":"Restricts AI speech rights",
  "restricts_chatbot_claims":"Restricts chatbot claims",
  "restricts_person_like_training":"Restricts person-like training",
  "covers_non_ai_entities":"Covers non-AI entities",
  "study_only":"Study only",
  "bars_marriage_or_union":"Bars marriage or union",
  "bars_property_ownership":"Bars property ownership",
  "bars_corporate_office":"Bars corporate office",
  "imposes_safety_duties":"Imposes safety duties",
  "incident_reporting_duty":"Incident-reporting duty",
  "addresses_corporate_veil":"Addresses corporate veil",
  "provides_compliance_safe_harbor":"Provides compliance safe harbour"}
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
                   f'<p class="muted small">Sentence-level comparison of the stored texts. '
                   f'Every version links to its source.</p>{dh}') if dh else ""
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

    cards = "".join(
        f'<li class="card"><h3><a href="bills/{esc(b["id"])}/">{esc(b["jurisdiction"]["state"])} '
        f'{esc(b["bill_number"])}</a></h3>'
        f'<p class="meta">{esc(b["session"]["year_introduced"])} · family {esc(b["family"])} · '
        f'{len(b["provisions"])} provision{"" if len(b["provisions"])==1 else "s"}</p>'
        f'<span class="chip s-{esc(b["status"]["stage"])}">{esc(b["status"]["stage"].replace("_"," "))}</span>'
        f'</li>' for b in bills)

    fam=sorted({b["family"] for b in bills})
    sts=sorted({b["status"]["stage"] for b in bills})
    provs=sorted({p for b in bills for p in b["provisions"]}, key=lambda x: PROV_ORDER.index(x))
    opt=lambda vs,lab: "".join(f'<option value="{esc(v)}">{esc(lab(v))}</option>' for v in vs)

    body = f"""
<h1>Legislation on the legal status of AI systems</h1>
<p class="lede"><span class="count">{len(bills)}</span> bills across
<span class="count">{len(states)}</span> US states since 2022, each read against its primary
source. A descriptive record of what these bills say — not an assessment of them.</p>

{tile_map(bills)}

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
