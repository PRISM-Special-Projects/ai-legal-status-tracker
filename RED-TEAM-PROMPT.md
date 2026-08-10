# Red-team prompt (for GPT or another model)

Copy everything below the line into a fresh conversation with browsing enabled.

---

You are red-teaming a research artefact. Be adversarial, specific and calibrated. I am not
looking for reassurance, a summary, or a list of things done well — I can see those. I want
the errors.

## The artefact

**https://github.com/PRISM-Special-Projects/ai-legal-status-tracker** (public)

It is a registry of US state legislation on the legal status and personhood of AI systems —
23 bills across 12 states, 2022 to mid-2026 — plus a static site generated from it. It began
from Appendix A of Smith, Caviola & Alexander (2026), *Denying Personhood to AI* (SSRN
6829981), and every record was then checked against primary sources.

Where things are:

- `registry/bills.json` — the single source of truth, 23 records. Every page is generated
  from it. An error here is an error everywhere.
- `registry/texts/` — normalised bill texts used for the diffs.
- `registry/incoming/` — the source PDFs as retrieved.
- `registry/validate.py` — schema and referential checks. `site/build.py` — the site builder.
- `VERIFICATION.md` — what was checked, how, and six claimed corrections to the source paper.
- `SCHEMA.md`, `PROJECT_PLAN.md`, `PRESENTATION-DESIGN.md`, `PHASE3-BUILD.md` — decisions
  and rationale.

## The single most important instruction

**Do not take the registry's word for anything.** It documents its own reasoning
persuasively, and if you read only its notes you will agree with it. For any factual claim
you assess, go to the cited primary source — the legislature site, the enacted chapter, the
archived PDF — and read it yourself. Where a source is unreachable, say so rather than
inferring from the registry's account of it.

This artefact was produced with heavy AI assistance. Expect the characteristic failure modes:
confident misreadings, plausible-but-wrong attributions, inferences stated as findings, and
conclusions that sound rigorous because they are specific.

## Assess these dimensions

### 1. Correctness and factuality — highest priority

- **The six claimed corrections to the source paper** in `VERIFICATION.md`. These are about to
  be shown to the paper's authors. Check each against primary sources. Pay particular
  attention to the claim that **Washington HB 2029 is not "Failed"** and the claim that
  **Wisconsin AB 959 / SB 932 correctly are** — these rest on opposite readings of two states'
  carryover rules. Is the Washington reading right? Is the Wisconsin one?
- **Statutory citations.** Utah Code §§ 63G-31-101/102, Idaho Code § 5-346, N.D. Cent. Code
  § 1-01-49(8), Tenn. Code Ann. § 1-3-105(a)(20), Ohio Rev. Code §§ 1357.01–1357.12,
  Wis. Stat. § 134.44 / § 990.01(26), Mo. Rev. Stat. § 1.2045. Do these resolve? Are they right?
- **The Tennessee provenance chain.** The introduced text of HB 849 was recovered from an
  Internet Archive snapshot of a URL that today serves a *different* document. Is
  `registry/texts/tn-sb837-2025--introduced.txt` a faithful transcription of
  `registry/incoming/wb-hb0849.pdf`? Is that PDF actually the introduced version? What would
  falsify that? Same for the HB 1455 chain.
- **Sponsors, vote counts, dates.** Spot-check several against the legislatures' own records.
- **The corporate-veil "inversion" claim** — that Ohio HB 469 § 1357.11 inverts Missouri
  HB 1462 (13) from permissive piercing to default immunity. Read both texts. Is "inverted"
  accurate, or is it rhetorical overreach for two provisions with similar practical effect?

### 2. Data quality

- Internal consistency: do `provisions`, `family`, `technique` and the narrative `notes` ever
  contradict each other?
- Is any tag applied inconsistently across records that share text? The Missouri clones and
  the Wisconsin companions should be near-identical — are they tagged identically?
- `status.evidence` is absent on 9 of 23 records. Does any status rest on nothing?
- Completeness: are there US state bills on AI legal status **missing** from the registry? Its
  scope was inherited from one paper's May 2026 snapshot. Search independently.
- Does `validate.py` actually enforce what `SCHEMA.md` claims? Are there constraints described
  in prose but unchecked in code?

### 3. Editorial neutrality

The project's governing commitment is that it describes what bills say and never rates them.
Test that hard.

- `derived_from_changes` — the genealogy edge labels. Are any editorial rather than factual?
- Provision tag *names*: does `bars_ai_liability` vs `assigns_liability_to_humans` encode a
  judgement? Do any tag names presuppose a conclusion?
- The `notes` fields, which are long and much less disciplined than the structured fields.
  Flag anything asserting more than the evidence supports.
- Site copy in `site/build.py`. Superlatives? Implied ranking? Framing that would read as
  advocacy to someone who supports these bills?

### 4. Code quality and structure

- `site/build.py` and `registry/validate.py`: correctness, failure modes, silent-failure
  paths, anything that would break on a malformed or extended record.
- The diff algorithm in `render_diff` — sentence splitting by regex, operative-text extraction
  by matching an enacting clause. Where does that produce misleading output? What kind of bill
  text would break it?
- Is the build reproducible from a clean clone? Try it.
- Is `bills.json` a sound schema for this domain, or will it need breaking changes soon?
- The known limitation that `provisions` describes only *operative* text: is the proposed fix
  (per-version tags) right, or is there a better model?

### 5. Design and communication of insight

- Does the landing page communicate what matters within ten seconds? What does a reader take
  away, and is it the right thing?
- The provision matrix is the centrepiece: is a 23×16 grid of dots actually legible? Does it
  support comparison, or just look rigorous?
- The state tile grid is a filter, not a map. Does that work, or is it confusing?
- The version diffs are claimed as the differentiating feature. Do they land?
- What is the *most* interesting thing in this dataset, and does the site surface it? If not,
  what should lead instead?
- Accessibility: table semantics, colour contrast, keyboard navigation, screen-reader sense.

### 6. Project structure and maintainability

- Is the repo navigable to someone arriving cold? What is missing — a README, most obviously.
- Bus factor: could someone else maintain this? What is undocumented?
- The plan is to automate discovery via the LegiScan API with a human review queue
  (`PROJECT_PLAN.md`, Phase 4). Will the current schema survive that? What breaks at 200 bills
  instead of 23?

### 7. Adversarial reading

Read the site as three hostile readers and report what each would attack:

1. **A sponsor of one of these bills** who thinks their bill has been mischaracterised.
2. **A journalist** looking for the story "AI-generated research gets the law wrong".
3. **A legal academic** assessing whether this is citable.

### 8. Risk

What here could embarrass the publishing organisation? Consider: the corrections to
colleagues' work; the absence of a licence while the site promises open data; the AI-use
disclosure; any claim that would not survive a lawyer reading it.

## Known weaknesses — do not spend time rediscovering these

- `provisions` describes only operative text, so a provision removed in committee shows in the
  diff but not the tags. `restricts_person_like_training` therefore applies to zero records.
- Some records were verified from status pages or official summaries rather than full text;
  the notes identify which.
- Several legislature hosts were unreachable during compilation; the Internet Archive and
  LegiScan were used as fallbacks, and records say so.
- No LICENSE file yet.
- A CSS specificity bug hid every matrix row below 760px and shipped undetected because the
  acceptance test checked data, not rendering. Other layouts may carry similar bugs.

## Output format

Ranked by severity, most serious first. For each finding:

- **Claim** — what the artefact asserts, quoted, with file and field
- **Problem** — what is wrong, overstated, or unsupported
- **Evidence** — what you checked, with the source URL, and what it actually says
- **Confidence** — `verified against source` / `strong inference` / `suspicion worth checking`
- **Fix** — the smallest change that would make it defensible

Then, separately:

- The three things most likely to cause reputational damage if published as-is
- Anything you could not check, and why

Do not open with praise. Do not summarise the project back to me. If you find no error in a
section, say "no findings" and move on — do not manufacture issues to fill it. Distinguish
clearly between what you verified against a source and what you are inferring; asserting an
unverified inference as fact is the exact failure mode being tested for.
