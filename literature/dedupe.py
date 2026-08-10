import csv, re, difflib, json
CORPUS="/Users/mitchel/Projects/untitled folder/digital-minds-corpus/master-corpus.csv"

def norm(s):
    s=(s or "").lower()
    s=re.sub(r"[^a-z0-9 ]"," ",s)
    return re.sub(r"\s+"," ",s).strip()

corpus=list(csv.DictReader(open(CORPUS)))
cmap=[(norm(c["title"]), c) for c in corpus if c.get("title")]

refs=list(csv.DictReader(open("seed-references.csv")))
rows=[]
for r in refs:
    t=norm(r["title"])
    best=None; score=0
    for ct, c in cmap:
        s=difflib.SequenceMatcher(None,t,ct).ratio()
        # boost containment (subtitle differences)
        if t and ct and (t in ct or ct in t) and min(len(t),len(ct))>=25: s=max(s,0.95)
        if s>score: score, best = s, c
    rows.append({
        "ref_key": r["ref_key"], "tier": r["tier"], "strand": r["strand"],
        "year": r["year"], "title": r["title"],
        "match_score": round(score,3),
        "corpus_layer": best["layer"] if best and score>=0.85 else "",
        "corpus_title": best["title"] if best and score>=0.85 else "",
        "corpus_discipline": best["discipline"] if best and score>=0.85 else "",
        "corpus_themes": best["themes"] if best and score>=0.85 else "",
        "status": "IN_CORPUS" if score>=0.85 else ("FUZZY_CHECK" if score>=0.70 else "NEW"),
        "near_miss": best["title"] if best and 0.70<=score<0.85 else "",
    })

with open("dedupe-report.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

import collections
print("STATUS:", dict(collections.Counter(r["status"] for r in rows)))
print("\n--- IN CORPUS ---")
for r in rows:
    if r["status"]=="IN_CORPUS": print(f"  [{r['corpus_layer']:<10}] {r['ref_key']:<18} {r['title'][:62]}")
print("\n--- FUZZY (manual check) ---")
for r in rows:
    if r["status"]=="FUZZY_CHECK": print(f"  {r['ref_key']:<18} {r['match_score']} {r['title'][:45]!r} ~ {r['near_miss'][:45]!r}")
print("\n--- NEW (not in corpus) ---")
for r in rows:
    if r["status"]=="NEW": print(f"  [{r['tier']:<8}] {r['ref_key']:<18} ({r['strand']}) {r['title'][:58]}")
