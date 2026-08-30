# R-435 -- V=2, d=17 original-source interval enclosure

`R-435 / EXP-001280` is a T0, claim-nonbearing finite continuation of the
R-433 source-interval route.  It keeps the R-419 rational oscillator fixture,
uses the same directed `mpmath.iv` source and Gibbs propagation primitives,
and increases the cutoff from 16 to 17.  The row is fixed before interval
evaluation as the beta-8, right-orientation unconditional one-site marginal
(emission ordinal zero).

## Exact finite scope

- volume `V=2`, cutoff dimension `d=17`, Hamiltonian dimension `289`;
- beta `8`, right orientation, unconditional one-site Gibbs marginal;
- tail threshold `4`, core indices `4..12`, tail indices
  `0..3,13..16`;
- source assembly from the hash-pinned R-419 rational fixture;
- exchange/global-parity blocks `[81,64,72,72]`;
- 50-point-digit eigendata, 45-digit interval endpoints and 80-digit interval
  arithmetic;
- fixed probes `4.2 < gap < 4.25`, rejection probe `4.3`, matrix-width budget
  `1e-6`, and bracket-width budget `0.1`.

The row selection is not made from the computed gap: the manifest fixes ordinal
zero and the beta/orientation order in advance.  The primary interval lane
passes `57/57`.  Its residual Rayleigh enclosure is

`[4.22153907112994631455003390284897397097200231,
4.22153907112994631578208377835242264266111368]`.

The maximum residual-matrix interval width is
`7.0922943110070923178721818130516e-13`, below `1e-6`; the bracket lies inside
the fixed probes.  Hamiltonian residual and Gram upper bounds are
`6.5554215021810497917e-41` and `6.2013656081312960463e-42`.  The independent
non-importing NumPy control passes `12/12` with gap `4.221539067848923`, and
the hostile lane rejects `8/8` mutations.  The integrated verifier passes
`15/15`; Lean `R435.lean` compiles.

## Assumptions

1. The R-419 rational fixture is unchanged and is the exact finite source at
   `V=2,d=17`.
2. Exchange and global Fock-parity commute with the finite Hamiltonian, so the
   four declared blocks preserve its spectrum.
3. The R-433 polar-correction and Gibbs perturbation inequalities remain valid
   after the d=17 residual and Gram checks.
4. The unconditional row is the normalized one-site marginal of the finite
   Gibbs diagonal and uses the fixed threshold four.
5. The Cholesky and Rayleigh checks act on one symmetric compressed interval.

## Devil's-advocate review

- **Dimension/row mismatch:** the d=17 block count and unconditional row
  cardinalities are checked independently and in Lean; the mutation lane
  rejects a d=16 substitution.  DISMISSED-FINITE.
- **Normalization or tail-boundary failure:** directed intervals contain unit
  mass and separate every declared core/tail entry from threshold four.
  DISMISSED-FINITE.
- **Numerical cancellation/conditioning:** the same interval enclosure is
  used for Cholesky and Rayleigh tests, with an explicit matrix-width and
  bracket budget; the independent lane is only a control.  DISMISSED-FINITE,
  OPEN-UNIFORM.
- **Post-selection of a favorable row:** ordinal zero, beta eight and right
  orientation are fixed in the manifest before the interval run.  The result
  does not claim an all-row or optimal-row theorem.  DISMISSED-PROTOCOL.
- **Physical promotion:** no common Q3 core, limit, physical reference,
  Reading-H tangent or Yang--Mills map is supplied.  UPHELD-OPEN.

## Decision and boundary

Advance only the finite source datapoint as `ORIGINAL_SOURCE_INTERVAL_CERTIFIED`
at T0.  This does not close residual reuse, cutoff/volume/phase/exhaustion
uniformity, a common core, history transfer, OS/KMS/GNS reconstruction, a
physical sector, or a continuum limit.  It provides no physical-empty energy
sign, Reading-H stationarity or symmetry-projected transverse-stability
result, and makes no C6, Sector-A, Pre-A, Yang--Mills or mass-gap claim.

Next gate: repeat the interval construction at another independently fixed
larger volume/cutoff with a predeclared row rule and an owner-approved tail
modulus; otherwise retain the finite evidence as a bounded calibration only.
