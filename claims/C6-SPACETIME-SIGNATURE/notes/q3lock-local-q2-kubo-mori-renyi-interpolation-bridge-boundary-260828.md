# R-380 Renyi interpolation bridge boundary

R-380 expands the R-379 beta/2 two-slice channel into a modular-frequency
weighted interpolation.  In a finite Gibbs eigenbasis, for centered Hermitian
`X`, define

```text
G(s)=sum_ij |log(p_i)-log(p_j)| p_i^s p_j^(1-s) |X_ij|^2.
```

Hermitian symmetry gives `G(s)=G(1-s)`.  The continuous logarithmic-mean
identity gives

```text
integral_0^1 G(s) ds = sum_ij |p_i-p_j| |X_ij|^2,
```

while `G(1/2)` is the beta/2 modular two-slice term and `G(0)=G(1)` is the
endpoint modular-frequency moment.  Convexity gives the finite envelopes

```text
G(1/2) <= integral_0^1 G(s) ds <= (G(0)+G(1))/2,
G(s) <= (1-s)G(0)+sG(1).
```

The primary and independent lanes cover 2,560 all-prefix actual-Q3 contexts;
the integrated verifier passes 69/69 and Lean R380 compiles.  The primary
largest meaningful midpoint/integral ratio is 0.9594837421464463 and the
largest integral/endpoint ratio is 0.9240035972845281.  These are finite
diagnostics: the endpoint moment is not controlled by the midpoint alone.

This package does not prove a source-, volume-, cutoff- or beta-uniform
endpoint estimate, a common unbounded core, direct D/delta-D Cauchy, common
alpha, OS/KMS/GNS dynamics, a mass gap, continuum, C6, Sector-A or Pre-A.
