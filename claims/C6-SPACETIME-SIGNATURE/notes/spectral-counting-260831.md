# R-410 spectral-counting note

R-410 is a finite, claim-nonbearing T0 checkpoint.  Starting with the R-409
normalized Green trace, order the positive eigenvalues of
`W=D_pi^(-1/2)L D_pi^(-1/2)` and set
`c2=min_k lambda_k/k^2`.  Row by row,

```
lambda_k >= c2*k^2,
tr(W^+) <= (sum_(k<d) k^(-2))/c2 <= pi^2/(6*c2).
```

The primary and independent lanes each pass `191473/191473` assertions over
7 systems, 2688 contexts and 21120 conditional rows.  The mode constant is
in `[0.19600096779786974,1.2046269661757882]`; the trace is in
`[0.44413751605172147,2.0052069566897663]`; and the finite zeta envelope is
in `[1.2140470537996502,7.467366756170776]`.  The hostile lane passes `6/6`,
the integrated verifier `46/46`, and Lean R410 compiles.

The hostile checks reject unsorted mode indices, inserting a linear `k`
constant into a quadratic envelope, Fiedler-only truncation, and the
disconnected diagonal-generator mutation.  The next obligation is a positive
`c2` lower bound uniform in cutoff, volume, phase and exhaustion on one
Hamiltonian common core, followed by transfer to the R-399 shell.  No claim
tier changes and no physical, continuum, C6, Sector-A or Pre-A result is
claimed.
