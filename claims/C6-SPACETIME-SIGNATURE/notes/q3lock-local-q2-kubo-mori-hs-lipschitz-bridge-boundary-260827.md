# R-376 Hilbert-Schmidt functional-calculus bridge boundary

R-376 tests the operator-level next step after the R-375 scalar
Matsubara budget.  Let

```text
f_beta(t) = (2/beta) tanh(beta |t|/2).
```

The scalar function is 1-Lipschitz.  For a finite self-adjoint Liouvillian,
the relevant candidate interface is the Schatten-2 comparison

```text
||f_beta(L)-f_beta(L')||_2 <= ||L-L'||_2,
```

which is the natural gap-free norm in which eigenvector rotations can be
paid without a minimum spectral spacing.  The N-term Matsubara partial
function has the corresponding finite budget `L_N=sum_(n<N)8/omega_n^2`.

The primary and independent lanes build a small actual-Q3 edge doubled-bond
Liouvillian at cutoff 2, perturb it with a noncommuting local term at two
declared scales, and compare exact and partial spectral functional calculi
in Frobenius norm.  They also link the source R-375 run and its 2816
all-prefix context count.  Lean R376 proves only the scalar absolute-value
nonexpansiveness used at the cusp; the full Schatten-2 theorem is recorded
as an analytic interface and is not claimed as formalized here.

This is T0 and claim-nonbearing.  The finite stress does not establish an
operator-norm Lieb--Robinson estimate, spatial locality, a common core,
common alpha, KMS/GNS dynamics, a gap, continuum, C6, Sector-A or Pre-A.
