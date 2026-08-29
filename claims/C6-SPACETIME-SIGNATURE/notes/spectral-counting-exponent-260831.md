# R-411 spectral-counting exponent note

R-411 is a finite, claim-nonbearing T0 checkpoint.  For the ordered positive
eigenvalues of `W = D_pi^(-1/2) L D_pi^(-1/2)`, and any declared
`0 < alpha < 1`, define
`C_alpha = max_k k/lambda_k^alpha`.  The finite implication is

```
lambda_k >= (k/C_alpha)^(1/alpha),
tr(W^+) <= C_alpha^(1/alpha) sum_(k<d) k^(-1/alpha).
```

An integral tail with exponent `1/alpha > 1` gives the corresponding infinite
comparison.  The primary and independent lanes each pass `508279/508279`
assertions over 7 systems, 2688 contexts and 21120 conditional rows.  The
declared exponents are `1/2, 2/3, 3/4, 4/5, 9/10`; every finite profile is
positive and the finite-to-infinite tail comparison passes.  The retained
quadratic cross-check has mode constant range
`[0.19600096779786974,1.2046269661757882]`, trace range
`[0.44413751605172147,2.0052069566897663]`, and finite zeta envelope range
`[1.2140470537996502,7.467366756170776]`.  The hostile lane passes `8/8`,
the integrated verifier `48/48`, and Lean R411 compiles.

The hostile lane rejects `alpha = 1`, unsorted modes, exponent-power
inversion, a linear shortcut inserted into a quadratic bound, Fiedler-only
truncation and a disconnected diagonal-generator mutation.  The next
obligation is a common-core bound for one exponent and its constant across
cutoff, volume, source, phase and exhaustion, followed by R-399 shell
transfer and the R-406 Schur split.  No physical, continuum, C6, Sector-A or
Pre-A result is claimed.
