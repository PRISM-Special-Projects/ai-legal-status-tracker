# Verification pass — 2026-08-10

Reading each bill against its primary source. `seeded_unverified` → `verified_primary`.

## Result: 23 of 23 verified against primary sources

Completed 2026-08-10. Every record read against its own bill text or enacted act.
Validator: 0 errors, 0 warnings. All 7 enacted bills carry a statutory citation.

Blocked hosts (Tennessee, Idaho, Ohio, Wisconsin, Missouri House) were resolved by
Mitchel supplying the documents. Two workarounds are worth remembering: Tennessee's
Secretary of State acts server (`publications.tnsosfiles.com`) is reachable and is the
better source anyway, and LegiScan pages carry the working state-source URLs when a
paper's cited link has gone stale.

## Corrections to the paper

1. **Washington HB 2029 is not "Failed."** Reintroduced and retained in present status
   12 Jan 2026; still in House Civil Rights & Judiciary. Washington carries bills across
   the biennium.
2. **Idaho HB 720's sponsor of record is the House State Affairs Committee**, printed on
   the face of the bill. Rep. Nichols drove it but is not the sponsor.
3. **Idaho is the 66th Legislature**, not the 68th as cited.
4. **Ohio HB 469 is the 136th General Assembly**; the reference-list entry says 135th.
5. **Sponsorship is more bipartisan than reported.** Both enacted Tennessee acts carry
   Democratic sponsors — Rep. Justin Pearson on Pub. Ch. 781 (6R–1D), Pearson and Rep.
   Karen Camper on Pub. Ch. 1066.
6. **Family C does not uniformly assign liability to humans.** Wisconsin negates AI
   liability without assigning it to anyone.

## What only a text-level registry could show

**The corporate-veil provision is the fault line.** Missouri's model text lets courts
pierce the veil where an AI subsidiary was undercapitalised to evade damages. Ohio kept the
same three triggers and **inverted the default** into parent-company immunity. Missouri's
own consolidated committee substitute **deleted the provision entirely**. Wisconsin never
had it. Meanwhile Missouri SB 859 and SB 1474 remain live *with* it — so Missouri
simultaneously carries vehicles with and without, which a single state row would hide.

**The "Responsibility" half degrades as the template travels**, while the non-sentience
half is copied intact:

| | Corporate veil | Human-liability anchor | AI definition |
|---|---|---|---|
| MO HB 1462 / 1769 / SB 859 / SB 1474 | courts **may pierce** | "liability remains with human actors" | homegrown, reaches "rules-based logic" |
| OH HB 469 | parents **immune except** | clause dropped from § 1357.08 | copied, still overbroad |
| MO HCS 1746 & 1769 | **deleted** | retained | federal, 15 U.S.C. § 9401(3) |
| WI AB 959 / SB 932 | absent | **none at all** | OECD / EU AI Act |

**The softening is attributable to a committee, not a sponsor.** Rep. Amato filed the
strong text twice (HB 1462, then HB 1769 verbatim). The veil deletion, the NIST AI 100-1
safe harbour, the negligence absolution and the open-source carve-out all appeared in the
House Committee Substitute.

**Diffusion is by commissioned drafts, not a shared file.** Identical text carries
different drafting numbers each time: Missouri 4626H.01I (Amato), 4600S.01I (Moon),
6352S.01I (Nicola); Wisconsin LRB-5476/1 and LRB-6000/1. Multiple legislators independently
commissioned drafts of the same model text — a stronger claim than "copy-and-paste," and
visible only in drafting metadata.

**Copy-paste is nonetheless provable at the token level.** "Emergent properties" is defined
and never used in Missouri HB 1462 — and the identical unused definition reappears in Ohio
HB 469.

**Two provisions nobody has written about.** Missouri's model text and Ohio both provide
that labelling a system "aligned," "ethically trained" or "value locked" does not diminish
liability — AI-safety vocabulary in statute. And Missouri's consolidated substitute ties
compliance to the **NIST AI Risk Management Framework (NIST AI 100-1)**, the only external
technical standard referenced anywhere in the registry.

## Facts recovered that the paper does not contain

Statutory citations for all 7 enacted bills · effective dates · full sponsor lists (North
Dakota 12, Wisconsin 11, Ohio 1, Washington 7) · vote counts (Idaho House 50–17–3, Senate
30–5; Oklahoma House 94–2; Tennessee committees unanimous) · Missouri sponsors Amato, Moon
and Nicola, none named in the paper.

## Status changes since the paper's 12 May 2026 snapshot

- **CA SB 1159** amended in the Assembly 25 June 2026 — past the Senate.
- **CA AB 2023** referred to the Senate Appropriations suspense file 3 August 2026.
- **MO SB 1012** received a Do Not Pass from House Emerging Issues.

## Corrections to my own earlier findings

**The Missouri House URLs are not dead.** I recorded `house.mo.gov/Bill.aspx?bill=HB1462...`
and its siblings as returning 404. They return HTTP 200. My fetch tool was being blocked by
user-agent and I misattributed that to a stale link. The paper's citations are correct, and
the pages carry full action histories with journal-page references. Retrieved with `curl`
and a normal user-agent.

## How states record a bill's death

Three mechanisms among the three states with failed bills, which `status.evidence` must
accommodate:

- **Wisconsin** posts an explicit line: *"Failed to pass pursuant to Senate Joint
  Resolution 1"*, 23 Mar 2026 for both AB 959 and SB 932.
- **Missouri** posts nothing. A bill simply stops; death is inferred from the last action
  plus adjournment. HB 1462's last action was a referral on 15 May 2025, the penultimate
  day of session.
- **Washington** posts nothing because bills do not die — they carry across the biennium,
  which is why HB 2029 survived and the paper's "Failed" was wrong.

Only Wisconsin's is a citable failure line. The other two require a reasoned reading, which
is exactly why the evidence field records the action rather than just the enum.

## Remaining data-quality tasks

1. **MO HB 1746's own introduced text** has not been read; only the consolidated
   substitute and the action history. Its companion HB 1769 as introduced proved to be a
   verbatim HB 1462 clone, so HB 1746 probably was too — an inference, not a reading.
2. Read full operative text for **ND HB 1361, OK HB 3546, SC HB 3796** — verified from
   status pages and summaries, not from bill text.

Every status now carries an evidence action line; the validator enforces it for terminal
stages.
