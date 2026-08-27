# Q3LOCK local Q2 modular-centering boundary

R-372 gives a sharper finite target for the R-371 critical-theta route.  In
the eigenbasis of the doubled-bond Gibbs generator, subtract the bond-Gibbs
mean `m=Tr(rho_bond X)` from the moved witness `X`.  The Kubo--Mori shell is
unchanged because the subtraction changes only zero-transition-energy
diagonal entries.  Its R-371 row-sum control is therefore

```text
N_(1/2)^2 <= (4/beta) Var_(rho_bond)(X)
```

rather than the raw second-moment bound.  Primary and independent R-372 each
pass 17002/17002 assertions over 2816 all-prefix contexts, integrated passes
114/114, and Lean R372 passes.  The raw maximum is 44.58328971021096 and the
variance maximum is 41.64826651661874; the edge d=3..6 variance maxima are
2.733031855844076, 3.4283208579615874, 4.703343964629605 and
41.64826651661874.  The centering identity error is at most 1.421e-14 and
the shell invariance error is zero in the stored run.

This is finite algebra plus a finite actual-Q3 proxy stress only.  The edge
growth leaves source/volume/cutoff-uniform variance, common core, common
alpha, global KMS, OS/KMS/GNS dynamics, gap, continuum, C6, Sector-A and
Pre-A open.  The local doubled-bond Gibbs proxy is not the full interacting
state, and no PDF is issued at this intermediate checkpoint.
