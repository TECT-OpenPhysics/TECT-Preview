# R-377 resolvent telescoping budget boundary

R-377 records the exact finite resolvent identity used to separate the
positive odd-Matsubara kernel into a resolvent-controlled term and an
absolute-value square-root term.  With

```text
R_n(A)=(omega_n^2 I+beta^2 A^2)^(-1),
```

the identity is

```text
R_n(B)-R_n(A)=R_n(B) beta^2(A^2-B^2) R_n(A).
```

The primary and independent scripts check this identity, positivity and the
finite operator-norm ceiling on the local V=2 cutoff-2 commutator fixture for
both beta values, both perturbation scales and all 64 odd modes.  The
integrated verifier links the R-376 source run, checks distinct source hashes,
and compiles Lean R377.

The resulting finite interface is a gap-free summable budget for the
resolvent component.  The full kernel difference is decomposed as

```text
8(|B|-|A|)R_n(B) + 8|A|(R_n(B)-R_n(A)).
```

The first term has a measured nonzero finite norm and is retained as an
explicit square-root/eigenvector-rotation debt.  Therefore this result does
not prove the general Schatten or operator-norm theorem, spatial resolvent
locality, source/volume/cutoff uniformity, a common polynomial core, a common
real-time alpha, KMS/GNS dynamics, a gap, a continuum, C6, Sector-A or Pre-A.
