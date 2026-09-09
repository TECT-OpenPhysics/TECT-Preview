# Q3LOCK external-review distribution

**Operator authorization:** 2026-09-08. Prepare the external-review and
submission-materials package, including PDFs, now. This supersedes the earlier
PDF deferral for this review edition only. It does not authorize transmission,
journal submission, public upload, a release tag, or scientific promotion.

**Paper:** q3lock-phase-coexistence. **Research source:** manuscript v0.1.38.
**Distribution:** q3lock-v0138-r1. **Result:** R-497, T0,
claim_bearing=false, RESEARCH_ONLY. EXP-000780 -> EXP-000781 -> EXP-000782
remains the research authority. C6 is routing context, not a physical conclusion.

The original manuscript, package manifest, and saved diagnostics are preserved
byte for byte. Their PDF-DEFERRED statements describe the pre-distribution
checkpoint, not the later operator authorization above. The generated review
edition replaces only presentation/status passages and applies documented
typesetting changes; its scientific text is checked against the original.
There is one research manuscript, not a second independently maintained paper.

The derived distribution is at
`publish/review-packages/q3lock-v0138-r1/`. It contains the review-edition
manuscript PDF and TeX, a reviewer guide PDF, an editable response form, a
review-request email, a journal-neutral submission cover-letter draft, a
submission checklist, and a hash manifest. The accompanying archive also
contains a read-only research-snapshot replay. Distribution hashes freeze only
this review snapshot; they do not close the final scientific-acceptance gates.

## Reading order

1. Read the reviewer guide for the request, scope, nonclaims and A1-A23 checklist.
2. Read the manuscript and its exact cited-theorem hypothesis crosswalk.
3. Inspect the source ledgers and run the included integrity/replay commands.
4. Return attributable, location-specific findings in the editable response.
   Partial reviews are useful; untouched rows must stay NOT REVIEWED.

## Remaining decisions

External mathematics and specialist literature reviews remain OPEN. There is
no claim of novelty, priority, independent acceptance, or readiness for a
particular journal. A journal has not been selected. Author affiliation,
ORCID, funding, conflicts, coauthor approval and the journal's AI/disclosure
requirements must be confirmed by the author, not inferred from the repository.
The letter is therefore a draft, not a signed declaration. Rebuild and re-review
after any mathematical correction or target-journal adaptation.

## Reproduction

From the repository root, using Python with the existing symbolic dependencies:

    python verification/scripts/build_q3lock_review_distribution.py --self-test
    python verification/scripts/q3lock_manuscript_integrated_replay.py --check

The distribution builder is a typesetting and provenance tool, not a proof.
Its build instructions and compiler provenance are recorded with the outputs.

## Adversarial packaging review

- **Historical evidence overwrite:** DISMISSED by byte-preserving source
  snapshotting and read-only replay; no expected historical hash is replaced.
- **Typesetting changes alter mathematics:** mitigated by an explicit,
  count-checked transformation list and comparison of the science-bearing
  sections before and after distribution preparation. Any nonpresentation
  change requires a separate research repair, not a formatter exception.
- **PDF mistaken for acceptance:** mitigated by explicit review-edition labels,
  retained T0/non-claim-bearing scope, OPEN review rows and submission hold.
- **Archive omits dependencies or leaks local data:** mitigated by a bounded
  public-path inventory, no Git metadata or P0 files, member hash checks and
  an actual extracted-copy replay. Hash checks do not certify mathematics.
- **Successful compilation hides bad layout:** mitigated by final log checks,
  page rendering and visual review. Compilation alone is insufficient.

Independent review of both the mathematics and the packaging is invited.
