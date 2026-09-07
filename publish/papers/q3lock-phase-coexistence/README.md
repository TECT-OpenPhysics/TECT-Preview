# Q3LOCK phase-coexistence paper

This directory is the content-first publication lane for
“Phase Coexistence in an Eight-Component Q3-Locked Quantum Anharmonic
Crystal.”  It is a manual P2 manuscript draft, not a submission or publication
record.

Current status: DRAFT / T0 INTERNAL_REVIEW_ONLY / PDF DEFERRED (v0.1.7,
2026-09-07).  The source assembles the seven proof blocks registered in R-497:
finite pressure, thermodynamic pressure, tempered DLR states, continuous-loop
FKG, reflection positivity and infrared domination, the collective
Falk--Bruch lower bound, and the strict cusp/DLR-pair composition.

The theorem in manuscript.tex is explicitly conditional on the named
finite-volume, source-limit, and external-theorem hypotheses.  The paper does
not promote C6-SPACETIME-SIGNATURE, does not convert R-497 from T0, and does
not assert a physical vacuum, real-time dynamics, a gap, a continuum limit,
cosmology, or sector closure.

## Contents

* manuscript.tex — integrated, reviewable manuscript source; no PDF is
  stored until the content and notation are frozen.
* claims-cited.md — exact claim/result scope and prohibited overclaims.
* theorem-applicability-audit.md — hypothesis-by-hypothesis source map.
* imported-source-ledger.md — exact current imports versus comparison citations,
  with individual hypothesis dispositions and external-acceptance boundary.
* literature-crosswalk.md — bounded primary-literature comparison and
  non-subsumption boundary.
* proof-audit.md — adversarial checklist and acceptance record.
* external-review-handoff.md — independent referee request and response
  template.
* submission-readiness.md — release gates, with PDF explicitly last.
* version-history.md — content-only revision history.
* verification/README.md and verification/package-manifest.json — canonical
  replay commands, expected artifacts, and the deferred hash-freeze contract.

## Scope-preserving build rule

Do not compile or render a PDF during active content review.  After the
manuscript, crosswalk, audits, and nonclaims are frozen, run the repository
release checks, capture fresh hashes, and compile once for final visual review.
The final PDF must be generated from the same frozen manuscript.tex whose hash
appears in the release manifest.
