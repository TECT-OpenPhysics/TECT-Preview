# Q3LOCK collective/Falk--Bruch load-bearing block audit (EXP-001669)

## Scope

This is a bounded internal audit of the collective lower-bound block in
`publish/papers/q3lock-phase-coexistence/manuscript.tex`, Sections
`sec:collective` and `sec:finite-falk-bruch`.  It was run after the
anisotropic literature boundary was recorded and before any content or
notation freeze.  The PDF remains deliberately deferred.

The audit asks whether the displayed finite algebra and normalization are
internally consistent for the exact Q3LOCK potential, and whether the finite
matrix Falk--Bruch factors, clipping derivative, moment substitution, and
threshold cancellation agree with the manuscript.  It does not attempt to
prove the unbounded form-domain passage, the Gibbs trace identities for the
unbounded coordinate, the volume limit, or the cusp theorem.

## Reproducible run

Run from the repository root with:

```text
E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/q3lock_collective_block_audit.py
```

The script writes
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-collective-block-audit/result.json`.
The result is a finite diagnostic, not a claim-card promotion.

## Checks performed

1. For `L=1,2,4` and four rational fixtures, the exact degree-four central
   difference reproduces the normalized common-displacement Hessian
   `r + 3 g S/(8 V) + lambda D/(8 V)` after dividing the unnormalized
   displacement curvature by `8 V`.  The spatial gradient term is exactly
   invariant under the common displacement.
2. The Q3 graph identity
   `D = 3 S - 2 sum_edge q_e q_f` is recomputed exactly, including the
   degree-three factor.  The moment implication used in the manuscript then
   gives `theta_Q = -r/[3(g+lambda)]` once the FKG sign supplies
   nonnegative off-diagonal expectations.
3. The displayed threshold cancellation is checked exactly for rational test
   values satisfying the formal relation
   `beta = 4 m theta x t`: the quantity `2 beta c theta t/x` becomes
   `8 c m theta^2 t^2`.
4. The bounded clip `A_R=R tanh(Q_0/R)` is checked numerically for its
   derivative `sech^2(Q_0/R)` and envelope `sech^4(Q_0/R) in [0,1]`.
5. Finite spectral matrices with degenerate and nondegenerate energy levels
   check the Duhamel range, nonnegative commutator sum, and the exact factors
   in the scalar Falk--Bruch inequality.

## Finding and boundary

The finite checks pass.  No new local coefficient, factor-of-eight, sign, or
finite-matrix normalization defect was found in this bounded audit.  This is
an internal consistency result only.  It does **not** sign the following
load-bearing obligations:

* the translated unbounded form and Gibbs-integrability argument;
* the finite-spectral-cutoff-to-unbounded-coordinate limit;
* identification of the limiting Duhamel form with `D_L(0,0)`;
* the volume-uniform lower bound and its combination with the infrared sum;
* the source-to-zero DLR tangent construction or the strict cusp.

The registered result therefore remains `R-497`, tier `T0`,
`claim_bearing=false`, and `RESEARCH_ONLY`.  The A14--A17 proof rows remain
`OPEN` pending independent line-by-line mathematical review.  This audit is
not a novelty, priority, anisotropic-literature, physical-sector, continuum,
KMS, mass-gap, cosmology, submission, or PDF result.

## Next gate

Send this note and its JSON output to the independent reviewer as a finite
normalization aid, then obtain a signed audit of the unbounded form/core,
spectral cutoff, Duhamel identification, and thermodynamic use.  Keep the
first Q3LOCK PDF for the final content/notation freeze only.
