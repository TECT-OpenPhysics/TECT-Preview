# R-432 Fixed Conditional-Row Ordinal Audit

## 1. Decision

R-432 is a T0, claim-nonbearing finite bookkeeping correction under
EXP-001277. The declared R-426 target is emission ordinal 7 in the actual
`conditional_rows` order. That order emits one radius-0 unconditional row at
ordinal 0 and then radius-1 rows by parent coordinate, so ordinal 7 is the
row conditioned on parent coordinate 6. The historical R-430 independent
lane used `target_index - 1`, and therefore evaluated ordinal 6, a different
finite row.

The corrected row reproduces the immutable R-426 direct residual gap and its
R-422 mismatch. The historical value is retained only as an ordinal-6
diagnostic; it is not source-precision evidence about target ordinal 7.

## 2. Exact scope

- Model: the finite R-419/R-416/R-402 oscillator/Hamiltonian construction.
- Volume and cutoff: `V=2`, `d=16`.
- Inverse temperature and orientation: `beta=8`, right.
- Emission target: ordinal `7`, parent coordinate `6`.
- Tail threshold and split: the immutable R-426 threshold, with core/tail
  sizes `7/9`.
- Comparison tolerance: `5e-7`, unchanged.
- Observable: the finite projected residual eigenvalue used by R-426.

No claim tier, physical interpretation, or Yang--Mills statement changes.

## 3. Executed evidence

The primary lane passes `13/13` assertions. It reconstructs the explicit
emission order and the canonical generator order, obtains the target gap
`5.36318835004781`, and reproduces the R-426 direct reference. The R-422
mismatch is `3.382884111502449e-06`, above `5e-7`. Ordinal 6 gives a distinct
finite gap near `6.094733955638`, matching the historical R-430 independent
lane within the declared finite tolerance.

The non-importing independent lane passes `10/10` with the same target and
historical-row diagnosis. The hostile lane rejects `7/7` mutations, including
ordinal substitution, parent remapping, tolerance relaxation, claim/status
promotion, source-interval promotion, and removal of the unconditional row.
The integrated verifier passes `15/15`, and Lean R432 compiles without
`sorry`, `admit`, `axiom`, or `unsafe`.

Run artifacts:

- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-fixed_row_ordinal_audit/primary.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-fixed_row_ordinal_audit/independent.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-fixed_row_ordinal_audit/hostile.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-fixed_row_ordinal_audit/integrated.json`
- `verification/lean/Tect/R432.lean`

## 4. Assumptions and missing assumptions

The finite source formulas, emission order, tail split, and fixed comparison
tolerance are taken from the hash-pinned parent authorities. The direct gap
is a reproducible finite matrix calculation.

Still missing are validated interval or ball enclosures for the original
coordinate and Hamiltonian eigensystems, propagated Gibbs-row and conductance
enclosures, a basis-independent original-source residual comparison, a
cutoff/volume/phase/exhaustion-uniform common-core estimate, and history or
OS/KMS/GNS transfer.

## 5. Adversarial boundary and non-claims

The audit prevents an ordinal bookkeeping error from being presented as
source precision sensitivity. It does not repair the R-426 residual-reuse
route for the unrounded source, and it does not prove a uniform gap, physical
sector, continuum limit, C6, Sector-A, Pre-A, Yang--Mills result, or mass gap.

The next unlock is a validated original-source eigensystem enclosure using
ordinal 7 with no index conversion.
