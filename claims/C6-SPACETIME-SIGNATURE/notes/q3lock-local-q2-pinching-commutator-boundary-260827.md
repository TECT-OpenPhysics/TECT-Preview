# Q3LOCK local-Q2 pinching commutator boundary

EXP-001205 / R-363 gives the next finite FI-2b reduction. In the doubled
coordinate basis, let `D` be full coordinate pinching, `omega=rho tensor rho`,
and `B` a Hermitian coordinate-diagonal bond generator. For a moved local
collision witness `X`, define `X_0=X-Tr(omega X)I` and
`X_perp=X_0-D(X_0)`. Then

```text
[B,X] = [B,X_perp]
```

exactly. The two-sided state-weighted Hilbert--Schmidt Cauchy inequality is

```text
|Tr(omega [B,X])|
  <= sqrt(Tr(omega B^2))
       * (sqrt(Tr(X_perp* omega X_perp))
          + sqrt(Tr(omega X_perp* X_perp))).
```

The finite primary and non-importing independent lanes cover every prefix,
both split orientations, time signs, history adjoints, beta values and local
sites on the R-362 `V=2`, cutoff `3,4` fixture. They pass `778/778` and
`519/519` assertions, respectively; the integrated verifier and Lean R363
also pass.

This is a finite exact reduction, not a local collar theorem. The remaining
obligation is a cutoff-, source-, volume-, prefix- and shape-uniform estimate
for the off-diagonal weighted norms. A finite nonzero off-diagonal term remains,
so no claim that all bond influence disappears is valid. Common alpha,
phase-weight preservation, OS/KMS/GNS reconstruction, a gap, continuum, C6,
Sector-A and Pre-A remain open.
