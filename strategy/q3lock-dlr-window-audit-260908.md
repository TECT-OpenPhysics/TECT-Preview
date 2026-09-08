# Q3LOCK DLR source-window interface audit (EXP-001670)

## Scope

This note records a bounded internal audit of the source-window and
zero-source tangent interface in Sections `sec:dlr-specification` through
`sec:dlr-source-tangents` of the Q3LOCK manuscript.  It checks only finite
formulae and bookkeeping that can be separated from the imported
Kozitsky--Pasurek theorem and from the infinite-volume limits.  The PDF
remains deferred.

## Reproducible run

From the paper worktree, run:

```text
E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/q3lock_dlr_window_audit.py
```

The output is written to
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-dlr-window-audit/result.json`.
It is a claim-non-bearing finite diagnostic.

## Checks performed

The checker recomputes the quadratic and linear Young maxima used in the
uniform envelope, the Q3 degree-three and three-dimensional spatial row
budgets, the Holder fixed point `t=1/2`, the cofinal weight direction and an
escaping-mass fixture, the full-beta source dictionary, positive Gaussian
normalizer events, the source-Lipschitz scalar maximum, fourth-moment clipping
scales, the Q3 mixed derivative identity, and the projective tail factor.

These checks are deliberately narrower than the analytic statements in the
manuscript.  They do not prove Fernique integrability, the KP hypothesis map,
Polish/projective compactness, Feller continuity, passage of a DLR equation,
or source-to-zero tangent limits.

## Finding and boundary

The finite checks pass with no new source-factor, envelope, row-sum, Holder,
tail-direction, clipping, or mixed-derivative defect.  The source dictionary
continues to give `p'(h)=8 beta P'(h)` and `P'(h)=E Q_0/8`; no extra beta is
inserted.  The slower-decaying weight `alpha_(k+1)<alpha_k` is the stronger
tail input, as used in the manuscript.

The result remains `R-497`, tier `T0`, `claim_bearing=false`, and
`RESEARCH_ONLY`.  The following remain open and require location-specific
independent review:

* exact applicability of KP Assumptions (A)/(B) to the positive-lambda
  non-radial potential;
* source-window Fernique and Holder constants for the interacting periodic
  family;
* compactness of the declared projective tempered topology;
* compact-boundary normalizer/Feller estimates and their Borel extension;
* the two-stage source-to-zero DLR passage and unbounded local expectation.

No pressure cusp, DLR multiplicity, KMS, gap, continuum, physical-sector,
cosmological, novelty, priority, submission, or PDF conclusion follows.

## Next gate

Send this finite interface audit with the existing EXP-001657 DLR topology
audit to the independent reviewer.  Obtain a signed line-by-line disposition
of the imported KP hypotheses and all source-window/projective/Feller limit
steps before final content freeze.
