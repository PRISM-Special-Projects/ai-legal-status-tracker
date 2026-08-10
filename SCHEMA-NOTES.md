# Schema notes for Phase 2 — provision tags discovered during Phase 1

Running list of registry fields and provision tags that reading the literature has shown
we need. Feeds the schema spike; settle at the checkpoint with Austin and Lucius.

## From Jaynes (2024), AI & Society Curmudgeon Corner

A short opinion piece, but it contains four provision-level distinctions sharper than
anything in the main paper. All four are checkable against bill text, so all four can be
flat descriptive tags — no judgement required.

### 1. `definitional_anchor` — how the bill bounds "human"

Utah HB 249 closes its list with *"any other member of a taxonomic domain that is not a
human being"* — a **taxonomic anchor**. Idaho HB 720 has no equivalent limiter.

Values: `taxonomic` · `none` · `enumerated_only` · `other`.

This is the highest-value tag on the list. It drives tag 2.

### 2. `augmented_human_exposure` — does the bill risk catching augmented people?

Jaynes's core argument: a bill that bans AI personhood without a human-anchoring clause
may sweep in people with AI-driven bionic implants, prosthetics, or completed gene
therapies, whose taxonomic classification has never been litigated.

Note this is the **same critique Alexander & Simon later made about Ohio HB 469** (neural
implants, 2025). Jaynes made it about Idaho in 2024. So there is a lineage of the
*critique*, not only of the bills — worth showing on the site alongside the bill genealogy.

Keep the tag descriptive: `anchored` · `unanchored` · `unclear`. Do not score risk.

### 3. `affects_algorithmic_entity_formation` — the zero-member LLC question

Shawn Bayern's zero-member LLC is the known route by which an AI could acquire de facto
legal personhood through **existing** corporate law, without any legislature granting it.
Jaynes argues Utah HB 249 likely bars forming one; Idaho HB 720 probably does not, and
will not be settled until an Idaho court is asked.

This matters more than most of what the bills say explicitly: it is the mechanism the
bills may or may not actually close. Values: `bars` · `does_not_bar` · `untested` ·
`not_analysed`.

Requires Bayern (2015) on the collect list — added.

### 4. `corporate_carve_out` — how corporate personhood is protected

Two distinct techniques, already visible in the paper but not tagged separately:

- **Idaho HB 720:** an express saving clause preserving the personhood of municipalities,
  corporations and other entities recognised *before the effective date*.
- **Utah HB 249:** no saving clause needed, because it only bars granting *new* personhood.

Values: `express_saving_clause` · `prospective_only` · `none` · `other`.

## Other fields this surfaced

- **`codified_at`** — enacted bills need their statutory citation, not just a bill number.
  Jaynes gives Idaho Code § 5-346 for HB 720; the paper does not. Without this you cannot
  link a law to the code section that actually binds.
- **`constitutional_exposure`** — provisions claimed to be in tension with specific
  amendments. The paper analyses the 1st, 5th and 14th. Jaynes additionally asserts the
  8th, 9th and 10th. Record *claims made and by whom*, never our own legal conclusion.
- **`non_western_framing`** — Jaynes argues the debate is Western-dominated and that
  non-Western jurisdictions tend to follow US/EU regulatory models. Our corpus already
  holds African-philosophy personhood work; Attoe et al. (2023) added to the collect list.
  Relevant when the tracker eventually goes international.

## Terminology

Jaynes called it **"copy-and-paste bill drafting"** in 2024; the paper later formalises the
same phenomenon as **legislative families**. Use the paper's term, credit the observation.

Also worth noting on the site's timeline: Jaynes warned in 2024 that other conservative
states would replicate the Idaho and Utah language. Twenty-one further bills followed. A
documented, dated, correct prediction is good evidence that this trend is trackable — which
is the tracker's whole premise.
