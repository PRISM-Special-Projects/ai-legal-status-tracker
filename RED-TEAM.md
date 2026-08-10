# Red-team brief — AI Legal Status Tracker

**Snapshot: 2026-08-10.** A registry of US state legislation on the legal status and
personhood of AI systems, plus a static site generated from it.

Everything here was compiled with heavy AI assistance. Assume it contains errors of the kind
AI produces: confident misreadings, plausible-but-wrong attributions, claims that outrun their
evidence, and conclusions that sound rigorous because they are specific. **Your job is to find
those, not to assess whether the project is a good idea.**

## Where to start

`registry/bills.json` is the single source of truth — 23 records. Every page in `site/dist/`
is generated from it. If a fact is wrong there, it is wrong everywhere.

`registry/texts/` holds normalised bill texts. `registry/incoming/` holds the source PDFs as
retrieved. `VERIFICATION.md` records what was checked and how.

To read the site: open `site/dist/index.html` in a browser, or run
`cd site && python3 build.py` to regenerate it.

## The highest-value attacks

### 1. Check the six claimed corrections to the source paper

The registry claims Smith, Caviola & Alexander (2026) got six things wrong. These are the
most consequential claims here, and they are about to be shown to the paper's authors, two of
whom are colleagues. If any is wrong, that matters more than anything else in this folder.
They are listed in `VERIFICATION.md` under "Corrections to the paper".

Particularly worth attacking: the claim that **Washington HB 2029 is not "Failed"**. It rests
on an understanding of Washington's biennial carryover rules. Is that reading right? Note that
the same reasoning was applied to Wisconsin and reached the *opposite* conclusion — check both.

### 2. Verify the Tennessee diffs against the source PDFs

The headline finding is that Tennessee HB 849 as introduced contained fetal-personhood
language that was removed in committee. The introduced text was recovered from an **Internet
Archive snapshot** of a URL that today serves a different document.

- Is `registry/texts/tn-sb837-2025--introduced.txt` a faithful transcription of
  `registry/incoming/wb-hb0849.pdf`?
- Is that PDF actually the *introduced* version, or could the archive have captured something
  else? What would prove it either way?
- Same for `tn-sb1493-2025--introduced.txt` vs `try-20251230002609.pdf`.
- Do the amendment PDFs (`tn-SA0922.pdf`, `tn-HA1260.pdf`) actually say what the records claim?

### 3. Attack the corporate-veil finding

The registry claims Ohio HB 469 **inverted** Missouri HB 1462's veil provision — Missouri lets
courts pierce, Ohio grants immunity with the same three exceptions. This is the project's
most-cited analytical claim. Read both texts in `registry/texts/` and decide whether
"inverted" is fair or overstated. Is it possible both provisions have the same practical
effect and the framing is doing rhetorical work?

### 4. Hunt for normative language in a registry that claims to be descriptive

The project's governing rule is that it describes what bills say and never rates them. Test
that claim against the artefacts:

- `derived_from_changes` — the genealogy edge labels. Are any of these editorial rather than
  factual? Look hard at wording like "weakened", "softened", "degraded".
- Provision tag names. Does `bars_ai_liability` vs `assigns_liability_to_humans` encode a
  judgement?
- The `notes` fields, which are long and were written with far less discipline than the
  structured fields. Flag anything asserting a conclusion the evidence does not support.
- Site copy in `site/build.py`. Any superlatives? Any implied ranking?

### 5. Check the claims that sound too neat

Several findings are suspiciously tidy. Test whether they survive scrutiny:

- "Diffusion by independently commissioned drafts, not a shared file" — inferred from LRB and
  draft numbers. Is that inference sound, or is there a simpler explanation?
- "'Emergent properties' is defined and never used in both Missouri and Ohio" — verify by
  searching the texts. Does the term truly appear nowhere else?
- The claim that the "Responsibility half degrades as the template travels". Is that a pattern
  or three anecdotes?

### 6. Look for what is missing

- Are there US state bills on AI legal status that the registry does not contain? It inherited
  its scope from one paper's May 2026 snapshot.
- `status.evidence` is absent on 9 of 23 records. Does any status rest on nothing?
- Sponsor lists are incomplete in places. Does any record imply completeness it does not have?

## Known weaknesses, already documented

Do not spend time rediscovering these — go past them:

- `provisions` describes only a record's **operative** text, so a provision present at
  introduction and removed later shows in the diff but not the tags. See `SCHEMA.md`.
- `restricts_person_like_training` applies to zero records for that reason.
- Some records were verified from status pages or official summaries rather than full
  operative text — the notes say which.
- Idaho's `corporate_carve_out` classification originally came from a secondary source
  (Jaynes 2024) before the enrolled text was read.
- The licence for the dataset is unresolved.
- Screenshots and layout were verified at three breakpoints only after a CSS bug hid every
  matrix row below 760px — other layouts may carry similar unrendered-but-valid-DOM bugs.

## What would be most useful back

Ranked findings, each with: the specific claim, the file and field, why it is wrong or
overstated, and what the evidence actually supports. False positives are cheap to dismiss;
a missed factual error that reaches the paper's authors is not.
