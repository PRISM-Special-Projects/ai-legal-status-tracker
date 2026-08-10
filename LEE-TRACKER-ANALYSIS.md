# Matthew Lee's AI Rights and Legal Personhood Tracker — comparison and pipeline

**Date:** 2026-08-10 · Assessed by reading the live site (naturalandartificiallaw.com).

## What it actually is

A page on the WordPress site of **Matthew Lee**, a barrister at Doughty Street Chambers
(England & Wales). It is one of **nine trackers** he runs, and the page states plainly that
it is an **"Ad/Marketing communication"** published "solely in connection with promoting or
advertising Matthew Lee's practice."

- Published **30 May 2026** — roughly two weeks after the Smith/Caviola/Alexander paper.
- **Last Verified 10 July 2026** — as is *every* other tracker on the site, which points to
  a periodic batch sweep rather than continuous updating. That is a month stale today.
- **Two entries.** In full:
  1. *Ships Waste Oil Collector B.V. and Others v. the Netherlands* (ECtHR, 1 April 2025) —
     a separate opinion musing that AI protection would need a new Protocol.
  2. *T 0528/25 (Designation of inventor/DABUS)*, EPO Boards of Appeal, 5 Feb 2026 — a
     machine cannot be an "inventor" under the EPC.

The thinness is not incompetence. His AI Hallucination Cases Tracker carries 67+ UK cases.
This one is thin because it is new and because **there genuinely are very few court cases**
on AI legal status. That is itself a useful datapoint for us.

## How comparable is it to what we outlined?

**Barely overlapping. Different branch of government, different object, different method.**

| | Lee's tracker | Ours as outlined |
|---|---|---|
| Object tracked | Court cases, judgments, separate opinions, official materials | Bills and enacted statutes |
| Branch | Judiciary (plus regulators, treaty bodies) | Legislatures |
| Geography | International — UK, ECtHR, EU, US, AU, CA, NZ | US states for v1 |
| Live entries | **2** | 23 seed, growing |
| Structure | Flat table: No · Date · Case Name · Judicial Comment | Versioned records: provisions, lineage, families, amendment diffs |
| Data model | Prose summary + link to source | Structured multi-select fields |
| Text versions | None | Introduced → substitute → enacted, with diffs |
| Export / API | None | CSV + JSON download |
| Source of truth | A WordPress page | JSON in git, dated commits |
| Purpose | Practice marketing and legal commentary | Public research resource |

**The one genuine collision risk:** his stated scope explicitly includes "legislative
materials", "legislative proposals" and the United States. In practice he has covered
**zero** legislation and **zero** US state bills. So the overlap is in the scope statement,
not the content. If he ever expanded into legislatures he would run into us — which is an
argument for making contact early rather than late.

**Assessment: complement, not competitor.** He tracks what courts have said; we would track
what legislatures have done. Our Phase 1 decision to keep courts out of scope for v1 now
looks correct for a second reason — not just focus, but non-duplication. Link to him for the
courts layer.

## How has he built the data pipeline?

**There isn't one, in the engineering sense.** Evidence from the site:

- **WordPress**, confirmed via the `api.w.org` link relation. One HTML `<table>` with three
  data rows.
- **No structured data at all** — no JSON-LD on the tracker page, no API, no export, no
  downloadable dataset, no version history.
- **Manual curation, explicitly stated:** "The tracker is maintained manually and may be
  assisted by research tools, including AI tools."
- **Crowdsourced tips:** the Hub "relies on a global community of legal professionals",
  with submissions via a contact form.
- **Batch verification:** every tracker shares the same "Last Verified" date.
- **Heavy SEO scaffolding:** Key Takeaway block, Table of Contents, FAQ section, "Trending
  now" — this is how the page gets found, and it works.

Speed over polish: the Hub says "9 trackers" in the title, "sevem live trackers" in the
body, and misspells a case name. Fine for content marketing; below the bar we would be held
to as a research organisation.

**Implication for us:** there is nothing here to reuse technically and nothing to be
deterred by. A LegiScan-driven sweep with a review queue would be substantially more capable
than anything on this site. The gap we identified is real and remains open.

## What is worth copying

His **editorial apparatus is genuinely good** and solves problems we have:

1. **The status triplet** — `Tracker Status: Active/Monitoring` · `Publication Date` ·
   `Last Verified` — displayed at the top. Simple, and it manages staleness expectations
   honestly. Adopt.
2. **An explicit Methodology section** and a stated **Source Hierarchy**: primary sources
   preferred, professional commentary only where no primary source exists. That is exactly
   our "traceable to a primary source URL" gate, expressed for readers.
3. **"Inclusion does not imply recognition."** He states repeatedly that listing a case does
   not mean any court recognised AI rights, and that entries may be refusals, warnings or
   mere discussion. **This is the solution to our neutrality problem** — how to track
   AI-personhood policy without being read as advocating AI personhood. He has already
   solved the same reputational risk. Adopt the pattern directly.
4. **AI-use disclosure** plus an explicit corrections invitation.
5. **A suggested citation format.** Cheap, and it makes the resource quotable — which is
   what turns a dashboard into a cited resource.
6. **SEO structure** — ToC, FAQ, key-takeaway summary. Relevant to the "convenient, free,
   findable" goal.

## Recommended actions

1. **Do not change scope.** Courts stay out of v1; link to Lee instead.
2. **Contact him before launch**, not after. He is a natural referral partner in both
   directions, he has a UK/international vantage point we lack, and his scope statement
   nominally covers legislation — better to agree the boundary than discover it.
3. **Lift the editorial apparatus** into our method page: status triplet, source hierarchy,
   inclusion-≠-endorsement disclaimer, AI-use disclosure, corrections route, citation format.
4. **Note the maintenance lesson.** A motivated specialist running nine trackers is a month
   between verification sweeps. Our automated discovery plus review queue is what would let
   us claim a tighter cadence — and we should only claim what the loop can actually hold.
