# Source documents needed — 11 bills

**How to hand them over:** save each as PDF or plain text into `registry/incoming/`, named
by the record id (e.g. `tn-sb837-2025-enrolled.pdf`). I can read PDFs directly, so a
download beats copy-paste. If a page is HTML-only, "Print → Save as PDF" is fine.

**If a document is quick to eyeball, the four things worth noting in a covering line are:**
final status + date · sponsors · the statutory section it enacts or amends · the operative
sentence about personhood/sentience. Everything else I can pull from the document.

I'll handle Missouri SB 859 and SB 1474 myself — those hosts are reachable.

---

## A. Tennessee — 4 records, and the last `codified_at` gaps

Host `wapp.capitol.tn.gov` refuses connections from here.

| Record | Document needed | Fills |
|---|---|---|
| `tn-hb849-2025` / `tn-sb837-2025` | **Public Chapter** (the enacted act, 2026) | `codified_at`, `effective_date`, final status |
| ″ | **Original introduced text** of HB 849 / SB 837 (2025) | The fetal-personhood clause that was later removed — the amendment diff |
| `tn-hb1455-2025` / `tn-sb1493-2025` | **Public Chapter** (the enacted act, 2026) | `codified_at`, confirms the enacted text is study-only |
| ″ | **Original introduced text** of HB 1455 / SB 1493 (2025) | The Class A felony training provisions as introduced |

Start at `wapp.capitol.tn.gov/apps/BillInfo/Default.aspx?BillNumber=SB0837&ga=114` and the
same for `SB1493`. The amendment PDFs are already linked and known:
`capitol.tn.gov/Bills/114/Amend/SA0922.pdf` and `capitol.tn.gov/Bills/114/Amend/HA1260.pdf`
— grab those too if they download cleanly.

**These two are the highest value in the whole list.** Both bills changed radically between
introduction and enactment, and those diffs are the registry's headline feature.

## B. Idaho — 1 record, the first law in the nation

| Record | Document needed | Fills |
|---|---|---|
| `id-hb720-2022` | **Signed/enrolled HB 720 (2022)**, and ideally the current text of **Idaho Code § 5-346** | Confirms `codified_at` (currently taken from Jaynes, not verified), `effective_date`, the saving clause wording, session law chapter |

Start at `legislature.idaho.gov/sessioninfo/2022/legislation/H0720/`. Host times out here;
Justia returned 403.

Specifically worth checking: the exact wording of the clause preserving personhood for
municipalities, corporations and other entities — that drives `corporate_carve_out`, and
Idaho is the only bill tagged `express_saving_clause`.

## C. Ohio — 1 record, the most-covered bill in the set

| Record | Document needed | Fills |
|---|---|---|
| `oh-hb469-2025` | **"As Introduced" bill text**, plus current committee status | Operative non-sentience language verbatim, sponsors/cosponsors, `codified_at` (which ORC sections it would create), current stage |

Start at `legislature.ohio.gov/legislation/136/hb469`.

Also useful if it's on the page: the **cosponsor list**. The paper names only Claggett, and
Ohio is the bill most likely to pass next.

## D. Wisconsin — 2 records, the only hybrid technique

| Record | Document needed | Fills |
|---|---|---|
| `wi-ab959-2026` | **AB 959 bill text** | Which general "person" definition it amends (I expect Wis. Stat. ch. 990, to confirm), the standalone provision, sponsors, final disposition |
| `wi-sb932-2026` | **SB 932 bill text** | Same for the Senate companion |

Start at `docs.legis.wisconsin.gov/2025/proposals/reg/asm/bill/ab959` and
`.../reg/sen/bill/sb932`.

This is the only bill in the set tagged `technique: hybrid` — it both amends the general
statutory definition of "person" *and* bans AI personhood by standalone provision. Worth
confirming that reading against the text.

Also: the paper records both as **Failed**. Given Washington turned out to be wrongly
recorded as failed, please note the actual final disposition and date.

## E. Missouri — 3 records with dead links

The URLs cited in the paper return **404** (both `Bill.aspx` and `BillContent.aspx`
patterns; host is up, paths are stale). What I need first is a **working URL**, then the text.

| Record | Bill | Needs |
|---|---|---|
| `mo-hb1462-2025` | HB 1462 (2025) | Working URL + text. This is the **originator of Family C** — the first bill anywhere to declare AI non-conscious. Its text is the template for Ohio and Wisconsin. |
| `mo-hb1746-2026` | HB 1746 (2026) | Working URL + text, plus the **consolidated replacement text** it was merged into with HB 1769 |
| `mo-hb1769-2026` | HB 1769 (2026) | Working URL + text |

Try the bill search at `house.mo.gov` for each number, or `documents.house.mo.gov`, which
did resolve for the committee testimony PDFs.

---

## What this closes

Right now: **10 of 23 verified**, 4 warnings outstanding (all Tennessee `codified_at`).

With A–E in hand: **23 of 23**, zero warnings, and the two amendment diffs that make the
registry say something no other tracker does.
