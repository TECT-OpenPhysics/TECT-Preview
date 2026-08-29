# R-413 Mellin heat-trace bridge note

R-413 is a finite, claim-nonbearing T0 checkpoint extending the R-412 mixed
IR/UV spectral envelope.  For a positive ordered spectrum and any interior
split, the exact finite identity at `tau>0` is

```
tr(W^+) = integral_0^tau sum_k exp(-t lambda_k) dt
          + sum_k exp(-tau lambda_k)/lambda_k.
```

The remainder is nonnegative.  The R-412 lower envelopes give a finite head
heat sum and the safe continuous tail
`C_UV alpha_UV Gamma(alpha_UV)t^(-alpha_UV)`.  Because every declared UV
exponent is below one, its integral from zero to `tau` is finite.  The late
remainder is bounded by the finite lower-envelope sum at `tau`.

The full volume-two grid has seven cutoff systems, 2688 contexts and 21120
conditional rows.  Primary passes `212594/212594`, independent passes
`149230/149230`, hostile passes `8/8`, integrated verification passes `44/44`,
and Lean R413 compiles.  The inverse trace is in
`[0.44413751605172147,2.0052069566897663]`; the minimum continuous-UV heat
slack is `2.4381603017647795e-05`, the minimum short-budget slack is
`0.1831599576706407`, and the maximum Mellin residual is
`1.7763568394002505e-15`.

The hostile lane rejects omission of the UV or IR terms, the wrong time power,
the wrong mode power, reversed time ordering, a negative Mellin remainder sign
and `alpha_UV=1`.  These are finite formula checks only.  A row-wise best
profile is not a common split rule, and the finite grid does not establish a
uniform heat budget.

Next gate: derive a fixed or analytically controlled split and uniform IR/UV
constants on one Hamiltonian common core, then transfer this heat budget to
the R-399 shell and combine it with R-406.  No physical, continuum, C6,
Sector-A or Pre-A conclusion is claimed.
