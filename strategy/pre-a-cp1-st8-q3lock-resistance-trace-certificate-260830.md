# R-409 certificate - resistance average as normalized Green trace

## Scope

R-409 is a T0, claim-nonbearing finite checkpoint under EXP-001254.  It
sharpens R-408 by identifying its tree-independent constant with a spectral
trace.  For a conditional law `pi`, `D=diag(pi)`, symmetric conductance
Laplacian `L`, and

```
W = D^(-1/2) L D^(-1/2),    u = sqrt(pi)
v_xy = D^(-1/2)(e_x-e_y),
```

the unordered pair vectors satisfy
`sum_(x<y) pi_x*pi_y*v_xy*v_xy^T = I-u*u^T`.  Since `u` is the sole null
direction of connected `W`,

```
Rbar_pi = sum_(x<y) pi_x*pi_y*R_xy
        = tr(W^+)
        = sum_(k=1)^(d-1) 1/lambda_k(W).
```

For a finite connected spectrum the final sum is also the termwise integral
`int_0^infinity (tr(exp(-tW))-1) dt`.  The identity turns the future
uniformity question into an integrated Green/heat-trace estimate rather than
an arbitrary tree load or one Fiedler eigenvalue.

## Verification

The volume-two fixture uses oscillator dimensions `3,4,5,6,8,10,12`, beta in
`{1/2,1,2}`, both source signs, both history signs, both split orders, all
prefixes, both history adjoints and both collar orientations.  The primary
lane passes `106990/106990` assertions over `7` systems, `2688` contexts and
`21120` conditional rows.  The independently reconstructed lane passes
`106990/106990` with aggregate and per-cutoff fields agreeing within `5e-6`;
the hostile lane passes `6/6`; the integrated verifier passes `37/37`; and
Lean R409 compiles.

Across all rows, the resistance average and normalized pseudoinverse trace
both range over `[0.44413751605180657,2.0052069566897672]`.  The largest pair
resistance is `85.99011817086347`, the smallest positive normalized
eigenvalue is `0.7570174175402339`, and the maximum direct pair-to-trace
residual is `2.537969834293108e-12`; transformed-pair and projector residuals
are at most `6.661338147750939e-16` and `4.440892098500626e-16` respectively.

## Adversarial review

1. **Pair normalization.**  A directed sum is exactly twice the unordered
   pair sum and is rejected on both selected dimensions.
2. **Normalization by `D`.**  The trace of the unnormalized Laplacian inverse
   differs materially from the normalized trace; the hostile lane rejects that
   substitution.
3. **One-mode shortcut.**  Keeping only `1/lambda_1(W)` underestimates the
   full inverse-spectrum trace on both selected dimensions; no Fiedler-only
   identity is accepted.
4. **Pseudoinverse zero mode.**  Exactly `d-1` eigenvalues must exceed the
   declared numerical zero threshold; a disconnected diagonal-q mutation has
   zero edges and zero positive spectrum.
5. **Independent reconstruction.**  The second lane rebuilds the finite
   oscillator, Gibbs states, histories, conditional graphs and both Laplacian
   traces without importing the R-409 primary module.
6. **Uniform promotion.**  Finite trace equality does not prove a
   cutoff-, volume-, phase- or exhaustion-uniform Green estimate, a common
   core, GNS gap, continuum, C6, Sector-A or Pre-A closure.

## Decision and next gate

R-409 advances an exact finite Green/heat-trace interface.  The next analytic
gate is an upper bound on `tr(W^+)`, or equivalently on the integrated heat
trace, uniform in cutoff, volume, phase and exhaustion on one Hamiltonian
common core.  That bound must then be transferred to the R-399 conditional
shell and combined with the R-406 Schur residual split.  If the trace diverges
or the positive spectrum collapses under a validated stress, retain this
identity and register the obstruction rather than promoting it.

## Boundary

No cutoff-independent, volume-independent, phase-uniform or exhaustion-
uniform gap is claimed.  No common-core/common-alpha estimate,
Hamiltonian-to-OS/KMS/GNS identification, physical mass gap, continuum, C6,
Sector-A or Pre-A closure follows.  No tier change, negative result or PDF is
issued.

The manifest, certificate, scope note, primary/independent/hostile scripts,
integrated verifier, Lean entrypoint and saved run artefacts are the complete
finite record.
