# R-411 certificate - sublinear spectral-counting exponent envelope

## Scope

R-411 is a T0, claim-nonbearing finite checkpoint under EXP-001256.  For
the normalized graph operator
`W = D_pi^(-1/2) L D_pi^(-1/2)`, order the positive eigenvalues as
`lambda_1 <= ... <= lambda_m`, where `m = d - 1`.  For each declared
`0 < alpha < 1`, set

```
C_alpha = max_(1 <= k <= m) k/lambda_k^alpha.
```

Then `lambda_k >= (k/C_alpha)^(1/alpha)` and the finite-dimensional trace
obeys

```
tr(W^+) <= C_alpha^(1/alpha) sum_(k=1)^m k^(-1/alpha).
```

Writing `s = 1/alpha > 1`, the infinite comparison uses only the explicit
integral tail
`m^(1-s)/(s-1)`.  This widens the finite diagnostic beyond the fixed
quadratic choice `alpha = 1/2`; it does not assert that any exponent or
constant is regulator-independent.

## Verification

The volume-two fixture uses dimensions `3,4,5,6,8,10,12`, beta in
`{1/2,1,2}`, both source signs, both history signs, both split orders, all
prefixes, both history adjoints and both collar orientations.  The primary
lane passes `508279/508279` assertions over `7` systems, `2688` contexts and
`21120` conditional rows.  The independent reconstruction passes the same
`508279/508279`; the hostile lane passes `8/8`, the integrated verifier
passes `48/48`, and Lean R411 compiles.

The retained quadratic cross-check has mode constant range
`[0.19600096779786974,1.2046269661757882]` and inverse-spectrum trace range
`[0.44413751605172147,2.0052069566897663]`.  The corresponding finite
quadratic envelope is in `[1.2140470537996502,7.467366756170776]`.
For the new exponent grid, all rows satisfy the declared finite and
infinite comparisons for `alpha` in
`{1/2,2/3,3/4,4/5,9/10}`.  The rowwise counting constants and bounds are
stored in the primary and independent JSON artefacts under `alpha_profiles`;
the largest absolute envelope residual is at floating-point roundoff
(`7.105427357601002e-15` or below).

## Adversarial review

1. **Domain of the exponent.**  The hostile lane calls the helper with
   `alpha = 1`; it is rejected because the reciprocal exponent is not
   strictly greater than one and the integral-tail route is unavailable.
2. **Eigenvalue ordering.**  Reversing a toy spectrum changes both the
   quadratic and `alpha = 9/10` constants; mode indices are assigned only
   after ascending spectral sort.
3. **Power convention.**  A toy mutation that multiplies by
   `lambda_k^alpha` instead of dividing by it gives a different constant and
   is rejected.
4. **Quadratic/linear confusion.**  A linear `k` constant inserted into the
   retained quadratic envelope gives a negative toy residual and is rejected.
5. **Fiedler-only truncation.**  The first positive inverse eigenvalue is
   strictly below the full inverse-spectrum trace on both selected rows.
6. **Zero mode and connectivity.**  Exactly `d-1` positive modes above the
   declared floor are required; a diagonal-generator mutation has no graph
   edges and no positive spectrum.
7. **Finite versus infinite tail.**  The finite sum is checked before the
   integral comparison; the infinite bound is never substituted as a finite
   equality.
8. **Independent reconstruction.**  A non-importing lane rebuilds the
   oscillator, Gibbs states, histories, conditional graph and exponent
   profiles and agrees with the primary lane within the declared tolerance.
9. **Uniform promotion.**  Finite positivity of several `C_alpha` values does
   not establish a common exponent or constant under cutoff, volume, phase or
   exhaustion, nor a common core, GNS coercivity, physical gap, continuum,
   C6, Sector-A or Pre-A closure.

## Decision and next gate

R-411 advances a broader analytic target: establish one exponent
`0 < alpha < 1` and a positive uniform lower bound for its inverse counting
constant on a Hamiltonian common core.  The estimate must be controlled under
cutoff, volume, source, phase and exhaustion changes, transferred to the
R-399 conditional shell, and combined with the R-406 Schur residual split.
If every exponent loses control in a validated stress, retain this finite
comparison and register the obstruction rather than promoting it.

## Boundary

No cutoff-independent, volume-independent, phase-uniform or exhaustion-
uniform result is claimed.  No common-core/common-alpha estimate,
Hamiltonian-to-OS/KMS/GNS identification, physical mass gap, continuum, C6,
Sector-A or Pre-A closure follows.  No tier change or negative result is
issued.  The manifest, certificate, scope note, four executable lanes, Lean
entrypoint and saved run artefacts are the complete finite record.
