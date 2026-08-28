# R-408 certificate - tree-independent effective-resistance bound

## Scope

R-408 is a T0, claim-nonbearing finite checkpoint under EXP-001253.  It
replaces the selected-tree constant of R-407 by the Green kernel of the same
intrinsic momentum conductance graph.  For a conditional law `pi`, symmetric
conductance Laplacian `L`, and Moore--Penrose inverse `L^+`, define

```
R_xy = (e_x-e_y)^T L^+ (e_x-e_y)
Rbar_pi = sum_{x<y} pi_x*pi_y*R_xy
```

The pairwise Cauchy--Schwarz identity gives the finite inequality
`Var_pi(f) <= Rbar_pi * E(f)`, hence `Rbar_pi**(-1)` is a lower bound for
every finite test function.  The sum is over unordered pairs, so no factor of
two is inserted.  The constant depends only on `L^+`; no spanning tree or
path choice enters it.

## Verification

The volume-two fixture uses oscillator dimensions `3,4,5,6,8,10,12`, beta in
`{1/2,1,2}`, both source signs, both history signs, both split orders, all
prefixes, both history adjoints and both collar orientations.  The primary
lane passes `43630/43630` assertions over `7` systems, `2688` contexts and
`21120` conditional rows.  The independently reconstructed lane passes
`43630/43630` with aggregate and per-cutoff fields agreeing within `5e-6`;
the hostile lane passes `6/6`; the integrated verifier passes `37/37`; and
Lean R408 compiles.

Across all rows, the exact intrinsic graph gap is
`[0.7570174175402339,5.647863075935321]`.  The resistance average is
`[0.44413751605180657,2.0052069566897672]`, giving the tree-independent
finite lower bound
`[0.49870164107689835,2.251554898783544]`.  The smallest positive
Laplacian eigenvalue is `0.020747640155030216`, the largest pair resistance is
`85.99011817086337`, and the minimum residual
`E-Rbar_pi**(-1)*Var` is `-1.0641664309263875e-25` (roundoff).
For comparison, the R-407 maximum-tree bound ranges over
`[0.2613815898804392,2.508986944248343]` on the same rows.

## Adversarial review

1. **Pair normalization.**  A three-node unit path has resistances `1,1,2`,
   so `Rbar=4/9` and the correct bound is `9/4`.  The doubled candidate has
   residual `-1` on `(1,0,-1)` and is rejected.
2. **Pseudoinverse zero mode.**  The computation requires exactly `d-1`
   eigenvalues above the declared `1e-14` floor and rejects a disconnected
   Laplacian instead of inverting its zero mode.
3. **Generator support.**  Replacing the momentum matrix by diagonal `q`
   produces zero off-diagonal conductances and zero positive spectrum; the
   hostile lane catches this mutation.
4. **Conditioning and numerical floors.**  Every conditional probability,
   resistance, Laplacian eigenvalue, likelihood residual and pair average is
   checked for finiteness; residuals are required to be no smaller than
   `-1e-8`.
5. **Independent reconstruction.**  The second lane rebuilds the oscillator
   Hamiltonian, Gibbs states, history prefixes, coordinate rows, conditional
   graphs and resistance sums without importing the R-408 primary module.
6. **Uniform promotion.**  A positive finite resistance envelope does not
   establish a cutoff-, volume-, phase- or exhaustion-uniform Green-kernel
   estimate, a common core, GNS gap, continuum, C6, Sector-A or Pre-A closure.

## Decision and next gate

R-408 advances a tree-independent finite interface.  The next analytic gate
is an upper bound on the weighted Green-kernel/resistance average on one
Hamiltonian common core, uniform in cutoff, volume, phase and exhaustion,
followed by transfer to the R-399 shell and combination with the R-406
Schur residual split.  If the resistance average diverges or the positive
Laplacian spectrum collapses under a validated stress, retain this as a finite
diagnostic and redesign the route.

## Boundary

No cutoff-independent, volume-independent, phase-uniform or exhaustion-
uniform gap is claimed.  No common-core/common-alpha estimate,
Hamiltonian-to-OS/KMS/GNS identification, physical mass gap, continuum, C6,
Sector-A or Pre-A closure follows.  No tier change, negative result or PDF is
issued.

The manifest, certificate, scope note, primary/independent/hostile scripts,
integrated verifier, Lean entrypoint and saved run artefacts are the complete
finite record.
