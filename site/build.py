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
