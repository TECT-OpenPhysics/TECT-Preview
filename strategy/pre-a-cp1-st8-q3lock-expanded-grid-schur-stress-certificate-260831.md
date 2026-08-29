# R-425 -- Expanded finite Q3 harmonic coarse-Schur stress

## Decision

R-425 / EXP-001270 is a T0, claim-nonbearing finite stress result.  It keeps
the R-424 functional, conditional Gibbs law, projected conductance, beta
grid, two orientations, `alpha=1/40`, tail threshold `theta=4` and
`sqrt(pi)` split fixed.  Only the declared finite `(volume, cutoff)` sample
is enlarged to the complete R-419 grid.  No regulator, boundary, source,
state, or limit input is changed or tuned per row.

For every row with at least two core and two tail coordinates, the transformed
graph is split into the two block-constant modes and their orthogonal
complement.  The residual complement is eliminated by the exact finite
Schur solve

```text
S = A_UU - A_UV A_VV^(-1) A_VU,
```

and the reported finite envelope is `0.5*min(coarse Schur gap,residual gap)`.
Rows without the required support are retained as an explicit eligibility
boundary rather than discarded from the coverage count.

## Fixed finite scope

The twelve systems are `(V,d)=(2,3),(2,4),(2,5),(2,6),(2,8),(2,10),
(2,12),(3,3),(3,4),(3,5),(3,6),(4,4)`.  The beta values are
`{1/2,2,8}` and both `right` and `left` histories are evaluated.  The
probability floor is `1e-300`, the comparison tolerance is `5e-7`, and the
gap floor is `1e-8`.

## Executed evidence

The primary lane passes `4678/4678` assertions over `1488` conditional rows,
`710` rows with a nonempty tail, and `326` eligible two-block rows.  All 326
eligible rows assemble successfully.  The coarse Schur gaps range from
`9.416287072814253` to `900.9775546526778`; residual gaps range from
`2.0277567083122383` to `7.874609499214968`; and the conservative combined
envelopes range from `1.0138783541561192` to `3.937304749607484`.  The maximum
independent residual reuse difference is `9.393117395006811e-10`, and the
minimum harmonic lower-margin probe is `0.15688515408073822`.

The non-importing reversible-fixture lane passes `27/27` assertions with
combined range `[0.35836604885331824,0.6590144479144613]` and maximum energy
split error `8.326672684688674e-17`.  The hostile lane rejects `7/7`
mutations, the integrated verifier passes `15/15`, and the scalar Lean R425
cross-check compiles.

## Adversarial review

1. **Input and normalization.**  Nonpositive, nonfinite or non-normalized
   weights and asymmetric/negative conductances are rejected; disposition:
   DISMISSED-FINITE.
2. **Support eligibility.**  Overlapping and undersized blocks are rejected.
   The zero-eligible d=3 systems and the d=4 volume-two boundary remain in
   the report; disposition: DISMISSED-FINITE / boundary retained.
3. **Schur direction.**  The coupling correction is subtracted, and the
   hostile lane rejects a forged envelope above the half-minimum; disposition:
   DISMISSED-FINITE.
4. **Residual reuse.**  A separately constructed block-mean-zero basis agrees
   with the harmonic residual block within `5e-7`; disposition:
   DISMISSED-FINITE.
5. **Singular graph.**  A disconnected mutation is rejected before a Schur
   value can be reported; disposition: DISMISSED-FINITE.
6. **Finite-to-uniform promotion.**  Positive values on twelve finite systems
   do not prove a uniform estimate, a common core, or a limit; disposition:
   UPHELD-OPEN.
7. **Physical promotion.**  The result does not identify a physical sector,
   empty reference, OS/KMS/GNS state, Yang--Mills theory, or mass gap;
   disposition: UPHELD-OPEN.

## Boundary and next action

R-425 advances the finite calibration envelope and exposes the support
eligibility boundary under a larger cutoff-volume sample.  It does not close
the Q3LOCK common-alpha, broken-sector coercivity, history-transfer,
OS/KMS/GNS, C6, Sector-A or Pre-A gates.  The next unlock is an analytic
common-core estimate whose constants survive cutoff, volume, phase and
exhaustion, followed by the declared history and state-identification
interfaces.

## Assumptions and missing assumptions

Assumptions used:

- hash-pinned R-419 positive normalized conditional laws and symmetric
  nonnegative projected conductances;
- exact reuse of the R-422 split and fixed beta/orientation/alpha/theta grid;
- disjoint finite core and tail blocks and a positive residual block on every
  admitted row;
- declared numerical tolerances are comparison thresholds only and lower
  bounds are never rounded upward.

Missing for promotion:

- a cutoff-, volume-, phase- and exhaustion-uniform coarse/residual estimate on
  one Hamiltonian common core;
- a common split-limit map and two-sided form control for R-399 histories;
- transfer through R-415 and Hamiltonian-to-OS/KMS/GNS identification;
- a physical-sector projection and a sectorwise coercive theorem.

Evidence level: `T0 / exact finite harmonic coarse-Schur decomposition on the
expanded R-419 sample`.  No regulator-independent or physical conclusion is
claimed.
