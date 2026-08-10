# Verification pass — 2026-08-10

Reading each bill against its primary source. `seeded_unverified` → `verified_primary`.

## Result: 23 of 23 records verified; operative text read in full for 16

Completed 2026-08-10. **Corrected 2026-08-10 after external review**, which found that the
earlier headline — "every record read against its own bill text or enacted act" — was
contradicted by this document's own caveats. It was.

What is actually true, now recorded per record under `verification`:

| Dimension | Result |
|---|---|
| Status established from a primary or citable record | **23 of 23** |
| **Operative text read in full** | **16 of 23** |
| Operative text read in part | 1 — MO HB 1746 (consolidated substitute read, its own introduced text not) |
| Operative text **not** read | 6 — ND HB 1361, OK HB 3546, SC HB 3796, WA HB 2029, CA AB 2023, MO SB 1012, each verified from an official status page or summary, each saying so |
| Sponsors established | 21 of 23 |
| `codified_at` verified against the **code** | 5 of 7 enacted (Idaho and North Dakota still bill-sourced) |
| Validator | 0 errors, 0 warnings |

`verified_primary` describes how a record's **status** was established. It never meant that
every version of every bill had been read, and the site should not have implied otherwise.

## Corrections to our own work

**Utah's codified citation was wrong.** This registry published
`Utah Code §§ 63G-31-101, 63G-31-102`. That is what the **enrolled bill** says it enacts.
Utah renumbered on codification: the published sections are **§§ 63G-32-101 and 63G-32-102**,
ch. 32 "Legal Personhood", effective 1 May 2024, enacted by 2024 Utah Laws ch. 451 — verified
against `le.utah.gov/xcode/Title63G/Chapter32/`.

The cause generalises. A bill states what it *intends* to enact; the code states the *result*,
and renumbering on codification is routine. **For an enacted law, `codified_at` must be
verified against the code, not the bill.** Idaho and North Dakota remain bill-sourced on that
field and are flagged as such in their records.

Found by external red-team review, not by us — exactly the class of error this registry exists
to catch, and the strongest available argument for adversarial review before publication.

**RETRACTED: our "correction" to Washington HB 2029 was wrong.** We recorded the bill as still
in committee and said the paper was wrong to call it Failed. The basis was its 12 Jan 2026
action, "By resolution, reintroduced and retained in present status". That resolution is
Washington's routine carryover from the first to the second year of a biennium — it keeps a
bill alive *into* the 2026 session, not beyond it. **Washington's 2026 session adjourned sine
die on 12 March 2026**, and unpassed bills die at the end of the biennium. HB 2029 never
advanced past its first referral. The paper's "Failed" was correct.

The reasoning error is worth naming: Washington posts **no terminal action**, so the page still
shows the last committee location. We treated the absence of a "failed" line as evidence of
life. Absence of a death notice is not evidence of life.

This also corrects a second claim of ours. We said Washington and Wisconsin differ in
*outcome* because of carryover rules. They do not — both sets of bills died at the end of the
2025–26 biennium. They differ only in **record-keeping convention**: Wisconsin posts an
explicit "Failed to pass pursuant to Senate Joint Resolution 1"; Washington posts nothing.

Flagged by external red-team review as "suspicion worth checking" — from a reviewer that could
not reach the primary sources and reasoned from general knowledge of biennial sessions. It was
right.

## Corrections to the paper (five, after one retraction)

1. **Idaho HB 720's sponsor of record is the House State Affairs Committee**, printed on
   the face of the bill. Rep. Nichols drove it but is not the sponsor.
2. **Idaho is the 66th Legislature**, not the 68th as cited.
3. **Ohio HB 469 is the 136th General Assembly**; the reference-list entry says 135th.
4. **Sponsorship is more bipartisan than reported.** Both enacted Tennessee acts carry
   Democratic sponsors — Rep. Justin Pearson on Pub. Ch. 781 (6R–1D), Pearson and Rep.
   Karen Camper on Pub. Ch. 1066.
5. **Family C does not uniformly assign liability to humans.** Wisconsin negates AI
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
- **Washington** posts nothing at all. Bills carry from the first to the second year of a
  biennium by resolution, then die at sine die if unpassed — but no terminal action is
  recorded, so the page still shows the last committee location. Death must be inferred from
  the session calendar.

Only Wisconsin's is a citable failure line. Missouri and Washington require a reasoned reading
against the session calendar — and misreading Washington's is precisely how we got it wrong.
The evidence field now records the action *and* the reasoning, not just the enum.

## Remaining data-quality tasks

1. **MO HB 1746's own introduced text** has not been read; only the consolidated
   substitute and the action history. Its companion HB 1769 as introduced proved to be a
   verbatim HB 1462 clone, so HB 1746 probably was too — an inference, not a reading.
2. Read full operative text for **ND HB 1361, OK HB 3546, SC HB 3796** — verified from
   status pages and summaries, not from bill text.

Every status now carries an evidence action line; the validator enforces it for terminal
stages.
