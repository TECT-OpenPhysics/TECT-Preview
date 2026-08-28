# R-409 resistance-trace note

R-409 is a finite, claim-nonbearing T0 checkpoint.  Writing
`W=D_pi^(-1/2)L D_pi^(-1/2)` and `u=sqrt(pi)`, the weighted unordered pair
vectors form the projector `I-u*u^T`.  Consequently the R-408 resistance
average is exactly the normalized Green trace

```
sum_(x<y) pi_x*pi_y*R_xy = tr(W^+) = sum_(k>0) 1/lambda_k(W).
```

The same finite spectral sum is the integrated heat trace
`int_0^infinity (tr(exp(-tW))-1) dt`.  This is an identity for each connected
finite graph; it is not a uniform-limit assertion.

The primary audit passes `106990/106990` assertions over `7` volume-two
cutoffs, `2688` contexts and `21120` conditional rows.  The independent lane
passes `106990/106990`, the hostile lane `6/6`, the integrated verifier `37/37`,
and Lean R409 compiles.  The resistance-average and trace ranges are both
`[0.44413751605180657,2.0052069566897672]`; the maximum direct identity
residual is `2.537969834293108e-12`.

The hostile lane rejects directed-pair doubling, an unnormalized-Laplacian
trace, a one-mode-only shortcut, and the disconnected diagonal-q mutation.
The next obligation is a cutoff/volume/phase/exhaustion-uniform Green-trace
bound on a common Hamiltonian core and its transfer to the R-399 shell.  No
claim tier changes and no physical, continuum, C6, Sector-A or Pre-A result is
claimed.
