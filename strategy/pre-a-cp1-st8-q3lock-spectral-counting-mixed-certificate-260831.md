# R-412 certificate - mixed IR/UV spectral-counting envelope

## Scope

R-412 is a T0, claim-nonbearing finite checkpoint under EXP-001257.  Let
`lambda_1 <= ... <= lambda_m` be the positive spectrum of
`W = D_pi^(-1/2) L D_pi^(-1/2)`, with `m=d-1`.  For every interior split
`1 <= r < m` and every pair `0 < alpha_IR, alpha_UV < 1`, define

```
C_IR = max_(k<=r) k/lambda_k^alpha_IR,
C_UV = max_(k>r) k/lambda_k^alpha_UV.
```

The two pieces obey

```
tr(W^+) <= C_IR^(1/alpha_IR) sum_(k=1)^r k^(-1/alpha_IR)
          + C_UV^(1/alpha_UV) sum_(k=r+1)^m k^(-1/alpha_UV).
```

Only the UV piece receives an infinite comparison, using the explicit
integral tail after `m`.  The row-wise best pair and split are diagnostics;
they are not a common split rule.

## Verification

The volume-two fixture uses dimensions `3,4,5,6,8,10,12`, beta in
`{1/2,1,2}`, both source signs, both history signs, both split orders, all
prefixes, both history adjoints and both collar orientations.  The primary
lane passes `592762/592762` assertions over `7` systems, `2688` contexts and
`21120` conditional rows.  The independent reconstruction passes the same
`592762/592762`; the hostile lane passes `9/9`, the integrated verifier
passes `55/55`, and Lean R412 compiles.

Every row enumerates all `25` exponent pairs and all admissible interior
splits.  The selected finite mixed envelope ranges over
`[0.5800949275086398,2.117318722273093]`, while the selected infinite
comparison ranges over `[0.6295715327320223,3.1299469867610137]`.  The
smallest selected trace slack is `-6.661338147750939e-16`, consistent with
floating-point roundoff, and the smallest selected UV-tail slack is
`0.0005947926662857039`.

## Adversarial review

1. **Exponent domain.**  The hostile lane supplies `alpha=1`; the helper
   rejects it because the reciprocal exponent is not greater than one.
2. **Eigenvalue ordering.**  Reversing a toy spectrum changes both quadratic
   and mixed envelope values; mode indices are assigned only after sorting.
3. **Power convention.**  Replacing division by `lambda^alpha` with
   multiplication changes the counting constant and fails the hostile check.
4. **Split membership.**  Moving the split boundary changes which modes pay
   the IR and UV constants; the hostile lane rejects a silent off-by-one.
5. **Quadratic/linear confusion.**  A linear `k` shortcut inserted into the
   retained quadratic envelope gives a negative toy residual.
6. **Fiedler-only truncation.**  The first positive inverse eigenvalue is
   strictly below the full inverse-spectrum trace on both selected rows.
7. **Zero mode and connectivity.**  Exactly `d-1` positive modes above the
   declared floor are required; a diagonal-generator mutation has no graph
   edges or positive spectrum.
8. **Finite versus infinite tail.**  The finite head and tail sums are
   checked before the UV integral comparison; the infinite bound is not used
   as a finite equality.
9. **Independent reconstruction.**  The non-importing lane rebuilds the
   finite model and agrees on the invariant aggregate fields within `5e-6`;
   row-wise optimizer histograms are intentionally not promoted because
   roundoff can swap tied minimizers.
10. **Uniform promotion.**  A row-wise best pair does not establish a fixed
    split rule or uniform constants under cutoff, volume, phase or exhaustion,
    nor a common core, GNS coercivity, physical gap, continuum, C6, Sector-A
    or Pre-A closure.

## Decision and next gate

R-412 advances a two-regime analytic target: prove a controlled split rule and
uniform IR and UV counting constants on one Hamiltonian common core.  The
result must be stable under cutoff, volume, source, phase and exhaustion
changes, transferred to the R-399 conditional shell, and combined with the
R-406 Schur residual split.  If no split survives validated stress, retain
the finite envelope and register the route-specific obstruction.

## Boundary

No cutoff-independent, volume-independent, phase-uniform or exhaustion-
uniform result is claimed.  No common-core/common-split estimate,
Hamiltonian-to-OS/KMS/GNS identification, physical mass gap, continuum, C6,
Sector-A or Pre-A closure follows.  No tier change or negative result is
issued.  The manifest, certificate, scope note, four executable lanes, Lean
entrypoint and saved run artefacts are the complete finite record.
