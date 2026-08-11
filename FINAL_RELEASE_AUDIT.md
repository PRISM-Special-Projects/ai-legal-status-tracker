# Final release audit — v1

Date: **2026-08-11**

## Purpose

The release gate tests whether difficult tracker conclusions can be independently reconstructed from source evidence rather than merely re-validating the registry's internal consistency.

For this gate, six deliberately difficult cases were reconstructed **source-first** and then compared with the tracker. The standard is substantive agreement on scope, current status, operative legal proposition, material history and evidentiary qualification. Parser perfection and exhaustive intermediate-version reconstruction are not part of this gate unless they change one of those conclusions.

## Result

**PASS WITH DOCUMENTED LIMITATIONS.**

No sampled record produced a material contradiction with the registry. The Idaho sample reproduces the already documented access limitation: the live Idaho Legislature/code portal was inaccessible to the retrieval environment during this independent pass, so direct live-code inspection could not be newly repeated. The bill/session-law result and § 5-346 text remain corroborated, and the registry correctly does **not** claim code-level verification for that record.

## Sample 1 — Utah HB 249 (2024)

**Why sampled:** enacted personhood prohibition and enactment/current-code numbering distinction.

**Source-first reconstruction:**

- Official Utah bill history identifies HB 249, sponsored by Rep. Walt Brooks with Sen. Don Ipson as floor sponsor, and records the governor signature on 20 March 2024.
- The official Utah Code currently publishes **Title 63G, Chapter 32 — Legal Personhood**, effective 1 May 2024, with §§ 63G-32-101 (Definitions) and 63G-32-102 (Legal personhood restricted).
- The enrolled bill used enactment-time Chapter 31 numbering; the published code is Chapter 32.

**Comparison with tracker:** **CONFIRMED.** The registry preserves the enrolled numbering as enactment-time provenance while using §§ 63G-32-101/102 for current `codified_at`.

Primary sources:
- https://le.utah.gov/~2024/bills/static/HB0249.html
- https://le.utah.gov/xcode/Title63G/Chapter32/63G-32.html

## Sample 2 — Washington HB 2029 (2025-26)

**Why sampled:** session-rule-derived failure and a known prior project error.

**Source-first reconstruction:**

- Official bill history records first referral to Civil Rights & Judiciary on 27 February 2025.
- On 12 January 2026 it was “reintroduced and retained in present status,” with no later passage action.
- Washington's official session page states that the 2026 regular session adjourned sine die on **12 March 2026**.
- House Concurrent Resolution 4409 formally adjourned the 2026 Regular Session sine die on that date.

The January carryover action therefore kept the bill alive into the second year of the biennium; it did not establish survival beyond sine die.

**Comparison with tracker:** **CONFIRMED.** Current stage `failed`, with `session_rule` basis, is the correct tracker classification. The earlier project interpretation that the bill remained in committee was correctly retracted.

Primary sources:
- https://app2.leg.wa.gov/billsummary?BillNumber=2029&Year=2026
- https://leg.wa.gov/bills-meetings-and-session/session/
- https://lawfilesext.leg.wa.gov/biennium/2025-26/Htm/Bills/House%20Passed%20Legislature/4409.PL.htm

## Sample 3 — Tennessee HB 1455 / SB 1493 (2025-26)

**Why sampled:** materially amended bill and effective-date correction.

**Source-first reconstruction:**

- The official Tennessee bill history records Senate adoption of **SA1113** on 23 April 2026 and describes that amendment as rewriting the bill to create a Tennessee Artificial Intelligence Advisory Council study.
- The House then adopted **HA1260**, which again rewrote the bill, replacing that mechanism with a TACIR study and report due 31 January 2027.
- The Senate concurred in HA1260 on 23 April.
- The governor signed the act on **22 May 2026**; the official history gives that as the effective date and identifies Public Chapter 1066.

**Comparison with tracker:** **CONFIRMED.** The material history is correctly represented as introduced substantive prohibition regime → SA1113 Advisory Council study → HA1260/final TACIR study. The registry's 22 May effective date is correct; 23 April is the legislative-concurrence date, not the effective date.

Primary source:
- https://wapp.capitol.tn.gov/apps/BillInfo/Default?BillNumber=SB1493&ga=114

## Sample 4 — North Dakota HB 1361 (2023)

**Why sampled:** code-renumbering case.

**Source-first reconstruction:**

- The official HB 1361 overview states that the bill amended **subsection 8 of § 1-01-49**, relating to the definition of person, and records governor signature / filing with the Secretary of State.
- The current official Century Code now places `Person` at **§ 1-01-49(17)** and states that the term does not include environmental elements, artificial intelligence, an animal, or an inanimate object.

Thus subsection (8) is the enactment-time location; subsection (17) is the current code location after later renumbering.

**Comparison with tracker:** **CONFIRMED.** The registry correctly distinguishes enactment-time numbering from current-code numbering and does not misattribute the later renumbering to HB 1361.

Primary sources:
- https://ndlegis.gov/assembly/68-2023/regular/bill-overview/bo1361.html
- https://ndlegis.gov/cencode/t01c01.pdf

## Sample 5 — Iowa SF 2417 (2026)

**Why sampled:** newly discovered chatbot-status law and scope-boundary test.

**Source-first reconstruction:**

- Official bill history says SF 2417 was signed by the governor on **2 May 2026**, with effective date 1 July 2026 and applicability date 1 July 2027.
- Iowa Acts Chapter 1068 requires reasonable measures to prevent a conversational AI service from generating statements that would lead a reasonable person to believe they are interacting with a human, expressly including claims that the service is **sentient or human**.

This crosses the tracker's settled scope boundary: it is not merely a generic software-disclosure rule; it expressly regulates person-like claims of sentience/humanity.

**Comparison with tracker:** **CONFIRMED.** Inclusion, enacted status, effective/applicability dates and `restricts_chatbot_claims` classification are supported by the enacted text.

Primary sources:
- https://www.legis.iowa.gov/legislation/billTracking/billHistory?billName=SF2417&ga=91
- https://www.legis.iowa.gov/docs/publications/iactc/91.2/CH1068.pdf

## Sample 6 — Idaho HB 720 (2022)

**Why sampled:** enacted personhood law plus documented official-code access limitation.

**Source-first reconstruction:**

- The official Idaho Legislature domain was blocked by `robots.txt` to the retrieval environment during this pass, so a new direct live-portal inspection could not be completed.
- Idaho Governor material confirms the 2022 legislative session context; secondary legislative mirrors that preserve the Idaho source links consistently record HB 720 as signed 31 March 2022, Session Law Chapter 322, effective 1 July 2022.
- The reproduced statutory text for **Idaho Code § 5-346** states that environmental elements, artificial intelligence, nonhuman animals and inanimate objects shall not be granted personhood, while preserving previously recognized municipalities, organizations, corporations and other legal/business entities. The history identifies § 5-346 as added by 2022 ch. 322, sec. 1.
- Earlier project work directly reviewed the bill text and independently corroborated the code text through multiple legal-code reproductions, while explicitly declining to label those reproductions as direct official-code inspection.

**Comparison with tracker:** **CONFIRMED WITH LIMITATION.** The registry's substantive account and bill/session-law citation are reproduced; `verification.codified_at_source = "bill"` remains the correct conservative evidence label. The inability to repeat live official-code inspection does not create a conflicting legal result.

Relevant sources:
- https://gov.idaho.gov/legislative-sessions/2022-legislative-session/
- official Legislature source retained by the registry: https://legislature.idaho.gov/sessioninfo/2022/legislation/H0720/

## Final gate decision

### Substantive audit — PASS

The six source-first reconstructions reproduce the material tracker conclusions.

### Data/status audit — PASS

No sampled current status, effective date, enacted/current-code distinction or material amendment sequence conflicts with the public source evidence.

### Scope audit — PASS

The Iowa sample confirms that the H-gate rule distinguishes a sentience/human-status provision from generic AI identity disclosure in a reproducible way.

### Reproducibility audit — PASS WITH DOCUMENTED LIMITATION

Five samples were directly reconstructed from accessible official public sources. Idaho's live Legislature/code portal was inaccessible to the audit retrieval environment; the registry already discloses that limitation and does not overstate its source level.

### Technical/release audit — PASS

Workstreams G, H, I and J passed their tracker-focused gates, and the full validation/build workflow passed on the clean J state before this final audit.

## Release decision

**v1 COMPLETE — PASS WITH DOCUMENTED LIMITATIONS.**

Known non-blocking items after v1:

- manually update the GitHub repository description from the old `23 bills / 12 states` text to `29 bills / 16 states`;
- Missouri SB 1012 structural-differ/PDF-normalisation hardening;
- exhaustive intermediate-version graphs where they do not alter tracker-facing conclusions;
- future completeness sweeps as new state legislation is introduced or amended.
