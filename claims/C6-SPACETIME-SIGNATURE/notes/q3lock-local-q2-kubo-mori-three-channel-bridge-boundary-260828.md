# R-379 three-channel half-density bridge boundary

R-379 refines the R-378 half-density interface.  In the bond-Hamiltonian
eigenbasis set `R=rho^(1/2)`, `Q=rho^(1/4)`, and let `X` be the centered
Hermitian moved witness.  Define

```text
L=||R X||_2^2,
Rr=||X R||_2^2,
T=||Q X Q||_2^2.
```

Direct finite matrix multiplication gives

```text
||{R,X}||_2^2=L+Rr+2T,
||[R,X]||_2^2=L+Rr-2T,
||{R,X}||_2^2+||[R,X]||_2^2=2(L+Rr),
0<=T<=(L+Rr)/2.
```

The `T` channel is a beta/2 Euclidean two-slice term.  It is not removable:
on the finite grid it reaches the arithmetic--geometric envelope and tracks
the large anticommutator cost.

Primary and independent scripts cover 2,560 all-prefix actual-Q3 contexts on
the edge and square fixtures, and Lean R379 checks the scalar channel
identities and AM--GM envelope.  This is a finite proxy-state interface only.
It does not prove a source-, volume-, cutoff- or beta-uniform estimate for any
channel, a common unbounded core, direct `D,delta D` Cauchy, common alpha,
OS/KMS/GNS dynamics, a mass gap, continuum, C6, Sector-A or Pre-A.
