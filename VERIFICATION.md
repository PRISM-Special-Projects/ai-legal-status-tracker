# Verification and audit history

Last substantive audit: **2026-08-11**.

This document records what was verified, material corrections made during the project, and known evidentiary limitations. Current per-record state lives in `registry/bills.json`; this file is an audit narrative, not a second registry.

## Current result

| Dimension | Current state |
|---|---|
| Records | **29 across 16 states** |
| Status established from a primary/citable record | **29 of 29** |
| Status basis: explicit legislative action | 23 |
| Status basis: sourced session-rule derivation | 6 |
| Status basis: secondary source | **0** |
| Operative text read in full | **29 of 29** |
| Enacted laws | 9 |
| `codified_at` checked against published code | 6 |
| `codified_at` established from bill/session law only | 3 |
| Terminal statuses carrying evidence | **18 of 18** |
| Core validator / publication audit | 0 blocking errors on the I-gate clean state |

The corpus-completeness sweep and publication audit are described in `METHODOLOGY.md` and `RELEASE_READINESS.md`.

## Important corrections to the registry

### Utah HB 249 — enacted numbering versus current code

The registry initially used **Utah Code §§ 63G-31-101 and 63G-31-102**, matching the enrolled bill. Utah renumbered the provisions on codification. The published code is **§§ 63G-32-101 and 63G-32-102**, Chapter 32, Legal Personhood.

The correction established a general rule for this project: an enrolled bill is evidence of the enactment-time destination; the published code is the authority for the codified result. Both can be preserved where the distinction matters.

### Washington HB 2029 — carryover was misread as continued life

An earlier project pass treated the 12 January 2026 action “reintroduced and retained in present status” as evidence that HB 2029 remained alive after the 2026 session. That was wrong. It was the ordinary carryover into the second year of the biennium. The 2026 session then adjourned sine die without passage, so the bill failed.

The failure mode matters: absence of a bill-history entry saying `failed` is not evidence that a bill remains live. Session-end rules must be consulted when a legislature does not post terminal actions for unpassed bills.

### Tennessee HB 1455 / SB 1493 — effective date

The registry initially carried **23 April 2026**, the date of final legislative concurrence, as the effective date. The enacted act took effect when signed by the governor on **22 May 2026**. The registry now distinguishes the legislative-completion date from the date the act became law.

### North Dakota HB 1361 — current code renumbering

HB 1361 enacted the relevant definition in 2023 as **N.D. Cent. Code § 1-01-49(8)**. The current published code places the same AI exclusion in **§ 1-01-49(17)** after later renumbering. The registry preserves both the enactment-time and current-code locations rather than treating the renumbering as a change made by HB 1361 itself.

### Missouri SB 1012 — current status

The bill passed the Senate but later received a House committee Do Not Pass action and did not pass the House before session end. The current stage is therefore `failed`; `passed_one_chamber` remains a historical event rather than the present status.

### Oklahoma HB 3546 and South Carolina HB 3796 — stale live statuses

The publication-focused G8 screen found both records still displayed as live after their relevant regular sessions had ended without passage. Both were corrected to `failed` using their last official actions plus sourced session-end rules.

## Corrections to the source paper inherited during verification

The registry's direct source review identified several differences from the May 2026 source-paper snapshot or reference metadata:

- Idaho HB 720 is a **House State Affairs Committee** bill on the face of the legislation; Rep. Tammy Nichols was an important proponent but not the sponsor of record.
- Idaho HB 720 was introduced in the **66th Legislature**, not the 68th.
- Ohio HB 469 belongs to the **136th General Assembly**.
- The enacted Tennessee measures include Democratic as well as Republican sponsors; sponsorship is therefore not accurately described as uniformly single-party.
- Family-C-style responsibility provisions are not textually uniform across jurisdictions; Wisconsin's bills negate AI liability without reproducing every human-liability mechanism found in the Missouri model language.

These are descriptive corrections to metadata/textual claims, not evaluations of the legislation.

## Material version-history findings

The version review was limited to changes that affect tracker-facing conclusions.

- **North Dakota HB 1361:** introduced `23.0346.02000` used a standalone personhood-status chapter; the Senate-amended `23.0346.04000` moved the mechanism into the general definition of `person`; enrollment preserved the amended operative wording.
- **Missouri HB 1746:** introduced `3891H.01I` contained the detailed corporate-veil provision; HCS `3891H.04C` removed it and added the NIST-based compliance safe-harbour/liability language captured by the tracker.
- **Missouri SB 1012:** the introduced bill did not contain the AI legal-personhood regime; the Senate committee substitute added § 1.2045; a first floor substitute was withdrawn; the later substitute/perfected path retained the legal-personhood prohibition while materially changing other provisions.
- **Tennessee HB 1455 / SB 1493:** the introduced criminal/civil prohibition regime was replaced first by **SA1113**, creating an Advisory Council study, and then by **HA1260**, producing the final TACIR study measure.
- **California records:** material amendment histories were reviewed where later text changed the tracker-facing legal-status/chatbot proposition.

Perfect machine reconstruction of every intermediate document is not a release requirement. Remaining Missouri PDF/parser hardening is recorded as technical backlog in `RELEASE_READINESS.md`.

## Corpus-completeness findings

A fresh national search after the original 23-record verification found six clearly in-scope omissions:

- Arizona HB 2371
- Arizona HB 2311
- Hawaii SB 3001
- Iowa SF 2417
- Virginia HB 635
- Virginia SB 796

They were added after direct text/status review. The current v1 working corpus is therefore **29 records across 16 states**. Representative near-miss exclusions and the final scope rule are recorded in `RELEASE_READINESS.md` and `METHODOLOGY.md`.

## Evidence and access limitations

`verified_primary` must not be read as “every field is exhaustively cited to a primary source.” It means the record has been substantively verified using primary/citable legislative evidence under the project's verification standard.

Selected high-risk claims have claim-specific mappings in `registry/claim_evidence.json`. Other narrative observations remain supported at record/source level and should not be treated as independently field-cited unless a claim-evidence entry exists.

Three enacted records retain bill/session-law-sourced `codified_at` rather than direct published-code verification. Those records are explicitly marked through `verification.codified_at_source = "bill"` and a provenance note. This includes the documented Idaho official-code access limitation rather than silently upgrading corroborating secondary reproductions to official-code inspection.

Document hashes establish integrity of retrieved/stored material; they do not prove semantic correctness of extraction or classification.

## Reproducibility lessons for future researchers

1. **Read the actual operative text.** A status page or bill summary is not a substitute when the tracker is making a substantive claim about legal effect.
2. **Separate current status from historical milestones.** Passing one chamber does not remain the current stage after a bill later fails.
3. **Check session rules where terminal actions are absent.** Washington and Missouri illustrate different record-keeping conventions for bills that die without passage.
4. **Distinguish enactment text from current code.** Renumbering can make the enrolled bill's proposed citation different from the published code.
5. **Treat amendments by adoption status.** A withdrawn substitute is evidence of legislative history, not necessarily an ancestor of the operative text.
6. **Do not infer textual absence from missing evidence.** Absence is recorded only when the relevant text was actually checked.
7. **Keep researcher inference visibly distinct from legislative fact.** A source-backed inference is still an inference.
8. **Record access limitations.** Strong corroboration does not become direct official-source inspection merely because the official portal is inaccessible.

These lessons are incorporated into `METHODOLOGY.md` and the validation/provenance tooling.
