# R-403 — increasing-cutoff Hamiltonian carré-du-champ stress

R-403 / EXP-001248 is a T0 claim-nonbearing finite stress following R-402.
It tests whether the actual Q3 kinetic carré-du-champ can be compared with
the physical-coordinate conditional form by a cutoff-independent upper
constant.  For `F=f(q)` in the one-site q basis,

```
D_q(f)   = sum min(pi_k,pi_(k+1))*((f_(k+1)-f_k)/(x_(k+1)-x_k))^2
E_kin(f) = (2 chi)^(-1) Tr(diag(pi)[p,F]^*[p,F]).
```

The volume-two Q3 fixture uses dimensions `3,4,5,6,8,10,12`, beta
`{1/2,1,2}`, both source/history signs, both split orders, all prefixes,
both history adjoints and both collar orientations.  The primary lane passes
`1397/1397` over `2688` contexts and `21120` rows; the independent lane passes
`1379/1379`, the hostile lane `7/7`, the integrated verifier `37/37`, and Lean
R403 compiles.  Of the rows, `15840` have nonzero `D_q`; their ratio range is
`[1.0461038216925114,109929.13074605557]`.  The cutoff maximum grows from
`4.456994387884469` at `d=3` to `109929.13074605557` at `d=12`, a factor of
`24664.408607934973`.

This is a finite-cutoff stress, not a divergence result.  It blocks automatic
promotion of the R-402 finite interval to a two-sided uniform comparison, but
it does not rule out a separately proved one-sided lower estimate or a
different common-core normalization.  Rows below the declared denominator
floor are counted rather than converted into ratios.  The hostile `p -> q`
mutation vanishes while a genuine late kinetic row is positive, and the
independent lane reconstructs the fixture without importing the primary
implementation.

No cutoff/volume/phase/exhaustion uniformity, common core, common alpha,
OS/KMS/GNS dynamics, gap, continuum, C6, Sector-A or Pre-A closure follows.
The next gate is an analytic direction-specific comparison on a
cutoff-independent Hamiltonian common core, followed by phase and exhaustion
stress before any R-399 shell-transfer promotion.
