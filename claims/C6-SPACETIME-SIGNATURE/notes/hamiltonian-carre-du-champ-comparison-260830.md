# R-402 — finite Hamiltonian carré-du-champ comparison

R-402 / EXP-001247 is a T0 claim-nonbearing finite checkpoint following
R-401.  It compares the physical-coordinate conditional form with the form
induced by the actual Q3 kinetic term on the finite history likelihood rows.

For `F=f(q)` in the one-site coordinate basis, the tested forms are

```
D_q(f)   = sum min(pi_k,pi_(k+1))*((f_(k+1)-f_k)/(x_(k+1)-x_k))^2
E_kin(f) = (2 chi)^(-1) Tr(diag(pi)[p,F]^*[p,F]).
```

The coordinate quadratic and quartic potentials and one Q3 bond commute with
`F`; consequently the finite first carré-du-champ is kinetic in this declared
observable class.  Over the five R-399 systems, all source/history signs,
split orders, prefixes, adjoints and both orientations, the primary lane
passes `5410/5410` on `3584` contexts and `71680` rows; the independent lane
passes `1815/1815`, the hostile lane `4/4`, the integrated verifier `33/33`,
and Lean R402 compiles.  The nonzero-row ratio `E_kin/D_q` lies in
`[1.0087179063711833, 11.074061483593928]`; the largest potential commutator
residual is zero on this finite coordinate tensor basis.

The hostile `p -> q` mutation yields a zero commutator while the genuine
kinetic form is nonzero on a selected history row, so the identification is
structural.  These values are finite diagnostics only.  They do not prove a
cutoff-, volume-, source-, phase- or shape-uniform comparison, an invariant
common core, common alpha, OS/KMS/GNS dynamics, a gap, continuum, C6,
Sector-A or Pre-A closure.  The next gate is the analytic common-core
comparison and its increasing-cutoff/phase stress.
