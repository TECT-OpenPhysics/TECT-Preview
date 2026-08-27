# Q3LOCK local-Q2 spectral-commutant boundary

EXP-001206 / R-364 refines the R-363 FI-2b reduction. For a finite Hermitian
bond generator `B=sum_lambda lambda P_lambda`, use the spectral pinching
`E_B(X)=sum_lambda P_lambda X P_lambda`. With
`X_0=X-Tr(omega X)I` and `X_perp=X_0-E_B(X_0)`,

```text
[B,X]=[B,X_perp]
```

and

```text
|Tr(omega [B,X])|
 <= sqrt(Tr(omega B^2))
      * (sqrt(Tr(X_perp* omega X_perp))
         +sqrt(Tr(omega X_perp* X_perp))).
```

The primary and non-importing independent lanes cover all 256 R-362 finite
contexts and pass 777/777 and 776/776 assertions. Integrated verification is
51/51 and Lean R364 passes. On the declared fixture the spectral residual is
slightly smaller than the coordinate residual in unweighted Frobenius norm,
but remains nonzero; weighted-norm uniformity is not implied.

This is a finite commutant refinement only. A finite-time collar estimate,
source/cutoff/volume/prefix/shape uniformity, common alpha, OS/KMS/GNS,
mass gap, continuum, C6, Sector-A and Pre-A remain open.
