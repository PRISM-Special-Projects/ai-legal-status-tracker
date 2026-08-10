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
