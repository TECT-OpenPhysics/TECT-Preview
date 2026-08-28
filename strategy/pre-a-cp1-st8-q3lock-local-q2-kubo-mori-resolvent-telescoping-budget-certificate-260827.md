# EXP-001219 / R-377 certificate

## Result and boundary

R-377 is a T0, claim-nonbearing finite operator-interface checkpoint.  For
the positive odd-Matsubara resolvent

```text
R_n(A) = (omega_n^2 I + beta^2 A^2)^(-1),
```

the exact algebraic difference is

```text
R_n(B)-R_n(A) = R_n(B) beta^2 (A^2-B^2) R_n(A).
```

The finite audit verifies this identity, its gap-free resolvent norm ceiling,
and the summable 64-layer budget.  For the capped positive kernel
`8 |A| R_n(A)`, the difference is split exactly into

```text
8 (|B|-|A|) R_n(B) + 8 |A| (R_n(B)-R_n(A)).
```

The first summand is retained as an explicit square-root/eigenvector-rotation
debt; it is not silently absorbed by the resolvent estimate.

## Finite verification

The primary and non-importing independent lanes use the actual V=2, cutoff-2
local bond commutator Liouvillian, two beta values, two noncommuting local
momentum perturbations, and all 64 declared odd frequencies.  Each lane
passes 1056/1056 assertions.  The integrated verifier passes 122/122, with
primary and independent reported values agreeing exactly at the stored
precision.  The largest identity residual is `6.11350532313155e-17`; the
largest operator-bound excess is `1.6653345369377348e-16`; and the largest
summed budget ratio is `0.9895313426497929`.  The smallest denominator
eigenvalue is `9.869604401089342`, equal to the first odd frequency squared
up to roundoff.  The maximum recorded square-root debt is
`0.1239852906116096`, while the corresponding resolvent-kernel term is
`0.0029917128279303984`.

## Lean cross-check

`verification/lean/Tect/R377.lean` proves positivity of the scalar
denominator, its domination of `omega^2`, positivity of the scalar
resolvent, and the exact scalar resolvent-difference identity.  The pinned
Lean toolchain compiles the file.  Matrix inverses, Schatten estimates,
locality, and thermodynamic limits are deliberately outside this scalar
cross-check.

## Devil's-advocate review

1. **Sign/order of the resolvent identity.** Status: DISMISSED-FINITE.  The
   verifier checks both matrix products and the residual is roundoff-sized.
2. **A hidden spectral-gap denominator.** Status: DISMISSED-FINITE.  The
   bound uses only the positive odd frequency; no minimum eigenvalue of `A` or
   `B` is inverted.
3. **The denominator could lose positivity.** Status: DISMISSED-FINITE.
   Every mode checks its minimum denominator eigenvalue against `omega^2`.
4. **The Frobenius budget might not be summable.** Status:
   DISMISSED-FINITE.  All 64 finite terms are summed and the accumulated
   matrix difference remains below the accumulated budget.
5. **The scalar resolvent identity might not transfer to matrices.** Status:
   DISMISSED-FINITE for the declared fixture: the matrix identity is checked
   directly; general operator-domain proof remains open.
6. **The absolute-value term could be hidden in the budget.** Status:
   DISMISSED-FINITE.  The exact decomposition records it separately and
   reports its nonzero debt.
7. **The local fixture could hide volume or cutoff growth.** Status:
   UPHELD-OPEN.  No uniformity is inferred from V=2 and cutoff 2.
8. **The doubled-bond shell could differ from the production shell.** Status:
   UPHELD-OPEN.  R-377 uses a local commutator interface, not the full
   weighted Q3 shell.
9. **The independent lane could import the primary implementation.** Status:
   DISMISSED-FINITE.  It uses the independent R-372 helper, `solve` rather
   than `inv`, and has a distinct source hash.
10. **A finite operator result could silently advance Q3 or Pre-A.** Status:
    DISMISSED-FIREWALL.  All locality, common-core, common-alpha, KMS/GNS,
    gap, continuum, C6, Sector-A and Pre-A flags remain false.

## Next gate

Prove a source-, volume- and cutoff-uniform energy-constrained estimate for
the isolated square-root/local-commutator term, then sum the resolvent layers
on the common polynomial core.  The common real-time `alpha`, KMS
identification and all continuum/physical-sector obligations remain open.
