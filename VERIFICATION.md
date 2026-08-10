# Verification pass — 2026-08-10

Reading each bill against its primary source. `seeded_unverified` → `verified_primary`.

## Result: 10 of 23 verified

| | Count |
|---|---|
| Verified against primary source | **10** |
| Blocked — host unreachable from this environment | **8** |
| Blocked — cited URL returns 404 | **3** |
| Reachable, not yet done | **2** |

## Host reachability

Probed all primary-source hosts on :443.

**Open (15 bills):** `le.utah.gov` · `www.revisor.mn.gov` · `leginfo.legislature.ca.gov` ·
`ndlegis.gov` · `www.oklegislature.gov` · `www.scstatehouse.gov` · `app.leg.wa.gov` ·
`www.senate.mo.gov` · `house.mo.gov` (connects, but paths 404)

**Blocked (8 bills):** `wapp.capitol.tn.gov` (TN ×4) · `legislature.idaho.gov` (ID) ·
`www.legislature.ohio.gov` (OH) · `docs.legis.wisconsin.gov` (WI ×2)

LegiScan sits behind a bot check, so it is not a fallback here. Justia returned 403.
These eight need running from a normal network — nothing about them is hard, just unreachable.

## What verification changed

**A correction to the paper.** Washington HB 2029 is recorded in Table 1 as **Failed**. It
is not. It was reintroduced and retained in present status on 12 Jan 2026 and remains in
House Civil Rights & Judiciary today. Washington carries bills across the two years of a
biennium. The tracker now shows `in_committee`.

**Two bills have moved since the paper's 12 May 2026 snapshot** — both in California, which
the paper flagged as the state to watch:
- **SB 1159** amended in the Assembly 25 June 2026, i.e. past the Senate.
- **AB 2023** in Senate Appropriations, referred to the suspense file 3 August 2026 —
  a week before this check.

**Statutory citations recovered**, none of which are in the paper:
- Utah HB 249 → Utah Code ch. 63G-31 (§§ 63G-31-101, -102), effective 1 May 2024
- North Dakota HB 1361 → N.D. Cent. Code § 1-01-49(8), signed 12 April 2023
- California SB 1159 → twelve sections across the Gov. Code and Pub. Res. Code
- California SB 1119 / AB 2023 → B&P Code ch. 22.6.1, §§ 22610–22617
- South Carolina HB 3796 → would add art. 29 to ch. 1, tit. 1

**Text broader than reported:**
- **CA SB 1159** excludes "artificial intelligence systems, autonomous agents, robots, or
  other nonhuman entities, whether physical or digital" — not AI alone.
- **MO SB 1012** also regulates companion chatbots (artificiality notice, suicide-prevention
  protocols, bar on sexually explicit content involving minors) and requires licensed
  professionals to retain final authority. `restricts_chatbot_claims` added.
- **CA SB 1119 § 22612(d)(5)(G)** bars a chatbot "Claiming that the companion chatbot is
  sentient, conscious, or human" — the clause is not itself limited to children, though the
  chapter is a children's-safety measure.

**Sponsors recovered.** North Dakota has twelve, not the two named. Washington has seven,
none named. Utah has a Senate sponsor (Don L. Ipson) the paper omits. Missouri SB 1012 is
Joe Nicola. Oklahoma's Senate author is David Bullard.

**Dead links.** The `house.mo.gov` URLs cited for HB 1462, HB 1746 and HB 1769 all return
404 (both `Bill.aspx` and `BillContent.aspx` patterns). The host is up; the paths are stale.

## Outstanding

1. **Eight blocked bills** — TN HB 849 / SB 837 / HB 1455 / SB 1493, ID HB 720, OH HB 469,
   WI AB 959 / SB 932. Run from a normal network. The four Tennessee records are the last
   `codified_at` gaps.
2. **Three Missouri House bills** — need repaired primary URLs first.
3. **Two Missouri Senate companions** (SB 859, SB 1474) — reachable, simply not yet done.
4. **Full text still to be read verbatim** for several records where only the status page
   was reachable: ND, OK, SC, MN sponsors.
