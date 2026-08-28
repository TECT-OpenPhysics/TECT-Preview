# R-378 half-density Hellinger bridge boundary

R-378 introduces a finite two-sided interface for the absolute theta-half
Kubo--Mori shell.  In a bond-Hamiltonian eigenbasis, write
`rho=diag(p_i)`, `R=rho^(1/2)`, and let `X` be the centered Hermitian moved
witness.  Then

```text
[R,X]_ij=(sqrt(p_i)-sqrt(p_j)) X_ij,
{R,X}_ij=(sqrt(p_i)+sqrt(p_j)) X_ij,
|p_i-p_j|=|sqrt(p_i)-sqrt(p_j)| (sqrt(p_i)+sqrt(p_j)).
```

The shell admits the finite geometric-mean estimate

```text
S_(1/2) <= (2/beta)||[R,X]||_2 ||{R,X}||_2
        <= beta^(-1)(||[R,X]||_2^2+||{R,X}||_2^2).
```

For Hermitian `X`, the final sum is exactly `4 Tr(rho X^2)`, so the bridge
recovers the R-371 arithmetic second-moment bound while exposing a separate
half-density commutator debt and its dual anticommutator cost.

The primary and independent lanes cover 2,816 all-prefix finite actual-Q3
contexts on the edge and square fixtures.  Lean R378 checks the scalar pair
factorization and arithmetic envelope.  These are finite matrix/proxy-state
checks only.  The half-density commutator and anticommutator estimates are not
uniform in source, volume, cutoff or beta; no common unbounded core, direct
`D,delta D` Cauchy theorem, common alpha, OS/KMS/GNS transfer, mass gap,
continuum, C6, Sector-A or Pre-A conclusion follows.
