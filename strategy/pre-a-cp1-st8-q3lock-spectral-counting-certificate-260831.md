# R-410 certificate - quadratic mode-counting envelope

## Scope

R-410 is a T0, claim-nonbearing finite checkpoint under EXP-001255.  It
starts from the R-409 identity and orders the positive eigenvalues of
`W=D_pi^(-1/2)L D_pi^(-1/2)` as
`lambda_1 <= ... <= lambda_(d-1)`.  Define

```
c2 = min_(1 <= k <= d-1) lambda_k/k^2.
```

Every finite row then satisfies `lambda_k >= c2*k^2`, so

```
tr(W^+) = sum_(k=1)^(d-1) 1/lambda_k
        <= H_(d-1)^(2)/c2
        <= pi^2/(6*c2).
```

The point is to replace a Fiedler-only target by a full low-mode counting
condition.  The implication is finite-dimensional; the value of `c2` still
has to be bounded uniformly in the regulator and thermodynamic limits.

## Verification

The volume-two fixture uses dimensions `3,4,5,6,8,10,12`, beta in
`{1/2,1,2}`, both source signs, both history signs, both split orders, all
prefixes, both history adjoints and both collar orientations.  The primary
lane passes `191473/191473` assertions over `7` systems, `2688` contexts and
`21120` conditional rows.  The independent reconstruction passes the same
`191473/191473`; the hostile lane passes `6/6`, the integrated verifier
passes `46/46`, and Lean R410 compiles.

Across all rows, the mode constant ranges over
`[0.19600096779786974,1.2046269661757882]`.  The exact inverse-spectrum trace
ranges over `[0.44413751605172147,2.0052069566897663]`; the finite harmonic
square envelope ranges over `[1.2140470537996502,7.467366756170776]`, while
the infinite zeta comparison ranges over
`[1.3655132360769229,8.392479309309332]`.  The largest mode-envelope
residual is `3.552713678800501e-15`.

## Adversarial review

1. **Eigenvalue ordering.**  A reversed toy spectrum changes `c2` from
   `1/3` to `1/9`; the hostile lane rejects assigning mode indices by input
   order.
2. **Quadratic scaling.**  A linear `lambda_k >= c*k` constant inserted into
   a `k^2` bound gives a toy residual `-6`; this shortcut is rejected.
3. **Fiedler-only truncation.**  `1/lambda_1` is strictly below the full
   inverse-spectrum trace on both selected dimensions.
4. **Zero mode and connectivity.**  Exactly `d-1` positive modes above the
   declared floor are required; the diagonal-generator mutation has zero
   edges and zero positive spectrum.
5. **Finite zeta factor.**  The row-wise harmonic-square bound is checked
   before the looser `pi^2/6` comparison; no infinite-series value is used as
   a finite equality.
6. **Independent reconstruction.**  The non-importing lane agrees on every
   aggregate/profile field within the declared cross-check tolerance.
7. **Uniform promotion.**  Finite positivity of `c2` does not establish a
   cutoff-, volume-, phase- or exhaustion-uniform estimate, a common core,
   GNS coercivity, a physical mass gap, continuum, C6, Sector-A or Pre-A.

## Decision and next gate

R-410 advances a concrete analytic target: prove a positive lower bound for
the ordered mode-counting constant, or equivalently a Nash/Weyl-type bound on
the integrated Green trace, on one Hamiltonian common core.  That estimate
must be transferred to the R-399 conditional shell and combined with the
R-406 Schur residual split.  If `c2` collapses in a validated cutoff or
volume stress, retain this finite envelope and register the obstruction
instead of promoting it.

## Boundary

No cutoff-independent, volume-independent, phase-uniform or exhaustion-
uniform result is claimed.  No common-core/common-alpha estimate,
Hamiltonian-to-OS/KMS/GNS identification, physical mass gap, continuum, C6,
Sector-A or Pre-A closure follows.  No tier change, negative result or PDF is
issued.

The manifest, certificate, scope note, primary/independent/hostile scripts,
integrated verifier, Lean entrypoint and saved run artefacts are the complete
finite record.
