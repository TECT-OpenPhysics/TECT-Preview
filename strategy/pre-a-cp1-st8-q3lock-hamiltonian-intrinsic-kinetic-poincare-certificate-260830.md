# R-404 certificate - intrinsic kinetic graph Poincare stress

## Scope

R-404 is a T0, claim-nonbearing finite checkpoint under EXP-001249.  It
continues the R-403 cutoff stress with a route change: use the actual kinetic
carre-du-champ as the conditional Dirichlet form instead of comparing it to a
cutoff-sensitive nearest-neighbour coordinate form.

For a positive conditional law `pi` and the one-site momentum matrix `p` in
the q basis, the tested symmetric conductance is

```
c_ij = (pi_i + pi_j) |p_ij|^2 / (2 chi),
L = diag(sum_j c_ij) - (c_ij),
gap(pi) = lambda_1(diag(pi)^(-1/2) L diag(pi)^(-1/2)).
```

The finite test checks the exact graph identity
`E_kin(f) = f^T L f` and the finite Poincare inequality
`E_kin(f) >= gap(pi) Var_pi(f)` for every actual Q3 likelihood row.

## Verification

The volume-two fixture uses oscillator dimensions `3,4,5,6,8,10,12`, beta in
`{1/2,1,2}`, both source signs, both history signs, both split orders, every
prefix, both history adjoints and both collar orientations.  The primary lane
passes `1398/1398` assertions over `7` systems, `2688` contexts and `21120`
conditional rows.  Of the rows, `15840` have variance above the declared
`1e-20` floor and `5280` are constant-row diagnostics.

The intrinsic graph gap range over all rows is
`[0.7570174175402339,5.647863075935321]`.  The minimum gap by cutoff is:

| cutoff | minimum gap | maximum gap |
|---:|---:|---:|
| 3 | 0.7570174175402339 | 2.481985895256327 |
| 4 | 0.7872756441265598 | 2.833778687459352 |
| 5 | 1.1950962017934934 | 2.3636300623347872 |
| 6 | 1.4721452785784677 | 3.8750382074539487 |
| 8 | 1.794632993768257 | 3.7780559388526536 |
| 10 | 2.1313269196275257 | 4.55943819352713 |
| 12 | 2.4233910464474144 | 5.647863075935321 |

The independent lane passes `1388/1388` and agrees with the aggregate and
per-cutoff fields within `5e-5`.  The hostile lane passes `6/6`: the genuine
momentum graph has positive gaps `0.757017...` and `2.91443...` at the first
and last cutoffs, while replacing `p` by the diagonal q operator leaves zero
edges.  The integrated verifier passes `37/37`, and Lean R404 compiles.

## Adversarial review

1. **Form identity.**  The trace commutator form and graph quadratic form are
   computed independently and compared row by row; the graph identity is not
   assumed from notation.
2. **Generalized eigenvalue.**  The mass matrix is the conditional law, the
   constant mode is checked at zero, and the first positive eigenvalue is used;
   disconnected or nonfinite graphs fail the lane.
3. **Constant rows and tiny scales.**  Rows below the variance floor are
   counted but not used for kinetic/variance ratios.  The Poincare residual is
   still checked on every row.
4. **Independent reconstruction.**  The independent lane rebuilds the finite
   oscillator model, Gibbs states, prefixes, conditional rows and spectrum
   without importing the primary implementation.
5. **Structural mutation.**  The q-for-p mutation is forced through the same
   conductance construction; because q is diagonal in the q basis it has no
   edges, while the genuine momentum graph remains connected.
6. **QFT promotion.**  A positive finite graph gap is not a cutoff-independent
   common-core estimate and supplies no phase, volume, exhaustion, OS/KMS/GNS,
   mass-gap, continuum, C6, Sector-A or Pre-A closure.

## Decision and next gate

R-404 advances a new finite route: the kinetic form itself has a well-defined
   intrinsic conditional graph and a positive finite Poincare gap across the
   R-403 cutoff ladder.  This avoids the unstable R-402 upper comparison at
   the diagnostic level.  It remains an advanced finite interface only; the
   ratio profile and graph gap are not uniform theorems.

The next mathematical gate is an analytic lower bound for this momentum-
weighted graph on a cutoff-independent Hamiltonian common core, with source,
phase, volume and exhaustion uniformity.  That bound must then be connected to
the actual R-399 shell and tested beyond the two-site finite fixture.

## Boundary

No cutoff-independent or volume-independent gap, common core, common alpha,
Hamiltonian-to-OS/KMS identification, GNS gap, continuum, C6, Sector-A or
Pre-A result is claimed.  Finite graph positivity is a route diagnostic only.

Proven in the manifest, primary/independent/hostile scripts, integrated
verifier, Lean entrypoint, scope note and saved run artefacts.
