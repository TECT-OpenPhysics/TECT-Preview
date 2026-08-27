# Q3LOCK local-Q2 spectral-gap Duhamel boundary

EXP-001207 / R-365 adds a finite-time form to the R-364 spectral commutant
reduction. For `U_t=exp(-i t B)` with Hermitian `B`, the spectral blocks obey

```text
||U_t* X U_t-X||_HS^2
 = sum_(a,b) |exp(i t(lambda_a-lambda_b))-1|^2 ||P_a X P_b||_HS^2
 <= t^2 ||[B,X]||_HS^2.
```

For a density matrix `omega`, Hilbert--Schmidt Cauchy gives the state-trace
corollary with an additional factor `||omega||_HS <= 1`. The B-commuting blocks
may first be removed by spectral pinching, including degenerate bond-energy
blocks.

The primary and non-importing independent lanes cover all 256 R-362 finite
contexts and pass 777/777 and 776/776 assertions. Integrated verification is
49/49 and Lean R365 passes. The largest finite-time/bound ratio is 0.999422;
the maximum finite-time change is 0.267414 against a Duhamel bound of 0.267991;
the maximum state-trace change is 1.125e-7 against a bound of 0.035551.

This remains a finite unweighted Hilbert--Schmidt result. A uniform local
collar, common alpha, phase-weight preservation, OS/KMS/GNS reconstruction,
mass gap, continuum, C6, Sector-A and Pre-A remain open.
