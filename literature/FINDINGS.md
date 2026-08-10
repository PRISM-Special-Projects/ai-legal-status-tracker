# Phase 1, Steps 1–2 — Reference extraction and corpus dedupe

**Date:** 2026-08-10 · **Inputs:** Smith, Caviola & Alexander (2026) reference list
(pp. 42–50) and Table of Cases (p. 41) · `digital-minds-corpus/master-corpus.csv`

**Authoritative artefact:** `reference-register.xlsx`. `dedupe-report.csv` is the raw
automated pass only — the workbook carries the hand-adjudicated result and supersedes it.

## Step 1 — Scholarly subset

The reference list holds **126 distinct entries**, plus 15 cases in a separate Table of
Cases. Of the 126:

| | Count | Share |
|---|---|---|
| Scholarly works | **46** | 36.5% |
| Evidence about the bills | **80** | 63.5% |

Scholarly = 40 `core` + 6 `marginal`. Evidence breaks down as advocacy pages (20),
news (15), testimony (14), legal documents (8), primary religious texts (3), press
releases (3), social posts (3), op-eds (2), blogs (2), media (2), reference works (2),
member pages (2), government reference (2).

**The paper is built roughly two-thirds on primary evidence, not on a prior scholarly
conversation** — consistent with its claim that no systematic analysis of these bills
existed. All 80 evidence records are retained in the workbook, keyed by jurisdiction and
related bill, and feed the Phase 2 bill registry.

## Step 2 — Dedupe against the DM corpus

Matched on normalised title against **all corpus layers** — an `adjacent` work is still
one we hold. Four borderline matches were adjudicated by hand against author *and* title.

| Of the 46 scholarly refs | Count | Share |
|---|---|---|
| Already held in the corpus | **24** | 52% |
| Not held — to collect | **21** | 46% |
| Needs verification | **1** | 2% |

Of the 24 held: 17 `core`, 6 `adjacent`, 1 `canon`.

### Correction to the first automated pass

An initial run reported 28 held (61%). That was inflated: a containment rule was matching
short generic titles against anything sharing a word. Requiring ≥25 characters before
allowing a containment match, then checking the residue by hand, removed three false
positives and flagged one genuine ambiguity:

- **Butlin et al. 2023**, *Consciousness in Artificial Intelligence* (arXiv 2308.08708) —
  **not held.** The corpus has other Butlin works (*Identifying indicators of
  consciousness in AI systems*, 2025) but not this report. A notable gap: it is among the
  most-cited works in AI consciousness.
- **Ivanov et al. 2022**, *Neuromorphic artificial intelligence systems* — **not held.**
  The corpus's neuromorphic entries are different papers.
- **Salib & Goldstein 2024a**, *AI Rights for Human Safety* — **not held.** Distinct from
  the corpus's *AI Rights for Human Flourishing*.
- **Salib & Goldstein 2024b**, *AI Rights for Economic Flourishing* — **needs
  verification.** The corpus holds *AI Rights for Human Flourishing* (2025), which may be
  this paper retitled on publication. Confirm against SSRN 5353214 before collecting.

The corrected saving is **just over half**, not two-thirds. Still material, but the
first number was wrong and the collect list is 3 items longer than first reported.

### Finding A — the corpus is a source, not just a dedupe target

The corpus holds a **59-work personhood / legal-status cluster** (core+canon) that the
paper does not cite: philosophy, law, humanities, psychology and engineering, producing
steadily since 2020. Examples: *No legal personhood for AI* (2023), *The legal personhood
of human brain organoids* (2023), *Do We Need New Legal Personhood in the Age of Robots
and AI?* (2018), *Stakeholder Personhood and Artificial Intelligence* (2026).

**Implication:** the working set for the review is **105 works**, not 46, and the
snowball should run outward from the corpus cluster as well as from the paper.

### Finding B — two structural gaps, and they are the two that matter most

Corpus title search across core+canon: **"rights of nature" 0 · "river" 0 ·
"corporate" 0 · "animal rights" 3 · "nonhuman" 6.**

The corpus has **no rights-of-nature and no corporate/juridical personhood literature**.
These are exactly the two doctrinal lineages the paper identifies as the *origin* of the
Exclusion Bills — Idaho HB 720 came out of the rights-of-nature backlash, and every
Family A and B bill carves out corporate personhood explicitly.

The gap is not in AI-consciousness scholarship, which is well covered. It is in the
**legal doctrine the bills descend from**. Ryan et al. (2021), Blair & Pollman (2015),
Bruner (2022) and Gray (1997) — all on the collect list — are the entry points.

### Finding C — the corpus under-weights legal scholarship

Six of the 24 held works sit in `adjacent` rather than `core`, including Chopra & White
(2011), Novelli et al. (2025) and Solum (1992) — foundational AI-legal-personhood texts.
`discipline = law` covers only 55 of 1,279 core+canon works (4.3%).

**Implication:** worth raising against the DM corpus separately. If the tracker's
literature layer draws on the corpus, this misclassification would under-represent
precisely the strand the tracker is about.

## The 21 to collect

**Core (15).** Legal-doctrinal: Forrest 2024 (Yale LJ Forum), O'Keefe et al. 2025
(Fordham), Ryan et al. 2021 (Cardozo — rights of nature), Blair & Pollman 2015 (W&M —
corporate constitutional rights), Bruner 2022 (Delaware corporate law), Gray 1997,
Salib & Goldstein 2024a. Consciousness / safety: Butlin et al. 2023, Bengio et al. 2026,
Wei et al. 2023, Sebo 2025 (*The Moral Circle* — the corpus has a symposium about it but
not the book). Architectures: Ivanov et al. 2022, Jin et al. 2026, Sirbu & Floridi 2026,
Wang et al. 2026.

**Marginal (6).** Buck 2024, Curhan et al. 2025, Fordham 2025, Roberts 2026,
Suleyman 2025, Weinberg 2026. Context, not literature — decide at the checkpoint whether
they enter the registry.

## Next (step 3)

Two-round snowball from the 105-work working set, prioritising the rights-of-nature and
corporate-personhood strands where coverage is zero. Backward from Solum 1992, Chopra &
White 2011, Gray 1997, Ryan et al. 2021; forward via citations to those anchors.

## Reproduce

```bash
python3 build_workbook.py
```
