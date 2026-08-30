# R-433 -- Validated original-source interval enclosure

## Decision

`R-433 / EXP-001278` is a T0, claim-nonbearing finite certificate for the
original oscillator source at the corrected conditional-row contract.  The
source is fixed to volume `2`, cutoff dimension `16`, `beta=8`, right
orientation, emission ordinal `7` (parent coordinate `6`), and the declared
core/tail split `7/9`.  The exact R-419 rational fixture is assembled with
real algebraic square roots.  Exchange and global Fock-parity symmetry split
the 256-dimensional Hamiltonian into blocks of dimensions `72, 56, 64, 64`.

The primary directed enclosure passes `40/40` checks.  Its key bounds are:

```text
Hamiltonian residual upper bound       5.0830027088533099603e-41
Hamiltonian Gram-defect upper bound    5.2743084774109142435e-42
coordinate residual upper bound        1.1450394871514047264e-43
coordinate Gram-defect upper bound     1.3067789239324602381e-43
corrected row minimum                  5.6229486461864869825e-13
residual interval matrix width         6.985088320724423794e-10
certified Rayleigh interval            [5.3631875357869327503,
                                        5.3631875357869329910]
certified bracket width                3.5786932990972513712e-8
margin above R-422 reference           2.532836301e-6
margin below R-426 direct reference    8.1426087700902748626e-7
```

The finite residual-basis interval dependency is explicitly bounded by the
contract threshold `1e-8`; the observed width is below that threshold.  The
independent non-importing NumPy reconstruction passes `12/12` and obtains the
finite control value `5.36318775241371`.  This double-precision value is a
control, not an enclosure.  The hostile lane rejects all `7/7` mutations,
including the parent/ordinal swap, fixture change, width/probe relaxation,
symmetry removal and physical promotion.  The integrated verifier passes
`13/13`; Lean R433 compiles without `sorry`, `admit`, `axiom` or `unsafe`.

The classification is `ORIGINAL_SOURCE_INTERVAL_CERTIFIED`.  It records a
validated finite original-source interval and two fixed-reference separations
only.  It does not close residual reuse uniformly and does not change any
claim tier.

## Exact scope and assumptions

- One finite source: `V=2`, `d=16`, `beta=8`, right orientation.
- One corrected row: emission ordinal `7`, parent coordinate `6`, with the
  R-432 ordinal convention.
- One fixed tail threshold `4`, core `{4,5,6,7,8,9,10}`, tail
  `{0,1,2,3,11,12,13,14,15}`.
- One source Hamiltonian assembled from the R-419 fixture
  (`chi=1`, `r=-1`, `g=3/5`, `c=3/5`, `lambda=1/10`).
- Directed source intervals, high-precision block eigendata, residual/Gram
  bounds, Gibbs-kernel propagation, conditional-row normalization, projected
  momentum, and the same fixed residual compression are all part of the
  finite run.
- The polar correction is used only in its small-defect regime.  The Gibbs
  shift is below the enclosed ground energy, so the finite exponential kernel
  is bounded on the shifted cone.

The original source is rebuilt rather than read from R-431's rounded graph
snapshot.  The large 256-column tables use midpoint/radius norm propagation;
the final spectral probes are directed interval Cholesky and interval
Rayleigh checks on the resulting symmetric enclosure.

## Missing assumptions and next unlock

- A cutoff-, volume-, phase- and exhaustion-uniform source enclosure.
- A common unbounded Q3 core and a residual or Schur estimate beyond this one
  finite source.
- History transfer, OS/KMS/GNS reconstruction, physical-sector admission and
  continuum control.
- A same-owner normalized physical-empty branch `E` and the full Reading-H
  functional needed for the three physical-empty tests.

The next finite unlock is an independently sourced larger-cutoff or larger-
volume interval enclosure with a declared tail modulus.  The next physical
unlock is separate: supply one owner-approved common `F_total` parent and an
admitted normalized `E` before evaluating any sign, stationarity or Hessian.

## Adversarial review

1. **Source rounding and eigensolver residual.**  The source expressions are
   enclosed with directed intervals; rounded eigendata carry an explicit
   decimal-radius enclosure, residual and Gram bounds, and a polar correction.
   Disposition: **DISMISSED-FINITE / OPEN-UNIFORM**.
2. **Interval dependency and conditioning.**  The residual-basis interval
   dependency widens the compressed matrix to `6.985...e-10`, not `1e-35`.
   The widened `1e-8` threshold is preregistered, observed below threshold,
   and the two-sided probes still have margins above `8e-7`.  Disposition:
   **DISMISSED-FINITE / CONDITIONING-BOUND RECORDED**.
3. **Reference and row selection.**  R-432 fixes emission ordinal `7` to
   parent `6`; the primary, independent and hostile lanes test this identity.
   Both fixed-reference separations are checked only for this row.  Disposition:
   **DISMISSED-FINITE / OPEN-REUSE**.
4. **Independent implementation.**  The NumPy lane reconstructs the source
   without importing the primary module and agrees within the declared finite
   control tolerance, but it is not an interval proof.  Disposition:
   **DISMISSED-CONTROL / OPEN-ROUNDING**.
5. **Finite-to-physical promotion.**  No common core, limit order, physical
   sector, normalized empty branch or Reading-H full tangent is supplied.
   Disposition: **UPHELD-OPEN**.

## Boundary

R-433 validates one finite original-source residual interval and its corrected
row propagation.  `residual_reuse_closed_for_original_source` remains false.
The result is not a uniform theorem, a physical-vacuum comparison, a
Yang--Mills result, a mass-gap result, a C6/sector-A closure, or a Pre-A
closure.

Evidence level: `T0 / EXECUTED VALIDATED FINITE ORIGINAL-SOURCE INTERVAL
ENCLOSURE; NO UNIFORM OR PHYSICAL PROMOTION`.
