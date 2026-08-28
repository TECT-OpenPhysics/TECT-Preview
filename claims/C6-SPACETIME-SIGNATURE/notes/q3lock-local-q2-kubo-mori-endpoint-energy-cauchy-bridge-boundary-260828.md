# R-381 endpoint modular moment to energy Cauchy bridge boundary

R-381 converts the R-380 endpoint modular-frequency moment into an energy
moment.  For finite Gibbs probabilities `p_i=Z^(-1) exp(-beta E_i)`,

```text
|log(p_i)-log(p_j)| = beta |E_i-E_j|.
```

For centered Hermitian `X`, define

```text
D_1=sum_ij p_i |log(p_i)-log(p_j)| |X_ij|^2
M_0=sum_ij p_i |X_ij|^2
M_2=sum_ij p_i (E_i-E_j)^2 |X_ij|^2.
```

Finite state-weighted Cauchy--Schwarz gives `D_1<=beta sqrt(M_0 M_2)`.
The primary and independent lanes cover 2,560 all-prefix actual-Q3 contexts;
the integrated verifier passes 61/61 and Lean R381 compiles.  The largest
endpoint-to-Cauchy ratio is 0.07927511037274983, with a maximum Cauchy
violation of -2.290857218268337e-16.

This package does not prove a source-, volume-, cutoff- or beta-uniform bound
for `M_0` or `M_2`, a common unbounded core, direct D/delta-D Cauchy, common
alpha, OS/KMS/GNS dynamics, a mass gap, continuum, C6, Sector-A or Pre-A.
