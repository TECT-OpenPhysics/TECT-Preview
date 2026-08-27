# R-374 odd-Matsubara resolvent-layer boundary

R-374 introduces a QFT-facing interface for the exact R-373 kernel.  With
`x=beta Delta/2`, use the positive partial-fraction expansion

```text
tanh(x) = sum_(n>=0) 8*x / ((2*n+1)^2*pi^2 + 4*x^2),
```

so that

```text
kappa_beta(Delta)
  = sum_(n>=0) 8*Delta / (((2*n+1)*pi)^2 + beta^2*Delta^2).
```

Every layer is nonnegative and is a resolvent-type function of the absolute
Liouvillian transition energy.  The first `N` layers are monotone below the
exact kernel.  For `N>=1`, a simple finite tail envelope used by the scripts is

```text
0 <= kappa_beta(Delta)-kappa_beta^(N)(Delta)
   <= 4*Delta / (pi^2*(2*N-1)).
```

The bound is intentionally elementary; it is not claimed to be the sharpest
Matsubara tail estimate.

Primary and independent lanes evaluate the partial sum on every R-373 history
context and verify the positive shell remainder.  Lean R374 proves positivity
of each symbolic odd-frequency layer and monotonicity of finite partial sums;
it does not formalize the infinite `tanh` series, matrix spectra, traces or
limits.

The finite result is T0 and claim-nonbearing.  The next analytic obligation is
to control each positive resolvent layer uniformly on a common Hamiltonian
core, then sum the layers without reintroducing the cutoff growth seen at the
edge.  No common-alpha, KMS/GNS, gap, continuum, C6, Sector-A or Pre-A closure
follows here.
