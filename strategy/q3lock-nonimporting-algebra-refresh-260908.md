# Q3LOCK non-importing algebra source-refresh checkpoint

Date: 2026-09-08. Exploration: EXP-001659. Task: T-054.
Status: T0 internal provenance repair, claim_bearing=false, not a signed
independent review. The paper remains UNFROZEN_CONTENT_REVIEW and PDF DEFERRED.

## Question

Can the exact non-importing polynomial audit be replayed against the current
manuscript and package without rewriting the older R2-era result?

## Method

The standalone checker was first rerun in read-only mode. Its 2026-09-07
result correctly rejected the current manuscript because it was pinned to the
older R2 manuscript hash. The checker was then revised to validate the current
T0/RESEARCH_ONLY/PDF-DEFERRED package scope while retaining frozen R-497
authority hashes. A new no-overwrite result was issued after the package and
reader-document synchronization. The old R2 result and the intervening current
refreshes were preserved. The integrated replay was updated to compare the
current result and to protect all prior algebra outputs.

## Finding

The current r3 algebra result passes 46 exact-rational assertions, including 38
coefficient identities, with no floating tolerance or sampled-parameter
substitution. The source set records the current manuscript, algebra note,
test, frozen authority manifest and checker. Package scope is checked but the
mutable package pointer is not included in the algebra source-hash set, which
prevents a pointer-only replay cycle while retaining the scope guard. The fresh
manuscript audit r73 passes 7/7 groups and 1171 assertions. The integrated r66
replay passes 7/7 manuscript groups, 7/7 canonical groups, independent 306/306,
finite-form r10, and the current algebra result; historical bytes remain
protected.

## Boundary

This repair is provenance and reproducibility maintenance. It does not change
the polynomial identities, establish any analytic inequality, close an A1-A23
proof-audit row, promote R-497, or certify a phase, DLR pair, cusp, continuum,
novelty or publication result. PDF generation remains deferred until content,
external review, final hash freeze and clean release review are complete.

## Evidence

* `verification/scripts/q3lock_nonimporting_algebra.py`
* `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-nonimporting-algebra-current-v016-r3/result.json`
* `verification/scripts/q3lock_manuscript_integrated_replay.py`
* `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-manuscript-fresh-audit-r73-algebra-refresh-v016/result.json`
* `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-paper-integrated-replay-r66-algebra-refresh-v016/result.json`
* `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-nonimporting-algebra-current-v016-r2/result.json`
* `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-nonimporting-algebra-current-v016/result.json`
* `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-nonimporting-algebra/result.json`

## Next action

Keep the current package at T0 and PDF DEFERRED. Obtain location-specific
external mathematical and literature dispositions, then perform a final
content/notation freeze and fresh clean replay before any PDF is generated.
