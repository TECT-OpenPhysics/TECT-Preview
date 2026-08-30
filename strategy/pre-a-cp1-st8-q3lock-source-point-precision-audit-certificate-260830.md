# R-430 -- Original-source point-precision audit

## Decision

`R-430 / EXP-001275` is a T0, claim-nonbearing source-point audit for the
fixed R-426 row.  It retains volume `2`, cutoff dimension `16`, `beta=8`,
right orientation, conditional row `7`, core/tail `7/9`, and the immutable
comparison tolerance `5e-7`.  The oscillator, coordinate basis, volume-two
Hamiltonian, Gibbs coordinate masses, projected conductance and residual
compression are rebuilt from the original R-419/R-416/R-402 rational fixture
using 50-digit `mpmath` arithmetic, rather than the R-428 graph snapshot.

The primary point calculation gives

```text
source residual gap       5.36318753578552619873719734720155508375451072...
R-422 reference           5.363184967163699
R-422 mismatch             0.000002568621827198737197347201555...
R-426 direct reference    5.36318835004781
direct mismatch            0.000000814262283801262802652798...
fixed comparison tolerance 0.0000005
```

Both point mismatches exceed the fixed tolerance, but this is not an interval
statement.  The independent NumPy reconstruction obtains a different finite
point gap (`6.094733971033106`), with a recorded source-point discrepancy of
`0.73154643524758` from the mpmath value.  This sensitivity is evidence that
an enclosure and conditioning analysis are still required; it is not a
reason to promote either point value.

The classification is `SOURCE_POINT_AUDIT_NO_INTERVAL`.  R-426's route-local
residual-reuse failure is preserved and no claim tier changes.

## Executed evidence

The primary mpmath lane passes `14/14` assertions, including positive row
normalization, graph reversibility at `2.7e-51`, a `16x14` residual basis and
the two fixed-reference separations.  The independent non-importing NumPy
source lane passes `9/9`; it records the source-point sensitivity above while
also finding a positive gap and a mismatch above `5e-7`.  The hostile lane
passes `10/10`, rejecting precision, row, tolerance, interval, exact-input,
residual-reuse and uniform-promotion mutations.  The integrated verifier
passes `13/13` with Lean R430 compiling successfully.

Lean checks only scalar rational consequences: both declared mismatch lower
bounds exceed `5e-7`, the 50-digit point precision and finite row parameters
are positive, and the file has no `sorry`, `admit`, `axiom` or `unsafe`.
Eigenvalue and source reconstruction remain executable Python, not Lean
certificates.

## Assumptions

- The original R-419/R-416/R-402 oscillator and Hamiltonian formulas are the
  declared finite source model.
- Fifty-digit `mpmath.eigsy` and log-sum-exp arithmetic provide a converged
  point estimate for this finite calculation.
- The row orientation, index, tail threshold, block split and comparison
  tolerance are unchanged.
- The blockwise weighted-zero-mean basis spans the intended finite residual
  subspace for the computed positive row.

## Missing assumptions

- Interval or ball-arithmetic enclosures for the coordinate and Hamiltonian
  eigensystems.
- Propagation of those enclosures through Gibbs normalization, the conditional
  row, conductance and residual eigenvalue.
- A basis-independent certified comparison for the original unrounded source.
- A common unbounded Q3 core, regulator/volume-uniform estimate, history
  transfer, OS/KMS/GNS reconstruction and physical-sector map.

## Adversarial review

1. **Upstream rounding and conditioning.**  The independent source-point gap
   differs from the mpmath point by `0.7315...`; no input enclosure exists.
   Disposition: **UPHELD-OPEN**.
2. **Reference separation.**  The mpmath point exceeds both fixed-reference
   tolerances, while the independent point also remains separated from the
   R-422 value.  This is a finite diagnostic only.  Disposition:
   **DISMISSED-FINITE / OPEN-CERTIFICATION**.
3. **Precision or tolerance manipulation.**  Hostile controls reject a
   reduced precision, changed row or changed comparison tolerance.
   Disposition: **DISMISSED-FINITE**.
4. **Point-to-interval promotion.**  Hostile controls reject forged interval,
   exact-input and residual-reuse closure fields.  Disposition:
   **UPHELD-OPEN**.
5. **Finite-to-physical promotion.**  The single volume-two row has no
   uniform, common-core, OS/KMS/GNS or physical-sector transfer.
   Disposition: **UPHELD-OPEN**.

## Boundary and next action

R-430 tests the upstream source precision boundary at one finite row.  It does
not certify the original unrounded model, repair R-426, close Q3LOCK or C6,
or establish a continuum, Yang--Mills or mass-gap result.  The next unlock is
an interval or ball-arithmetic reconstruction with propagated enclosures at
the same row and tolerance, followed by a decision on whether the certified
interval still misses the R-422 reference.

Evidence level: `T0 / executed 50-digit mpmath source-point audit with an
independent double-source sensitivity control; no interval certification`.

No Yang--Mills, mass-gap, physical-vacuum, Sector-A or Pre-A conclusion is
claimed.
