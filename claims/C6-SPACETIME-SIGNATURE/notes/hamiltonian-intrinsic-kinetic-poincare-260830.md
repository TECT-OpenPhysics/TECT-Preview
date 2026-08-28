# R-404 - intrinsic kinetic graph Poincare stress

R-404 / EXP-001249 is a T0 claim-nonbearing finite route checkpoint following
R-403.  The R-403 upper ratio grew strongly because the physical-coordinate
form becomes small in selected high-cutoff rows.  R-404 therefore removes that
comparison step and tests the actual kinetic form directly.

For a conditional q-law `pi` and the momentum matrix `p` in the q basis, set

```
c_ij = (pi_i + pi_j)|p_ij|^2/(2 chi),
L = diag(sum_j c_ij) - (c_ij).
```

The trace commutator identity gives `E_kin(f)=f^T L f`.  The finite generalized
eigenvalue `gap(pi)` of `(L,diag(pi))` is then tested against
`Var_pi(f)` on every actual likelihood row.

On the volume-two actual Q3 fixture with dimensions `3,4,5,6,8,10,12`, beta
`{1/2,1,2}`, both source/history signs, both split orders, all prefixes, both
history adjoints and both collar orientations, the primary lane passes
`1398/1398` over `2688` contexts and `21120` rows.  The independent lane passes
`1388/1388`, the hostile lane `6/6`, the integrated verifier `37/37`, and Lean
R404 compiles.  The intrinsic gap range is
`[0.7570174175402339,5.647863075935321]`; its minimum remains positive at each
declared cutoff, from `0.7570174175402339` at `d=3` to `2.4233910464474144` at
`d=12`.

This is evidence that an intrinsic-form route is viable on the finite ladder,
not a uniform lower-bound theorem.  The generalized eigenvalues, graph
connectivity, conditional laws and finite matrices still require an analytic
cutoff-independent common-core treatment.  The q-for-p hostile mutation has
zero edges, confirming that the nonzero gap is tied to the kinetic momentum
operator rather than the diagonal coordinate multiplier.

No phase/volume/exhaustion uniformity, common core, common alpha, OS/KMS/GNS
dynamics, mass gap, continuum, C6, Sector-A or Pre-A closure follows.  The next
gate is the analytic intrinsic-gap lower bound and its transfer to the R-399
shell without reintroducing the unstable coordinate upper comparison.
